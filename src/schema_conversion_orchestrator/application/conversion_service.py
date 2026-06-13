from typing import List

from schema_conversion_orchestrator.application.attempt_conversions import attempt_all_conversion_paths
from schema_conversion_orchestrator.converters.base import Converter
from schema_conversion_orchestrator.domain.conversion_graph import build_conversion_graph, find_paths
from schema_conversion_orchestrator.domain.conversion_types import ConversionGraph, ConversionResults
from schema_conversion_orchestrator.domain.ranking import rank_results
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
        # Ranking is fully automatic: a single fallback chain that orders
        # successful attempts by benchmark accuracy (where available), then by
        # empirical edge quality, then by shorter path, then by larger output
        # (see schema_conversion_orchestrator.domain.ranking.rank_results).
        rank_results(results, source.value, target.value)
