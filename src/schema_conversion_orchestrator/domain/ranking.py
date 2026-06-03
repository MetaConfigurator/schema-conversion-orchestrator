try:
    from enum import StrEnum
except ImportError:
    from strenum import StrEnum

from schema_conversion_orchestrator.domain.conversion_types import ConversionResults


class RankingStrategy(StrEnum):
    LeastCharacterLoss = "LeastCharacterLoss"


def rank_with_strategy_least_character_loss(unsorted_results: ConversionResults):
    """ Always tries all paths and then ranks the results by character length (descending order)."""
    # sort all attempts by success by length of resulting schema (descending), which is second prop in tuple
    unsorted_results.sort(key=lambda x: (x[0], len(x[1]) if x[0] else 0), reverse=True)
