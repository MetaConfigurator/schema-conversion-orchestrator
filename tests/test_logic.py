"""
Unit tests for pure-Python logic: graph building, pathfinding, ranking,
schema type parsing, serialization, and conversion attempt mechanics.
None of these tests require heavy external converters (LinkML, Java, Node).
"""

import pytest
from schema_conversion_orchestrator.converters.base import (
    Converter,
    ConverterInternal,
)
from schema_conversion_orchestrator.domain.conversion_types import (
    ConversionPath,
    conversion_path_to_string,
)
from schema_conversion_orchestrator.domain.conversion_graph import build_conversion_graph, find_paths
from schema_conversion_orchestrator.domain.schema_types import SchemaLanguage, schema_language_from_string
from schema_conversion_orchestrator.domain.ranking import rank_with_strategy_character_length
from schema_conversion_orchestrator.application.serialize_results import serialize_conversion_results
from schema_conversion_orchestrator.application.attempt_conversions import attempt_all_conversion_paths


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

class _MockConverter(ConverterInternal):
    """Lightweight converter that returns a fixed string, for graph/logic tests."""

    def __init__(self, source: SchemaLanguage, target: SchemaLanguage, result: str = "converted"):
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
        raise RuntimeError("intentional failure")


# ---------------------------------------------------------------------------
# schema_language_from_string
# ---------------------------------------------------------------------------

class TestSchemaLanguageFromString:
    def test_exact_match(self):
        assert schema_language_from_string("JsonSchema") == SchemaLanguage.JsonSchema

    def test_case_insensitive(self):
        assert schema_language_from_string("jsonschema") == SchemaLanguage.JsonSchema
        assert schema_language_from_string("LINKML") == SchemaLanguage.LinkMl
        assert schema_language_from_string("XSD") == SchemaLanguage.Xsd

    def test_unknown_raises(self):
        with pytest.raises(ValueError, match="Unknown schema language"):
            schema_language_from_string("NotALanguage")


# ---------------------------------------------------------------------------
# build_conversion_graph
# ---------------------------------------------------------------------------

class TestBuildConversionGraph:
    def test_empty(self):
        assert build_conversion_graph([]) == {}

    def test_single_converter(self):
        conv = _MockConverter(SchemaLanguage.JsonSchema, SchemaLanguage.LinkMl)
        graph = build_conversion_graph([conv])
        assert SchemaLanguage.JsonSchema in graph
        assert graph[SchemaLanguage.JsonSchema] == [conv]

    def test_multiple_converters_same_source(self):
        c1 = _MockConverter(SchemaLanguage.JsonSchema, SchemaLanguage.LinkMl)
        c2 = _MockConverter(SchemaLanguage.JsonSchema, SchemaLanguage.Xsd)
        graph = build_conversion_graph([c1, c2])
        assert len(graph[SchemaLanguage.JsonSchema]) == 2

    def test_multiple_sources(self):
        c1 = _MockConverter(SchemaLanguage.JsonSchema, SchemaLanguage.LinkMl)
        c2 = _MockConverter(SchemaLanguage.LinkMl, SchemaLanguage.Xsd)
        graph = build_conversion_graph([c1, c2])
        assert SchemaLanguage.JsonSchema in graph
        assert SchemaLanguage.LinkMl in graph


# ---------------------------------------------------------------------------
# find_paths
# ---------------------------------------------------------------------------

class TestFindPaths:
    def _make_graph(self, edges):
        convs = [_MockConverter(src, tgt) for src, tgt in edges]
        return build_conversion_graph(convs), convs

    def test_same_source_target(self):
        _, _ = self._make_graph([])
        graph = build_conversion_graph([])
        paths = find_paths(SchemaLanguage.JsonSchema, SchemaLanguage.JsonSchema, graph)
        assert paths == [[]]

    def test_direct_path(self):
        graph, [conv] = self._make_graph([(SchemaLanguage.JsonSchema, SchemaLanguage.LinkMl)])
        paths = find_paths(SchemaLanguage.JsonSchema, SchemaLanguage.LinkMl, graph)
        assert len(paths) == 1
        assert paths[0] == [conv]

    def test_no_path(self):
        graph, _ = self._make_graph([(SchemaLanguage.JsonSchema, SchemaLanguage.LinkMl)])
        paths = find_paths(SchemaLanguage.JsonSchema, SchemaLanguage.Xsd, graph)
        assert paths == []

    def test_multi_hop_path(self):
        graph, convs = self._make_graph([
            (SchemaLanguage.JsonSchema, SchemaLanguage.LinkMl),
            (SchemaLanguage.LinkMl, SchemaLanguage.Xsd),
        ])
        paths = find_paths(SchemaLanguage.JsonSchema, SchemaLanguage.Xsd, graph)
        assert len(paths) == 1
        assert len(paths[0]) == 2

    def test_multiple_paths(self):
        # Direct path + two-hop path both exist
        graph, _ = self._make_graph([
            (SchemaLanguage.JsonSchema, SchemaLanguage.Xsd),         # direct
            (SchemaLanguage.JsonSchema, SchemaLanguage.LinkMl),
            (SchemaLanguage.LinkMl, SchemaLanguage.Xsd),             # via LinkMl
        ])
        paths = find_paths(SchemaLanguage.JsonSchema, SchemaLanguage.Xsd, graph)
        assert len(paths) == 2

    def test_no_cycles(self):
        # Graph with a potential cycle should not loop forever
        graph, _ = self._make_graph([
            (SchemaLanguage.JsonSchema, SchemaLanguage.LinkMl),
            (SchemaLanguage.LinkMl, SchemaLanguage.JsonSchema),
        ])
        paths = find_paths(SchemaLanguage.JsonSchema, SchemaLanguage.Xsd, graph)
        assert paths == []


# ---------------------------------------------------------------------------
# conversion_path_to_string
# ---------------------------------------------------------------------------

class TestConversionPathToString:
    def test_single_step(self):
        conv = _MockConverter(SchemaLanguage.JsonSchema, SchemaLanguage.LinkMl)
        result = conversion_path_to_string([conv])
        assert "JsonSchema" in result
        assert "LinkMl" in result

    def test_multi_step(self):
        c1 = _MockConverter(SchemaLanguage.JsonSchema, SchemaLanguage.LinkMl)
        c2 = _MockConverter(SchemaLanguage.LinkMl, SchemaLanguage.Xsd)
        result = conversion_path_to_string([c1, c2])
        assert "JsonSchema" in result
        assert "Xsd" in result

    def test_empty_path(self):
        result = conversion_path_to_string([])
        assert result == ""


# ---------------------------------------------------------------------------
# rank_with_strategy_character_length
# ---------------------------------------------------------------------------

class TestRanking:
    def _make_results(self, entries):
        """entries: list of (success, schema_or_error) — path can be []"""
        return [(success, content, [], None) for success, content in entries]

    def test_successful_before_failed(self):
        results = self._make_results([(False, "err"), (True, "ok")])
        rank_with_strategy_character_length(results)
        assert results[0][0] is True

    def test_longer_schema_wins_among_successes(self):
        results = self._make_results([(True, "short"), (True, "much_longer_schema")])
        rank_with_strategy_character_length(results)
        assert results[0][1] == "much_longer_schema"

    def test_failed_error_length_ignored(self):
        results = self._make_results([
            (False, "very long error message that should not beat a success"),
            (True, "x"),
        ])
        rank_with_strategy_character_length(results)
        assert results[0][0] is True


# ---------------------------------------------------------------------------
# serialize_conversion_results
# ---------------------------------------------------------------------------

class TestSerializeConversionResults:
    def test_structure(self):
        conv = _MockConverter(SchemaLanguage.JsonSchema, SchemaLanguage.LinkMl)
        results = [(True, "output", [conv], None)]
        serialized = serialize_conversion_results(results)
        assert len(serialized) == 1
        entry = serialized[0]
        assert entry["success"] is True
        assert entry["result"] == "output"
        assert len(entry["conversionPath"]) == 1
        step = entry["conversionPath"][0]
        assert step["sourceLanguage"] == "JsonSchema"
        assert step["targetLanguage"] == "LinkMl"

    def test_failed_result(self):
        results = [(False, "some error", [], 0)]
        serialized = serialize_conversion_results(results)
        assert serialized[0]["success"] is False
        assert serialized[0]["result"] == "some error"
        assert serialized[0]["failedStepIndex"] == 0

    def test_empty(self):
        assert serialize_conversion_results([]) == []

    def test_multiple_steps_in_path(self):
        c1 = _MockConverter(SchemaLanguage.JsonSchema, SchemaLanguage.LinkMl)
        c2 = _MockConverter(SchemaLanguage.LinkMl, SchemaLanguage.Xsd)
        results = [(True, "output", [c1, c2], None)]
        serialized = serialize_conversion_results(results)
        assert len(serialized[0]["conversionPath"]) == 2


# ---------------------------------------------------------------------------
# attempt_all_conversion_paths
# ---------------------------------------------------------------------------

class TestAttemptAllConversionPaths:
    def test_successful_conversion(self):
        conv = _MockConverter(SchemaLanguage.JsonSchema, SchemaLanguage.LinkMl, result="result_schema")
        paths = [[conv]]
        results = attempt_all_conversion_paths(
            SchemaLanguage.JsonSchema, SchemaLanguage.LinkMl, "input", paths
        )
        assert len(results) == 1
        success, schema, path, failed_step_index = results[0]
        assert success is True
        assert schema == "result_schema"
        assert failed_step_index is None

    def test_failing_conversion_recorded(self):
        conv = _FailingConverter(SchemaLanguage.JsonSchema, SchemaLanguage.LinkMl)
        paths = [[conv]]
        results = attempt_all_conversion_paths(
            SchemaLanguage.JsonSchema, SchemaLanguage.LinkMl, "input", paths
        )
        assert len(results) == 1
        success, error_msg, _, failed_step_index = results[0]
        assert success is False
        assert "intentional failure" in error_msg
        assert failed_step_index == 0

    def test_failed_step_index_points_at_failing_step(self):
        # First step succeeds, second step fails -> failed_step_index should be 1
        c_ok = _MockConverter(SchemaLanguage.JsonSchema, SchemaLanguage.LinkMl, result="linkml")
        c_fail = _FailingConverter(SchemaLanguage.LinkMl, SchemaLanguage.Xsd)
        paths = [[c_ok, c_fail]]
        results = attempt_all_conversion_paths(
            SchemaLanguage.JsonSchema, SchemaLanguage.Xsd, "input", paths
        )
        success, _error_msg, _path, failed_step_index = results[0]
        assert success is False
        assert failed_step_index == 1

    def test_multiple_paths_attempted(self):
        # Use two-step paths so that each path has a distinct cache key
        c_ok_mid = _MockConverter(SchemaLanguage.JsonSchema, SchemaLanguage.LinkMl, result="linkml")
        c_ok_end = _MockConverter(SchemaLanguage.LinkMl, SchemaLanguage.Xsd, result="xsd_output")

        class _FailMid(_FailingConverter):
            def __init__(self):
                super().__init__(SchemaLanguage.JsonSchema, SchemaLanguage.MdModels)
                self.service_name = "fail-mock"

        c_fail = _FailMid()
        c_fail_end = _MockConverter(SchemaLanguage.MdModels, SchemaLanguage.Xsd)
        paths = [[c_ok_mid, c_ok_end], [c_fail, c_fail_end]]
        results = attempt_all_conversion_paths(
            SchemaLanguage.JsonSchema, SchemaLanguage.Xsd, "input", paths
        )
        assert len(results) == 2
        successes = [r[0] for r in results]
        assert True in successes
        assert False in successes

    def test_intermediate_result_cached(self):
        call_count = {"n": 0}

        class CountingConverter(_MockConverter):
            def converter_logic(self, schema: str) -> str:
                call_count["n"] += 1
                return "intermediate"

        c1 = CountingConverter(SchemaLanguage.JsonSchema, SchemaLanguage.LinkMl)
        c2a = _MockConverter(SchemaLanguage.LinkMl, SchemaLanguage.Xsd, result="xsd_a")
        c2b = _MockConverter(SchemaLanguage.LinkMl, SchemaLanguage.Xsd, result="xsd_b")
        # Two paths share the first step (JsonSchema→LinkMl)
        paths = [[c1, c2a], [c1, c2b]]
        attempt_all_conversion_paths(
            SchemaLanguage.JsonSchema, SchemaLanguage.Xsd, "input", paths
        )
        # c1 should only be called once due to caching
        assert call_count["n"] == 1

    def test_intermediate_result_not_cached_when_disabled(self):
        call_count = {"n": 0}

        class CountingConverter(_MockConverter):
            def converter_logic(self, schema: str) -> str:
                call_count["n"] += 1
                return "intermediate"

        c1 = CountingConverter(SchemaLanguage.JsonSchema, SchemaLanguage.LinkMl)
        c2a = _MockConverter(SchemaLanguage.LinkMl, SchemaLanguage.Xsd, result="xsd_a")
        c2b = _MockConverter(SchemaLanguage.LinkMl, SchemaLanguage.Xsd, result="xsd_b")
        paths = [[c1, c2a], [c1, c2b]]
        attempt_all_conversion_paths(
            SchemaLanguage.JsonSchema, SchemaLanguage.Xsd, "input", paths, use_cache=False
        )
        assert call_count["n"] == 2
