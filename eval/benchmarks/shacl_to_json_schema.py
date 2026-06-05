"""SHACL -> JSON Schema benchmark, backed by the shacl-bridge benchmark.

This is the first concrete :class:`ConversionBenchmark`. It reads
``<name>.ttl`` / ``<name>.json`` test pairs from the shacl-bridge benchmark and
scores produced JSON Schemas against the expected ones with the structural
F1 / Jaccard metric (see ``compare_json_schemas.py``), matching the methodology
of the shacl-bridge thesis.

Other conversion paths can be added analogously by implementing their own
benchmark module and registering it.
"""
from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any, Dict, List

from compare_json_schemas import compare_schemas

from .base import BenchmarkCase, ConversionBenchmark, register

REPO_ROOT = Path(__file__).resolve().parents[2]
# Default: a sibling clone of the shacl-bridge repo next to this repository.
DEFAULT_BENCHMARK_DIR = REPO_ROOT.parent / "shacl-bridge" / "benchmark" / "shacl-to-json-schema"


class ShaclToJsonSchemaBenchmark(ConversionBenchmark):
    source_language = "SHACL_TTL"
    target_language = "JsonSchema"
    primary_metric = "f1"
    metric_names = ["f1", "jaccard"]
    # Collapse the RdfLib-vs-n3 duplicates (both only build the SHACL JSON-LD
    # intermediate); keep the n3-based variants as representatives.
    report_exclude = ["RdfLib"]
    # Short plot labels (the via-JSON-LD converter chains are otherwise long).
    # Order matters: the first matching substring wins.
    label_overrides = {
        "JsonSchema:@comake": "via JSON-LD -> @comake",
        "SHACL_JSON_LD:JsonSchema:shacl-bridge": "via JSON-LD -> shacl-bridge",
        "SHACL_TTL:JsonSchema:shacl-jsonschema-converter": "shacl-jsonschema-converter",
        "SHACL_TTL:JsonSchema:shacl-bridge": "shacl-bridge",
    }

    def __init__(self, benchmark_dir: Path | None = None) -> None:
        self.benchmark_dir = Path(
            benchmark_dir or os.environ.get("BENCHMARK_DIR", DEFAULT_BENCHMARK_DIR)
        )

    def load_cases(self) -> List[BenchmarkCase]:
        if not self.benchmark_dir.exists():
            raise FileNotFoundError(
                f"Benchmark directory not found: {self.benchmark_dir}\n"
                f"Clone https://github.com/MetaConfigurator/shacl-bridge next to this repo, "
                f"or set BENCHMARK_DIR."
            )
        cases: List[BenchmarkCase] = []
        for ttl_path in sorted(self.benchmark_dir.rglob("*.ttl")):
            json_path = ttl_path.with_suffix(".json")
            if not json_path.exists():
                continue
            rel = ttl_path.relative_to(self.benchmark_dir)
            category = rel.parts[1] if len(rel.parts) > 2 else rel.parts[0]
            cases.append(BenchmarkCase(
                name=str(rel.with_suffix("")),
                source_schema=ttl_path.read_text(),
                expected=json.loads(json_path.read_text()),
                category=category,
            ))
        return cases

    def compare(self, expected: Any, predicted_text: str) -> Dict[str, float]:
        try:
            predicted = json.loads(predicted_text)
        except (json.JSONDecodeError, TypeError):
            return self.zero_metrics
        result = compare_schemas(expected, predicted, semantic_normalization=False,
                                 compare_metadata_and_pattern=False)
        return {"f1": result.f1_score, "jaccard": result.jaccard}


@register
def _factory() -> ConversionBenchmark:
    return ShaclToJsonSchemaBenchmark()
