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
    build_direct_edge_quality_matrix,
    build_intermediate_edge_quality_matrix,
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
PROTOBUF_EDGE_ROBUSTNESS_PATH = DEFAULT_OUTPUT_DIR / "protobuf_edge_robustness_scores.json"
EVALUATION_LANGUAGES = {
    "JsonSchema",
    "Xsd",
    "SHACL_TTL",
    "LinkMl",
    "MdModels",
}
# The graphical abstract shows only schema languages. GraphQL (a query
# language), SQLAlchemy (an ORM toolkit), and Mermaid (a diagramming language)
# are generated targets but not schema languages, so they are excluded; the
# data-schema languages Protobuf and ShEx are kept.
GRAPHICAL_ABSTRACT_LANGUAGES = EVALUATION_LANGUAGES | {
    "Dtd",
    "Protobuf",
    "Shex",
    "Owl_OFN",
}


def normalize_status(value) -> str:
    if pd.isna(value):
        return ""
    return str(value).strip().upper()


def path_steps(path_signature: str) -> list[str]:
    return [step.strip() for step in str(path_signature).split(" -> ") if step.strip()]


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


def _metrics_from_reviewed_edge_rows(group: pd.DataFrame, excluded: int = 0) -> dict:
    cases = len(group)
    auto_valid = group["automatic_valid"].astype(str).str.strip().str.lower().isin({"true", "1", "yes"})
    valid_outputs = int(auto_valid.sum())
    auto_invalid = cases - valid_outputs
    quality_rows = group[auto_valid]
    quality_cases = len(quality_rows)
    good = int((quality_rows["status_normalized"] == "G").sum())
    lacking = int((quality_rows["status_normalized"] == "L").sum())
    quality_invalid = int((quality_rows["status_normalized"] == "I").sum())
    invalid = int((group["status_normalized"] == "I").sum())
    robustness = valid_outputs / cases if cases else 0.0
    quality = (good + 0.5 * lacking) / quality_cases if quality_cases else 0.0
    reliability = robustness * quality
    return {
        "robustness": round(robustness, 4),
        "validity": round(robustness, 4),
        "quality": round(quality, 4),
        "reliability": round(reliability, 4),
        "good": good,
        "lacking": lacking,
        "invalid": invalid,
        "quality_invalid": quality_invalid,
        "cases": cases,
        "valid_outputs": valid_outputs,
        "auto_invalid": auto_invalid,
        "quality_cases": quality_cases,
        "excluded_invalid_input": excluded,
    }


def compute_direct_edge_metrics(final_review: pd.DataFrame) -> dict[str, dict]:
    """Compute edge metrics from one-step final conversion results.

    This is the default paper-facing metric. A direct final row has exactly one
    converter in ``path_signature``, so the final output is also that converter's
    edge output on a real source-language schema.
    """
    scores: dict[str, dict] = {}
    if final_review.empty:
        return scores

    direct = final_review.copy()
    direct["status_normalized"] = direct["status"].map(normalize_status)
    direct = direct[direct["path_signature"].map(lambda signature: len(path_steps(signature)) == 1)]
    reviewed = direct[direct["status_normalized"].isin({"G", "L", "I"})]

    for edge_signature, group in reviewed.groupby("path_signature"):
        scores[str(edge_signature)] = _metrics_from_reviewed_edge_rows(group)
    return scores


def compute_intermediate_edge_metrics(edge_review: pd.DataFrame) -> dict[str, dict]:
    """Deprecated: compute edge metrics from annotated intermediate step outputs.

    Samples whose *direct input* was invalid are excluded (see
    ``_direct_input_invalid``), so a converter is not penalised for information
    an earlier step already lost or for being handed an unusable input.

    ``robustness`` / ``validity`` is the fraction of reviewed edge uses whose
    output was syntactically valid (``automatic_valid``).

    ``quality`` is the human G/L/I quality score conditional on syntactically
    valid outputs, so a converter that often fails but is good when it succeeds
    has high quality and lower robustness.

    The paper-facing evaluation now uses ``compute_direct_edge_metrics`` because
    direct one-step final outputs are substantially easier to annotate and make
    the metric claim clearer.
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
        scores[str(edge_signature)] = _metrics_from_reviewed_edge_rows(kept, excluded=excluded)
    return scores


def persist_edge_robustness(scores: dict[str, dict], path: Path) -> None:
    """Persist per-edge robustness scores for the orchestrator to load at runtime."""
    path.parent.mkdir(parents=True, exist_ok=True)
    ordered = dict(sorted(scores.items()))
    path.write_text(json.dumps(ordered, indent=2) + "\n", encoding="utf-8")


def load_edge_scores(path: Path) -> dict[str, dict]:
    """Load persisted edge metric entries keyed by edge signature."""
    if not path.exists():
        return {}
    return json.loads(path.read_text(encoding="utf-8"))


def filter_scores_to_registered_edges(scores: dict[str, dict], converters) -> dict[str, dict]:
    """Drop stale score rows for converters that are no longer registered."""
    registered = {
        f"{converter.source_language.value}:{converter.target_language.value}:{converter.name}"
        for converter in converters
    }
    return {signature: score for signature, score in scores.items() if signature in registered}


def main() -> None:
    parser = argparse.ArgumentParser(description="Plot broad orchestrator evaluation results.")
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT_DIR)
    parser.add_argument("--plots-dir", type=Path, default=None)
    parser.add_argument("--full-graph", action="store_true", help="Use all registered converters, not only core-language converters.")
    parser.add_argument(
        "--edge-score-source",
        choices=["direct-final", "intermediate-edge"],
        default="direct-final",
        help=(
            "Source for edge reliability scores. The default 'direct-final' uses one-step rows "
            "from final_outputs.csv. 'intermediate-edge' uses edge_outputs.csv and is deprecated."
        ),
    )
    args = parser.parse_args()

    review_dir = args.output_dir / "review"
    final_review_path = review_dir / "final_outputs.csv"
    edge_review_path = review_dir / "edge_outputs.csv"
    if not final_review_path.exists():
        raise SystemExit(f"Missing final review CSV: {final_review_path}")
    if args.edge_score_source == "intermediate-edge" and not edge_review_path.exists():
        raise SystemExit(f"Missing edge review CSV: {edge_review_path}")

    plots_dir = args.plots_dir or (args.output_dir / "plots")
    plots_dir.mkdir(parents=True, exist_ok=True)

    final_review = pd.read_csv(final_review_path)
    annotations, heat = build_orchestrator_result_matrix(final_review)
    matrix_path = plots_dir / "orchestrator_result_matrix.png"
    plot_orchestrator_result_matrix(annotations, heat, output_path=str(matrix_path))

    if args.edge_score_source == "intermediate-edge":
        edge_review = pd.read_csv(edge_review_path)
        edge_quality = build_intermediate_edge_quality_matrix(edge_review)
        edge_robustness = compute_intermediate_edge_metrics(edge_review)
    else:
        edge_quality = build_direct_edge_quality_matrix(final_review)
        edge_robustness = compute_direct_edge_metrics(final_review)

    edge_matrix_path = plots_dir / "edge_robustness_matrix.png"
    plot_edge_quality_matrix(edge_quality, output_path=str(edge_matrix_path))

    converters = register_converters(only_core_languages=not args.full_graph)
    full_converters = register_converters(only_core_languages=False)
    edge_robustness = filter_scores_to_registered_edges(
        edge_robustness,
        full_converters,
    )
    # Persist the per-edge robustness scores so the orchestrator can load them
    # for the edge-robustness ranking strategy (analogous to accuracy scores).
    persist_edge_robustness(edge_robustness, DEFAULT_ROBUSTNESS_PATH)
    persist_edge_robustness(edge_robustness, RESULTS_ROBUSTNESS_PATH)
    persist_edge_robustness(edge_robustness, args.output_dir / "edge_robustness_scores.json")
    edge_scores = edge_robustness
    protobuf_edge_scores = {
        signature: metrics
        for signature, metrics in load_edge_scores(PROTOBUF_EDGE_ROBUSTNESS_PATH).items()
        if ":Protobuf:" in signature
    }
    graphical_edge_scores = {
        **edge_scores,
        **protobuf_edge_scores,
    }
    conversion_graph = build_conversion_graph(converters)
    graph_path = plots_dir / "conversion_graph_edge_robustness.png"
    visualize_conversion_graph_with_metrics(
        conversion_graph,
        output_path=str(graph_path),
        show_edge_labels=True,
        edge_scores=edge_scores,
        include_languages=EVALUATION_LANGUAGES,
        show_colorbar=True,
    )

    full_graph_path = plots_dir / "conversion_graph_all_languages.png"
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
    graphical_abstract_svg_path = plots_dir / "graphical_abstract_conversion_graph.svg"
    visualize_graphical_abstract(
        full_conversion_graph,
        output_path=str(graphical_abstract_path),
        include_languages=GRAPHICAL_ABSTRACT_LANGUAGES,
        edge_scores=graphical_edge_scores,
    )
    visualize_graphical_abstract(
        full_conversion_graph,
        output_path=str(graphical_abstract_pdf_path),
        include_languages=GRAPHICAL_ABSTRACT_LANGUAGES,
        edge_scores=graphical_edge_scores,
    )
    visualize_graphical_abstract(
        full_conversion_graph,
        output_path=str(graphical_abstract_svg_path),
        include_languages=GRAPHICAL_ABSTRACT_LANGUAGES,
        edge_scores=graphical_edge_scores,
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
    print(f"Wrote {graphical_abstract_svg_path}")
    print(f"Wrote {full_graph_path}")
    print(f"Wrote edge robustness scores -> {DEFAULT_ROBUSTNESS_PATH}")
    print(f"Wrote edge robustness scores -> {RESULTS_ROBUSTNESS_PATH}")


if __name__ == "__main__":
    main()
