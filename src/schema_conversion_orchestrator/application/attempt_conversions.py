import traceback
from typing import List
try:
    from enum import StrEnum
except ImportError:
    from strenum import StrEnum

from schema_conversion_orchestrator.converters.base import Converter
from schema_conversion_orchestrator.domain.conversion_types import (
    ConversionPath,
    ConversionPaths,
    ConversionResult,
    ConversionResults,
    ConversionsCache,
    conversion_path_to_string,
)
from schema_conversion_orchestrator.domain.schema_types import SchemaLanguage

PRINT_STEPS_IN_CONSOLE = False
DETAILED_ERROR_OUTPUT = True
DETAILED_RESULT_OUTPUT = False
ERROR_OUTPUT_INCLUDE_PREVIOUS_RUNS = True


class ConversionStrategy(StrEnum):
    LeastCharacterLoss = "LeastCharacterLoss"


class ConversionPathError(Exception):
    """Raised when a conversion path fails, carrying the index of the failing step."""

    def __init__(self, message: str, failed_step_index: int | None) -> None:
        super().__init__(message)
        self.failed_step_index = failed_step_index


def attempt_all_conversion_paths(source: SchemaLanguage, target: SchemaLanguage, schema: str,
                                 paths: ConversionPaths) -> ConversionResults:
    """ Attempts all conversion paths without any ranking or selection. Returns all results as is."""
    all_attempts: List[ConversionResult] = []
    conversions_cache = {}  # cache for all conversion sub-paths
    for path in paths:
        try:
            result_schema, conversions_cache_update = attempt_conversion_path(source, target, path, schema,
                                                                              conversions_cache)
            conversions_cache = conversions_cache_update

            if not result_schema:
                all_attempts.append((False, "Conversion resulted in 'None' schema.", path, None))
            else:
                all_attempts.append((True, result_schema, path, None))
        except Exception as e:
            error_output = str(e)
            if DETAILED_ERROR_OUTPUT:
                full_traceback = traceback.format_exc()
                error_output = f"Error: {e}\nTraceback:\n{full_traceback}"
            if ERROR_OUTPUT_INCLUDE_PREVIOUS_RUNS:
                previous_runs_info = collect_previous_step_results_for_debug(path, conversions_cache)
                error_output += f"\n\n\n\n\nPrevious steps results for this path:\n{previous_runs_info}"
            failed_step_index = getattr(e, "failed_step_index", None)
            all_attempts.append((False, error_output, path, failed_step_index))
    return all_attempts


def collect_previous_step_results_for_debug(path: ConversionPath, conversions_cache: ConversionsCache) -> str:
    """Appends the results of the previous steps to one string for debugging purposes"""
    debug_info = ""
    for i in range(1, len(path) + 1):
        sub_path = path[:i]
        sub_path_hash = conversion_path_to_string(sub_path)
        if sub_path_hash in conversions_cache:
            cached_result = conversions_cache[sub_path_hash]
            if cached_result is not None:
                debug_info += f"Result after step {i} ({sub_path[-1].source_language} to {sub_path[-1].target_language} via {sub_path[-1].service_name}):\n{cached_result}\n\n\n"
            else:
                debug_info += f"Step {i} ({sub_path[-1].source_language} to {sub_path[-1].target_language} via {sub_path[-1].service_name}) previously failed.\n\n\n"
        else:
            debug_info += f"Step {i} ({sub_path[-1].source_language} to {sub_path[-1].target_language} via {sub_path[-1].service_name}) not attempted yet.\n\n\n"
    return debug_info


# the conversions cache contains the results of all previously attempted conversion sub-paths
def attempt_conversion_path(source: str, target: str, path: List[Converter], schema: str,
                            conversions_cache: ConversionsCache) -> tuple[str, ConversionsCache]:
    print_conversion_path(source, target, path)
    current_schema = schema
    current_converter = None
    current_step_index = None
    conversion_sub_path = []
    try:
        for step_index, conv in enumerate(path):
            current_converter = conv
            current_step_index = step_index
            conversion_sub_path.append(conv)

            # check cache
            conversion_sub_path_hash = conversion_path_to_string(conversion_sub_path)
            if conversion_sub_path_hash in conversions_cache:
                # cache hit
                cached_result = conversions_cache[conversion_sub_path_hash]
                if cached_result is None:
                    # previously failed conversion for this sub-path
                    raise Exception("Previously failed conversion for this sub-path.")
                else:
                    # use cached result in case of cache hit and good previous conversion
                    current_schema = cached_result
                    if PRINT_STEPS_IN_CONSOLE:
                        print(
                            "Using cached intermediate schema of format " + conv.target_language + " after conversion via " + conv.service_name + ": " + current_schema)
                    continue
            else:
                # cache miss - perform conversion
                current_schema = conv.convert(current_schema)
                if DETAILED_RESULT_OUTPUT and PRINT_STEPS_IN_CONSOLE:
                    print(
                        "\n\nIntermediate schema of format " + conv.target_language + " after conversion via " + conv.service_name + ": \n" + current_schema + "\n\n\n\n")
                # store in cache
                conversions_cache[conversion_sub_path_hash] = current_schema

        return current_schema, conversions_cache
    except Exception as e:
        if DETAILED_ERROR_OUTPUT and PRINT_STEPS_IN_CONSOLE:
            print(
                "Conversion failed at step from " + current_converter.source_language + " to " + current_converter.target_language + " via " + current_converter.service_name + " because of error: " + str(
                    e) + ".")
            print("With intermediate schema: " + current_schema)
        raise ConversionPathError(
            f"Conversion failed at step from {current_converter.source_language} to {current_converter.target_language} via {current_converter.service_name} because of error: {str(e)}.",
            failed_step_index=current_step_index)


def print_conversion_path(source: str, target: str, path: List[Converter]) -> None:
    print("Conversion path for source format '" + source + "' and target format '" + target + "':")
    for conv in path:
        print(f"- {conv.source_language} --({conv.name} ({conv.service_address})--> {conv.target_language})")
