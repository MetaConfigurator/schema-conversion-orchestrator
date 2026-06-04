"""Conversion benchmarks for the orchestrator's accuracy-based ranking.

Importing this package registers all concrete benchmarks. Add new conversion
paths by creating a module here that defines and registers a
:class:`~benchmarks.base.ConversionBenchmark`, then import it below.
"""
from .base import (  # noqa: F401
    BenchmarkCase,
    ConversionBenchmark,
    available_benchmarks,
    get_benchmark,
    register,
)

# Register concrete benchmarks (import for side effect of @register).
from . import shacl_to_json_schema  # noqa: E402,F401
from . import json_schema_to_shacl  # noqa: E402,F401
