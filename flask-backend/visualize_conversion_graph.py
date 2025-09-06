from typing import Dict, List

import networkx as nx
import matplotlib
matplotlib.use("TkAgg")  # or "Qt5Agg"
import matplotlib.pyplot as plt

from data_structures import Converter, ConversionGraph

def visualize_conversion_graph(conversion_graph: ConversionGraph):
    # Create a directed graph
    G = nx.DiGraph()

    # Add edges from converters
    for source, converters in conversion_graph.items():
        for converter in converters:
            G.add_edge(str(converter.source_format), str(converter.target_format))

    # Layout for nodes
    pos = nx.spring_layout(G, seed=42, k=1.5)

    # Draw nodes
    nx.draw_networkx_nodes(G, pos, node_size=0, node_color="lightblue", edgecolors="black")

    # Draw edges
    nx.draw_networkx_edges(G, pos, arrowstyle="->", arrowsize=30, edge_color="gray")

    # Draw labels
    nx.draw_networkx_labels(G, pos, font_size=10, font_family="sans-serif")

    # Show plot
    plt.title("Schema Conversion Graph", fontsize=14)
    plt.axis("off")
    plt.show()


# main function to generate graph and then plot it
if __name__ == "__main__":
    from register_python_converters import register_python_converters
    from logic import build_conversion_graph
    converters: List[Converter] = register_python_converters()
    conversion_graph: ConversionGraph = build_conversion_graph(converters)
    visualize_conversion_graph(conversion_graph)