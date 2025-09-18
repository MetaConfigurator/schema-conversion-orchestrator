import networkx as nx
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from typing import List
from data_structures import Converter, ConversionGraph


def build_conversion_matrix(conversion_graph: ConversionGraph) -> pd.DataFrame:
    # Build directed graph
    G = nx.DiGraph()
    for source, converters in conversion_graph.items():
        for converter in converters:
            G.add_edge(str(converter.source_format), str(converter.target_format))

    nodes = sorted(G.nodes())
    matrix = pd.DataFrame(index=nodes, columns=nodes)

    for src in nodes:
        for tgt in nodes:
            if src == tgt:
                matrix.loc[src, tgt] = "—"  # mark diagonal
                continue

            # Number of direct conversions
            direct_count = 1 if G.has_edge(src, tgt) else 0

            # Number of total paths (all simple paths)
            all_paths = list(nx.all_simple_paths(G, source=src, target=tgt))
            total_count = len(all_paths)

            if total_count == 0:
                matrix.loc[src, tgt] = "0"
            else:
                matrix.loc[src, tgt] = f"{direct_count} / {total_count}"

    matrix.index.name = "Source Format"
    matrix.columns.name = "Target Format"
    return matrix


def plot_conversion_matrix(matrix: pd.DataFrame):
    # Build weighted numeric matrix for coloring
    numeric_matrix = matrix.copy()

    for i in numeric_matrix.index:
        for j in numeric_matrix.columns:
            val = matrix.loc[i, j]

            if val == "—":  # diagonal
                numeric_matrix.loc[i, j] = 8  # highest weight
            elif val == "0":
                numeric_matrix.loc[i, j] = 0
            else:
                direct, total = val.split(" / ")
                direct = int(direct)
                total = int(total)
                score = min(total, 8)
                if direct > 0:
                    score = min(score + 3, 8)
                numeric_matrix.loc[i, j] = score

    numeric_matrix = numeric_matrix.astype(int)

    plt.figure(figsize=(12, 10))
    ax = sns.heatmap(
        numeric_matrix,
        annot=matrix,  # show "direct / total" in cells
        fmt="",
        cmap="Blues",
        cbar_kws={"label": "Weighted score (direct + paths)"},
        linewidths=0.5,
        linecolor="gray"
    )
    plt.title("Schema Conversion Matrix", fontsize=16)
    plt.xticks(rotation=45, ha="right")
    plt.yticks(rotation=0)
    plt.tight_layout()
    plt.show()


if __name__ == "__main__":
    from register_python_converters import register_python_converters
    from logic import build_conversion_graph

    converters: List[Converter] = register_python_converters()
    conversion_graph: ConversionGraph = build_conversion_graph(converters)

    df = build_conversion_matrix(conversion_graph)

    # Print in console
    print(df.to_string())

    # Plot nicely
    plot_conversion_matrix(df)
