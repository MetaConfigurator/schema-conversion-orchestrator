"""Unit tests for ranking: edge robustness, accuracy-based ranking, and the
automatic ranking-strategy selection in the conversion service.

These tests inject scores (or monkeypatch the score lookups) so they do not
depend on the persisted accuracy / edge-robustness data files.
"""
import pytest

from schema_conversion_orchestrator.converters.base import ConverterInternal
from schema_conversion_orchestrator.domain.schema_types import SchemaLanguage
from schema_conversion_orchestrator.domain import edge_robustness as er
from schema_conversion_orchestrator.domain import ranking
from schema_conversion_orchestrator.domain.ranking import (
    rank_with_strategy_accuracy_based,
    rank_with_strategy_character_length,
    rank_with_strategy_edge_robustness,
)

XSD = SchemaLanguage.Xsd
JS = SchemaLanguage.JsonSchema
SH = SchemaLanguage.SHACL_TTL


class _Edge(ConverterInternal):
    """Minimal converter used only to give a path real edges (src/tgt/name)."""

    def __init__(self, source: SchemaLanguage, target: SchemaLanguage, name: str):
        super().__init__(
            name=name,
            service_address="mock",
            service_name="mock",
            source_language=source,
            target_language=target,
        )

    def converter_logic(self, schema: str) -> str:
        return schema

    def validate_input(self, schema: str) -> bool:
        return True

    def validate_output(self, schema: str) -> bool:
        return True


def edge(source, target, name):
    return _Edge(source, target, name)


def result(success, content, path):
    return (success, content, path, None)


# ---------------------------------------------------------------------------
# edge_robustness module
# ---------------------------------------------------------------------------

class TestEdgeRobustnessModule:
    def test_edge_key_format(self):
        assert er.edge_key("Xsd", "JsonSchema", "Jsonix") == "Xsd:JsonSchema:Jsonix"

    def test_unknown_edge_uses_default(self):
        assert er.lookup_edge_robustness("Xsd", "JsonSchema", "Nope", scores={}) == er.DEFAULT_EDGE_ROBUSTNESS

    def test_lookup_dict_entry(self):
        scores = {"Xsd:JsonSchema:Jsonix": {"robustness": 0.1, "good": 0, "lacking": 1, "invalid": 9, "cases": 10}}
        assert er.lookup_edge_robustness("Xsd", "JsonSchema", "Jsonix", scores=scores) == pytest.approx(0.1)

    def test_lookup_plain_float_entry(self):
        assert er.lookup_edge_robustness("A", "B", "c", scores={"A:B:c": 0.3}) == pytest.approx(0.3)

    def test_path_robustness_is_product_of_edges(self):
        scores = {
            er.edge_key("Xsd", "JsonSchema", "xjc"): {"robustness": 0.4},
            er.edge_key("JsonSchema", "SHACL_TTL", "x"): {"robustness": 0.5},
        }
        path = [edge(XSD, JS, "xjc"), edge(JS, SH, "x")]
        assert er.path_robustness(path, scores=scores) == pytest.approx(0.2)

    def test_default_factor_prefers_shorter_paths(self):
        # With no stored scores every edge contributes the 0.5 default, so a
        # longer path always has a strictly smaller robustness product.
        short = [edge(XSD, JS, "a")]
        longer = [edge(XSD, JS, "a"), edge(JS, SH, "b")]
        assert er.path_robustness(short, scores={}) > er.path_robustness(longer, scores={})

    def test_has_robustness_scores(self):
        assert er.has_robustness_scores({}) is False
        assert er.has_robustness_scores({"A:B:c": 0.5}) is True


# ---------------------------------------------------------------------------
# rank_with_strategy_edge_robustness
# ---------------------------------------------------------------------------

class TestEdgeRobustnessRanking:
    def test_higher_robustness_ranked_first(self, monkeypatch):
        monkeypatch.setattr(ranking, "path_robustness",
                            lambda path, scores=None: {"good": 0.9, "bad": 0.1}[path[0].name])
        results = [
            result(True, "x", [edge(XSD, JS, "bad")]),
            result(True, "y", [edge(XSD, JS, "good")]),
        ]
        rank_with_strategy_edge_robustness(results)
        assert results[0][2][0].name == "good"

    def test_failures_ranked_last(self, monkeypatch):
        monkeypatch.setattr(ranking, "path_robustness", lambda path, scores=None: 0.0)
        results = [
            result(True, "x", [edge(XSD, JS, "a")]),
            result(False, "long error message", []),
        ]
        rank_with_strategy_edge_robustness(results)
        assert results[0][0] is True

    def test_ties_broken_by_character_length(self, monkeypatch):
        monkeypatch.setattr(ranking, "path_robustness", lambda path, scores=None: 0.5)
        results = [
            result(True, "short", [edge(XSD, JS, "a")]),
            result(True, "a_much_longer_output", [edge(XSD, JS, "b")]),
        ]
        rank_with_strategy_edge_robustness(results)
        assert results[0][1] == "a_much_longer_output"

    def test_verbose_but_unrobust_loses_to_robust_direct(self, monkeypatch):
        # A verbose output (would win under character length) but with low edge
        # robustness must lose to a shorter, high-robustness direct conversion.
        monkeypatch.setattr(ranking, "path_robustness",
                            lambda path, scores=None: {"jsonix": 0.1, "direct": 1.0}[path[0].name])
        results = [
            result(True, "x" * 1000, [edge(XSD, JS, "jsonix")]),
            result(True, "short_but_good", [edge(XSD, JS, "direct")]),
        ]
        rank_with_strategy_edge_robustness(results)
        assert results[0][2][0].name == "direct"


# ---------------------------------------------------------------------------
# rank_with_strategy_accuracy_based
# ---------------------------------------------------------------------------

class TestAccuracyRanking:
    def test_higher_accuracy_ranked_first(self, monkeypatch):
        monkeypatch.setattr(ranking, "lookup_score",
                            lambda source, target, signature, *a, **k:
                            {"hi": 0.9, "lo": 0.2}.get(signature.split(":")[-1]))
        results = [
            result(True, "x", [edge(XSD, JS, "lo")]),
            result(True, "y", [edge(XSD, JS, "hi")]),
        ]
        rank_with_strategy_accuracy_based(results, "Xsd", "JsonSchema")
        assert results[0][2][0].name == "hi"

    def test_scored_above_unscored_above_failure(self, monkeypatch):
        monkeypatch.setattr(ranking, "lookup_score",
                            lambda source, target, signature, *a, **k:
                            0.8 if signature.endswith("scored") else None)
        results = [
            result(True, "x", [edge(XSD, JS, "absent")]),
            result(True, "y", [edge(XSD, JS, "scored")]),
            result(False, "err", []),
        ]
        rank_with_strategy_accuracy_based(results, "Xsd", "JsonSchema")
        assert results[0][2][0].name == "scored"
        assert results[-1][0] is False


# ---------------------------------------------------------------------------
# automatic ranking-strategy selection (ConversionService._rank_results)
# ---------------------------------------------------------------------------

class TestAutomaticRankingSelection:
    def _patch(self, monkeypatch, accuracy: bool, robustness: bool):
        import schema_conversion_orchestrator.application.conversion_service as cs
        calls = []
        monkeypatch.setattr(cs, "has_accuracy_scores", lambda s, t: accuracy)
        monkeypatch.setattr(cs, "has_robustness_scores", lambda *a, **k: robustness)
        monkeypatch.setattr(cs, "rank_with_strategy_accuracy_based", lambda *a, **k: calls.append("accuracy"))
        monkeypatch.setattr(cs, "rank_with_strategy_edge_robustness", lambda *a, **k: calls.append("robustness"))
        monkeypatch.setattr(cs, "rank_with_strategy_character_length", lambda *a, **k: calls.append("length"))
        service = cs.ConversionService(converters=[])
        service._rank_results([], XSD, JS)
        return calls

    def test_accuracy_has_priority(self, monkeypatch):
        assert self._patch(monkeypatch, accuracy=True, robustness=True) == ["accuracy"]

    def test_robustness_when_no_accuracy(self, monkeypatch):
        assert self._patch(monkeypatch, accuracy=False, robustness=True) == ["robustness"]

    def test_character_length_when_neither(self, monkeypatch):
        assert self._patch(monkeypatch, accuracy=False, robustness=False) == ["length"]
