from converter import ConversionResults, conversion_path_to_string


def print_conversion_results(results: ConversionResults):
    # print overall result: how many succeeded/failed and their character lengths
    success_count = sum(1 for attempt in results if attempt[0])
    failure_count = len(results) - success_count
    print(f"Conversion attempts completed: {success_count} succeeded, {failure_count} failed.")
    for i, attempt in enumerate(results):
        success, result_schema_or_error, path = attempt
        if success:
            print(
                f"- Attempt {i + 1} ({conversion_path_to_string(path)}): Success, Resulting schema length: {len(result_schema_or_error)} characters.")
        else:
            print(f"- Attempt {i + 1} ({conversion_path_to_string(path)}): Failure, Error: {result_schema_or_error}")
