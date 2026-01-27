from strenum import StrEnum

from converter import (ConversionResults)


class RankingStrategy(StrEnum):
    LeastCharacterLoss = "LeastCharacterLoss"


def rank_with_strategy_least_character_loss(unsorted_results: ConversionResults):
    """ Always tries all paths and then ranks the results by character length (descending order).
    Does not stop at success but explores all paths. Trivial feature loss strategy which is character based.
    Much less effort than a proper feature loss analysis and still effective."""
    # sort all attempts by success: success first. Then by length of resulting schema (descending)
    unsorted_results.sort(key=lambda x: (not x[0], -len(x[1]) if x[0] else float('inf')))

