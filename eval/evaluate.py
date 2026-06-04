"""Run the broad real-world orchestrator evaluation.

This evaluation is separate from the SHACL/JSON accuracy benchmarks used for
accuracy-based ranking. It measures the orchestrator as a system over a corpus
of real-world input schemas: for each source language, each input file, and each
target language, every discovered conversion path is executed once. The runner
stores final and intermediate outputs and creates review CSV files for human
annotation.

Input corpus layout:

    eval/real_world_inputs/
      JsonSchema/
        example_01.schema.json
      Xsd/
      SHACL_TTL/
      LinkMl/
      MdModels/

Output layout:

    eval/orchestrator_outputs/
      runs/<run_id>/<source>/<input_stem>/<target>/path_001/
        metadata.json
        final_output.<ext> | error.txt
        steps/step_01_output.<ext>
      review/
        final_outputs.csv
        edge_outputs.csv

Human annotation:
    Fill the ``status`` column in both review CSVs with:
      G = good, L = lacking, I = invalid.
    The runner pre-fills I for failed/invalid outputs and leaves valid outputs
    blank for human inspection.
"""
from __future__ import annotations

import argparse
import csv
import json
import re
import sys
import time
import traceback
from dataclasses import asdict, dataclass
from datetime import datetime
from pathlib import Path
from typing import Iterable
from xml.etree import ElementTree

import yaml

EVAL_DIR = Path(__file__).resolve().parent
REPO_ROOT = EVAL_DIR.parent
SRC_DIR = REPO_ROOT / "src"
sys.path.insert(0, str(SRC_DIR))

from schema_conversion_orchestrator.application.conversion_service import ConversionService  # noqa: E402
from schema_conversion_orchestrator.converters.base import Converter  # noqa: E402
from schema_conversion_orchestrator.converters.registry import register_converters  # noqa: E402
from schema_conversion_orchestrator.domain.conversion_graph import find_paths  # noqa: E402
from schema_conversion_orchestrator.domain.conversion_types import ConversionPath, ConversionResult  # noqa: E402
from schema_conversion_orchestrator.domain.schema_types import SchemaLanguage  # noqa: E402


SOURCE_LANGUAGES = [
    SchemaLanguage.JsonSchema,
    SchemaLanguage.Xsd,
    SchemaLanguage.SHACL_TTL,
    SchemaLanguage.LinkMl,
    SchemaLanguage.MdModels,
]

TARGET_LANGUAGES = [
    SchemaLanguage.JsonSchema,
    SchemaLanguage.Xsd,
    SchemaLanguage.SHACL_TTL,
    SchemaLanguage.LinkMl,
    SchemaLanguage.MdModels,
]

INPUT_DIR = EVAL_DIR / "real_world_inputs"
OUTPUT_DIR = EVAL_DIR / "orchestrator_outputs"

LANGUAGE_EXTENSIONS = {
    SchemaLanguage.JsonSchema.value: ".schema.json",
    SchemaLanguage.Xsd.value: ".xsd",
    SchemaLanguage.SHACL_TTL.value: ".ttl",
    SchemaLanguage.SHACL_JSON_LD.value: ".jsonld",
    SchemaLanguage.LinkMl.value: ".yaml",
    SchemaLanguage.MdModels.value: ".md",
}

REVIEW_FIELDS = [
    "status",
    "automatic_valid",
    "source_language",
    "target_language",
    "input_file",
    "path_id",
    "path_rank",
    "path_count",
    "path_signature",
    "output_path",
    "notes",
]

EDGE_REVIEW_FIELDS = [
    "status",
    "automatic_valid",
    "source_language",
    "target_language",
    "input_file",
    "path_id",
    "path_signature",
    "step_index",
    "edge_signature",
    "edge_source_language",
    "edge_target_language",
    "converter_name",
    "library",
    "output_path",
    "notes",
]

FINAL_REVIEW_KEY_FIELDS = [
    "source_language",
    "target_language",
    "input_file",
    "path_signature",
]

EDGE_REVIEW_KEY_FIELDS = [
    "source_language",
    "target_language",
    "input_file",
    "path_id",
    "step_index",
    "edge_signature",
]


@dataclass
class StepRecord:
    step_index: int
    source_language: str
    target_language: str
    converter_name: str
    service_name: str
    library: str | None
    library_version: str | None
    library_url: str | None
    success: bool
    automatic_valid: bool
    output_path: str | None
    error: str | None
    duration_seconds: float


@dataclass
class AttemptRecord:
    source_language: str
    target_language: str
    input_file: str
    path_id: str
    path_rank: int | None
    path_count: int
    path_signature: str
    success: bool
    automatic_valid: bool
    final_output_path: str | None
    error_path: str | None
    failed_step_index: int | None
    duration_seconds: float
    steps: list[StepRecord]


def language_from_dir(name: str) -> SchemaLanguage:
    for language in SchemaLanguage:
        if language.value.lower() == name.lower():
            return language
    raise ValueError(f"Unknown schema-language directory: {name}")


def safe_name(value: str) -> str:
    return re.sub(r"[^A-Za-z0-9_.-]+", "_", value).strip("_")


def output_extension(language: str) -> str:
    return LANGUAGE_EXTENSIONS.get(language, ".txt")


def path_signature(path: ConversionPath) -> str:
    return " -> ".join(
        f"{conv.source_language.value}:{conv.target_language.value}:{conv.name}"
        for conv in path
    )


def edge_signature(converter: Converter) -> str:
    return f"{converter.source_language.value}:{converter.target_language.value}:{converter.name}"


def converter_library(converter: Converter) -> str:
    return converter.library or converter.name


def validate_output(schema: str | None, language: str) -> bool:
    if schema is None or not schema.strip():
        return False

    try:
        if language in {SchemaLanguage.JsonSchema.value, SchemaLanguage.SHACL_JSON_LD.value}:
            json.loads(schema)
            return True

        if language in {SchemaLanguage.LinkMl.value}:
            yaml.safe_load(schema)
            return True

        if language == SchemaLanguage.Xsd.value:
            ElementTree.fromstring(schema.encode("utf-8"))
            return True

        if language == SchemaLanguage.SHACL_TTL.value:
            try:
                from rdflib import Graph
            except ImportError:
                return bool(schema.strip())
            Graph().parse(data=schema, format="turtle")
            return True

        return bool(schema.strip())
    except Exception:
        return False


def discover_inputs(input_dir: Path, source_languages: Iterable[SchemaLanguage]) -> dict[SchemaLanguage, list[Path]]:
    discovered: dict[SchemaLanguage, list[Path]] = {}
    for language in source_languages:
        language_dir = input_dir / language.value
        language_dir.mkdir(parents=True, exist_ok=True)
        files = [
            path for path in sorted(language_dir.iterdir())
            if path.is_file() and not path.name.startswith(".")
        ]
        discovered[language] = files
    return discovered


def write_text(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def execute_path(
    source: SchemaLanguage,
    target: SchemaLanguage,
    input_file: Path,
    input_schema: str,
    path: ConversionPath,
    path_id: str,
    path_count: int,
    attempt_dir: Path,
) -> AttemptRecord:
    current_schema = input_schema
    steps: list[StepRecord] = []
    failed_step_index: int | None = None
    final_output_path: Path | None = None
    error_path: Path | None = None
    error: str | None = None
    success = False

    attempt_start = time.perf_counter()
    for step_index, converter in enumerate(path, start=1):
        step_start = time.perf_counter()
        output_path = attempt_dir / "steps" / f"step_{step_index:02d}_output{output_extension(converter.target_language.value)}"
        try:
            current_schema = converter.convert(current_schema)
            automatic_valid = validate_output(current_schema, converter.target_language.value)
            write_text(output_path, current_schema)
            steps.append(
                StepRecord(
                    step_index=step_index,
                    source_language=converter.source_language.value,
                    target_language=converter.target_language.value,
                    converter_name=converter.name,
                    service_name=converter.service_name,
                    library=converter.library,
                    library_version=converter.library_version,
                    library_url=converter.library_url,
                    success=True,
                    automatic_valid=automatic_valid,
                    output_path=str(output_path.relative_to(OUTPUT_DIR)),
                    error=None,
                    duration_seconds=round(time.perf_counter() - step_start, 4),
                )
            )
        except Exception as exc:
            failed_step_index = step_index - 1
            error = f"{exc}\n\nTraceback:\n{traceback.format_exc()}"
            error_path = attempt_dir / "error.txt"
            write_text(error_path, error)
            steps.append(
                StepRecord(
                    step_index=step_index,
                    source_language=converter.source_language.value,
                    target_language=converter.target_language.value,
                    converter_name=converter.name,
                    service_name=converter.service_name,
                    library=converter.library,
                    library_version=converter.library_version,
                    library_url=converter.library_url,
                    success=False,
                    automatic_valid=False,
                    output_path=None,
                    error=str(exc),
                    duration_seconds=round(time.perf_counter() - step_start, 4),
                )
            )
            break
    else:
        success = bool(current_schema)
        final_output_path = attempt_dir / f"final_output{output_extension(target.value)}"
        write_text(final_output_path, current_schema)

    automatic_valid = success and validate_output(current_schema, target.value)
    record = AttemptRecord(
        source_language=source.value,
        target_language=target.value,
        input_file=str(input_file.relative_to(INPUT_DIR)),
        path_id=path_id,
        path_rank=None,
        path_count=path_count,
        path_signature=path_signature(path),
        success=success,
        automatic_valid=automatic_valid,
        final_output_path=str(final_output_path.relative_to(OUTPUT_DIR)) if final_output_path else None,
        error_path=str(error_path.relative_to(OUTPUT_DIR)) if error_path else None,
        failed_step_index=failed_step_index,
        duration_seconds=round(time.perf_counter() - attempt_start, 4),
        steps=steps,
    )
    metadata_path = attempt_dir / "metadata.json"
    metadata_path.write_text(json.dumps(asdict(record), indent=2) + "\n", encoding="utf-8")
    return record


def run_evaluation(input_dir: Path, output_dir: Path, run_id: str, only_core_languages: bool) -> Path:
    global OUTPUT_DIR
    OUTPUT_DIR = output_dir
    run_dir = output_dir / "runs" / run_id
    review_dir = output_dir / "review"
    run_dir.mkdir(parents=True, exist_ok=True)
    review_dir.mkdir(parents=True, exist_ok=True)
    previous_final_reviews = load_review_annotations(
        review_dir / "final_outputs.csv",
        FINAL_REVIEW_KEY_FIELDS,
    )
    previous_edge_reviews = load_review_annotations(
        review_dir / "edge_outputs.csv",
        EDGE_REVIEW_KEY_FIELDS,
    )

    service = ConversionService(register_converters(only_core_languages=only_core_languages))
    inputs = discover_inputs(input_dir, SOURCE_LANGUAGES)

    final_review_rows: list[dict[str, str | int | bool | None]] = []
    edge_review_rows: list[dict[str, str | int | bool | None]] = []
    all_metadata: list[dict] = []

    for source, input_files in inputs.items():
        if not input_files:
            print(f"No input files for {source.value}; skipping source language.")
            continue

        for input_file in input_files:
            input_schema = input_file.read_text(encoding="utf-8")
            for target in TARGET_LANGUAGES:
                if source == target:
                    continue

                paths = find_paths(source, target, service.conversion_graph)
                path_count = len(paths)
                if path_count == 0:
                    continue

                print(f"{source.value} -> {target.value}: {input_file.name} ({path_count} paths)")
                attempts: list[AttemptRecord] = []
                conversion_results: list[ConversionResult] = []

                for path_index, path in enumerate(paths, start=1):
                    path_id = f"path_{path_index:03d}"
                    attempt_dir = (
                        run_dir
                        / source.value
                        / safe_name(input_file.stem)
                        / target.value
                        / path_id
                    )
                    attempt = execute_path(
                        source=source,
                        target=target,
                        input_file=input_file,
                        input_schema=input_schema,
                        path=path,
                        path_id=path_id,
                        path_count=path_count,
                        attempt_dir=attempt_dir,
                    )
                    attempts.append(attempt)
                    result_text = (
                        Path(output_dir / attempt.final_output_path).read_text(encoding="utf-8")
                        if attempt.final_output_path
                        else (Path(output_dir / attempt.error_path).read_text(encoding="utf-8") if attempt.error_path else "")
                    )
                    conversion_results.append((attempt.success, result_text, path, attempt.failed_step_index))

                service._rank_results(conversion_results, source, target)
                rank_by_signature = {
                    path_signature(path): rank
                    for rank, (_success, _schema_or_error, path, _failed_step_index)
                    in enumerate(conversion_results, start=1)
                }

                for attempt in attempts:
                    attempt.path_rank = rank_by_signature.get(attempt.path_signature)
                    metadata_path = (
                        run_dir
                        / attempt.source_language
                        / safe_name(Path(attempt.input_file).stem)
                        / attempt.target_language
                        / attempt.path_id
                        / "metadata.json"
                    )
                    metadata_path.write_text(json.dumps(asdict(attempt), indent=2) + "\n", encoding="utf-8")
                    all_metadata.append(asdict(attempt))
                    final_status = "I" if not attempt.automatic_valid else ""
                    final_review_rows.append({
                        "status": final_status,
                        "automatic_valid": attempt.automatic_valid,
                        "source_language": attempt.source_language,
                        "target_language": attempt.target_language,
                        "input_file": attempt.input_file,
                        "path_id": attempt.path_id,
                        "path_rank": attempt.path_rank,
                        "path_count": attempt.path_count,
                        "path_signature": attempt.path_signature,
                        "output_path": attempt.final_output_path or attempt.error_path,
                        "notes": "",
                    })

                    for step in attempt.steps:
                        edge_status = "I" if not step.automatic_valid else ""
                        edge_review_rows.append({
                            "status": edge_status,
                            "automatic_valid": step.automatic_valid,
                            "source_language": attempt.source_language,
                            "target_language": attempt.target_language,
                            "input_file": attempt.input_file,
                            "path_id": attempt.path_id,
                            "path_signature": attempt.path_signature,
                            "step_index": step.step_index,
                            "edge_signature": f"{step.source_language}:{step.target_language}:{step.converter_name}",
                            "edge_source_language": step.source_language,
                            "edge_target_language": step.target_language,
                            "converter_name": step.converter_name,
                            "library": step.library or step.converter_name,
                            "output_path": step.output_path,
                            "notes": "",
                        })

    carry_forward_review_annotations(final_review_rows, previous_final_reviews, FINAL_REVIEW_KEY_FIELDS)
    carry_forward_review_annotations(edge_review_rows, previous_edge_reviews, EDGE_REVIEW_KEY_FIELDS)
    run_review_dir = run_dir / "review"
    write_review_csv(run_review_dir / "final_outputs.csv", REVIEW_FIELDS, final_review_rows)
    write_review_csv(run_review_dir / "edge_outputs.csv", EDGE_REVIEW_FIELDS, edge_review_rows)
    write_review_csv(review_dir / "final_outputs.csv", REVIEW_FIELDS, final_review_rows)
    write_review_csv(review_dir / "edge_outputs.csv", EDGE_REVIEW_FIELDS, edge_review_rows)
    (run_dir / "all_metadata.json").write_text(json.dumps(all_metadata, indent=2) + "\n", encoding="utf-8")
    (output_dir / "latest_run.txt").write_text(run_id + "\n", encoding="utf-8")
    return run_dir


def review_key(row: dict, key_fields: list[str]) -> tuple[str, ...]:
    return tuple(str(row.get(field, "")) for field in key_fields)


def load_review_annotations(path: Path, key_fields: list[str]) -> dict[tuple[str, ...], tuple[str, str]]:
    if not path.exists():
        return {}
    with path.open(newline="", encoding="utf-8") as handle:
        reader = csv.DictReader(handle)
        annotations: dict[tuple[str, ...], tuple[str, str]] = {}
        for row in reader:
            status = (row.get("status") or "").strip()
            notes = row.get("notes") or ""
            if status:
                annotations[review_key(row, key_fields)] = (status, notes)
        return annotations


def carry_forward_review_annotations(
    rows: list[dict],
    previous_annotations: dict[tuple[str, ...], tuple[str, str]],
    key_fields: list[str],
) -> None:
    for row in rows:
        previous = previous_annotations.get(review_key(row, key_fields))
        if previous is None:
            continue
        previous_status, previous_notes = previous
        if previous_status:
            row["status"] = previous_status
            row["notes"] = previous_notes


def write_review_csv(path: Path, fields: list[str], rows: list[dict]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)


def main() -> None:
    parser = argparse.ArgumentParser(description="Run the broad real-world orchestrator evaluation.")
    parser.add_argument("--input-dir", type=Path, default=INPUT_DIR)
    parser.add_argument("--output-dir", type=Path, default=OUTPUT_DIR)
    parser.add_argument("--run-id", default=datetime.now().strftime("%Y%m%d_%H%M%S"))
    parser.add_argument("--full-graph", action="store_true", help="Use all registered converters, not only core-language converters.")
    args = parser.parse_args()

    run_dir = run_evaluation(
        input_dir=args.input_dir,
        output_dir=args.output_dir,
        run_id=args.run_id,
        only_core_languages=not args.full_graph,
    )
    print(f"Evaluation run stored in {run_dir}")
    print(f"Review CSVs stored in {args.output_dir / 'review'}")


if __name__ == "__main__":
    main()
