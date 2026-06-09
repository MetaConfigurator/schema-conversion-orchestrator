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
RESULTS_DIR = EVAL_DIR / "results"
sys.path.insert(0, str(SRC_DIR))
sys.path.insert(0, str(EVAL_DIR))

from crop_to_content import crop_to_content  # noqa: E402

from schema_conversion_orchestrator.domain.edge_robustness import (  # noqa: E402
    DEFAULT_ROBUSTNESS_PATH,
)

from schema_conversion_orchestrator.converters.registry import register_converters  # noqa: E402
from schema_conversion_orchestrator.domain.conversion_graph import build_conversion_graph  # noqa: E402
from plotting_conversion_matrix import (  # noqa: E402
    build_edge_quality_matrix,
    build_orchestrator_result_matrix,
    plot_edge_quality_matrix,
    plot_orchestrator_result_matrix,
)
from plotting_conversion_graph import (  # noqa: E402
    visualize_graphical_abstract,
    visualize_conversion_graph_with_metrics,
)


DEFAULT_OUTPUT_DIR = RESULTS_DIR / "orchestrator_outputs"
RESULTS_ROBUSTNESS_PATH = RESULTS_DIR / "edge_robustness_scores.json"
EVALUATION_LANGUAGES = {
    "JsonSchema",
    "Xsd",
    "SHACL_TTL",
    "LinkMl",
    "MdModels",
}
GRAPHICAL_ABSTRACT_LANGUAGES = EVALUATION_LANGUAGES | {
    "Dtd",
    "GraphQL",
    "Mermaid",
    "Protobuf",
    "Shex",
    "Owl_OFN",
    "SqlAlchemy",
}


def normalize_status(value) -> str:
    if pd.isna(value):
        return ""
    return str(value).strip().upper()


def _direct_input_invalid(row, prev_index: dict) -> bool:
    """Whether an edge's direct input (the previous step's output) was invalid.

    Edge robustness judges each converter against its direct input. If that input
    was itself invalid (the previous step's output was automatically invalid or
    human-annotated ``I``), the sample tests the upstream step, not this converter,
    so it is excluded. First steps consume the real source schema and are kept.
    """
    try:
        step_index = int(row["step_index"])
    except (TypeError, ValueError):
        return False
    if step_index <= 1:
        return False
    prev = prev_index.get(
        (row["source_language"], row["target_language"], row["input_file"], row["path_id"], step_index - 1)
    )
    if prev is None:
        return False
    prev_status = normalize_status(prev.get("status"))
    prev_auto = str(prev.get("automatic_valid")).strip().lower()
    return prev_status == "I" or prev_auto in {"false", "0", "no"}


def compute_edge_robustness(edge_review: pd.DataFrame) -> dict[str, dict]:
    """Compute per-edge robustness from immediate edge outputs.

    For each converter edge, robustness is ``(G + 0.5*L) / (G + L + I)`` over its
    reviewed immediate outputs (statuses G/L/I). Samples whose *direct input* was
    invalid are excluded (see ``_direct_input_invalid``), so a converter is not
    penalised for information an earlier step already lost or for being handed an
    unusable input. Returns a dict keyed by edge signature with the robustness
    value and the underlying counts (including how many samples were excluded).
    """
    scores: dict[str, dict] = {}
    if edge_review.empty:
        return scores

    edge_review = edge_review.copy()
    edge_review["status_normalized"] = edge_review["status"].map(normalize_status)

    prev_index = {
        (r["source_language"], r["target_language"], r["input_file"], r["path_id"], int(r["step_index"])): r
        for _, r in edge_review.iterrows()
        if str(r["step_index"]).strip().isdigit()
    }

    reviewed = edge_review[edge_review["status_normalized"].isin({"G", "L", "I"})]

    for edge_signature, group in reviewed.groupby("edge_signature"):
        excluded = int(group.apply(lambda r: _direct_input_invalid(r, prev_index), axis=1).sum())
        kept = group[~group.apply(lambda r: _direct_input_invalid(r, prev_index), axis=1)]
        total = len(kept)
        good = int((kept["status_normalized"] == "G").sum())
        lacking = int((kept["status_normalized"] == "L").sum())
        invalid = int((kept["status_normalized"] == "I").sum())
        robustness = (good + 0.5 * lacking) / total if total else 0.0
        scores[str(edge_signature)] = {
            "robustness": round(robustness, 4),
            "good": good,
            "lacking": lacking,
            "invalid": invalid,
            "cases": total,
            "excluded_invalid_input": excluded,
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
    persist_edge_robustness(edge_robustness, RESULTS_ROBUSTNESS_PATH)
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
        show_colorbar=False,
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

    graphical_abstract_path = plots_dir / "graphical_abstract_conversion_graph.png"
    graphical_abstract_pdf_path = plots_dir / "graphical_abstract_conversion_graph.pdf"
    visualize_graphical_abstract(
        full_conversion_graph,
        output_path=str(graphical_abstract_path),
        include_languages=GRAPHICAL_ABSTRACT_LANGUAGES,
    )
    visualize_graphical_abstract(
        full_conversion_graph,
        output_path=str(graphical_abstract_pdf_path),
        include_languages=GRAPHICAL_ABSTRACT_LANGUAGES,
    )

    # Trim the residual white margin left by matplotlib so the graph plots embed
    # tightly in the manuscript.
    crop_to_content(graph_path)
    crop_to_content(full_graph_path)

    print(f"Wrote {matrix_path}")
    print(f"Wrote {edge_matrix_path}")
    print(f"Wrote {graph_path}")
    print(f"Wrote {graphical_abstract_path}")
    print(f"Wrote {graphical_abstract_pdf_path}")
    print(f"Wrote {full_graph_path}")
    print(f"Wrote edge robustness scores -> {DEFAULT_ROBUSTNESS_PATH}")
    print(f"Wrote edge robustness scores -> {RESULTS_ROBUSTNESS_PATH}")


if __name__ == "__main__":
    main()
