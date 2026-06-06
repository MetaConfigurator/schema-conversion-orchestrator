from __future__ import annotations

import math
import textwrap

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


def _normalize_status(value) -> str:
    if pd.isna(value):
        return ""
    return str(value).strip().upper()


def _status_counts(rows: pd.DataFrame) -> tuple[int, int, int, int]:
    statuses = rows["status"].map(_normalize_status)
    good = int((statuses == "G").sum())
    lacking = int((statuses == "L").sum())
    invalid = int((statuses == "I").sum())
    unknown = int((~statuses.isin({"G", "L", "I"})).sum())
    return good, lacking, invalid, unknown


def build_edge_quality_matrix(edge_review: pd.DataFrame) -> pd.DataFrame:
    """Aggregate edge-local quality counts by concrete converter edge."""
    if edge_review.empty:
        return pd.DataFrame()

    rows = []
    for edge_signature, group in edge_review.groupby("edge_signature", sort=False):
        good, lacking, invalid, unknown = _status_counts(group)
        total = len(group)
        score = (good + 0.5 * lacking) / total if total else 0.0
        first = group.iloc[0]
        rows.append({
            "edge_signature": edge_signature,
            "edge_source_language": first["edge_source_language"],
            "edge_target_language": first["edge_target_language"],
            "converter_name": first["converter_name"],
            "library": first["library"],
            "total": total,
            "good": good,
            "lacking": lacking,
            "invalid": invalid,
            "unknown": unknown,
            "score": score,
        })

    matrix = pd.DataFrame(rows)
    if matrix.empty:
        return matrix

    source_order = {lang.value: index for index, lang in enumerate(SchemaLanguage)}
    matrix["pair"] = matrix["edge_source_language"] + " -> " + matrix["edge_target_language"]
    matrix["_source_order"] = matrix["edge_source_language"].map(source_order).fillna(999)
    matrix["_target_order"] = matrix["edge_target_language"].map(source_order).fillna(999)
    matrix = matrix.sort_values(
        ["_source_order", "_target_order", "score", "good", "lacking", "total", "converter_name"],
        ascending=[True, True, False, False, False, False, True],
    ).drop(columns=["_source_order", "_target_order"]).reset_index(drop=True)
    return matrix


def plot_edge_quality_matrix(
    edge_quality: pd.DataFrame,
    output_path: str | None = None,
) -> None:
    if edge_quality.empty:
        raise ValueError("Cannot plot an empty edge quality matrix.")

    plot_data = edge_quality.copy()
    pairs = plot_data["pair"].drop_duplicates().tolist()
    ncols = min(3, len(pairs))
    nrows = math.ceil(len(pairs) / ncols)
    fig, axes = plt.subplots(
        nrows,
        ncols,
        figsize=(max(8, 6.4 * ncols), max(5, 4.4 * nrows)),
        squeeze=False,
    )

    colors = {
        "good": "#5BAF72",
        "lacking": "#F2D06B",
        "invalid": "#C94C4C",
        "unknown": "#9CA3AF",
    }
    legend_handles = None

    for axis, pair in zip(axes.flatten(), pairs):
        pair_data = plot_data[plot_data["pair"] == pair].reset_index(drop=True)
        labels = [
            "\n".join(textwrap.wrap(str(name), width=18, break_long_words=False))
            for name in pair_data["converter_name"]
        ]
        x_positions = range(len(pair_data))

        invalid = pair_data["invalid"].to_numpy()
        lacking = pair_data["lacking"].to_numpy()
        good = pair_data["good"].to_numpy()
        unknown = pair_data["unknown"].to_numpy()

        invalid_bars = axis.bar(x_positions, invalid, color=colors["invalid"], label="Invalid")
        lacking_bars = axis.bar(x_positions, lacking, bottom=invalid, color=colors["lacking"], label="Lacking")
        good_bars = axis.bar(
            x_positions,
            good,
            bottom=invalid + lacking,
            color=colors["good"],
            label="Good",
        )
        unknown_bars = None
        if unknown.any():
            unknown_bars = axis.bar(
                x_positions,
                unknown,
                bottom=invalid + lacking + good,
                color=colors["unknown"],
                label="Unknown",
            )

        if legend_handles is None:
            legend_handles = [good_bars[0], lacking_bars[0], invalid_bars[0]]
            if unknown_bars is not None:
                legend_handles.append(unknown_bars[0])

        for index, row in pair_data.iterrows():
            axis.text(
                index,
                float(row["total"]) + 0.15,
                f"{row['score']:.2f}",
                ha="center",
                va="bottom",
                fontsize=8,
            )

        axis.set_title(pair, fontsize=12, fontweight="semibold")
        axis.set_xticks(list(x_positions))
        axis.set_xticklabels(labels, rotation=35, ha="right", fontsize=8)
        axis.set_ylabel("Annotated edge uses")
        axis.set_ylim(0, max(pair_data["total"].max() + 1, 3))
        axis.grid(axis="y", alpha=0.25)

    for axis in axes.flatten()[len(pairs):]:
        axis.axis("off")

    legend_labels = ["Good", "Lacking", "Invalid"]
    if legend_handles and len(legend_handles) == 4:
        legend_labels.append("Unknown")
    if legend_handles:
        fig.legend(
            legend_handles,
            legend_labels,
            loc="upper center",
            ncol=len(legend_labels),
            frameon=False,
            bbox_to_anchor=(0.5, 0.995),
        )
    fig.suptitle("Direct Converter Edge Robustness by Language Pair", y=1.01, fontsize=15, fontweight="semibold")
    fig.text(
        0.5,
        0.01,
        "Bars show concrete converter edges; height is annotated edge-output uses; numbers above bars are robustness scores (G + 0.5L) / total.",
        ha="center",
        va="center",
        fontsize=10,
    )
    fig.tight_layout(rect=(0, 0.025, 1, 0.965))

    if output_path:
        fig.savefig(output_path, dpi=300, bbox_inches="tight")
    else:
        plt.show()

    plt.close()


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
        annot_kws={"fontsize": 12, "fontweight": "semibold"},
    )
    plt.xticks(rotation=45, ha="right")
    plt.yticks(rotation=0)
    plt.gcf().text(
        0.5,
        0.02,
        "G = good, L = lacking, I = invalid",
        ha="center",
        va="center",
        fontsize=11,
    )
    plt.tight_layout()

    if output_path:
        plt.savefig(output_path, dpi=300, bbox_inches="tight")
    else:
        plt.show()

    plt.close()
