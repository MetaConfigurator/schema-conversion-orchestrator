import traceback
from typing import List
from strenum import StrEnum

from converter import (ConversionResult, ConversionResults, ConversionPaths, Converter)
from schema_types import SchemaLanguage
from logic import identify_schema_features, rank_paths
from app import DETAILED_ERROR_OUTPUT, schema_languages_features


class ConversionStrategy(StrEnum):
    LeastCharacterLoss = "LeastCharacterLoss"
    MostFeaturesPreserved = "MostFeaturesPreserved"


def convert_with_strategy_most_features_preserved(source: SchemaLanguage, target: SchemaLanguage, schema: str,
                                                  paths: ConversionPaths) -> ConversionResults:
    """ Ranks paths by how many features they preserve from the document schema and tries them in that order.
    Stops at first success."""
    doc_features = set(identify_schema_features(schema, source))
    if not doc_features:
        print("Warning: No schema feature identification available for the given schema format '" + source + "'.")
    ranked_paths = rank_paths(paths, doc_features, schema_languages_features)
    all_attempts: List[ConversionResult] = []
    result_schema = None

    # attempt conversion via best path and if it fails, try remaining paths and print error message only to console
    # if no path is left, return the error messages of all attempts consolidated
    # create only one loop and try and catch and do not treat the first path specially
    while result_schema is None and len(ranked_paths) > 0:
        best_path, unsupported_features = ranked_paths[0]
        try:
            result_schema = attempt_conversion_path(source, target, best_path, schema)

            if not result_schema:
                all_attempts.append((False, "Conversion resulted in 'None' schema.", best_path))
            else:
                all_attempts.append((True, result_schema, best_path))
                break
        except Exception as e:
            ranked_paths = ranked_paths[1:]
            if DETAILED_ERROR_OUTPUT:
                full_traceback = traceback.format_exc()
                all_attempts.append((False, f"Error: {e}\nTraceback:\n{full_traceback}", best_path))
            else:
                all_attempts.append((False, str(e), best_path))

    # sort all attempts by success: success first. Otherwise keep same order
    all_attempts.sort(key=lambda x: not x[0])
    return all_attempts


def convert_with_strategy_least_character_loss(source: SchemaLanguage, target: SchemaLanguage, schema: str,
                                               paths: ConversionPaths) -> ConversionResults:
    """ Always tries all paths and then ranks the results by character length (descending order).
    Does not stop at success but explores all paths. Trivial feature loss strategy which is character based.
    Much less effort than a proper feature loss analysis and still effective."""
    all_attempts: List[ConversionResult] = []
    for path in paths:
        result_schema = None
        try:
            result_schema = attempt_conversion_path(source, target, path, schema)

            if not result_schema:
                all_attempts.append((False, "Conversion resulted in 'None' schema.", path))
            else:
                all_attempts.append((True, result_schema, path))
        except Exception as e:
            if DETAILED_ERROR_OUTPUT:
                full_traceback = traceback.format_exc()
                all_attempts.append((False, f"Error: {e}\nTraceback:\n{full_traceback}", path))
            else:
                all_attempts.append((False, str(e), path))

    # sort all attempts by success: success first. Then by length of resulting schema (descending)
    all_attempts.sort(key=lambda x: (not x[0], -len(x[1]) if x[0] else float('inf')))

    return all_attempts


def attempt_conversion_path(source: str, target: str, path: List[Converter], schema: str) -> str:
    print_conversion_path(source, target, path)
    current_schema = schema
    current_converter = None
    try:
        for conv in path:
            current_converter = conv
            current_schema = conv.convert(current_schema)
            print(
                "Intermediate schema of format " + conv.target_format + " after conversion via " + conv.service_name + ": " + current_schema)
        return current_schema
    except Exception as e:
        print(
            "Conversion failed at step from " + current_converter.source_format + " to " + current_converter.target_format + " via " + current_converter.service_name + " because of error: " + str(
                e) + ".")
        print("With intermediate schema: " + current_schema)
        raise Exception(
            f"Conversion failed at step from {current_converter.source_format} to {current_converter.target_format} via {current_converter.service_name} because of error: {str(e)}.")


def print_conversion_path(source: str, target: str, path: List[Converter]) -> None:
    print("Given the source format " + source + " and target format " + target + ", the best available path is:")
    for conv in path:
        print(f"{conv.source_format} -> {conv.target_format} via {conv.name} ({conv.service_address})")
