import os
from typing import Tuple
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

import requests

SERVER_URL = "http://localhost:5002/convert"
SOURCE_LANGUAGES = ["JsonSchema", "Xsd", "Shacl_TTL", "Owl_TTL", "LinkML"]
TARGET_LANGUAGES = ["JsonSchema", "Xsd", "Shacl_TTL", "Owl_TTL", "LinkML", "GraphQL", "Protobuf"]


def send_conversion_request(source_language: str, target_language: str, schema: str) -> any | Tuple[int, str]:
    # Build payload
    payload = {
        "sourceLanguage": source_language,
        "targetLanguage": target_language,
        "schema": schema
    }

    # Send request
    print(f"Sending conversion request {source_language} → {target_language} ...")
    resp = requests.post(SERVER_URL, json=payload)

    # Handle response
    if resp.status_code == 200:
        result = resp.json()
        return result
    else:
        print(f"Error {resp.status_code}: {resp.text}")
        return resp.status_code, resp.text


def load_golden_schemas(schema_languages: list[str]) -> dict[str, str]:
    """
    Loads the golden schemas for each schema language from the 'golden_schemas/' folder.

    :param schema_languages: List of schema languages to load.
    :return: A map of schema language to its corresponding golden schema string.
    """
    golden_schemas = {}
    for language in schema_languages:
        source_folder = os.path.join("golden_schemas", language)
        for filename in os.listdir(source_folder):
            with open(os.path.join(source_folder, filename), "r") as f:
                golden_schemas[language] = f.read()
            break  # There is only one schema file per language
    return golden_schemas


def request_conversion_results(source_languages: list[str], target_languages: list[str], golden_schemas: dict[str, str]) -> dict[str, dict[str, any]]:
    results = {}  # multi-dimensional map [source_language][target_language] = result_schema
    successes = 0
    errors = 0
    for source_language in source_languages:

        input_schema = golden_schemas[source_language]

        source_language_results = {}
        for target_language in target_languages:
            if source_language == target_language:
                continue

            request_result = send_conversion_request(source_language, target_language, input_schema)
            if isinstance(request_result, tuple):
                error_code, error_message = request_result
                errors += 1
                print("Conversion request error code " + str(error_code) + ": " + error_message)

            else:
                successes += 1
                # results is an object { "results": [ "conversionPath": [...], "result": {...}, "success": bool ] }
                # we want to extract all result schemas and their corresponding success value and prettified path
                formatted_results = []
                for idx, result_entry in enumerate(request_result["results"]):
                    conversion_path_short = "__".join(
                        [f"to_{step['targetLanguage']}_via_{step['serviceName']}" for step in result_entry["conversionPath"]]
                    )
                    conversion_path_full = " -> ".join(
                        [f"{step['sourceLanguage']} to {step['targetLanguage']} via {step['serviceName']}[{step['converterName']}]" for step in result_entry["conversionPath"]]
                    )
                    formatted_results.append({
                        "attempt": idx + 1,
                        "success": result_entry["success"],
                        "result_schema": result_entry.get("result", None),
                        "conversion_path": conversion_path_short,
                        "conversion_path_full": conversion_path_full
                    })

                source_language_results[target_language] = formatted_results

        # if source_language_results is not empty, store it
        if source_language_results:
            results[source_language] = source_language_results
        else:
            results[source_language] = {
                target_language: [] for target_language in target_languages if target_language != source_language
            }
    print(f"Conversions completed: {successes} successful conversions, {errors} errors.")
    return results


def store_conversion_results(results: dict[str, dict[str, any]]) -> None:
    # Store result schemas in output_schemas/source_language/target_language/attempt_<attempt>_<success>_
    # <conversion_path>.txt
    output_base_folder = "output_schemas"

    # First clear the output folder if it already exists
    if os.path.exists(output_base_folder):
        for root, dirs, files in os.walk(output_base_folder, topdown=False):
            for name in files:
                os.remove(os.path.join(root, name))
            for name in dirs:
                os.rmdir(os.path.join(root, name))

    for source_language, target_language_results in results.items():
        for target_language, result_entries in target_language_results.items():
            output_folder = os.path.join(output_base_folder, source_language, target_language)
            os.makedirs(output_folder, exist_ok=True)

            for entry in result_entries:
                attempt = entry["attempt"]
                success = entry["success"]
                result_schema = entry["result_schema"]
                conversion_path = entry["conversion_path"]
                conversion_path_full = entry["conversion_path_full"]

                output_filename = f"attempt_{attempt}_success_{success}_path_{conversion_path}.txt"
                output_filepath = os.path.join(output_folder, output_filename)

                with open(output_filepath, "w") as f:
                    if result_schema is not None:
                        f.write(result_schema)
                    else:
                        f.write("No result schema.")

                # Additionally store full conversion path in a separate metadata file
                output_metadata_filepath = os.path.join(output_folder, f"attempt_{attempt}_success_{success}_path_{conversion_path}_metadata.txt")
                with open(output_metadata_filepath, "w") as f:
                    f.write(f"Full Conversion Path:\n{conversion_path_full}\n")


def evaluate():
    """
    Runs the conversion of the golden schemas from each schema language (source) to each other schema language (target).
    Assumes the Schema Conversion Orchestrator (the subject to be evaluated) is already running locally.

    All golden schemas are stored in a dedicated folder structure under 'golden_schemas/'.
    The output schemas resulting from the conversions will be stored in 'output_schemas/'.

    """
    print("Running evaluation...")

    # List of all relevant schema languages

    # Extract golden schema (source schema) for each schema language.
    golden_schemas = load_golden_schemas(SOURCE_LANGUAGES)

    # Go through each combination of source language and target language
    results = request_conversion_results(SOURCE_LANGUAGES, TARGET_LANGUAGES, golden_schemas)

    # Store result schemas
    store_conversion_results(results)

    # Build conversion matrix
    conversion_matrix = compute_conversion_matrix(golden_schemas, results)

    # Plot conversion matrix
    plot_conversion_matrix(conversion_matrix, output_path="conversion_matrix.png")


def compute_conversion_matrix(golden_schemas: dict[str, str], results: dict[str, dict[str, any]]) -> pd.DataFrame:
    """
    Computes a matrix that shows the character lengths of the converted schemas for each source-target language pair.
    For a source-target pair with multiple conversion attempts, the lengths are comma-separated.
    For unconvertible pairs, a dash ("—") is used.
    For paths where source and target language are the same, the length of the original schema is used.
    :param golden_schemas:
    :param results:
    :return:
    """
    matrix = pd.DataFrame(index=results.keys(), columns=results.keys())

    for source_language, target_language_results in results.items():
        for target_language in matrix.columns:
            if source_language == target_language:
                # length of original schema
                original_schema_length = len(golden_schemas[source_language])
                matrix.loc[source_language, target_language] = str(original_schema_length)
                continue

            result_entries = target_language_results.get(target_language, [])
            if not result_entries:
                matrix.loc[source_language, target_language] = "—"
                continue

            lengths = []
            for entry in result_entries:
                if not entry["success"]:
                    continue
                result_schema = entry["result_schema"]
                if result_schema is not None:
                    lengths.append(str(len(result_schema)))

            if lengths:
                matrix.loc[source_language, target_language] = ", ".join(lengths)
            else:
                matrix.loc[source_language, target_language] = "—"

    matrix.index.name = "Source Language"
    matrix.columns.name = "Target Language"
    return matrix


def plot_conversion_matrix(matrix: pd.DataFrame, output_path: str = None) -> None:
    numeric_matrix = matrix.copy()

    for i in numeric_matrix.index:
        for j in numeric_matrix.columns:
            val = matrix.loc[i, j]

            if val == "—":
                numeric_matrix.loc[i, j] = 0
            else:
                # take the minimum length if multiple attempts
                lengths = list(map(int, val.split(", ")))
                numeric_matrix.loc[i, j] = min(lengths)

    plt.figure(figsize=(8, 6))
    sns.heatmap(numeric_matrix.astype(float), annot=matrix, fmt='', cmap="YlGnBu", cbar_kws={'label': 'Schema Length'})
    plt.title("Schema Conversion Length Matrix")
    plt.tight_layout()

    if output_path:
        plt.savefig(output_path)
    else:
        plt.show()


if __name__ == "__main__":
    evaluate()
