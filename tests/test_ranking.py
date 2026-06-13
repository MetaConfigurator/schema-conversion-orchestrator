"""Unit tests for ranking: the edge-robustness module and the single fallback
chain (:func:`rank_results`) used by the conversion service.

These tests inject scores (or monkeypatch the score lookups) so they do not
depend on the persisted accuracy / edge-robustness data files.
"""
import pytest

from schema_conversion_orchestrator.converters.base import ConverterInternal
from schema_conversion_orchestrator.domain.schema_types import SchemaLanguage
from schema_conversion_orchestrator.domain import edge_robustness as er
from schema_conversion_orchestrator.domain import ranking
from schema_conversion_orchestrator.domain.ranking import rank_results

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

    def test_lookup_dict_entry_uses_quality(self):
        scores = {"Xsd:JsonSchema:Jsonix": {"robustness": 0.8, "quality": 0.5, "reliability": 0.4}}
        assert er.lookup_edge_robustness("Xsd", "JsonSchema", "Jsonix", scores=scores) == pytest.approx(0.5)

    def test_path_robustness_is_product_of_edge_qualities(self):
        scores = {
            er.edge_key("Xsd", "JsonSchema", "xjc"): {"robustness": 0.8, "quality": 0.5, "reliability": 0.4},
            er.edge_key("JsonSchema", "SHACL_TTL", "x"): {"robustness": 1.0, "quality": 0.8, "reliability": 0.8},
        }
        path = [edge(XSD, JS, "xjc"), edge(JS, SH, "x")]
        assert er.path_robustness(path, scores=scores) == pytest.approx(0.4)

    def test_default_factor_prefers_shorter_paths(self):
        # With no stored scores every edge contributes the 0.5 default, so a
        # longer path always has a strictly smaller robustness product.
        short = [edge(XSD, JS, "a")]
        longer = [edge(XSD, JS, "a"), edge(JS, SH, "b")]
        assert er.path_robustness(short, scores={}) > er.path_robustness(longer, scores={})

    def test_has_robustness_scores(self):
        assert er.has_robustness_scores({}) is False
        assert er.has_robustness_scores({"A:B:c": {"robustness": 1.0, "quality": 0.5, "reliability": 0.5}}) is True


# ---------------------------------------------------------------------------
# rank_results: the single fallback chain
#   accuracy -> edge quality -> shorter path -> longer output, failures last
# ---------------------------------------------------------------------------

class TestRankResultsChain:
    def test_failures_ranked_last(self, monkeypatch):
        monkeypatch.setattr(ranking, "has_accuracy_scores", lambda s, t: False)
        monkeypatch.setattr(ranking, "path_robustness", lambda path, scores=None: 1.0)
        results = [
            result(True, "x", [edge(XSD, JS, "a")]),
            result(False, "a very long error message", []),
        ]
        rank_results(results, "Xsd", "JsonSchema")
        assert results[0][0] is True
        assert results[-1][0] is False

    def test_accuracy_takes_priority_over_quality(self, monkeypatch):
        # Accuracy must decide even when edge quality would prefer the other path.
        monkeypatch.setattr(ranking, "has_accuracy_scores", lambda s, t: True)
        monkeypatch.setattr(ranking, "lookup_score",
                            lambda s, t, sig, *a, **k: {"hi": 0.9, "lo": 0.2}[sig.split(":")[-1]])
        monkeypatch.setattr(ranking, "path_robustness",
                            lambda path, scores=None: {"hi": 0.1, "lo": 1.0}[path[0].name])
        results = [
            result(True, "x", [edge(XSD, JS, "lo")]),
            result(True, "y", [edge(XSD, JS, "hi")]),
        ]
        rank_results(results, "Xsd", "JsonSchema")
        assert results[0][2][0].name == "hi"

    def test_scored_above_unscored_in_benchmarked_task(self, monkeypatch):
        monkeypatch.setattr(ranking, "has_accuracy_scores", lambda s, t: True)
        monkeypatch.setattr(ranking, "lookup_score",
                            lambda s, t, sig, *a, **k: 0.8 if sig.endswith("scored") else None)
        monkeypatch.setattr(ranking, "path_robustness", lambda path, scores=None: 1.0)
        results = [
            result(True, "x", [edge(XSD, JS, "absent")]),
            result(True, "y", [edge(XSD, JS, "scored")]),
            result(False, "err", []),
        ]
        rank_results(results, "Xsd", "JsonSchema")
        assert results[0][2][0].name == "scored"
        assert results[-1][0] is False

    def test_quality_decides_when_no_benchmark(self, monkeypatch):
        monkeypatch.setattr(ranking, "has_accuracy_scores", lambda s, t: False)
        monkeypatch.setattr(ranking, "path_robustness",
                            lambda path, scores=None: {"good": 0.9, "bad": 0.1}[path[0].name])
        results = [
            result(True, "x", [edge(XSD, JS, "bad")]),
            result(True, "y", [edge(XSD, JS, "good")]),
        ]
        rank_results(results, "Xsd", "JsonSchema")
        assert results[0][2][0].name == "good"

    def test_quality_breaks_accuracy_ties(self, monkeypatch):
        # Equal accuracy: edge quality is the next criterion.
        monkeypatch.setattr(ranking, "has_accuracy_scores", lambda s, t: True)
        monkeypatch.setattr(ranking, "lookup_score", lambda s, t, sig, *a, **k: 0.5)
        monkeypatch.setattr(ranking, "path_robustness",
                            lambda path, scores=None: {"good": 0.9, "bad": 0.1}[path[0].name])
        results = [
            result(True, "x", [edge(XSD, JS, "bad")]),
            result(True, "y", [edge(XSD, JS, "good")]),
        ]
        rank_results(results, "Xsd", "JsonSchema")
        assert results[0][2][0].name == "good"

    def test_shorter_path_breaks_quality_ties(self, monkeypatch):
        # Equal quality: the shorter (single-edge) path wins even though the
        # longer chain produces more output.
        monkeypatch.setattr(ranking, "has_accuracy_scores", lambda s, t: False)
        monkeypatch.setattr(ranking, "path_robustness", lambda path, scores=None: 1.0)
        results = [
            result(True, "x" * 1000, [edge(XSD, JS, "a"), edge(JS, SH, "b")]),
            result(True, "short_direct", [edge(XSD, JS, "direct")]),
        ]
        rank_results(results, "Xsd", "SHACL_TTL")
        assert results[0][2][0].name == "direct"
        assert len(results[0][2]) == 1

    def test_output_length_breaks_path_length_ties(self, monkeypatch):
        # Equal quality and equal path length: larger output wins.
        monkeypatch.setattr(ranking, "has_accuracy_scores", lambda s, t: False)
        monkeypatch.setattr(ranking, "path_robustness", lambda path, scores=None: 1.0)
        results = [
            result(True, "short", [edge(XSD, JS, "a")]),
            result(True, "a_much_longer_output", [edge(XSD, JS, "b")]),
        ]
        rank_results(results, "Xsd", "JsonSchema")
        assert results[0][1] == "a_much_longer_output"

    def test_unevaluated_edges_favour_shorter_path(self):
        # With no monkeypatching, unevaluated edges default to 0.5 each, so the
        # quality product shrinks with length and the direct path wins without
        # needing the explicit path-length tie-breaker.
        results = [
            result(True, "x" * 1000, [edge(XSD, JS, "nope_a"), edge(JS, SH, "nope_b")]),
            result(True, "short", [edge(XSD, SH, "nope_direct")]),
        ]
        rank_results(results, "Xsd", "SHACL_TTL")
        assert len(results[0][2]) == 1

    def test_verbose_but_low_quality_loses_to_good_direct(self, monkeypatch):
        # A verbose output that would win on length alone must lose to a shorter,
        # higher-quality direct conversion.
        monkeypatch.setattr(ranking, "has_accuracy_scores", lambda s, t: False)
        monkeypatch.setattr(ranking, "path_robustness",
                            lambda path, scores=None: {"jsonix": 0.1, "direct": 1.0}[path[0].name])
        results = [
            result(True, "x" * 1000, [edge(XSD, JS, "jsonix")]),
            result(True, "short_but_good", [edge(XSD, JS, "direct")]),
        ]
        rank_results(results, "Xsd", "JsonSchema")
        assert results[0][2][0].name == "direct"


# ---------------------------------------------------------------------------
# ConversionService._rank_results delegates to the chain with language values
# ---------------------------------------------------------------------------

class TestServiceRanking:
    def test_rank_results_called_with_language_values(self, monkeypatch):
        import schema_conversion_orchestrator.application.conversion_service as cs
        calls = []
        monkeypatch.setattr(cs, "rank_results", lambda results, s, t: calls.append((s, t)))
        service = cs.ConversionService(converters=[])
        service._rank_results([], XSD, JS)
        assert calls == [("Xsd", "JsonSchema")]
