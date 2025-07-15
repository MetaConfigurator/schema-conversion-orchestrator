from .data_structures import Converter, SchemaFeature
from .logic import build_conversion_tree, identify_schema_features, find_paths, determine_best_path
from flask import Flask, request, jsonify
from enum import Enum
from typing import List, Dict
import requests

app = Flask(__name__)


converters: List[Converter] = []
conversion_graph: Dict[str, List[Converter]] = {}

@app.route("/registerConversion", methods=["POST"])
def register_conversion():
    data = request.json
    conv = Converter(
        data["serviceAddress"],
        data["sourceFormat"],
        data["targetFormat"],
        data["supportedFeatures"]
    )
    converters.append(conv)
    build_conversion_tree(converters)
    return {"status": "registered"}, 200


@app.route("/convert", methods=["POST"])
def convert():
    data = request.json
    source = data["sourceFormat"]
    target = data["targetFormat"]
    schema = data["schema"]

    all_paths = find_paths(source, target)
    if not all_paths:
        return {"error": "No path found"}, 404

    doc_features = set(identify_schema_features(schema, source))
    best_path, unsupported_features = determine_best_path(all_paths, doc_features)

    current_schema = schema
    current_format = source
    for conv in best_path:
        if conv.serviceAddress == "internal":
            current_schema = call_internal_converter(conv.sourceFormat, conv.targetFormat, current_schema)
        else:
            r = requests.post(conv.serviceAddress + "/convert", json={
                "sourceFormat": conv.sourceFormat,
                "targetFormat": conv.targetFormat,
                "schema": current_schema
            })
            current_schema = r.json()["schema"]
        current_format = conv.targetFormat

    return {"schema": current_schema}, 200

def call_internal_converter(source: str, target: str, schema: str) -> str:
    if source == "JsonSchema" and target == "LinkMl":
        return f"[Python] Converted from {source} to {target}: {schema}"
    elif source == "LinkMl" and target == "OntologyRdf":
        return f"[Python] Converted from {source} to {target}: {schema}"
    else:
        raise Exception("Unsupported internal conversion")

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
