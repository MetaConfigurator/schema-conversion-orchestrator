from schema_conversion_orchestrator.domain.conversion_types import ConversionResults
from schema_conversion_orchestrator.domain.accuracy_scores import lookup_score, path_signature
from schema_conversion_orchestrator.domain.edge_robustness import path_robustness


def rank_with_strategy_character_length(unsorted_results: ConversionResults):
    """ Always tries all paths and then ranks the results by character length (descending order)."""
    # sort all attempts by success by length of resulting schema (descending), which is second prop in tuple
    unsorted_results.sort(key=lambda x: (x[0], len(x[1]) if x[0] else 0), reverse=True)


def rank_with_strategy_accuracy_based(unsorted_results: ConversionResults, source: str, target: str) -> None:
    """Rank results by benchmark-derived conversion accuracy (descending).

    Successful attempts are ranked first by their path's benchmark score for this
    source -> target task, then by resulting schema length as a tie-breaker.
    Failures (and paths without a benchmark score) are sorted to the bottom.
    Falls back to character length for any successful path that has no stored
    score for this task.
    """
    def sort_key(result):
        success, schema_or_error, path, _failed_step_index = result
        if not success:
            return (0, -1.0, 0)
        score = lookup_score(source, target, path_signature(path))
        # No score for this path -> rank just above failures, ordered by length.
        score = score if score is not None else -0.5
        return (1, score, len(schema_or_error))

    unsorted_results.sort(key=sort_key, reverse=True)


def rank_with_strategy_edge_robustness(unsorted_results: ConversionResults) -> None:
    """Rank results by per-edge robustness (descending).

    Each successful path is scored by the product of its edges' robustness
    values (derived from the broad orchestrator evaluation; edges without a
    stored score default to 0.5). Paths with a higher robustness product are
    ranked first; ties are broken by resulting schema length (the naive
    character-length heuristic). Failures are sorted to the bottom.
    """
    def sort_key(result):
        success, schema_or_error, path, _failed_step_index = result
        if not success:
            return (0, -1.0, 0)
        return (1, path_robustness(path), len(schema_or_error))

    unsorted_results.sort(key=sort_key, reverse=True)
