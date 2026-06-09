from collections import defaultdict
from math import hypot

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

# Scatter marker area (points^2) used for the language nodes; shared with the
# label placement so labels can be kept clear of the node circles.
NODE_MARKER_AREA = 2500
LABEL_GAP_PX = 8.0

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

GRAPHICAL_ABSTRACT_POSITIONS = {
    "Dtd": (-3.0, 0.72),
    "Xsd": (-2.35, 0.2),
    "JsonSchema": (-0.78, 0.38),
    "SHACL_TTL": (-0.35, -0.9),
    "LinkMl": (0.48, 0.56),
    "MdModels": (0.58, -0.82),
    "Owl_OFN": (1.08, 1.25),
    "GraphQL": (2.42, 1.12),
    "Protobuf": (2.82, 0.56),
    "SqlAlchemy": (2.82, -0.08),
    "Shex": (2.42, -0.78),
    "Mermaid": (1.86, -1.28),
}

GRAPHICAL_ABSTRACT_LABELS = {
    "SHACL_TTL": "SHACL",
    "Owl_OFN": "OWL",
}

GRAPHICAL_ABSTRACT_TITLE = "Graph-Based Schema Conversion Orchestration"


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


def _edge_radii(edge_count: int, spacing: float = 0.16) -> list[float]:
    if edge_count == 1:
        return [0.0]
    start = -spacing * (edge_count - 1) / 2
    return [start + i * spacing for i in range(edge_count)]


def _bezier_point(p0, control, p1, t):
    """Point at parameter ``t`` on the quadratic Bezier ``p0 -> control -> p1``."""
    mt = 1.0 - t
    x = mt * mt * p0[0] + 2 * mt * t * control[0] + t * t * p1[0]
    y = mt * mt * p0[1] + 2 * mt * t * control[1] + t * t * p1[1]
    return x, y


def _arc_control_point(p0, p1, rad):
    """Control point of matplotlib's ``arc3`` quadratic Bezier for a given rad."""
    mx, my = (p0[0] + p1[0]) / 2.0, (p0[1] + p1[1]) / 2.0
    dx, dy = p1[0] - p0[0], p1[1] - p0[1]
    return (mx + rad * dy, my - rad * dx)


def _draw_edge(
    ax,
    src: str,
    tgt: str,
    label: str,
    rad: float,
    pos: dict[str, tuple[float, float]],
    show_label: bool,
    color: str,
    init_param: float = 0.5,
):
    p0 = pos[src]
    p1 = pos[tgt]
    arrow = FancyArrowPatch(
        p0,
        p1,
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

    if not show_label:
        return None

    # The label sits centered *on* the edge (the same quadratic Bezier the arc
    # follows) at parameter ``init_param``; the de-overlap pass only slides it
    # back and forth along this curve, so it stays attached to its edge.
    control = _arc_control_point(p0, p1, rad)
    text = ax.text(
        *_bezier_point(p0, control, p1, init_param),
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
    return {"text": text, "p0": p0, "p1": p1, "control": control, "param": init_param}


def _rect_overlap(a, b, pad=0.0):
    """Whether two ``(x0, y0, x1, y1)`` boxes overlap, optionally inflated by pad."""
    return not (
        a[2] + pad < b[0]
        or a[0] - pad > b[2]
        or a[3] + pad < b[1]
        or a[1] - pad > b[3]
    )


def _place_labels_along_edges(
    fig,
    ax,
    labels,
    node_positions=(),
    node_area=NODE_MARKER_AREA,
    node_pad_px=5.0,
    label_gap_px=LABEL_GAP_PX,
    param_min=0.12,
    param_max=0.88,
    step=0.015,
):
    """Place each edge label on its edge, sliding it to avoid collisions.

    Each label starts at the edge center and is moved *along its own edge*,
    toward the target first and then back toward the source, stopping at the
    first collision-free position. A first pass tries to avoid the other edge
    lines, the other labels, and the node circles. If no such spot exists for a
    label, a second pass for that label allows it to sit on top of other edge
    lines, but still enforces spacing from other labels and the node circles.
    """
    labels = [item for item in labels if item is not None]
    if not labels:
        return

    fig.canvas.draw()
    renderer = fig.canvas.get_renderer()

    def _point(item, param):
        return _bezier_point(item["p0"], item["control"], item["p1"], param)

    # Sample every edge into a display-space polyline (obstacle for the first pass).
    samples = 36
    edge_polylines = [
        [
            tuple(ax.transData.transform(_point(item, param_min + (param_max - param_min) * k / (samples - 1))))
            for k in range(samples)
        ]
        for item in labels
    ]

    node_centers = [tuple(ax.transData.transform(p)) for p in node_positions]
    node_radius = (node_area ** 0.5) / 2.0 * (fig.dpi / 72.0) + node_pad_px

    # Candidate parameters: edge center first, then toward the target, then back.
    candidates = [0.5]
    forward = 0.5 + step
    while forward <= param_max + 1e-9:
        candidates.append(forward)
        forward += step
    backward = 0.5 - step
    while backward >= param_min - 1e-9:
        candidates.append(backward)
        backward -= step

    def _extent(item, param):
        item["text"].set_position(_point(item, param))
        box = item["text"].get_window_extent(renderer=renderer)
        return (box.x0, box.y0, box.x1, box.y1)

    def _hits_nodes(box):
        for ncx, ncy in node_centers:
            nx = min(max(ncx, box[0]), box[2])
            ny = min(max(ncy, box[1]), box[3])
            if hypot(ncx - nx, ncy - ny) < node_radius:
                return True
        return False

    def _hits_labels(box, placed):
        return any(_rect_overlap(box, other, label_gap_px) for other in placed)

    def _hits_edges(box, self_index):
        for index, polyline in enumerate(edge_polylines):
            if index == self_index:
                continue
            if any(box[0] <= px <= box[2] and box[1] <= py <= box[3] for px, py in polyline):
                return True
        return False

    placed = []
    for i, item in enumerate(labels):
        chosen = None
        # First pass: avoid other edges, other labels, and node circles.
        for param in candidates:
            box = _extent(item, param)
            if _hits_nodes(box) or _hits_labels(box, placed) or _hits_edges(box, i):
                continue
            chosen = (param, box)
            break
        # Second pass: allow crossing other edge lines, but not labels or nodes.
        if chosen is None:
            for param in candidates:
                box = _extent(item, param)
                if _hits_nodes(box) or _hits_labels(box, placed):
                    continue
                chosen = (param, box)
                break
        # Last resort: keep the edge center.
        if chosen is None:
            chosen = (0.5, _extent(item, 0.5))
        param, box = chosen
        item["param"] = param
        item["text"].set_position(_point(item, param))
        placed.append(box)


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
    show_colorbar: bool = True,
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
    label_texts = []

    for (src, tgt), edge_entries in sorted(edges_by_pair.items()):
        reverse_count = len(edges_by_pair.get((tgt, src), []))
        pair_count = len(edge_entries) + reverse_count
        base_radii = _edge_radii(pair_count)
        if reverse_count:
            radii = base_radii[reverse_count:]
        else:
            radii = _edge_radii(len(edge_entries))
        for (label, signature), rad in zip(edge_entries, radii):
            score = edge_scores.get(signature) if edge_scores else None
            color = cmap(norm(score)) if score is not None else "#5F6B76"
            item = _draw_edge(
                ax,
                src,
                tgt,
                label,
                rad,
                pos,
                show_label=show_edge_labels,
                color=color,
            )
            if item is not None:
                label_texts.append(item)

    for node, (x, y) in pos.items():
        group = NODE_GROUPS.get(node, "generated")
        ax.scatter(
            [x],
            [y],
            s=NODE_MARKER_AREA,
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
    if edge_scores and show_colorbar:
        sm = plt.cm.ScalarMappable(cmap=cmap, norm=norm)
        sm.set_array([])
        cbar = fig.colorbar(sm, ax=ax, fraction=0.028, pad=0.012)
        cbar.set_label("Edge robustness score: (G + 0.5L) / total")

    xs = [x for x, _ in pos.values()]
    ys = [y for _, y in pos.values()]
    ax.set_xlim(min(xs) - 1.0, max(xs) + 1.0)
    ax.set_ylim(min(ys) - 0.9, max(ys) + 0.85)
    ax.axis("off")
    fig.tight_layout(pad=0.25)
    _place_labels_along_edges(fig, ax, label_texts, node_positions=list(pos.values()))
    fig.savefig(output_path, dpi=300, bbox_inches="tight", facecolor="white")
    plt.close(fig)


def visualize_graphical_abstract(
    conversion_graph: ConversionGraph,
    output_path,
    include_languages: set[str] | None = None,
):
    """Render a compact, label-free graph for graphical abstracts.

    This intentionally does not share the full evaluation graph renderer:
    parallel converter implementations are collapsed into one directed edge,
    edges are neutral, and node positions are tuned for a compact submission
    image rather than for detailed converter inspection.
    """
    nodes = set()
    edge_pairs = set()
    for source, converters in conversion_graph.items():
        for converter in converters:
            src = _language_value(converter.source_language)
            tgt = _language_value(converter.target_language)
            if include_languages is not None and (src not in include_languages or tgt not in include_languages):
                continue
            nodes.update([src, tgt])
            edge_pairs.add((src, tgt))

    pos = {node: GRAPHICAL_ABSTRACT_POSITIONS[node] for node in nodes if node in GRAPHICAL_ABSTRACT_POSITIONS}
    missing = sorted(nodes - set(pos))
    if missing:
        fallback = _positions_for(missing)
        pos.update(fallback)

    fig, ax = plt.subplots(figsize=(13.28, 5.31))
    ax.set_facecolor("#FFFFFF")
    edge_color = "#74808A"

    for src, tgt in sorted(edge_pairs):
        if src not in pos or tgt not in pos:
            continue
        arrowstyle = "-|>"
        if {src, tgt} == {"Owl_OFN", "LinkMl"}:
            arrowstyle = "<|-|>"
        if (tgt, src) in edge_pairs:
            rad = 0.055 if src < tgt else -0.055
        else:
            rad = 0.0
        arrow = FancyArrowPatch(
            pos[src],
            pos[tgt],
            arrowstyle=arrowstyle,
            mutation_scale=14,
            linewidth=1.35,
            color=edge_color,
            alpha=0.9,
            shrinkA=40,
            shrinkB=40,
            connectionstyle=f"arc3,rad={rad}",
            zorder=1,
        )
        ax.add_patch(arrow)

    for node, (x, y) in pos.items():
        group = NODE_GROUPS.get(node, "generated")
        ax.scatter(
            [x],
            [y],
            s=4400,
            c=GROUP_COLORS[group],
            edgecolors="#28323C",
            linewidths=1.15,
            zorder=4,
        )
        ax.text(
            x,
            y,
            GRAPHICAL_ABSTRACT_LABELS.get(node, _display_label(node)),
            ha="center",
            va="center",
            fontsize=12.2,
            fontweight="semibold",
            color="#17202A",
            linespacing=0.9,
            zorder=5,
        )

    xs = [x for x, _ in pos.values()]
    ys = [y for _, y in pos.values()]
    ax.set_xlim(min(xs) - 1.05, max(xs) + 1.05)
    ax.set_ylim(min(ys) - 0.35, max(ys) + 0.35)
    ax.axis("off")
    fig.text(
        0.5,
        0.94,
        GRAPHICAL_ABSTRACT_TITLE,
        ha="center",
        va="center",
        fontsize=17,
        fontweight="semibold",
        color="#17202A",
    )
    fig.tight_layout(rect=(0, 0, 1, 0.88), pad=0.03)
    fig.savefig(output_path, dpi=300, facecolor="white")
    plt.close(fig)
