import os
from pathlib import Path
from typing import List
from schema_conversion_orchestrator.converters.base import Converter
from schema_conversion_orchestrator.domain.conversion_types import ConversionGraph
from schema_conversion_orchestrator.reporting.visualize_conversion_graph import visualize_conversion_graph
from schema_conversion_orchestrator.reporting.conversion_graph_rdf import conversion_graph_to_rdf
from schema_conversion_orchestrator.reporting.conversion_matrix import build_conversion_matrix, plot_conversion_matrix
from schema_conversion_orchestrator.converters.registry import register_converters
from schema_conversion_orchestrator.domain.conversion_graph import build_conversion_graph


def generate_diagrams(conversion_graph: ConversionGraph, artifacts_dir: str):
    conversion_graph_img_output_path = os.path.join(artifacts_dir, "conversion_graph.png")
    turtle_output_path = os.path.join(artifacts_dir, "conversion_graph.ttl")
    conversion_matrix_path = os.path.join(artifacts_dir, "conversion_matrix.png")

    visualize_conversion_graph(conversion_graph, output_path=conversion_graph_img_output_path)
    conversion_graph_to_rdf(conversion_graph, output_path=turtle_output_path)

    conversion_matrix = build_conversion_matrix(conversion_graph)
    plot_conversion_matrix(conversion_matrix, output_path=conversion_matrix_path)

def main() -> None:
    converters_full: List[Converter] = register_converters()
    conversion_graph_full: ConversionGraph = build_conversion_graph(converters_full)

    converters_core: List[Converter] = register_converters(True)
    conversion_graph_core: ConversionGraph = build_conversion_graph(converters_core)

    root_dir = Path(__file__).resolve().parents[3]
    artifacts_dir_full = os.path.join(root_dir, "artifacts", "diagrams", "full")
    artifacts_dir_core = os.path.join(root_dir, "artifacts", "diagrams", "core")

    # create output directories if they don't exist
    os.makedirs(artifacts_dir_full, exist_ok=True)
    os.makedirs(artifacts_dir_core, exist_ok=True)

    generate_diagrams(conversion_graph_full, artifacts_dir_full)
    generate_diagrams(conversion_graph_core, artifacts_dir_core)


if __name__ == "__main__":
    main()
