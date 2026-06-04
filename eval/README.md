# Evaluation Workflows

This directory contains three separate evaluation workflows:

1. Broad orchestrator evaluation over real-world schemas.
2. SHACL/JSON Schema accuracy benchmarks used for accuracy-based ranking.
3. Cache timing analysis for the benchmark runner.

Run commands from the repository root unless stated otherwise.

## Broad Orchestrator Evaluation

This evaluation measures the Schema Conversion Orchestrator as a system. For each real-world input schema, it tries every paper-evaluation target language and every discovered conversion path. It stores final outputs, intermediate step outputs, path metadata, and review CSVs for human annotation.

### Input Corpus

Place real-world schemas in:

```text
eval/real_world_inputs/
  JsonSchema/
  Xsd/
  SHACL_TTL/
  LinkMl/
```

Use 3 files per source language for the paper run where possible: one simple, one medium-complexity, and one complex schema. The current broad evaluation deliberately excludes OWL to keep the manual inspection effort manageable.

The source languages are JSON Schema, XSD, SHACL TTL, and LinkML. The target languages are JSON Schema, XSD, SHACL TTL, LinkML, GraphQL, and Protobuf.

The local corpus and source provenance are documented in:

```text
eval/real_world_inputs/example_manifest.csv
```

EnzymeML is used as the preferred medium-complexity anchor where a suitable schema exists in the corresponding language.

The corpus is self-contained; the evaluation runner reads the local files and does not dynamically download schemas. If a source schema is refreshed later, update the local file and the corresponding manifest row.

### Run

```bash
PYTHONPATH=src venv/bin/python eval/evaluate.py
```

By default this uses only the core schema languages. To include all registered converters/languages:

```bash
PYTHONPATH=src venv/bin/python eval/evaluate.py --full-graph
```

Outputs are written to:

```text
eval/orchestrator_outputs/
  runs/<run_id>/
  review/final_outputs.csv
  review/edge_outputs.csv
  latest_run.txt
```

Each path attempt stores:

```text
metadata.json
final_output.<ext> or error.txt
steps/step_01_output.<ext>
steps/step_02_output.<ext>
...
```

### Human Annotation

Fill the `status` column in both review CSV files:

- `G`: good, valid and practically usable.
- `L`: lacking, valid and partially useful but missing important structure or constraints.
- `I`: invalid, failed, syntactically invalid, empty/trivial, wrong target language, or unusable.

The runner pre-fills `I` for failed or automatically invalid outputs. Valid outputs are left blank for inspection.

`final_outputs.csv` is used for the orchestrator-level matrix. Only the best-ranked path per `(source_language, target_language, input_file)` is counted there.

`edge_outputs.csv` is used for the edge-colored graph. It evaluates each converter edge on its own immediate output, not on downstream path success.

### Plot

After annotation:

```bash
PYTHONPATH=src venv/bin/python eval/plot_orchestrator_evaluation.py
```

Generated plots:

```text
eval/orchestrator_outputs/plots/orchestrator_result_matrix.png
eval/orchestrator_outputs/plots/conversion_graph_edge_quality.png
```

The matrix cell format is:

```text
4P
2G 2L 1I
```

`4P` is the number of discovered paths for that source-target pair. `2G 2L 1I` summarizes the best-ranked orchestrator result over the input files.

The matrix uses the same red-yellow-green quality scale as the edge graph, but based on the orchestrator's best-ranked final output per input:

```text
(G + 0.5L) / total
```

The edge graph labels each edge with a short library name and colors it by:

```text
(G + 0.5L) / total
```

using only edge-local annotations from `edge_outputs.csv`.

## Accuracy-Based Ranking Benchmarks

These benchmarks evaluate SHACL `->` JSON Schema and JSON Schema `->` SHACL paths against ground-truth test suites. Their per-path scores are persisted to `src/schema_conversion_orchestrator/data/accuracy_scores.json` and used by the orchestrator's accuracy-based ranking strategy.

The orchestrator service must be running locally:

```bash
scripts/run.sh
```

In another terminal, run all registered benchmarks:

```bash
PYTHONPATH=src python3 eval/benchmark_runner.py
```

Run one benchmark:

```bash
PYTHONPATH=src python3 eval/benchmark_runner.py "SHACL_TTL -> JsonSchema"
PYTHONPATH=src python3 eval/benchmark_runner.py "JsonSchema -> SHACL_TTL"
```

Useful environment variable:

```bash
ORCHESTRATOR_URL=http://localhost:5002/convert
```

Generated outputs:

```text
eval/benchmark_results_<task>.csv
eval/benchmark_accuracy_<task>.png
src/schema_conversion_orchestrator/data/accuracy_scores.json
```

The benchmark definitions live in:

```text
eval/benchmarks/
```

The comparison utilities are:

```text
eval/compare_json_schemas.py
eval/compare_shacl.py
```

## Cache Timing Analysis

This measures full benchmark runtime once with request-level sub-path caching enabled and once with caching disabled.

The orchestrator service must be running locally:

```bash
scripts/run.sh
```

Run all timing tasks:

```bash
PYTHONPATH=src python3 eval/cache_timing_analysis.py
```

Run one timing task:

```bash
PYTHONPATH=src python3 eval/cache_timing_analysis.py "SHACL_TTL -> JsonSchema"
```

Choose an output path:

```bash
PYTHONPATH=src python3 eval/cache_timing_analysis.py --output eval/cache_timing_results.csv
```

Generated outputs:

```text
eval/cache_timing_results.csv
eval/cache_timing_results.json
```

## Notes

- The broad orchestrator evaluation runs converters in-process and does not require the Flask service to be running.
- The accuracy benchmark and cache timing workflows use the HTTP API and do require the service.
- The broad orchestrator evaluation is intended for the paper's overall system evaluation.
- The SHACL/JSON accuracy benchmarks are intended for ranking and conversion-quality evaluation.
