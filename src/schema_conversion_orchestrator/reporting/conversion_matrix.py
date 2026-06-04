from __future__ import annotations

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import networkx as nx
import pandas as pd
import seaborn as sns
from matplotlib.colors import LinearSegmentedColormap

from schema_conversion_orchestrator.domain.conversion_types import ConversionGraph
from schema_conversion_orchestrator.domain.schema_types import SchemaLanguage


def _language_value(language) -> str:
    return getattr(language, "value", str(language))


def build_path_count_matrix(conversion_graph: ConversionGraph) -> pd.DataFrame:
    """Build a matrix of possible path lengths for the converter graph."""
    graph = nx.DiGraph()
    for source, converters in conversion_graph.items():
        for converter in converters:
            graph.add_edge(
                _language_value(converter.source_language),
                _language_value(converter.target_language),
            )

    nodes = [lang.value for lang in SchemaLanguage if lang.value in graph.nodes()]
    matrix = pd.DataFrame(index=nodes, columns=nodes)

    for src in nodes:
        for tgt in nodes:
            if src == tgt:
                matrix.loc[src, tgt] = "0"
                continue

            if not nx.has_path(graph, src, tgt):
                matrix.loc[src, tgt] = "-"
                continue

            path_lengths = sorted(
                len(path) - 1 for path in nx.all_simple_paths(graph, source=src, target=tgt)
            )
            matrix.loc[src, tgt] = ", ".join(map(str, path_lengths))

    matrix.index.name = "Source Language"
    matrix.columns.name = "Target Language"
    return matrix


# Backwards-compatible function name for diagram generation.
def build_conversion_matrix(conversion_graph: ConversionGraph) -> pd.DataFrame:
    return build_path_count_matrix(conversion_graph)


def plot_path_count_matrix(matrix: pd.DataFrame, output_path: str | None = None) -> None:
    numeric_matrix = matrix.copy()

    for i in numeric_matrix.index:
        for j in numeric_matrix.columns:
            val = matrix.loc[i, j]
            if val == "0":
                numeric_matrix.loc[i, j] = 0
            elif val == "-":
                numeric_matrix.loc[i, j] = 5
            else:
                shortest_length = min(map(int, val.split(", ")))
                numeric_matrix.loc[i, j] = min(shortest_length, 4)

    numeric_matrix = numeric_matrix.astype(int)

    plt.figure(figsize=(12, 10))
    sns.heatmap(
        numeric_matrix,
        annot=matrix,
        fmt="",
        cmap="Blues",
        cbar_kws={"label": "Shortest possible path length"},
        linewidths=0.5,
        linecolor="gray",
    )
    plt.title("Schema Conversion Path Matrix", fontsize=16)
    plt.xticks(rotation=45, ha="right")
    plt.yticks(rotation=0)
    plt.tight_layout()

    if output_path:
        plt.savefig(output_path, dpi=300, bbox_inches="tight")
    else:
        plt.show()

    plt.close()


# Backwards-compatible function name for diagram generation.
def plot_conversion_matrix(matrix: pd.DataFrame, output_path: str | None = None) -> None:
    plot_path_count_matrix(matrix, output_path=output_path)


def build_orchestrator_result_matrix(final_review: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Build annotation and heat matrices for orchestrator-level best results.

    The input is ``eval/orchestrator_outputs/review/final_outputs.csv`` after
    optional human annotation. Only the best-ranked path per
    (source, target, input) is counted, because this matrix evaluates the
    orchestrator result shown to the user, not every individual path.
    """
    if final_review.empty:
        return pd.DataFrame(), pd.DataFrame()

    path_rank = pd.to_numeric(final_review["path_rank"], errors="coerce")
    best = final_review[path_rank == 1].copy()
    languages = list(dict.fromkeys(best["source_language"].tolist() + best["target_language"].tolist()))
    ordered = [lang.value for lang in SchemaLanguage if lang.value in languages]

    annotations = pd.DataFrame("", index=ordered, columns=ordered)
    heat = pd.DataFrame(0.0, index=ordered, columns=ordered)

    for source in ordered:
        for target in ordered:
            if source == target:
                annotations.loc[source, target] = "-"
                heat.loc[source, target] = 1.0
                continue

            pair = best[(best["source_language"] == source) & (best["target_language"] == target)]
            if pair.empty:
                annotations.loc[source, target] = "-"
                heat.loc[source, target] = 0.0
                continue

            path_count = int(pair["path_count"].max())
            statuses = pair["status"].fillna("").replace("", "?").str.upper()
            good = int((statuses == "G").sum())
            lacking = int((statuses == "L").sum())
            invalid = int((statuses == "I").sum())
            unknown = int((statuses == "?").sum())

            status_line = f"{good}G {lacking}L {invalid}I"
            if unknown:
                status_line += f" {unknown}?"
            annotations.loc[source, target] = f"{path_count}P\n{status_line}"

            total = max(len(pair), 1)
            heat.loc[source, target] = (good + 0.5 * lacking) / total

    annotations.index.name = "Source Language"
    annotations.columns.name = "Target Language"
    return annotations, heat


def plot_orchestrator_result_matrix(
    annotations: pd.DataFrame,
    heat: pd.DataFrame,
    output_path: str | None = None,
) -> None:
    if annotations.empty:
        raise ValueError("Cannot plot an empty orchestrator result matrix.")

    cmap = LinearSegmentedColormap.from_list("orchestrator_quality", ["#C94C4C", "#F2D06B", "#5BAF72"])
    plt.figure(figsize=(12, 9))
    sns.heatmap(
        heat.astype(float),
        annot=annotations,
        fmt="",
        cmap=cmap,
        vmin=0.0,
        vmax=1.0,
        linewidths=0.8,
        linecolor="white",
        cbar_kws={"label": "Best-result quality score: (G + 0.5L) / total"},
        annot_kws={"fontsize": 9},
    )
    plt.title("Orchestrator Evaluation Matrix", fontsize=16)
    plt.xticks(rotation=45, ha="right")
    plt.yticks(rotation=0)
    plt.tight_layout()

    if output_path:
        plt.savefig(output_path, dpi=300, bbox_inches="tight")
    else:
        plt.show()

    plt.close()
