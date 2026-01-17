import os
from typing import List
from converter import ConversionGraph, Converter
from output_visualize_conversion_graph import visualize_conversion_graph
from output_conversion_graph_to_rdf import conversion_graph_to_rdf
from output_build_conversion_matrix import build_conversion_matrix, plot_conversion_matrix
from register_converters import register_converters
from logic import build_conversion_graph


def generate_diagrams(conversion_graph: ConversionGraph, outputs_dir: str):
    conversion_graph_img_output_path = os.path.join(outputs_dir, "conversion_graph.png")
    turtle_output_path = os.path.join(outputs_dir, "conversion_graph.ttl")
    conversion_matrix_path = os.path.join(outputs_dir, "conversion_matrix.png")

    visualize_conversion_graph(conversion_graph, output_path=conversion_graph_img_output_path)
    conversion_graph_to_rdf(conversion_graph, output_path=turtle_output_path)

    conversion_matrix = build_conversion_matrix(conversion_graph)
    plot_conversion_matrix(conversion_matrix, output_path=conversion_matrix_path)



if __name__ == "__main__":
    converters_full: List[Converter] = register_converters()
    conversion_graph_full: ConversionGraph = build_conversion_graph(converters_full)

    converters_core: List[Converter] = register_converters(True)
    conversion_graph_core: ConversionGraph = build_conversion_graph(converters_core)

    # dir of current file
    python_code_dir = os.path.dirname(os.path.abspath(__file__))
    root_dir = os.path.dirname(python_code_dir)
    outputs_dir_full = os.path.join(root_dir, "outputs", "full")
    outputs_dir_core = os.path.join(root_dir, "outputs", "core")

    # create output directories if they don't exist
    os.makedirs(outputs_dir_full, exist_ok=True)
    os.makedirs(outputs_dir_core, exist_ok=True)

    generate_diagrams(conversion_graph_full, outputs_dir_full)
    generate_diagrams(conversion_graph_core, outputs_dir_core)
