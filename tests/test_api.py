"""
Flask integration tests for the /health and /convert endpoints.
All tests use mock converters injected via create_app() so no external
processes (Java, Node) or heavy Python packages (LinkML) are invoked.
"""

import json
import pytest

from schema_conversion_orchestrator.converters.base import ConverterInternal
from schema_conversion_orchestrator.domain.schema_types import SchemaLanguage
from schema_conversion_orchestrator.app import create_app


# ---------------------------------------------------------------------------
# Mock converter
# ---------------------------------------------------------------------------

class _MockConverter(ConverterInternal):
    def __init__(self, source: SchemaLanguage, target: SchemaLanguage, result: str = "mock_output"):
        super().__init__(
            name=f"Mock {source}->{target}",
            service_address="mock",
            service_name="mock",
            source_language=source,
            target_language=target,
        )
        self._result = result

    def converter_logic(self, schema: str) -> str:
        return self._result

    def validate_input(self, schema: str) -> bool:
        return True

    def validate_output(self, schema: str) -> bool:
        return True


class _FailingConverter(_MockConverter):
    def converter_logic(self, schema: str) -> str:
        raise RuntimeError("converter broke")


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

MOCK_CONVERTERS = [
    _MockConverter(SchemaLanguage.JsonSchema, SchemaLanguage.LinkMl, result='{"id": "Person"}'),
    _MockConverter(SchemaLanguage.LinkMl, SchemaLanguage.Xsd, result="<xs:schema/>"),
    _MockConverter(SchemaLanguage.JsonSchema, SchemaLanguage.Xsd, result="<xs:schema/>"),
    _MockConverter(SchemaLanguage.SHACL_TTL, SchemaLanguage.JsonSchema, result='{"type":"object"}'),
]


@pytest.fixture
def client():
    app = create_app(converters=MOCK_CONVERTERS)
    app.config["TESTING"] = True
    with app.test_client() as c:
        yield c


@pytest.fixture
def client_no_converters():
    app = create_app(converters=[])
    app.config["TESTING"] = True
    with app.test_client() as c:
        yield c


@pytest.fixture
def client_failing():
    app = create_app(converters=[
        _FailingConverter(SchemaLanguage.JsonSchema, SchemaLanguage.LinkMl),
    ])
    app.config["TESTING"] = True
    with app.test_client() as c:
        yield c


# ---------------------------------------------------------------------------
# /health
# ---------------------------------------------------------------------------

class TestHealth:
    def test_returns_200(self, client):
        resp = client.get("/health")
        assert resp.status_code == 200

    def test_returns_ok_status(self, client):
        data = resp_json(client.get("/health"))
        assert data["status"] == "ok"


# ---------------------------------------------------------------------------
# /convert — success cases
# ---------------------------------------------------------------------------

class TestConvertSuccess:
    def test_direct_path(self, client):
        resp = client.post("/convert", json={
            "sourceLanguage": "JsonSchema",
            "targetLanguage": "LinkMl",
            "schema": '{"type": "object"}',
        })
        assert resp.status_code == 200
        data = resp_json(resp)
        assert "results" in data
        assert len(data["results"]) > 0

    def test_result_has_required_fields(self, client):
        resp = client.post("/convert", json={
            "sourceLanguage": "JsonSchema",
            "targetLanguage": "LinkMl",
            "schema": '{"type": "object"}',
        })
        result = resp_json(resp)["results"][0]
        assert "success" in result
        assert "result" in result
        assert "conversionPath" in result

    def test_successful_result_first(self, client):
        resp = client.post("/convert", json={
            "sourceLanguage": "JsonSchema",
            "targetLanguage": "LinkMl",
            "schema": '{"type": "object"}',
        })
        first = resp_json(resp)["results"][0]
        assert first["success"] is True

    def test_multi_hop_path(self, client):
        # JsonSchema → LinkMl → Xsd (no direct JsonSchema→Xsd except there is one too — both returned)
        resp = client.post("/convert", json={
            "sourceLanguage": "JsonSchema",
            "targetLanguage": "Xsd",
            "schema": '{"type": "object"}',
        })
        assert resp.status_code == 200
        data = resp_json(resp)
        assert len(data["results"]) >= 1

    def test_schema_as_dict_accepted(self, client):
        resp = client.post("/convert", json={
            "sourceLanguage": "JsonSchema",
            "targetLanguage": "LinkMl",
            "schema": {"type": "object", "properties": {"name": {"type": "string"}}},
        })
        assert resp.status_code == 200

    def test_case_insensitive_language(self, client):
        resp = client.post("/convert", json={
            "sourceLanguage": "jsonschema",
            "targetLanguage": "linkml",
            "schema": "{}",
        })
        assert resp.status_code == 200

    def test_conversion_path_info_correct(self, client):
        resp = client.post("/convert", json={
            "sourceLanguage": "JsonSchema",
            "targetLanguage": "LinkMl",
            "schema": "{}",
        })
        results = resp_json(resp)["results"]
        direct = next(r for r in results if len(r["conversionPath"]) == 1)
        step = direct["conversionPath"][0]
        assert step["sourceLanguage"] == "JsonSchema"
        assert step["targetLanguage"] == "LinkMl"


# ---------------------------------------------------------------------------
# /convert — error cases
# ---------------------------------------------------------------------------

class TestConvertErrors:
    def test_no_path_returns_400(self, client):
        resp = client.post("/convert", json={
            "sourceLanguage": "JsonSchema",
            "targetLanguage": "MdModels",  # no converter registered
            "schema": "{}",
        })
        assert resp.status_code == 400
        assert "error" in resp_json(resp)

    def test_unknown_source_language_returns_400(self, client):
        resp = client.post("/convert", json={
            "sourceLanguage": "NonExistentLang",
            "targetLanguage": "LinkMl",
            "schema": "{}",
        })
        assert resp.status_code == 400
        assert "error" in resp_json(resp)

    def test_unknown_target_language_returns_400(self, client):
        resp = client.post("/convert", json={
            "sourceLanguage": "JsonSchema",
            "targetLanguage": "FakeLang",
            "schema": "{}",
        })
        assert resp.status_code == 400

    def test_failing_converter_still_returns_200_with_failure(self, client_failing):
        # A converter that throws should return 200 with success=False, not 500
        resp = client_failing.post("/convert", json={
            "sourceLanguage": "JsonSchema",
            "targetLanguage": "LinkMl",
            "schema": "{}",
        })
        assert resp.status_code == 200
        results = resp_json(resp)["results"]
        assert len(results) == 1
        assert results[0]["success"] is False

    def test_no_converters_returns_400(self, client_no_converters):
        resp = client_no_converters.post("/convert", json={
            "sourceLanguage": "JsonSchema",
            "targetLanguage": "LinkMl",
            "schema": "{}",
        })
        assert resp.status_code == 400


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def resp_json(resp):
    return json.loads(resp.data)
