from typing import List, Set, Tuple, Dict
from converter import Converter, ConversionGraph, ConversionPath, ConversionPaths
from schema_types import SchemaLanguage, SchemaFeature
from identify_schema_features_json_schema import identify_schema_features_json_schema


# Builds a schema conversion graph from the list of registered converters, connecting source formats to target
# formats with the edges being converters.
def build_conversion_graph(converters: List[Converter]) -> Dict[str, List[Converter]]:
    conversion_graph = {}
    for conv in converters:
        if conv.source_format not in conversion_graph:
            conversion_graph[conv.source_format] = []
        conversion_graph[conv.source_format].append(conv)
    return conversion_graph


def identify_schema_features(schema: str, format: SchemaLanguage) -> List[SchemaFeature] | None:
    """
    # Analyzes the input schema to identify which schema features it uses.
    :param schema: The input schema as a string.
    :param format: The format of the input schema.
    :return: A dictionary mapping SchemaFeature to SchemaFeatureSupport, or None if no analysis is available for the
    given schema language.
    """
    if format == SchemaLanguage.JsonSchema:
        return identify_schema_features_json_schema(schema)

    return None


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


# ranks the paths based on how many features they support from the document schema plus returns a list of unsupported
# features for each path
def rank_paths(paths: ConversionPaths, doc_features: set[SchemaFeature] | None) -> List[
    Tuple[ConversionPath, set[SchemaFeature]]]:
    if doc_features is None:
        # todo: assume ALL features in case of no known list of features
        doc_features = set()

    ranked_paths = []

    for path in paths:
        supported_features = set()
        unsupported_features = set(doc_features)

        for conv in path:
            supported_features.update(conv.supported_features)
            # remove supported features from unsupported features
            unsupported_features.difference_update(conv.supported_features)

        score = len(supported_features)
        ranked_paths.append((path, unsupported_features, score))

    # Sort by score (descending) and then by length of unsupported features (ascending)
    ranked_paths.sort(key=lambda x: (-x[2], len(x[1])))

    return [(path, unsupported) for path, unsupported, _ in ranked_paths]


# Returns either the best path + a list of schema features that are in the core document but not supported and will
# be omitted, or None if no path is found.
def determine_best_path(paths: ConversionPaths, doc_features: set[SchemaFeature]) -> Tuple[ConversionPath, Set[
    SchemaFeature]] | None:
    if not paths:
        return None

    ranked_paths = rank_paths(paths, doc_features)

    # Select the path with the highest score and the least unsupported features
    best_path, unsupported_features = ranked_paths[0]

    return best_path, unsupported_features
