from schema_conversion_orchestrator.domain.conversion_types import ConversionResults
from schema_conversion_orchestrator.domain.accuracy_scores import (
    has_accuracy_scores,
    lookup_score,
    path_signature,
)
from schema_conversion_orchestrator.domain.edge_robustness import path_robustness

# Accuracy value assigned to a successful path for which no benchmark score
# applies. For a task without a benchmark every path gets this same neutral
# value, so accuracy ties and the next criterion decides. For a task that does
# have a benchmark, a path that was never scored ranks below every scored one.
_NO_ACCURACY = 0.0
_UNSCORED_IN_SCORED_TASK = -1.0


def rank_results(unsorted_results: ConversionResults, source: str, target: str) -> None:
    """Rank conversion results in place by a single fallback chain of criteria.

    The orchestrator does not switch between separate ranking strategies; it
    applies one ordering in which each criterion only breaks ties left open by
    the previous one. For successful attempts, in decreasing priority:

    1. **Benchmark accuracy** for the requested ``source -> target`` task, where
       a benchmark exists. For tasks without a benchmark this criterion is
       neutral (every path shares the same value) and the next one decides; in a
       benchmarked task, a path with no stored score ranks below scored ones.
    2. **Empirical edge quality**: the product of the path's per-edge quality
       values. This is always computable, because edges that were never
       evaluated default to ``0.5``; in the absence of any measurements the
       product therefore shrinks with each additional edge and already favours
       shorter paths.
    3. **Path length**: among paths of equal quality, the shorter one (fewer
       converter edges) is preferred.
    4. **Output length**: among paths of equal length, the larger resulting
       schema is preferred, on the assumption that longer output preserves more
       of the source schema.

    Failed attempts are ranked below all successful ones.
    """
    accuracy_available = has_accuracy_scores(source, target)

    def sort_key(result):
        success, schema_or_error, path, _failed_step_index = result
        if not success:
            return (0, 0.0, 0.0, 0, 0)
        if accuracy_available:
            score = lookup_score(source, target, path_signature(path))
            accuracy = score if score is not None else _UNSCORED_IN_SCORED_TASK
        else:
            accuracy = _NO_ACCURACY
        return (1, accuracy, path_robustness(path), -len(path), len(schema_or_error))

    unsorted_results.sort(key=sort_key, reverse=True)
