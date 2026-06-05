"""Generic interface for orchestrator conversion benchmarks.

A *benchmark* defines everything needed to evaluate one source -> target
conversion task: the set of test cases (a source schema plus its expected
ground-truth target schema) and a comparison function that scores a produced
output against the ground truth, returning one or more metrics.

The generic runner (``eval/benchmark_runner.py``) is agnostic to the concrete
languages and metrics: it asks a benchmark for its cases, sends each source
schema through the orchestrator, scores every returned conversion path with the
benchmark's :meth:`ConversionBenchmark.compare`, aggregates per path, and
persists the per-path scores used for the orchestrator's accuracy-based ranking.

To support a new conversion path, implement a :class:`ConversionBenchmark`
subclass (defining ``source_language``, ``target_language``, :meth:`load_cases`,
and :meth:`compare`) and register it with :func:`register`.
"""
from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any, Callable, Dict, List


@dataclass
class BenchmarkCase:
    """One test case: a source schema and its expected target ground truth."""
    name: str
    source_schema: str
    expected: Any  # ground truth, in whatever form the benchmark's compare() expects
    category: str = "default"


class ConversionBenchmark(ABC):
    """Definition of a benchmark for one source -> target conversion task.

    Subclasses fix the languages, provide the test cases, and implement the
    comparison metric(s). Everything else (calling the orchestrator, scoring
    paths, aggregating, persisting, plotting) is handled generically by the
    runner.
    """

    #: Backend language identifiers (must match the orchestrator's SchemaLanguage values).
    source_language: str
    target_language: str

    #: Metric used to rank paths (must be one of the keys returned by compare()).
    primary_metric: str = "f1"

    #: Substrings of path labels to exclude from the *reported* output (tables /
    #: plots) to keep the presentation focused on the most relevant paths, e.g.
    #: redundant or always-failing paths. Ranking still uses all paths.
    report_exclude: List[str] = []

    #: Optional ``substring -> short label`` overrides for plots/tables. If a
    #: path's signature contains one of the substrings, the mapped label is used
    #: instead of the (often very long) auto-generated converter-chain label.
    label_overrides: Dict[str, str] = {}

    def is_reported(self, label: str) -> bool:
        """Whether a path (by its short label) should appear in tables/plots."""
        return not any(excl in label for excl in self.report_exclude)

    def report_label(self, signature: str, default_label: str) -> str:
        """Short, human-readable label for a path signature in plots/tables."""
        for substring, label in self.label_overrides.items():
            if substring in signature:
                return label
        return default_label

    @abstractmethod
    def load_cases(self) -> List[BenchmarkCase]:
        """Return all test cases for this benchmark."""

    @abstractmethod
    def compare(self, expected: Any, predicted_text: str) -> Dict[str, float]:
        """Score a produced output (raw string) against the expected ground truth.

        Returns a dict of metric name -> value in ``[0, 1]``. Must always return
        the same set of keys (including :attr:`primary_metric`); on a malformed
        or unusable output, return zeros for every metric rather than raising.
        """

    @property
    def task_name(self) -> str:
        return f"{self.source_language} -> {self.target_language}"

    @property
    def metric_names(self) -> List[str]:
        """Metric names this benchmark reports.

        Defaults to just :attr:`primary_metric`; a subclass that returns more
        metrics from :meth:`compare` should override this (a plain class
        attribute list is sufficient) to list them all.
        """
        return [self.primary_metric]

    @property
    def zero_metrics(self) -> Dict[str, float]:
        """Metrics dict of all-zeros (used for failed / unparseable attempts)."""
        return {m: 0.0 for m in self.metric_names}


# ---------------------------------------------------------------------------
# Registry
# ---------------------------------------------------------------------------

_REGISTRY: Dict[str, Callable[[], ConversionBenchmark]] = {}


def register(factory: Callable[[], ConversionBenchmark]) -> Callable[[], ConversionBenchmark]:
    """Register a benchmark factory (decorator). Keyed by its task name."""
    instance = factory()
    _REGISTRY[instance.task_name] = factory
    return factory


def available_benchmarks() -> Dict[str, Callable[[], ConversionBenchmark]]:
    return dict(_REGISTRY)


def get_benchmark(task_name: str) -> ConversionBenchmark:
    if task_name not in _REGISTRY:
        raise KeyError(f"No benchmark registered for task '{task_name}'. "
                       f"Available: {list(_REGISTRY)}")
    return _REGISTRY[task_name]()
