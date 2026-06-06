from typing import List

from schema_conversion_orchestrator.application.attempt_conversions import attempt_all_conversion_paths
from schema_conversion_orchestrator.converters.base import Converter
from schema_conversion_orchestrator.domain.conversion_graph import build_conversion_graph, find_paths
from schema_conversion_orchestrator.domain.conversion_types import ConversionGraph, ConversionResults
from schema_conversion_orchestrator.domain.accuracy_scores import has_accuracy_scores
from schema_conversion_orchestrator.domain.edge_robustness import has_robustness_scores
from schema_conversion_orchestrator.domain.ranking import (
    rank_with_strategy_accuracy_based,
    rank_with_strategy_edge_robustness,
    rank_with_strategy_character_length,
)
from schema_conversion_orchestrator.domain.schema_types import SchemaLanguage


class NoConversionPathError(ValueError):
    """Raised when no converter path exists between two schema languages."""


class ConversionService:
    def __init__(self, converters: List[Converter]) -> None:
        self.converters = converters
        self.conversion_graph: ConversionGraph = build_conversion_graph(converters)

    def convert(
        self,
        source: SchemaLanguage,
        target: SchemaLanguage,
        schema: str,
        use_cache: bool = True,
    ) -> ConversionResults:
        paths = find_paths(source, target, self.conversion_graph)
        if not paths:
            raise NoConversionPathError(
                f"No path found for conversion from source {source} to target {target}."
            )

        results = attempt_all_conversion_paths(source, target, schema, paths, use_cache=use_cache)
        self._rank_results(results, source, target)
        return sorted(results, key=lambda x: x[0], reverse=True)

    def _rank_results(self, results: ConversionResults, source: SchemaLanguage, target: SchemaLanguage) -> None:
        # Ranking is fully automatic, applied in a fixed priority order:
        #   1. accuracy scores for this source -> target task, if available;
        #   2. otherwise per-edge robustness scores (product over the path's
        #      edges; unevaluated edges default to 0.5, ties broken by length);
        #   3. otherwise the naive character-length heuristic.
        if has_accuracy_scores(source.value, target.value):
            rank_with_strategy_accuracy_based(results, source.value, target.value)
        elif has_robustness_scores():
            rank_with_strategy_edge_robustness(results)
        else:
            rank_with_strategy_character_length(results)
