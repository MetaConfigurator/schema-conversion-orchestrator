import networkx as nx
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from converter import ConversionGraph
from schema_types import SchemaLanguage


def build_conversion_matrix(conversion_graph: ConversionGraph) -> pd.DataFrame:
    G = nx.DiGraph()
    for source, converters in conversion_graph.items():
        for converter in converters:
            G.add_edge(
                str(converter.source_language),
                str(converter.target_language)
            )

    # enum-defined order, filtered to languages present in the graph
    nodes = [
        lang.value
        for lang in SchemaLanguage
        if lang.value in G.nodes()
    ]
    matrix = pd.DataFrame(index=nodes, columns=nodes)

    for src in nodes:
        for tgt in nodes:
            if src == tgt:
                matrix.loc[src, tgt] = "0"
                continue

            if not nx.has_path(G, src, tgt):
                matrix.loc[src, tgt] = "—"
                continue

            # collect lengths of all simple paths
            path_lengths = [
                len(path) - 1
                for path in nx.all_simple_paths(G, source=src, target=tgt)
            ]

            path_lengths.sort()
            matrix.loc[src, tgt] = ", ".join(map(str, path_lengths))

    matrix.index.name = "Source Language"
    matrix.columns.name = "Target Language"
    return matrix


def plot_conversion_matrix(matrix: pd.DataFrame, output_path: str = None) -> None:
    numeric_matrix = matrix.copy()

    for i in numeric_matrix.index:
        for j in numeric_matrix.columns:
            val = matrix.loc[i, j]

            if val == "0":
                numeric_matrix.loc[i, j] = 0
            elif val == "—":
                numeric_matrix.loc[i, j] = 5
            else:
                # otherwise length of shortest path, to a max of 6
                shortest_length = min(map(int, val.split(", ")))
                numeric_matrix.loc[i, j] = min(shortest_length, 4)

    numeric_matrix = numeric_matrix.astype(int)

    plt.figure(figsize=(12, 10))
    ax = sns.heatmap(
        numeric_matrix,
        annot=matrix,
        fmt="",
        cmap="Blues",
        cbar_kws={"label": "Distances of the possible conversion paths"},
        linewidths=0.5,
        linecolor="gray"
    )
    plt.title("Schema Conversion Matrix", fontsize=16)
    plt.xticks(rotation=45, ha="right")
    plt.yticks(rotation=0)
    plt.tight_layout()

    if output_path:
        plt.savefig(output_path)
    else:
        plt.show()

    plt.close()
