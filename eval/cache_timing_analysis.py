"""Measure the runtime benefit of sub-path caching during benchmark evaluation.

The script runs the registered conversion benchmarks once with the orchestrator's
per-request sub-path cache enabled and once with it disabled, then reports the
absolute timings and percentage speed-up, together with the hardware and software
environment the measurement ran on.

Prerequisites: the orchestrator must be running locally (default
http://localhost:5002). The script passes ``useCache`` in each /convert request,
so it exercises the same HTTP interface used by normal evaluations.

Usage:

    python eval/cache_timing_analysis.py
    python eval/cache_timing_analysis.py "SHACL_TTL -> JsonSchema"
    python eval/cache_timing_analysis.py --output eval/results/cache_timing_results.csv
"""
from __future__ import annotations

import argparse
import json
import os
import platform
import subprocess
import sys
import time
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Iterable

import pandas as pd

EVAL_DIR = Path(__file__).resolve().parent
REPO_ROOT = EVAL_DIR.parent
RESULTS_DIR = EVAL_DIR / "results"
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


def collect_hardware() -> dict:
    """Record the hardware and software environment of the timing run."""
    info: dict = {
        "os": f"{platform.system()} {platform.release()}",
        "machine": platform.machine(),
        "python": platform.python_version(),
        "timestamp": time.strftime("%Y-%m-%dT%H:%M:%S%z"),
    }
    if sys.platform == "darwin":

        def _sysctl(key: str) -> str | None:
            try:
                return subprocess.check_output(["sysctl", "-n", key], text=True).strip()
            except (subprocess.CalledProcessError, OSError):
                return None

        info["model"] = _sysctl("hw.model")
        info["chip"] = _sysctl("machdep.cpu.brand_string")
        memsize = _sysctl("hw.memsize")
        if memsize:
            info["memory_gb"] = round(int(memsize) / 1024**3, 1)
    else:
        info["chip"] = platform.processor() or None
        try:
            info["memory_gb"] = round(
                os.sysconf("SC_PAGE_SIZE") * os.sysconf("SC_PHYS_PAGES") / 1024**3, 1
            )
        except (ValueError, OSError, AttributeError):
            pass
    return info


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


def write_outputs(results: list[TimingResult], output_csv: Path, hardware: dict) -> None:
    output_csv.parent.mkdir(parents=True, exist_ok=True)
    rows = [asdict(result) for result in results]
    pd.DataFrame(rows).to_csv(output_csv, index=False)

    output_json = output_csv.with_suffix(".json")
    output_json.write_text(json.dumps({"hardware": hardware, "results": rows}, indent=2) + "\n")

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
        default=RESULTS_DIR / "cache_timing_results.csv",
        help="CSV output path. A JSON file with the same stem is written too.",
    )
    args = parser.parse_args()

    benchmarks = resolve_tasks(args.tasks)
    hardware = collect_hardware()
    print(f"Environment: {hardware}")
    print(f"Timing benchmarks: {[benchmark.task_name for benchmark in benchmarks]}")
    results = [measure_task(benchmark) for benchmark in benchmarks]
    write_outputs(results, args.output, hardware)


if __name__ == "__main__":
    main()
