from typing import List

from schema_conversion_orchestrator.application.attempt_conversions import attempt_all_conversion_paths
from schema_conversion_orchestrator.converters.base import Converter
from schema_conversion_orchestrator.domain.conversion_graph import build_conversion_graph, find_paths
from schema_conversion_orchestrator.domain.conversion_types import ConversionGraph, ConversionResults
from schema_conversion_orchestrator.domain.feature_scores import has_benchmark
from schema_conversion_orchestrator.domain.ranking import (
    RankingStrategy,
    rank_with_strategy_feature_based,
    rank_with_strategy_least_character_loss,
)
from schema_conversion_orchestrator.domain.schema_types import SchemaLanguage


class NoConversionPathError(ValueError):
    """Raised when no converter path exists between two schema languages."""


class ConversionService:
    def __init__(
        self,
        converters: List[Converter],
        ranking_strategy: RankingStrategy = RankingStrategy.LeastCharacterLoss,
    ) -> None:
        self.converters = converters
        self.ranking_strategy = ranking_strategy
        self.conversion_graph: ConversionGraph = build_conversion_graph(converters)

    def convert(self, source: SchemaLanguage, target: SchemaLanguage, schema: str) -> ConversionResults:
        paths = find_paths(source, target, self.conversion_graph)
        if not paths:
            raise NoConversionPathError(
                f"No path found for conversion from source {source} to target {target}."
            )

        results = attempt_all_conversion_paths(source, target, schema, paths)
        self._rank_results(results, source, target)
        return sorted(results, key=lambda x: x[0], reverse=True)

    def _rank_results(self, results: ConversionResults, source: SchemaLanguage, target: SchemaLanguage) -> None:
        # Prefer the benchmark-based ranking whenever offline feature scores
        # exist for this source -> target task; otherwise fall back to the
        # configured (naive) strategy.
        if has_benchmark(source.value, target.value):
            rank_with_strategy_feature_based(results, source.value, target.value)
            return

        if self.ranking_strategy == RankingStrategy.LeastCharacterLoss:
            rank_with_strategy_least_character_loss(results)
            return

        if self.ranking_strategy == RankingStrategy.FeatureBased:
            rank_with_strategy_feature_based(results, source.value, target.value)
            return

        raise ValueError(f"Unknown conversion strategy: {self.ranking_strategy}")
