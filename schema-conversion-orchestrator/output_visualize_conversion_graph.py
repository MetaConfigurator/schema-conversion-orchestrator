import matplotlib
matplotlib.use("TkAgg")  # or "Qt5Agg"
import matplotlib.pyplot as plt
import networkx as nx
from converter import ConversionGraph


def visualize_conversion_graph(conversion_graph: ConversionGraph, output_path):
    # Build directed graph
    G = nx.DiGraph()
    edge_labels = {}

    for source, converters in conversion_graph.items():
        for converter in converters:
            src, tgt = str(converter.source_format), str(converter.target_format)
            G.add_edge(src, tgt)
            edge_labels[(src, tgt)] = converter.name

    # Layout: shell spreads nodes in concentric circles
    pos = nx.shell_layout(G)

    plt.figure(figsize=(16, 12))

    # --- Draw nodes ---
    nx.draw_networkx_nodes(
        G, pos,
        node_size=1800,
        node_color="skyblue",
        edgecolors="black",
        linewidths=1.2
    )

    # --- Draw edges with curvature for bidirectional ones ---
    curved_edges = [edge for edge in G.edges() if (edge[1], edge[0]) in G.edges()]
    straight_edges = list(set(G.edges()) - set(curved_edges))

    # Straight edges
    nx.draw_networkx_edges(
        G, pos,
        edgelist=straight_edges,
        arrowstyle="->",
        arrowsize=35,
        edge_color="gray"
    )

    # Curved edges (for bidirectional connections)
    nx.draw_networkx_edges(
        G, pos,
        edgelist=curved_edges,
        arrowstyle="->",
        arrowsize=35,
        edge_color="gray",
        connectionstyle="arc3,rad=0.25"
    )

    # --- Draw labels ---
    nx.draw_networkx_labels(
        G, pos,
        font_size=10,
        font_family="sans-serif"
    )

    # --- Draw edge labels (converter names) ---
    nx.draw_networkx_edge_labels(
        G, pos,
        edge_labels=edge_labels,
        font_size=8,
        rotate=False,
        bbox=dict(boxstyle="round,pad=0.2", fc="white", alpha=0.7)
    )

    plt.title("Schema Conversion Graph", fontsize=16)
    plt.axis("off")
    plt.tight_layout()

    # save plot to file
    plt.savefig(output_path)

