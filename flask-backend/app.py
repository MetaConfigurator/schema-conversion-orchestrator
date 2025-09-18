import traceback

from data_structures import Converter, ConverterExternal, schema_language_from_string
from logic import build_conversion_graph, identify_schema_features, find_paths, rank_paths
from register_python_converters import register_python_converters
from flask import Flask, request
from typing import List, Dict

app = Flask(__name__)


converters: List[Converter] = register_python_converters()
conversion_graph: Dict[str, List[Converter]] = build_conversion_graph(converters)

@app.route("/health", methods=["GET"])
def health():
    return {"status": "ok"}, 200

@app.route("/registerConversion", methods=["POST"])
def register_conversion():
    data = request.json
    conv = ConverterExternal(
        data["name"],
        data["serviceAddress"],
        data["sourceFormat"],
        data["targetFormat"],
        data["supportedFeatures"]
    )
    converters.append(conv)
    global conversion_graph
    conversion_graph = build_conversion_graph(converters)
    print(f"Registered new converter: {conv.name} from {conv.source_format} to {conv.target_format} at {conv.service_address}.")
    return {"status": "registered"}, 200


@app.route("/convert", methods=["POST"])
def convert():
    data = request.json
    source = data["sourceFormat"]
    target = data["targetFormat"]
    schema = data["schema"]

    source = schema_language_from_string(source)
    target = schema_language_from_string(target)

    # if schema is an object, convert it to string
    if isinstance(schema, dict):
        import json
        schema = json.dumps(schema)

    all_paths = find_paths(source, target, conversion_graph)
    if not all_paths:
        return {"error": "No path found for conversion from source " + source + " to target " + target + "."}, 400

    doc_features = set(identify_schema_features(schema, source, conversion_graph))
    ranked_paths = rank_paths(all_paths, doc_features)
    attempt_errors = []
    result_schema = None

    # attempt conversion via best path and if it fails, try remaining paths and print error message only to console
    # if no path is left, return the error messages of all attempts consolidated
    # create only one loop and try and catch and do not treat the first path specially
    while result_schema is None and len(ranked_paths) > 0:
        best_path, unsupported_features = ranked_paths[0]
        try:
            result_schema = attempt_conversion_path(source, target, best_path, schema)
        except Exception as e:
            full_traceback = traceback.format_exc()
            attempt_errors.append(f"Error: {e}\nTraceback:\n{full_traceback}")
            ranked_paths = ranked_paths[1:]

    if result_schema is None:
        # return error message of all attempts together with the attempt number (1 to n)
        return {"error": "All conversion paths failed. Details: " + " | ".join([f"Attempt {i+1}: {msg}" for i, msg in enumerate(attempt_errors)])}, 500

    return {"schema": result_schema}, 200


def attempt_conversion_path(source: str, target: str, path: List[Converter], schema: str) -> str:
    print_conversion_path(source, target, path)
    current_schema = schema
    current_converter = None
    try:
        for conv in path:
            current_converter = conv
            current_schema = conv.convert(current_schema)
        return current_schema
    except Exception as e:
        raise Exception(f"Conversion failed at step from {current_converter.source_format} to {current_converter.target_format} via {current_converter.service_address} because of error: {str(e)}.")

def print_conversion_path(source: str, target: str, path: List[Converter]) -> None:
    print("Given the source format " + source + " and target format " + target + ", the best available path is:")
    for conv in path:
        print(f"{conv.source_format} -> {conv.target_format} via {conv.service_address}")

def call_internal_converter(source: str, target: str, schema: str) -> str:
    if source == "JsonSchema" and target == "LinkMl":
        return f"[Python] Converted from {source} to {target}: {schema}"
    elif source == "LinkMl" and target == "OntologyRdf":
        return f"[Python] Converted from {source} to {target}: {schema}"
    else:
        raise Exception("Unsupported internal conversion")

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5002)
