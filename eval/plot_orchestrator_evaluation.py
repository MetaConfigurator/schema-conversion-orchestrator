"""Generate plots for the broad orchestrator evaluation.

Run this after ``eval/evaluate.py`` and after filling the review CSV ``status``
columns with G, L, or I.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import pandas as pd

EVAL_DIR = Path(__file__).resolve().parent
REPO_ROOT = EVAL_DIR.parent
SRC_DIR = REPO_ROOT / "src"
sys.path.insert(0, str(SRC_DIR))

from schema_conversion_orchestrator.domain.edge_robustness import (  # noqa: E402
    DEFAULT_ROBUSTNESS_PATH,
)

from schema_conversion_orchestrator.converters.registry import register_converters  # noqa: E402
from schema_conversion_orchestrator.domain.conversion_graph import build_conversion_graph  # noqa: E402
from schema_conversion_orchestrator.reporting.conversion_matrix import (  # noqa: E402
    build_edge_quality_matrix,
    build_orchestrator_result_matrix,
    plot_edge_quality_matrix,
    plot_orchestrator_result_matrix,
)
from schema_conversion_orchestrator.reporting.visualize_conversion_graph import (  # noqa: E402
    visualize_conversion_graph_with_metrics,
)


DEFAULT_OUTPUT_DIR = EVAL_DIR / "orchestrator_outputs"
EVALUATION_LANGUAGES = {
    "JsonSchema",
    "Xsd",
    "SHACL_TTL",
    "LinkMl",
    "MdModels",
}


def normalize_status(value) -> str:
    if pd.isna(value):
        return ""
    return str(value).strip().upper()


def compute_edge_robustness(edge_review: pd.DataFrame) -> dict[str, dict]:
    """Compute per-edge robustness from immediate edge outputs.

    For each converter edge, robustness is ``(G + 0.5*L) / (G + L + I)`` over all
    reviewed immediate outputs. Only reviewed statuses G/L/I are included, so the
    graph does not pretend unreviewed valid outputs are good or lacking.
    Returns a dict keyed by edge signature (``source:target:converter``) with the
    robustness value and the underlying counts (for transparency / persistence).
    """
    scores: dict[str, dict] = {}
    if edge_review.empty:
        return scores

    edge_review = edge_review.copy()
    edge_review["status_normalized"] = edge_review["status"].map(normalize_status)
    reviewed = edge_review[edge_review["status_normalized"].isin({"G", "L", "I"})]

    for edge_signature, group in reviewed.groupby("edge_signature"):
        total = len(group)
        good = int((group["status_normalized"] == "G").sum())
        lacking = int((group["status_normalized"] == "L").sum())
        invalid = int((group["status_normalized"] == "I").sum())
        robustness = (good + 0.5 * lacking) / total if total else 0.0
        scores[str(edge_signature)] = {
            "robustness": round(robustness, 4),
            "good": good,
            "lacking": lacking,
            "invalid": invalid,
            "cases": total,
        }
    return scores


def persist_edge_robustness(scores: dict[str, dict], path: Path) -> None:
    """Persist per-edge robustness scores for the orchestrator to load at runtime."""
    path.parent.mkdir(parents=True, exist_ok=True)
    ordered = dict(sorted(scores.items()))
    path.write_text(json.dumps(ordered, indent=2) + "\n", encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser(description="Plot broad orchestrator evaluation results.")
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT_DIR)
    parser.add_argument("--plots-dir", type=Path, default=None)
    parser.add_argument("--full-graph", action="store_true", help="Use all registered converters, not only core-language converters.")
    args = parser.parse_args()

    review_dir = args.output_dir / "review"
    final_review_path = review_dir / "final_outputs.csv"
    edge_review_path = review_dir / "edge_outputs.csv"
    if not final_review_path.exists():
        raise SystemExit(f"Missing final review CSV: {final_review_path}")
    if not edge_review_path.exists():
        raise SystemExit(f"Missing edge review CSV: {edge_review_path}")

    plots_dir = args.plots_dir or (args.output_dir / "plots")
    plots_dir.mkdir(parents=True, exist_ok=True)

    final_review = pd.read_csv(final_review_path)
    annotations, heat = build_orchestrator_result_matrix(final_review)
    matrix_path = plots_dir / "orchestrator_result_matrix.png"
    plot_orchestrator_result_matrix(annotations, heat, output_path=str(matrix_path))

    edge_review = pd.read_csv(edge_review_path)
    edge_quality = build_edge_quality_matrix(edge_review)
    edge_matrix_path = plots_dir / "edge_robustness_matrix.png"
    plot_edge_quality_matrix(edge_quality, output_path=str(edge_matrix_path))

    edge_robustness = compute_edge_robustness(edge_review)
    # Persist the per-edge robustness scores so the orchestrator can load them
    # for the edge-robustness ranking strategy (analogous to accuracy scores).
    persist_edge_robustness(edge_robustness, DEFAULT_ROBUSTNESS_PATH)
    persist_edge_robustness(edge_robustness, args.output_dir / "edge_robustness_scores.json")
    edge_scores = {sig: entry["robustness"] for sig, entry in edge_robustness.items()}
    converters = register_converters(only_core_languages=not args.full_graph)
    conversion_graph = build_conversion_graph(converters)
    graph_path = plots_dir / "conversion_graph_edge_robustness.png"
    visualize_conversion_graph_with_metrics(
        conversion_graph,
        output_path=str(graph_path),
        show_edge_labels=True,
        edge_scores=edge_scores,
        include_languages=EVALUATION_LANGUAGES,
    )

    full_graph_path = plots_dir / "conversion_graph_all_languages.png"
    full_converters = register_converters(only_core_languages=False)
    full_conversion_graph = build_conversion_graph(full_converters)
    visualize_conversion_graph_with_metrics(
        full_conversion_graph,
        output_path=str(full_graph_path),
        show_edge_labels=True,
        edge_scores=None,
        include_languages=None,
    )

    print(f"Wrote {matrix_path}")
    print(f"Wrote {edge_matrix_path}")
    print(f"Wrote {graph_path}")
    print(f"Wrote {full_graph_path}")
    print(f"Wrote edge robustness scores -> {DEFAULT_ROBUSTNESS_PATH}")


if __name__ == "__main__":
    main()
