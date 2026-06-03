"""Structural comparison of two SHACL shapes graphs.

Delegates to the ``shacl-bridge compare`` CLI, which canonicalizes both graphs
(RDFC-1.0) and reports precision/recall/F1 over canonical triples -- the same
SHACL comparison used by the shacl-bridge benchmark and thesis. The Jaccard
index is derived from precision and recall as ``1 / (1/p + 1/r - 1)``.

This keeps the SHACL comparison identical to shacl-bridge's own, so
orchestrator-level and library-level evaluations are directly comparable.
"""
from __future__ import annotations

import re
import subprocess
import tempfile
from pathlib import Path
from typing import Dict

REPO_ROOT = Path(__file__).resolve().parents[1]
SHACL_BRIDGE_BIN = REPO_ROOT / "external_converters" / "node" / "node_modules" / ".bin" / "shacl-bridge"

_METRIC_RE = re.compile(r"Precision:\s+(\S+)\s+Recall:\s+(\S+)\s+F1:\s+(\S+)")


def _jaccard(precision: float, recall: float) -> float:
    if precision <= 0 or recall <= 0:
        return 0.0
    return 1.0 / (1.0 / precision + 1.0 / recall - 1.0)


def compare_shacl(expected_ttl: str, predicted_ttl: str) -> Dict[str, float]:
    """Compare two SHACL Turtle documents, returning {"f1", "jaccard"} in [0, 1].

    Returns zeros if the comparison cannot be performed (e.g. invalid Turtle).
    """
    if not predicted_ttl:
        return {"f1": 0.0, "jaccard": 0.0}

    with tempfile.NamedTemporaryFile("w", suffix=".ttl", delete=False) as ef, \
            tempfile.NamedTemporaryFile("w", suffix=".ttl", delete=False) as af:
        ef.write(expected_ttl)
        af.write(predicted_ttl)
        expected_path, actual_path = ef.name, af.name

    try:
        result = subprocess.run(
            ["node", str(SHACL_BRIDGE_BIN), "compare",
             "--expected", expected_path, "--actual", actual_path],
            capture_output=True, text=True, timeout=60,
        )
        match = _METRIC_RE.search(result.stdout)
        if not match:
            return {"f1": 0.0, "jaccard": 0.0}
        precision, recall, f1 = (float(match.group(i)) for i in (1, 2, 3))
        return {"f1": f1, "jaccard": _jaccard(precision, recall)}
    except (subprocess.SubprocessError, ValueError):
        return {"f1": 0.0, "jaccard": 0.0}
    finally:
        Path(expected_path).unlink(missing_ok=True)
        Path(actual_path).unlink(missing_ok=True)
