from typing import List, Tuple

from schema_conversion_orchestrator.converters.base import Converter

ConversionGraph = dict[str, list[Converter]]
ConversionPath = List[Converter]
ConversionPaths = List[ConversionPath]

# Tuple of (success: bool, result_schema_or_error_message: str, conversion_path: ConversionPath)
ConversionResult = Tuple[bool, str, ConversionPath]
ConversionResults = List[ConversionResult]

ConversionsCache = dict[str, str | None]


def conversion_path_to_string(path: ConversionPath) -> str:
    return " -> ".join(
        [f"{conv.source_language.value} to {conv.target_language.value} via {conv.service_name}" for conv in path]
    )


def prepare_conversion_results_for_serializing(results: ConversionResults) -> dict:
    serialized_results = {}
    for idx, (success, schema_or_error, path) in enumerate(results):
        path_str = conversion_path_to_string(path)
        serialized_results[f"Attempt {idx + 1}"] = {
            "success": success,
            "schema_or_error": schema_or_error,
            "conversion_path": path_str,
        }
    return serialized_results
