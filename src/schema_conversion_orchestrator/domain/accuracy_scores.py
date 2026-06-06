"""Benchmark-derived accuracy scores used for ranking conversion paths.

The orchestrator can rank conversion paths by how accurately they reproduce a
ground-truth target schema on an offline benchmark. These scores come from an
evaluation run (see ``eval/benchmark_runner.py``) that converts benchmark source
schemas to the target language along every available path and compares each
result to the expected target schema, yielding an F1 / Jaccard score per path.

The scores are persisted to a JSON file that this module loads at runtime. The
same path-signature function is used by the evaluation (to key the scores) and
by the orchestrator (to look them up online), so the two always agree.
"""
from __future__ import annotations

import json
import os
from functools import lru_cache
from pathlib import Path
from typing import Dict, List, Optional, Sequence, Tuple

DEFAULT_SCORES_PATH = Path(__file__).resolve().parents[1] / "data" / "accuracy_scores.json"


def task_key(source: str, target: str) -> str:
    """Key identifying a source -> target conversion task."""
    return f"{source}->{target}"


def path_signature_from_steps(steps: Sequence[Tuple[str, str, str]]) -> str:
    """Canonical signature of a path given (sourceLang, targetLang, converterName) steps."""
    return " -> ".join(f"{s}:{t}:{n}" for s, t, n in steps)


def path_signature(path: List) -> str:
    """Canonical signature of a conversion path (list of Converter)."""
    return path_signature_from_steps(
        [(c.source_language.value, c.target_language.value, c.name) for c in path]
    )


@lru_cache(maxsize=1)
def _load_scores(path_str: str) -> Dict[str, Dict[str, dict]]:
    path = Path(path_str)
    if not path.exists():
        return {}
    try:
        with open(path) as f:
            return json.load(f)
    except (OSError, json.JSONDecodeError) as e:  # pragma: no cover - defensive
        print(f"Warning: could not load accuracy scores from {path}: {e}")
        return {}


def load_scores(scores_path: Optional[os.PathLike | str] = None) -> Dict[str, Dict[str, dict]]:
    """Load the persisted accuracy scores (cached). Empty dict if none exist."""
    resolved = str(
        scores_path
        or os.environ.get("SCHEMA_CONVERTER_ACCURACY_SCORES")
        or DEFAULT_SCORES_PATH
    )
    return _load_scores(resolved)


def has_accuracy_scores(source: str, target: str, scores: Optional[Dict] = None) -> bool:
    """Whether accuracy scores exist for this source -> target task."""
    scores = scores if scores is not None else load_scores()
    return bool(scores.get(task_key(source, target)))


def lookup_score(
    source: str,
    target: str,
    signature: str,
    scores: Optional[Dict] = None,
    metric: str = "f1",
) -> Optional[float]:
    """Look up the benchmark score for a specific path, or None if unknown."""
    scores = scores if scores is not None else load_scores()
    entry = scores.get(task_key(source, target), {}).get(signature)
    if entry is None:
        return None
    return entry.get(metric)
