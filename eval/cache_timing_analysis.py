"""Measure the runtime benefit of sub-path caching during benchmark evaluation.

The script runs the registered conversion benchmarks once with the orchestrator's
per-request sub-path cache enabled and once with it disabled, then reports the
absolute timings and percentage speed-up.

Prerequisites: the orchestrator must be running locally (default
http://localhost:5002). The script passes ``useCache`` in each /convert request,
so it exercises the same HTTP interface used by normal evaluations.

Usage:

    python eval/cache_timing_analysis.py
    python eval/cache_timing_analysis.py "SHACL_TTL -> JsonSchema"
    python eval/cache_timing_analysis.py --output eval/cache_timing_results.csv
"""
from __future__ import annotations

import argparse
import json
import sys
import time
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Iterable

import pandas as pd

EVAL_DIR = Path(__file__).resolve().parent
REPO_ROOT = EVAL_DIR.parent
sys.path.insert(0, str(EVAL_DIR))
sys.path.insert(0, str(REPO_ROOT / "src"))

from benchmark_runner import aggregate, run_one  # noqa: E402
from benchmarks import ConversionBenchmark, available_benchmarks, get_benchmark  # noqa: E402


@dataclass
class TimingResult:
    task: str
    cache_enabled_seconds: float
    cache_disabled_seconds: float
    absolute_saved_seconds: float
    speedup_percent: float
    cache_enabled_rows: int
    cache_disabled_rows: int
    cache_enabled_cases: int
    cache_disabled_cases: int


def timed_run(benchmark: ConversionBenchmark, use_cache: bool) -> tuple[float, pd.DataFrame]:
    start = time.perf_counter()
    df = run_one(benchmark, use_cache=use_cache)
    if not df.empty:
        # Include aggregation cost so the measured run corresponds to a full
        # accuracy evaluation, except for writing result files and plots.
        aggregate(df, benchmark)
    return time.perf_counter() - start, df


def measure_task(benchmark: ConversionBenchmark) -> TimingResult:
    print(f"\n=== Timing {benchmark.task_name} ===")

    cached_seconds, cached_df = timed_run(benchmark, use_cache=True)
    uncached_seconds, uncached_df = timed_run(benchmark, use_cache=False)

    saved_seconds = uncached_seconds - cached_seconds
    speedup_percent = (
        (saved_seconds / uncached_seconds) * 100.0
        if uncached_seconds > 0
        else 0.0
    )

    result = TimingResult(
        task=benchmark.task_name,
        cache_enabled_seconds=round(cached_seconds, 4),
        cache_disabled_seconds=round(uncached_seconds, 4),
        absolute_saved_seconds=round(saved_seconds, 4),
        speedup_percent=round(speedup_percent, 2),
        cache_enabled_rows=int(len(cached_df)),
        cache_disabled_rows=int(len(uncached_df)),
        cache_enabled_cases=int(cached_df["name"].nunique()) if not cached_df.empty else 0,
        cache_disabled_cases=int(uncached_df["name"].nunique()) if not uncached_df.empty else 0,
    )

    print(
        f"  cache enabled : {result.cache_enabled_seconds:.4f}s "
        f"({result.cache_enabled_cases} cases)"
    )
    print(
        f"  cache disabled: {result.cache_disabled_seconds:.4f}s "
        f"({result.cache_disabled_cases} cases)"
    )
    print(
        f"  saved         : {result.absolute_saved_seconds:.4f}s "
        f"({result.speedup_percent:.2f}%)"
    )
    return result


def write_outputs(results: list[TimingResult], output_csv: Path) -> None:
    output_csv.parent.mkdir(parents=True, exist_ok=True)
    rows = [asdict(result) for result in results]
    pd.DataFrame(rows).to_csv(output_csv, index=False)

    output_json = output_csv.with_suffix(".json")
    output_json.write_text(json.dumps(rows, indent=2) + "\n")

    print(f"\nTiming CSV  -> {output_csv}")
    print(f"Timing JSON -> {output_json}")


def resolve_tasks(requested: Iterable[str]) -> list[ConversionBenchmark]:
    task_names = list(requested) or list(available_benchmarks())
    if not task_names:
        raise SystemExit("No benchmarks registered.")
    return [get_benchmark(task_name) for task_name in task_names]


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Run benchmark timing once with caching and once without caching."
    )
    parser.add_argument(
        "tasks",
        nargs="*",
        help="Benchmark task names. Defaults to all registered benchmarks.",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=EVAL_DIR / "cache_timing_results.csv",
        help="CSV output path. A JSON file with the same stem is written too.",
    )
    args = parser.parse_args()

    benchmarks = resolve_tasks(args.tasks)
    print(f"Timing benchmarks: {[benchmark.task_name for benchmark in benchmarks]}")
    results = [measure_task(benchmark) for benchmark in benchmarks]
    write_outputs(results, args.output)


if __name__ == "__main__":
    main()
