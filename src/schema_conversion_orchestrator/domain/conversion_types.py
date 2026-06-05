from typing import List, Tuple

from schema_conversion_orchestrator.converters.base import Converter

ConversionGraph = dict[str, list[Converter]]
ConversionPath = List[Converter]
ConversionPaths = List[ConversionPath]

# Tuple of (success, result_schema_or_error_message, conversion_path, failed_step_index)
# failed_step_index is the 0-based index into conversion_path of the step that
# raised the error, or None for successful attempts (and failures without a
# specific failing step).
ConversionResult = Tuple[bool, str, ConversionPath, int | None]
ConversionResults = List[ConversionResult]

ConversionsCache = dict[str, str | None]


def conversion_path_to_string(path: ConversionPath) -> str:
    # The converter name must be part of this string: it is used as the sub-path
    # cache key, and two different converters between the same source and target
    # language (e.g. several SHACL -> JSON Schema converters) share the same
    # source/target/service_name. Without the name they would collide in the
    # cache and the second converter would return the first one's result.
    return " -> ".join(
        [f"{conv.source_language.value} to {conv.target_language.value} via {conv.service_name} ({conv.name})"
         for conv in path]
    )


def prepare_conversion_results_for_serializing(results: ConversionResults) -> dict:
    serialized_results = {}
    for idx, (success, schema_or_error, path, _failed_step_index) in enumerate(results):
        path_str = conversion_path_to_string(path)
        serialized_results[f"Attempt {idx + 1}"] = {
            "success": success,
            "schema_or_error": schema_or_error,
            "conversion_path": path_str,
        }
    return serialized_results
