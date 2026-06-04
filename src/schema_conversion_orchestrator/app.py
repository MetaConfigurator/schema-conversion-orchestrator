from flask import Flask, request
from flask_cors import CORS
from typing import List, Optional
import json
import os

from schema_conversion_orchestrator.application.conversion_service import (
    ConversionService,
    NoConversionPathError,
)
from schema_conversion_orchestrator.converters.base import Converter
from schema_conversion_orchestrator.application.print_results import print_conversion_results
from schema_conversion_orchestrator.application.serialize_results import serialize_conversion_results
from schema_conversion_orchestrator.domain.schema_types import schema_language_from_string


def create_app(converters: Optional[List[Converter]] = None) -> Flask:
    if converters is None:
        from schema_conversion_orchestrator.converters.registry import register_converters

        converters = register_converters()

    conversion_service = ConversionService(converters)

    print("Started Schema Conversion Orchestrator with the following converters:")
    for conv in conversion_service.converters:
        print(f"- {conv.name}: {conv.source_language} -> {conv.target_language} at {conv.service_address}")

    app = Flask(__name__)

    # CORS: required when the frontend (e.g. MetaConfigurator) is served from a
    # different origin than this service. In the joint production deployment the
    # service sits behind the same reverse proxy (same origin), so CORS is not
    # strictly needed there, but it is harmless. For local development the MC dev
    # server (http://localhost:5173) talks cross-origin to this service, so the
    # default allowlist includes it. Override with the CORS_ALLOWED_ORIGINS env
    # var (comma-separated list, or "*" to allow any origin).
    cors_origins_raw = os.environ.get(
        "CORS_ALLOWED_ORIGINS",
        "http://localhost:5173,"
        "https://metaconfigurator.github.io,"
        "https://logende.github.io,"
        "https://www.metaconfigurator.org,"
        "https://metaconfigurator.org,"
        "https://metaconfigurator.informatik.uni-stuttgart.de",
    ).strip()
    if cors_origins_raw == "*":
        CORS(app)
    else:
        origins = [o.strip() for o in cors_origins_raw.split(",") if o.strip()]
        CORS(app, resources={r"/*": {"origins": origins}})

    @app.route("/health", methods=["GET"])
    def health():
        return {"status": "ok"}, 200

    @app.route("/convert", methods=["POST"])
    def convert():
        data = request.json
        source = data["sourceLanguage"]
        target = data["targetLanguage"]
        schema = data["schema"]
        use_cache = data.get("useCache", True)
        if not isinstance(use_cache, bool):
            return {"error": "useCache must be a boolean when provided."}, 400

        try:
            source = schema_language_from_string(source)
            target = schema_language_from_string(target)
        except ValueError as e:
            return {"error": str(e)}, 400

        if isinstance(schema, dict):
            schema = json.dumps(schema)

        try:
            results = conversion_service.convert(source, target, schema, use_cache=use_cache)
        except NoConversionPathError as e:
            return {"error": str(e)}, 400
        except ValueError as e:
            return {"error": str(e)}, 500

        print_conversion_results(results)

        return {"results": serialize_conversion_results(results)}, 200

    return app


if __name__ == "__main__":
    create_app().run(host="0.0.0.0", port=5002)
