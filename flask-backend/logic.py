from typing import List, Set, Tuple
from .data_structures import Converter, SchemaFeature, SchemaFormat

def build_conversion_tree(converters: List[Converter]):
    global conversion_graph
    conversion_graph = {}
    for conv in converters:
        if conv.sourceFormat not in conversion_graph:
            conversion_graph[conv.sourceFormat] = []
        conversion_graph[conv.sourceFormat].append(conv)

def identify_schema_features(schema: str, format: SchemaFormat) -> List[SchemaFeature]:
    # Dummy logic
    return [
        SchemaFeature.Constraints,
        SchemaFeature.Properties,
        SchemaFeature.Hierarchy,
        SchemaFeature.References
    ]

def find_paths(source: SchemaFormat, target: SchemaFormat, path: List[List[Converter]]|None=None, visited: Set[SchemaFormat]|None=None) -> List[List[Converter]]:
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
        if conv.targetFormat not in visited:
            new_path = path + [conv]
            sub_paths = find_paths(conv.targetFormat, target, new_path, visited.copy())
            paths.extend(sub_paths)

    return paths


# ranks the paths based on how many features they support from the document schema plus returns a list of unsupported features for each path
def rank_paths(paths: List[List[Converter]], doc_features: set[SchemaFeature]) -> List[Tuple[List[Converter], Set[SchemaFeature]]]:
    ranked_paths = []

    for path in paths:
        supported_features = set()
        unsupported_features = set(doc_features)

        for conv in path:
            supported_features.update(conv.supportedFeatures)
            unsupported_features -= conv.supportedFeatures

        score = len(supported_features)
        ranked_paths.append((path, unsupported_features, score))

    # Sort by score (descending) and then by length of unsupported features (ascending)
    ranked_paths.sort(key=lambda x: (-x[2], len(x[1])))

    return [(path, unsupported) for path, unsupported, _ in ranked_paths]


# Returns either the best path + a list of schema features that are in the core document but not supported and will be omitted, or None if no path is found.
def determine_best_path(paths: List[List[Converter]], doc_features: set[SchemaFeature]) -> Tuple[List[Converter], Set[SchemaFeature]] | None:
    if not paths:
        return None

    ranked_paths = rank_paths(paths, doc_features)

    # Select the path with the highest score and the least unsupported features
    best_path, unsupported_features = ranked_paths[0]

    return best_path, unsupported_features