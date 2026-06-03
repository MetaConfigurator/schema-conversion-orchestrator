"""Generic offline evaluation runner for orchestrator conversion benchmarks.

This runner is independent of any specific source/target languages or metrics.
For each registered :class:`ConversionBenchmark` (see ``eval/benchmarks/``) it:

  1. loads the benchmark's test cases,
  2. sends each source schema to a locally running orchestrator targeting the
     benchmark's target language,
  3. scores every returned conversion path with the benchmark's ``compare``,
  4. aggregates the scores per path (mean over all cases; failed/missing
     outputs count as zero), and
  5. persists the per-path scores (consumed by the orchestrator's feature-based
     ranking), a per-case CSV, and an accuracy plot.

Usage::

    python benchmark_runner.py                      # run all registered benchmarks
    python benchmark_runner.py "SHACL_TTL -> JsonSchema"   # run one benchmark

Prerequisites: the orchestrator must be running locally (default
http://localhost:5002), and any data a benchmark needs (e.g. a cloned
shacl-bridge repo) must be available.
"""
import json
import sys
from pathlib import Path
from typing import Dict, List

import matplotlib.pyplot as plt
import pandas as pd
import requests

EVAL_DIR = Path(__file__).resolve().parent
REPO_ROOT = EVAL_DIR.parent
sys.path.insert(0, str(EVAL_DIR))
sys.path.insert(0, str(REPO_ROOT / "src"))

from schema_conversion_orchestrator.domain.feature_scores import (  # noqa: E402
    DEFAULT_SCORES_PATH,
    path_signature_from_steps,
    task_key,
)

from benchmarks import ConversionBenchmark, available_benchmarks, get_benchmark  # noqa: E402

import os  # noqa: E402

SERVER_URL = os.environ.get("ORCHESTRATOR_URL", "http://localhost:5002/convert")


def request_conversion(source: str, target: str, schema: str) -> List[dict] | None:
    payload = {"sourceLanguage": source, "targetLanguage": target, "schema": schema}
    resp = requests.post(SERVER_URL, json=payload, timeout=120)
    if resp.status_code != 200:
        print(f"  request error {resp.status_code}: {resp.text[:200]}")
        return None
    return resp.json().get("results", [])


def run_one(benchmark: ConversionBenchmark) -> pd.DataFrame:
    """Run a single benchmark, returning a per-(case, path) results DataFrame."""
    cases = benchmark.load_cases()
    print(f"\n=== {benchmark.task_name}: {len(cases)} cases ===")
    rows = []
    for i, case in enumerate(cases, 1):
        print(f"[{i}/{len(cases)}] {case.name}")
        results = request_conversion(benchmark.source_language, benchmark.target_language,
                                     case.source_schema)
        if results is None:
            continue
        for attempt in results:
            steps = [(s["sourceLanguage"], s["targetLanguage"], s["converterName"])
                     for s in attempt["conversionPath"]]
            signature = path_signature_from_steps(steps)
            success = bool(attempt.get("success"))
            metrics = (benchmark.compare(case.expected, attempt.get("result"))
                       if success else benchmark.zero_metrics)
            rows.append({"name": case.name, "category": case.category,
                         "signature": signature, "success": success, **metrics})
    return pd.DataFrame(rows)


def aggregate(df: pd.DataFrame, benchmark: ConversionBenchmark) -> Dict[str, dict]:
    """Per-path mean of each metric over all cases (missing cases count as 0)."""
    n_cases = df["name"].nunique()
    path_scores: Dict[str, dict] = {}
    for signature, group in df.groupby("signature"):
        entry = {m: round(group[m].sum() / n_cases, 4) for m in benchmark.metric_names}
        entry["score"] = entry[benchmark.primary_metric]
        entry["cases"] = n_cases
        entry["successes"] = int(group["success"].sum())
        path_scores[signature] = entry
    return path_scores


def short_label(signature: str) -> str:
    return " -> ".join(step.split(":")[-1] for step in signature.split(" -> "))


def persist_scores(task: str, path_scores: Dict[str, dict]) -> None:
    DEFAULT_SCORES_PATH.parent.mkdir(parents=True, exist_ok=True)
    existing = {}
    if DEFAULT_SCORES_PATH.exists():
        try:
            existing = json.loads(DEFAULT_SCORES_PATH.read_text())
        except json.JSONDecodeError:
            existing = {}
    existing[task] = path_scores
    DEFAULT_SCORES_PATH.write_text(json.dumps(existing, indent=2) + "\n")
    print(f"  scores -> {DEFAULT_SCORES_PATH}")


def plot(df: pd.DataFrame, path_scores: Dict[str, dict], benchmark: ConversionBenchmark,
         output_path: Path) -> None:
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(15, 6))
    metrics = benchmark.metric_names
    # Curate which paths appear in the report (ranking still uses all of them).
    reported = {s: v for s, v in path_scores.items() if benchmark.is_reported(short_label(s))}
    path_scores = reported or path_scores
    labels = [short_label(s) for s in path_scores]
    x = range(len(labels))
    width = 0.8 / max(len(metrics), 1)
    for k, m in enumerate(metrics):
        offset = (k - (len(metrics) - 1) / 2) * width
        ax1.bar([i + offset for i in x], [path_scores[s][m] for s in path_scores], width, label=m)
    ax1.set_xticks(list(x))
    ax1.set_xticklabels(labels, rotation=30, ha="right", fontsize=8)
    ax1.set_ylim(0, 1)
    ax1.set_ylabel("Mean score over benchmark")
    ax1.set_title(f"{benchmark.task_name}: accuracy per conversion path")
    ax1.legend()

    best_sig = max(path_scores, key=lambda s: path_scores[s]["score"]) if path_scores else None
    if best_sig is not None:
        best = df[df["signature"] == best_sig]
        cat_means = best.groupby("category")[benchmark.primary_metric].mean().sort_values()
        ax2.barh(cat_means.index, cat_means.values, color="#2a9d8f")
        ax2.set_xlim(0, 1)
        ax2.set_xlabel(f"Mean {benchmark.primary_metric}")
        ax2.set_title(f"Best path ({short_label(best_sig)}) by category")

    plt.tight_layout()
    plt.savefig(output_path, dpi=150)
    print(f"  plot   -> {output_path}")


def slug(task: str) -> str:
    return task.replace(" -> ", "_to_").replace(" ", "")


def run_benchmark(benchmark: ConversionBenchmark) -> None:
    df = run_one(benchmark)
    if df.empty:
        print(f"  no results for {benchmark.task_name} (is the orchestrator running at {SERVER_URL}?)")
        return
    path_scores = aggregate(df, benchmark)

    print(f"\nPer-path mean scores for {benchmark.task_name} (over {df['name'].nunique()} cases):")
    for sig, s in sorted(path_scores.items(), key=lambda kv: kv[1]["score"], reverse=True):
        metric_str = " ".join(f"{m}={s[m]:.3f}" for m in benchmark.metric_names)
        print(f"  {metric_str} successes={s['successes']}/{s['cases']}  {short_label(sig)}")

    out_slug = slug(benchmark.task_name)
    df.to_csv(EVAL_DIR / f"benchmark_results_{out_slug}.csv", index=False)
    print(f"  csv    -> {EVAL_DIR / f'benchmark_results_{out_slug}.csv'}")
    persist_scores(task_key(benchmark.source_language, benchmark.target_language), path_scores)
    plot(df, path_scores, benchmark, EVAL_DIR / f"benchmark_accuracy_{out_slug}.png")


def main() -> None:
    requested = sys.argv[1:]
    tasks = requested if requested else list(available_benchmarks())
    if not tasks:
        sys.exit("No benchmarks registered.")
    print(f"Running benchmarks: {tasks}")
    for task in tasks:
        run_benchmark(get_benchmark(task))


if __name__ == "__main__":
    main()
