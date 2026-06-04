"""Generate plots for the broad orchestrator evaluation.

Run this after ``eval/evaluate.py`` and after filling the review CSV ``status``
columns with G, L, or I.
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

import pandas as pd

EVAL_DIR = Path(__file__).resolve().parent
REPO_ROOT = EVAL_DIR.parent
SRC_DIR = REPO_ROOT / "src"
sys.path.insert(0, str(SRC_DIR))

from schema_conversion_orchestrator.converters.registry import register_converters  # noqa: E402
from schema_conversion_orchestrator.domain.conversion_graph import build_conversion_graph  # noqa: E402
from schema_conversion_orchestrator.reporting.conversion_matrix import (  # noqa: E402
    build_orchestrator_result_matrix,
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


def compute_edge_scores(edge_review: pd.DataFrame) -> dict[str, float]:
    """Compute edge-local quality scores from immediate edge outputs.

    Only reviewed statuses G/L/I are included. This keeps the graph from
    pretending unreviewed valid outputs are good or lacking. Failed/invalid edge
    outputs are prefilled as I by the runner and therefore count immediately.
    """
    scores: dict[str, float] = {}
    if edge_review.empty:
        return scores

    edge_review = edge_review.copy()
    edge_review["status_normalized"] = edge_review["status"].map(normalize_status)
    reviewed = edge_review[edge_review["status_normalized"].isin({"G", "L", "I"})]

    for edge_signature, group in reviewed.groupby("edge_signature"):
        total = len(group)
        good = int((group["status_normalized"] == "G").sum())
        lacking = int((group["status_normalized"] == "L").sum())
        scores[edge_signature] = (good + 0.5 * lacking) / total if total else 0.0
    return scores


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
    edge_scores = compute_edge_scores(edge_review)
    converters = register_converters(only_core_languages=not args.full_graph)
    conversion_graph = build_conversion_graph(converters)
    graph_path = plots_dir / "conversion_graph_edge_quality.png"
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
    print(f"Wrote {graph_path}")
    print(f"Wrote {full_graph_path}")


if __name__ == "__main__":
    main()
