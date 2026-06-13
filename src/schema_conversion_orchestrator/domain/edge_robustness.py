"""Edge-reliability scores used for ranking conversion paths.

Analogous to :mod:`accuracy_scores`, but instead of a per-task, per-path
benchmark score, these are per-edge (per direct converter) reliability scores
derived from the broad orchestrator evaluation. Score files distinguish:

``robustness`` / ``validity``
    Fraction of edge attempts that produce syntactically valid output.

``quality``
    ``(G + 0.5 * L) / (G + L + I)`` over syntactically valid edge outputs.
    This conditional value is used for path ranking: whether a path succeeds
    syntactically is already known at ranking time (failures sort last), so
    only the expected quality of the produced output matters.

``reliability``
    ``robustness * quality``. Kept in the score files for the evaluation
    plots, but not used for ranking.

A path's score is the product of its edges' quality values. Edges without a
stored score default to :data:`DEFAULT_EDGE_ROBUSTNESS` (0.5), which keeps
unevaluated edges neutral and, because the values multiply, naturally favours
shorter paths over longer ones.

The same edge-key format is used by the evaluation (to key the scores, see
``eval/plot_orchestrator_evaluation.py``) and by the orchestrator (to look them
up online), so the two always agree.
"""
from __future__ import annotations

import json
import os
from functools import lru_cache
from pathlib import Path
from typing import Dict, List, Optional

DEFAULT_ROBUSTNESS_PATH = (
    Path(__file__).resolve().parents[1] / "data" / "edge_robustness_scores.json"
)
DEFAULT_EDGE_ROBUSTNESS = 0.5


def edge_key(source: str, target: str, converter: str) -> str:
    """Key identifying a single converter edge (source -> target via converter)."""
    return f"{source}:{target}:{converter}"


@lru_cache(maxsize=1)
def _load_scores(path_str: str) -> Dict[str, dict]:
    path = Path(path_str)
    if not path.exists():
        return {}
    try:
        with open(path) as f:
            return json.load(f)
    except (OSError, json.JSONDecodeError) as e:  # pragma: no cover - defensive
        print(f"Warning: could not load edge robustness scores from {path}: {e}")
        return {}


def load_robustness_scores(scores_path: Optional[os.PathLike | str] = None) -> Dict[str, dict]:
    """Load the persisted edge-robustness scores (cached). Empty dict if none."""
    resolved = str(
        scores_path
        or os.environ.get("SCHEMA_CONVERTER_EDGE_ROBUSTNESS_SCORES")
        or DEFAULT_ROBUSTNESS_PATH
    )
    return _load_scores(resolved)


def has_robustness_scores(scores: Optional[Dict] = None) -> bool:
    """Whether any edge-robustness scores are available."""
    scores = scores if scores is not None else load_robustness_scores()
    return bool(scores)


def lookup_edge_robustness(
    source: str,
    target: str,
    converter: str,
    scores: Optional[Dict] = None,
) -> float:
    """Quality score of a single edge, or the default if unknown."""
    scores = scores if scores is not None else load_robustness_scores()
    entry = scores.get(edge_key(source, target, converter))
    if entry is None:
        return DEFAULT_EDGE_ROBUSTNESS
    return float(entry["quality"])


def path_robustness(path: List, scores: Optional[Dict] = None) -> float:
    """Combined path score: product of its edges' quality values."""
    scores = scores if scores is not None else load_robustness_scores()
    product = 1.0
    for converter in path:
        product *= lookup_edge_robustness(
            converter.source_language.value,
            converter.target_language.value,
            converter.name,
            scores,
        )
    return product
