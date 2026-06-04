from collections import defaultdict
from math import atan2, cos, sin

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.colors import LinearSegmentedColormap, Normalize
from matplotlib.patches import FancyArrowPatch
import networkx as nx

from schema_conversion_orchestrator.domain.conversion_types import ConversionGraph


DISPLAY_LABELS = {
    "JsonSchema": "JSON\nSchema",
    "SHACL_TTL": "SHACL\nTTL",
    "SHACL_JSON_LD": "SHACL\nJSON-LD",
    "Owl_TTL": "OWL\nTTL",
    "Owl_XML": "OWL\nXML",
    "Owl_OFN": "OWL\nOFN",
    "OWL_OBO": "OWL\nOBO",
    "OntologyRdf": "Ontology\nRDF",
    "LinkMl": "LinkML",
    "MdModels": "MdModels",
    "GraphQL": "GraphQL",
    "Protobuf": "Protobuf",
    "SqlAlchemy": "SQL\nAlchemy",
}

NODE_GROUPS = {
    "Dtd": "xml",
    "Xsd": "xml",
    "JsonSchema": "json",
    "SHACL_TTL": "semantic",
    "SHACL_JSON_LD": "semantic",
    "Owl_TTL": "semantic",
    "Owl_XML": "semantic",
    "Owl_OFN": "semantic",
    "OWL_OBO": "semantic",
    "OntologyRdf": "semantic",
    "LinkMl": "pivot",
    "MdModels": "pivot",
    "GraphQL": "generated",
    "Protobuf": "generated",
    "Shex": "generated",
    "Mermaid": "generated",
    "SqlAlchemy": "generated",
}

GROUP_COLORS = {
    "xml": "#F3C17A",
    "json": "#8BC3D9",
    "semantic": "#98C79A",
    "pivot": "#D9B3E6",
    "generated": "#C7CCD6",
}

PREFERRED_POSITIONS = {
    "Dtd": (-4.7, 1.8),
    "Xsd": (-3.1, 0.9),
    "JsonSchema": (-0.8, 0.1),
    "LinkMl": (1.4, 1.15),
    "MdModels": (1.4, -1.15),
    "SHACL_TTL": (-0.4, -2.0),
    "SHACL_JSON_LD": (-2.7, -2.05),
    "Owl_TTL": (0.1, 2.25),
    "Owl_XML": (-1.9, 2.85),
    "Owl_OFN": (2.0, 2.85),
    "OWL_OBO": (3.2, 2.0),
    "OntologyRdf": (-3.6, 2.85),
    "GraphQL": (4.0, 0.95),
    "Protobuf": (4.25, 0.15),
    "Shex": (4.1, -0.65),
    "SqlAlchemy": (4.05, 1.75),
    "Mermaid": (4.2, -1.45),
}


def _language_value(language) -> str:
    return getattr(language, "value", str(language))


def _display_label(language: str) -> str:
    return DISPLAY_LABELS.get(language, language.replace("_", "\n"))


def _converter_label(name: str) -> str:
    replacements = {
        "JSON Schema": "JSON Schema",
        "JsonSchema": "JSON Schema",
        "SHACL TTL": "SHACL TTL",
        "SHACL_TTL": "SHACL TTL",
        "SHACL JSON LD": "SHACL JSON-LD",
        "SHACL_JSON_LD": "SHACL JSON-LD",
        "MdModels": "MdModels",
        "LinkMl": "LinkML",
    }
    label = name.replace("_", " ").replace(" TO ", " -> ").replace(" to ", " -> ")
    for old, new in replacements.items():
        label = label.replace(old, new)
    if len(label) > 34:
        label = label[:31].rstrip() + "..."
    return label


def _library_label(converter) -> str:
    label = converter.library or converter.name
    replacements = {
        "schema-automator": "LinkML",
        "linkml": "LinkML",
        "mdmodels": "MdModels",
        "xsd-json-converter": "xsd-json",
        "@comake/shacl-to-json-schema": "@comake",
        "shacl-bridge": "shacl-bridge",
        "xsd2jsonschema": "xsd2jsonschema",
    }
    return replacements.get(label, label)


def _positions_for(nodes: list[str]) -> dict[str, tuple[float, float]]:
    positions = {node: PREFERRED_POSITIONS[node] for node in nodes if node in PREFERRED_POSITIONS}
    missing = [node for node in nodes if node not in positions]
    if missing:
        fallback = nx.spring_layout(nx.Graph([(node, node) for node in missing]), seed=7)
        for node, (x, y) in fallback.items():
            positions[node] = (float(x) + 4.2, float(y) - 2.4)
    return positions


def _edge_radii(edge_count: int) -> list[float]:
    if edge_count == 1:
        return [0.0]
    spacing = 0.16
    start = -spacing * (edge_count - 1) / 2
    return [start + i * spacing for i in range(edge_count)]


def _draw_edge(
    ax,
    src: str,
    tgt: str,
    label: str,
    rad: float,
    pos: dict[str, tuple[float, float]],
    show_label: bool,
    color: str,
    label_shift: float = 0.0,
) -> None:
    x1, y1 = pos[src]
    x2, y2 = pos[tgt]
    arrow = FancyArrowPatch(
        (x1, y1),
        (x2, y2),
        arrowstyle="-|>",
        mutation_scale=14,
        linewidth=1.35,
        color=color,
        alpha=0.86,
        shrinkA=28,
        shrinkB=28,
        connectionstyle=f"arc3,rad={rad}",
        zorder=1,
    )
    ax.add_patch(arrow)

    if show_label:
        mid_x = (x1 + x2) / 2
        mid_y = (y1 + y2) / 2
        angle = atan2(y2 - y1, x2 - x1)
        tangent_x = cos(angle)
        tangent_y = sin(angle)
        normal_x = -sin(angle)
        normal_y = cos(angle)
        distance = ((x2 - x1) ** 2 + (y2 - y1) ** 2) ** 0.5
        curve_offset = rad * distance * 0.5
        clearance = 0.09 if rad == 0 else 0.04
        clearance *= 1 if rad >= 0 else -1
        ax.text(
            mid_x + tangent_x * label_shift + normal_x * (curve_offset + clearance),
            mid_y + tangent_y * label_shift + normal_y * (curve_offset + clearance),
            label,
            ha="center",
            va="center",
            fontsize=7.2,
            color="#26313A",
            bbox={
                "boxstyle": "round,pad=0.18,rounding_size=0.08",
                "facecolor": "white",
                "edgecolor": "#D5DAE0",
                "linewidth": 0.55,
                "alpha": 0.94,
            },
            zorder=3,
        )


def visualize_conversion_graph(conversion_graph: ConversionGraph, output_path, show_edge_labels: bool = False):
    visualize_conversion_graph_with_metrics(
        conversion_graph,
        output_path=output_path,
        show_edge_labels=show_edge_labels,
        edge_scores=None,
        include_languages=None,
    )


def visualize_conversion_graph_with_metrics(
    conversion_graph: ConversionGraph,
    output_path,
    show_edge_labels: bool = True,
    edge_scores: dict[str, float] | None = None,
    include_languages: set[str] | None = None,
):
    nodes = set()
    edges_by_pair = defaultdict(list)
    for source, converters in conversion_graph.items():
        for converter in converters:
            src = _language_value(converter.source_language)
            tgt = _language_value(converter.target_language)
            if include_languages is not None and (src not in include_languages or tgt not in include_languages):
                continue
            nodes.update([src, tgt])
            signature = f"{src}:{tgt}:{converter.name}"
            label = _library_label(converter) if show_edge_labels else _converter_label(converter.name)
            edges_by_pair[(src, tgt)].append((label, signature))

    pos = _positions_for(sorted(nodes))
    fig, ax = plt.subplots(figsize=(13.5, 8.2))
    ax.set_facecolor("#FFFFFF")
    cmap = LinearSegmentedColormap.from_list("edge_quality", ["#C94C4C", "#F2D06B", "#5BAF72"])
    norm = Normalize(vmin=0.0, vmax=1.0)

    for (src, tgt), edge_entries in sorted(edges_by_pair.items()):
        reverse_count = len(edges_by_pair.get((tgt, src), []))
        pair_count = len(edge_entries) + reverse_count
        base_radii = _edge_radii(pair_count)
        if reverse_count:
            radii = base_radii[reverse_count:]
        else:
            radii = _edge_radii(len(edge_entries))
        label_shifts = [
            (index - (len(edge_entries) - 1) / 2) * 0.38
            for index in range(len(edge_entries))
        ]
        for (label, signature), rad, label_shift in zip(edge_entries, radii, label_shifts):
            score = edge_scores.get(signature) if edge_scores else None
            color = cmap(norm(score)) if score is not None else "#5F6B76"
            _draw_edge(
                ax,
                src,
                tgt,
                label,
                rad,
                pos,
                show_label=show_edge_labels,
                color=color,
                label_shift=label_shift,
            )

    for node, (x, y) in pos.items():
        group = NODE_GROUPS.get(node, "generated")
        ax.scatter(
            [x],
            [y],
            s=2500,
            c=GROUP_COLORS[group],
            edgecolors="#28323C",
            linewidths=1.15,
            zorder=4,
        )
        ax.text(
            x,
            y,
            _display_label(node),
            ha="center",
            va="center",
            fontsize=8.8,
            fontweight="semibold",
            color="#17202A",
            linespacing=0.9,
            zorder=5,
        )

    legend_handles = [
        plt.Line2D(
            [0],
            [0],
            marker="o",
            color="none",
            label=label,
            markerfacecolor=GROUP_COLORS[key],
            markeredgecolor="#28323C",
            markersize=9,
        )
        for key, label in [
            ("xml", "XML"),
            ("json", "JSON"),
            ("semantic", "Semantic Web"),
            ("pivot", "Pivot/modeling"),
            ("generated", "Generated targets"),
        ]
        if any(NODE_GROUPS.get(node, "generated") == key for node in nodes)
    ]
    ax.legend(
        handles=legend_handles,
        loc="lower center",
        bbox_to_anchor=(0.5, -0.02),
        ncol=len(legend_handles),
        frameon=False,
        fontsize=9,
    )
    if edge_scores:
        sm = plt.cm.ScalarMappable(cmap=cmap, norm=norm)
        sm.set_array([])
        cbar = fig.colorbar(sm, ax=ax, fraction=0.028, pad=0.012)
        cbar.set_label("Edge quality score: (G + 0.5L) / total")

    xs = [x for x, _ in pos.values()]
    ys = [y for _, y in pos.values()]
    ax.set_xlim(min(xs) - 1.0, max(xs) + 1.0)
    ax.set_ylim(min(ys) - 0.9, max(ys) + 0.85)
    ax.axis("off")
    fig.tight_layout(pad=0.25)
    fig.savefig(output_path, dpi=300, bbox_inches="tight", facecolor="white")
    plt.close(fig)
