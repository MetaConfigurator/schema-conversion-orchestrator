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


# Human-readable, correctly spelled labels for schema-language enum values,
# used for the matrix axis ticks (single line, unlike the graph node labels).
LANGUAGE_DISPLAY = {
    "Dtd": "DTD",
    "Xsd": "XSD",
    "JsonSchema": "JSON Schema",
    "SHACL_TTL": "SHACL",
    "SHACL_JSON_LD": "SHACL JSON-LD",
    "Owl_TTL": "OWL (TTL)",
    "Owl_XML": "OWL (XML)",
    "Owl_OFN": "OWL (OFN)",
    "OWL_OBO": "OWL (OBO)",
    "OntologyRdf": "Ontology RDF",
    "LinkMl": "LinkML",
    "MdModels": "MD-Models",
    "GraphQL": "GraphQL",
    "Protobuf": "Protobuf",
    "Shex": "ShEx",
    "Mermaid": "Mermaid",
    "SqlAlchemy": "SQLAlchemy",
}


def _display_languages(frame: pd.DataFrame) -> pd.DataFrame:
    """Rename a square matrix's index/columns to display labels for plotting."""
    return frame.rename(index=LANGUAGE_DISPLAY, columns=LANGUAGE_DISPLAY)


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

    The input is ``eval/results/orchestrator_outputs/review/final_outputs.csv`` after
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


def _path_steps(path_signature: str) -> list[str]:
    return [step.strip() for step in str(path_signature).split(" -> ") if step.strip()]


def _parse_edge_signature(edge_signature: str) -> tuple[str, str, str]:
    source, target, converter = str(edge_signature).split(":", 2)
    return source, target, converter


def _append_edge_quality_row(rows: list[dict], edge_signature: str, group: pd.DataFrame, metadata: dict) -> None:
    reviewed = group[group["status_normalized"].isin({"G", "L", "I"})]
    good, lacking, invalid, unknown = _status_counts(group)
    total = len(reviewed)
    auto_valid = reviewed["automatic_valid"].astype(str).str.strip().str.lower().isin({"true", "1", "yes"})
    valid_outputs = int(auto_valid.sum())
    quality_rows = reviewed[auto_valid]
    quality_cases = len(quality_rows)
    quality_good = int((quality_rows["status_normalized"] == "G").sum())
    quality_lacking = int((quality_rows["status_normalized"] == "L").sum())
    robustness = valid_outputs / total if total else 0.0
    quality = (quality_good + 0.5 * quality_lacking) / quality_cases if quality_cases else 0.0
    score = robustness * quality
    rows.append({
        "edge_signature": edge_signature,
        "edge_source_language": metadata["edge_source_language"],
        "edge_target_language": metadata["edge_target_language"],
        "converter_name": metadata["converter_name"],
        "library": metadata.get("library", metadata["converter_name"]),
        "total": total,
        "good": good,
        "lacking": lacking,
        "invalid": invalid,
        "unknown": unknown,
        "score": score,
        "robustness": robustness,
        "quality": quality,
        "valid_outputs": valid_outputs,
        "quality_cases": quality_cases,
    })


def _direct_input_invalid(row, prev_index: dict) -> bool:
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
    prev_status = _normalize_status(prev.get("status"))
    prev_auto = str(prev.get("automatic_valid")).strip().lower()
    return prev_status == "I" or prev_auto in {"false", "0", "no"}


def _sort_edge_quality_matrix(matrix: pd.DataFrame) -> pd.DataFrame:
    if matrix.empty:
        return matrix

    source_order = {lang.value: index for index, lang in enumerate(SchemaLanguage)}
    matrix["pair"] = matrix["edge_source_language"] + " -> " + matrix["edge_target_language"]
    matrix["_source_order"] = matrix["edge_source_language"].map(source_order).fillna(999)
    matrix["_target_order"] = matrix["edge_target_language"].map(source_order).fillna(999)
    return matrix.sort_values(
        ["_source_order", "_target_order", "score", "good", "lacking", "total", "converter_name"],
        ascending=[True, True, False, False, False, False, True],
    ).drop(columns=["_source_order", "_target_order"]).reset_index(drop=True)


def build_direct_edge_quality_matrix(final_review: pd.DataFrame) -> pd.DataFrame:
    """Aggregate edge reliability from one-step final conversion results."""
    if final_review.empty:
        return pd.DataFrame()

    direct = final_review.copy()
    direct["status_normalized"] = direct["status"].map(_normalize_status)
    direct = direct[direct["path_signature"].map(lambda signature: len(_path_steps(signature)) == 1)]

    rows = []
    for edge_signature, group in direct.groupby("path_signature", sort=False):
        source, target, converter = _parse_edge_signature(edge_signature)
        _append_edge_quality_row(
            rows,
            edge_signature,
            group,
            {
                "edge_source_language": source,
                "edge_target_language": target,
                "converter_name": converter,
                "library": converter,
            },
        )
    return _sort_edge_quality_matrix(pd.DataFrame(rows))


def build_intermediate_edge_quality_matrix(edge_review: pd.DataFrame) -> pd.DataFrame:
    """Deprecated: aggregate metrics from annotated intermediate edge outputs."""
    if edge_review.empty:
        return pd.DataFrame()

    edge_review = edge_review.copy()
    edge_review["status_normalized"] = edge_review["status"].map(_normalize_status)
    prev_index = {
        (r["source_language"], r["target_language"], r["input_file"], r["path_id"], int(r["step_index"])): r
        for _, r in edge_review.iterrows()
        if str(r["step_index"]).strip().isdigit()
    }
    reviewed = edge_review[edge_review["status_normalized"].isin({"G", "L", "I"})]

    rows = []
    for edge_signature, group in reviewed.groupby("edge_signature", sort=False):
        kept = group[~group.apply(lambda r: _direct_input_invalid(r, prev_index), axis=1)]
        first = group.iloc[0]
        _append_edge_quality_row(
            rows,
            edge_signature,
            kept,
            {
                "edge_source_language": first["edge_source_language"],
                "edge_target_language": first["edge_target_language"],
                "converter_name": first["converter_name"],
                "library": first["library"],
            },
        )
    return _sort_edge_quality_matrix(pd.DataFrame(rows))


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
                f"{row['score']:.2f}\nR {row['robustness']:.2f} Q {row['quality']:.2f}",
                ha="center",
                va="bottom",
                fontsize=7.4,
            )

        axis.set_title(pair, fontsize=12, fontweight="semibold")
        axis.set_xticks(list(x_positions))
        axis.set_xticklabels(labels, rotation=35, ha="right", fontsize=8)
        axis.set_ylabel("Annotated direct outputs")
        axis.set_ylim(0, max(pair_data["total"].max() + 1.8, 3))
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
    fig.suptitle("Direct Converter Edge Reliability by Language Pair", y=1.01, fontsize=15, fontweight="semibold")
    fig.text(
        0.5,
        0.01,
        "Bars show annotated direct one-step outputs; labels show combined reliability, then R=syntactic robustness and Q=conditional quality.",
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

    annotations = _display_languages(annotations)
    heat = _display_languages(heat)

    cmap = LinearSegmentedColormap.from_list("orchestrator_quality", ["#C94C4C", "#F2D06B", "#5BAF72"])
    rows, cols = annotations.shape
    fig_width = max(5.8, cols * 1.05 + 1.65)
    fig_height = max(4.5, rows * 0.95 + 1.5)
    plt.figure(figsize=(fig_width, fig_height))
    axis = sns.heatmap(
        heat.astype(float),
        annot=annotations,
        fmt="",
        cmap=cmap,
        vmin=0.0,
        vmax=1.0,
        linewidths=0.8,
        linecolor="white",
        cbar_kws={"label": ""},
        annot_kws={"fontsize": 10.8, "fontweight": "semibold"},
    )
    colorbar = axis.collections[0].colorbar
    colorbar.set_label("Result quality score: (G + 0.5L) / total", fontsize=12)
    colorbar.set_ticks([0.0, 1.0])
    colorbar.set_ticklabels(["Invalid (0)", "Good (1)"])
    axis.set_xlabel("Output Schema Language")
    axis.set_ylabel("Input Schema Language")
    plt.xticks(rotation=45, ha="right")
    plt.yticks(rotation=0)
    plt.tight_layout()

    if output_path:
        plt.savefig(output_path, dpi=300, bbox_inches="tight")
    else:
        plt.show()

    plt.close()
