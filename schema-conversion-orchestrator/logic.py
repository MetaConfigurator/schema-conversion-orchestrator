from typing import List, Set, Dict
from converter import Converter, ConversionGraph, ConversionPaths
from schema_types import SchemaLanguage


# Builds a schema conversion graph from the list of registered converters, connecting source formats to target
# formats with the edges being converters.
def build_conversion_graph(converters: List[Converter]) -> Dict[str, List[Converter]]:
    conversion_graph = {}
    for conv in converters:
        if conv.source_format not in conversion_graph:
            conversion_graph[conv.source_format] = []
        conversion_graph[conv.source_format].append(conv)
    return conversion_graph


def find_paths(source: SchemaLanguage, target: SchemaLanguage, conversion_graph: ConversionGraph,
               path: ConversionPaths | None = None, visited: Set[SchemaLanguage] | None = None) -> ConversionPaths:
    if path is None:
        path = []
    if visited is None:
        visited = set()

    if source == target:
        return [path]

    if source not in conversion_graph:
        return []

    visited.add(source)
    paths = []

    for conv in conversion_graph[source]:
        if conv.target_format not in visited:
            new_path = path + [conv]
            sub_paths = find_paths(conv.target_format, target, conversion_graph, new_path, visited.copy())
            paths.extend(sub_paths)

    return paths

