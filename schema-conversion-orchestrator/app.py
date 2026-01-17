from conversion_strategies import ConversionStrategy, \
    convert_with_strategy_least_character_loss
from converter import (Converter, prepare_conversion_results_for_serializing)
from schema_types import schema_language_from_string
from logic import build_conversion_graph, find_paths
from register_converters import register_converters
from flask import Flask, request
from typing import List, Dict
import json

app = Flask(__name__)

CONVERSION_STRATEGY = ConversionStrategy.LeastCharacterLoss

converters: List[Converter] = register_converters()
conversion_graph: Dict[str, List[Converter]] = build_conversion_graph(converters)

print("Started Schema Conversion Orchestrator with the following converters:")
for conv in converters:
    print(f"- {conv.name}: {conv.source_format} -> {conv.target_format} at {conv.service_address}")


@app.route("/health", methods=["GET"])
def health():
    return {"status": "ok"}, 200


@app.route("/convert", methods=["POST"])
def convert():
    data = request.json
    source = data["sourceFormat"]
    target = data["targetFormat"]
    schema = data["schema"]

    try:
        source = schema_language_from_string(source)
        target = schema_language_from_string(target)
    except ValueError as e:
        return {"error": str(e)}, 400

    # if schema is an object, convert it to string
    if isinstance(schema, dict):
        schema = json.dumps(schema)

    all_paths = find_paths(source, target, conversion_graph)
    if not all_paths:
        return {"error": "No path found for conversion from source " + source + " to target " + target + "."}, 400

    if CONVERSION_STRATEGY == ConversionStrategy.LeastCharacterLoss:
        attempts = convert_with_strategy_least_character_loss(
            source, target, schema, all_paths)
    else:
        return {"error": "Unknown conversion strategy: " + CONVERSION_STRATEGY}, 500

    best_attempt = attempts[0]
    success, schema, conversion_path = best_attempt

    if not success:
        # return error message of all attempts together with the attempt number (1 to n)
        return {"error": "All conversion paths failed.", "attempts": prepare_conversion_results_for_serializing(attempts)}, 500

    return {"schema": schema}, 200


def call_internal_converter(source: str, target: str, schema: str) -> str:
    if source == "JsonSchema" and target == "LinkMl":
        return f"[Python] Converted from {source} to {target}: {schema}"
    elif source == "LinkMl" and target == "OntologyRdf":
        return f"[Python] Converted from {source} to {target}: {schema}"
    else:
        raise Exception("Unsupported internal conversion")


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5002)
