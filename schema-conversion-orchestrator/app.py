from conversion_strategies import convert_with_strategy_most_features_preserved, ConversionStrategy, \
    convert_with_strategy_least_character_loss
from converter import (Converter, ConverterExternal)
from schema_types import schema_language_from_string, SchemaLanguagesFeatures
from logic import build_conversion_graph, find_paths
from register_converters import register_converters
from flask import Flask, request
from typing import List, Dict
from schema_languages_loader import load_schema_language_features

app = Flask(__name__)

DETAILED_ERROR_OUTPUT = False
CONVERSION_STRATEGY = ConversionStrategy.LeastCharacterLoss

converters: List[Converter] = register_converters()
conversion_graph: Dict[str, List[Converter]] = build_conversion_graph(converters)
schema_languages_features: SchemaLanguagesFeatures = load_schema_language_features()

print("Started Schema Conversion Orchestrator with the following converters:")
for conv in converters:
    print(f"- {conv.name}: {conv.source_format} -> {conv.target_format} at {conv.service_address}")


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
    print(
        f"Registered new converter: {conv.name} from {conv.source_format} to {conv.target_format} at {conv.service_address}.")
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

    if CONVERSION_STRATEGY == ConversionStrategy.MostFeaturesPreserved:
        attempts = convert_with_strategy_most_features_preserved(
            source, target, schema, all_paths)
    elif CONVERSION_STRATEGY == ConversionStrategy.LeastCharacterLoss:
        attempts = convert_with_strategy_least_character_loss(
            source, target, schema, all_paths)
    else:
        return {"error": "Unknown conversion strategy: " + CONVERSION_STRATEGY}, 500

    best_attempt = attempts[0]
    success, schema, conversion_path = best_attempt

    if not success:
        # return error message of all attempts together with the attempt number (1 to n)
        return {"error": "All conversion paths failed.", attempts: attempts}, 500

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
