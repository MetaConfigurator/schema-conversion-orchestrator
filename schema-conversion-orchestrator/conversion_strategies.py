import traceback
from typing import List
from strenum import StrEnum

from converter import (ConversionResult, ConversionResults, ConversionPaths, Converter, conversion_path_to_string,
                       ConversionsCache)
from schema_types import SchemaLanguage

DETAILED_ERROR_OUTPUT = False
DETAILED_RESULT_OUTPUT = True


class ConversionStrategy(StrEnum):
    LeastCharacterLoss = "LeastCharacterLoss"


def convert_with_strategy_least_character_loss(source: SchemaLanguage, target: SchemaLanguage, schema: str,
                                               paths: ConversionPaths) -> ConversionResults:
    """ Always tries all paths and then ranks the results by character length (descending order).
    Does not stop at success but explores all paths. Trivial feature loss strategy which is character based.
    Much less effort than a proper feature loss analysis and still effective."""
    all_attempts: List[ConversionResult] = []
    conversions_cache = {}  # cache for all conversion sub-paths
    for path in paths:
        try:
            result_schema, conversions_cache_update = attempt_conversion_path(source, target, path, schema,
                                                                              conversions_cache)
            conversions_cache = conversions_cache_update

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

    # print overall result: how many succeeded/failed and their character lengths
    success_count = sum(1 for attempt in all_attempts if attempt[0])
    failure_count = len(all_attempts) - success_count
    print(f"Conversion attempts completed: {success_count} succeeded, {failure_count} failed.")
    for i, attempt in enumerate(all_attempts):
        success, result_schema_or_error, path = attempt
        if success:
            print(
                f"- Attempt {i + 1} ({conversion_path_to_string(path)}): Success, Resulting schema length: {len(result_schema_or_error)} characters.")
        else:
            print(f"- Attempt {i + 1} ({conversion_path_to_string(path)}): Failure, Error: {result_schema_or_error}")

    return all_attempts


# the conversions cache contains the results of all previously attempted conversion sub-paths
def attempt_conversion_path(source: str, target: str, path: List[Converter], schema: str,
                            conversions_cache: ConversionsCache) -> tuple[str, ConversionsCache]:
    print_conversion_path(source, target, path)
    current_schema = schema
    current_converter = None
    conversion_sub_path = []
    try:
        for conv in path:
            current_converter = conv
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
                    print(
                        "Using cached intermediate schema of format " + conv.target_format + " after conversion via " + conv.service_name + ": " + current_schema)
                    continue
            else:
                # cache miss - perform conversion
                current_schema = conv.convert(current_schema)
                if DETAILED_RESULT_OUTPUT:
                    print(
                        "\n\nIntermediate schema of format " + conv.target_format + " after conversion via " + conv.service_name + ": \n" + current_schema + "\n\n\n\n")
                # store in cache
                conversions_cache[conversion_sub_path_hash] = current_schema

        return current_schema, conversions_cache
    except Exception as e:
        print(
            "Conversion failed at step from " + current_converter.source_format + " to " + current_converter.target_format + " via " + current_converter.service_name + " because of error: " + str(
                e) + ".")
        print("With intermediate schema: " + current_schema)
        raise Exception(
            f"Conversion failed at step from {current_converter.source_format} to {current_converter.target_format} via {current_converter.service_name} because of error: {str(e)}.")


def print_conversion_path(source: str, target: str, path: List[Converter]) -> None:
    print("Conversion path for source format '" + source + "' and target format '" + target + "':")
    for conv in path:
        print(f"- {conv.source_format} --({conv.name} ({conv.service_address})--> {conv.target_format})")
