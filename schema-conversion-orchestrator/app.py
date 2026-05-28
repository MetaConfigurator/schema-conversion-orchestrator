from flask import Flask, request
from typing import List, Dict, Optional
import json

from ranking_strategies import RankingStrategy, rank_with_strategy_least_character_loss
from attempt_conversions import attempt_all_conversion_paths
from converter import Converter
from print_conversion_results import print_conversion_results
from serialize_conversion_results import serialize_conversion_results
from schema_types import schema_language_from_string
from logic import build_conversion_graph, find_paths

RANKING_STRATEGY = RankingStrategy.LeastCharacterLoss


def create_app(converters: Optional[List[Converter]] = None) -> Flask:
    if converters is None:
        from register_converters import register_converters
        converters = register_converters()

    conversion_graph: Dict[str, List[Converter]] = build_conversion_graph(converters)

    print("Started Schema Conversion Orchestrator with the following converters:")
    for conv in converters:
        print(f"- {conv.name}: {conv.source_language} -> {conv.target_language} at {conv.service_address}")

    app = Flask(__name__)

    @app.route("/health", methods=["GET"])
    def health():
        return {"status": "ok"}, 200

    @app.route("/convert", methods=["POST"])
    def convert():
        data = request.json
        source = data["sourceLanguage"]
        target = data["targetLanguage"]
        schema = data["schema"]

        try:
            source = schema_language_from_string(source)
            target = schema_language_from_string(target)
        except ValueError as e:
            return {"error": str(e)}, 400

        if isinstance(schema, dict):
            schema = json.dumps(schema)

        all_paths = find_paths(source, target, conversion_graph)
        if not all_paths:
            return {"error": f"No path found for conversion from source {source} to target {target}."}, 400

        results = attempt_all_conversion_paths(source, target, schema, all_paths)

        if RANKING_STRATEGY == RankingStrategy.LeastCharacterLoss:
            rank_with_strategy_least_character_loss(results)
        else:
            return {"error": "Unknown conversion strategy: " + RANKING_STRATEGY}, 500
        results = sorted(results, key=lambda x: x[0], reverse=True)

        print_conversion_results(results)

        return {"results": serialize_conversion_results(results)}, 200

    return app


if __name__ == "__main__":
    create_app().run(host="0.0.0.0", port=5002)
