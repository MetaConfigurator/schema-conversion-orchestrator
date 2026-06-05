"""JSON Schema -> SHACL benchmark, backed by the shacl-bridge benchmark.

The source inputs of this suite are derived from the official JSON Schema Test
Suite (github.com/json-schema-org/JSON-Schema-Test-Suite), organized by JSON
Schema keyword, with hand-constructed ground-truth SHACL shapes graphs. Produced
SHACL is scored against the ground truth via RDF-canonicalization comparison
(see ``compare_shacl.py``), matching the shacl-bridge methodology.

This benchmark demonstrates that the generic evaluation runner is agnostic to
the conversion direction and to the comparison metric: it reuses the same runner
as the SHACL -> JSON Schema benchmark but plugs in a different comparison
function and operates on SHACL outputs.
"""
from __future__ import annotations

import os
from pathlib import Path
from typing import Any, Dict, List

from compare_shacl import compare_shacl

from .base import BenchmarkCase, ConversionBenchmark, register

REPO_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_BENCHMARK_DIR = REPO_ROOT.parent / "shacl-bridge" / "benchmark" / "json-schema-to-shacl"


class JsonSchemaToShaclBenchmark(ConversionBenchmark):
    source_language = "JsonSchema"
    target_language = "SHACL_TTL"
    primary_metric = "f1"
    metric_names = ["f1", "jaccard"]
    # MdModels cannot ingest these minimal JSON Schema inputs (the library
    # rejects schemas without `properties`), so its path is omitted from the report.
    report_exclude = ["MdModels"]
    # The LinkML import/export chain has very long converter names; show a short
    # label in the plot instead.
    label_overrides = {
        "schema_automator": "via LinkML",
        "jsonschema2shacl": "jsonschema2shacl",
        "JsonSchema:SHACL_TTL:shacl-bridge": "shacl-bridge",
    }

    def __init__(self, benchmark_dir: Path | None = None) -> None:
        self.benchmark_dir = Path(
            benchmark_dir or os.environ.get("BENCHMARK_DIR_JSON_TO_SHACL", DEFAULT_BENCHMARK_DIR)
        )

    def load_cases(self) -> List[BenchmarkCase]:
        if not self.benchmark_dir.exists():
            raise FileNotFoundError(
                f"Benchmark directory not found: {self.benchmark_dir}\n"
                f"Clone https://github.com/MetaConfigurator/shacl-bridge next to this repo, "
                f"or set BENCHMARK_DIR_JSON_TO_SHACL."
            )
        cases: List[BenchmarkCase] = []
        for json_path in sorted(self.benchmark_dir.rglob("*.json")):
            ttl_path = json_path.with_suffix(".ttl")
            if not ttl_path.exists():
                continue
            rel = json_path.relative_to(self.benchmark_dir)
            category = rel.parts[0]
            cases.append(BenchmarkCase(
                name=str(rel.with_suffix("")),
                source_schema=json_path.read_text(),
                expected=ttl_path.read_text(),  # ground-truth SHACL Turtle
                category=category,
            ))
        return cases

    def compare(self, expected: Any, predicted_text: str) -> Dict[str, float]:
        return compare_shacl(expected, predicted_text or "")


@register
def _factory() -> ConversionBenchmark:
    return JsonSchemaToShaclBenchmark()
