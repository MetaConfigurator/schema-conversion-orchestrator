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
  MdModels/
```

Use 3 files per source language for the paper run where possible: one simple, one medium-complexity, and one complex schema.

The source and target languages for the broad paper evaluation are JSON Schema, XSD, SHACL TTL, LinkML, and MdModels. OWL and generated target languages such as GraphQL and Protobuf are intentionally excluded from this system-level matrix because they are not connected enough for the current evaluation corpus.

The local corpus and source provenance are documented in:

```text
eval/real_world_inputs/example_manifest.csv
```

EnzymeML is used as the preferred medium-complexity anchor where a suitable schema exists in the corresponding language.

The corpus is self-contained; the evaluation runner reads the local files and does not dynamically download schemas. If a source schema is refreshed later, update the local file and the corresponding manifest row.

### Source Schema Provenance

The three input schemas per source language (one simple, one medium-complexity, one complex, classified by manual judgement) used in the broad orchestrator evaluation of the accompanying paper originate from the following sources. This table is the authoritative, citable record of the evaluation inputs; the paper refers here instead of listing every URL inline. Where a local adaptation was necessary for the current parsers, it is noted in the last column (see also `real_world_inputs/example_manifest.csv`).

The "Reference" column gives the peer-reviewed paper describing the schema/standard where one exists (the EnzymeML, NMDC, and ThermoML models, and the DCAT-AP specification). The remaining inputs are documentation examples, tutorial schemas, or tooling registries without an associated paper.

| Source language | Tier | Input schema (origin) | Source URL / origin | Local change | Reference |
| --- | --- | --- | --- | --- | --- |
| JSON Schema | simple | Address example (json-schema.org) | https://json-schema.org/learn/miscellaneous-examples#address | local compact baseline | — |
| JSON Schema | medium | EnzymeML v2 data model | https://raw.githubusercontent.com/EnzymeML/enzymeml-specifications/main/schemes/v2/enzymeml-v2.json | none | Lauterbach et al., *Nat. Methods* 20:400–402 (2023), doi:10.1038/s41592-022-01763-1 |
| JSON Schema | complex | GitHub Workflow (SchemaStore) | https://json.schemastore.org/github-workflow.json | none | — |
| XSD | simple | Ship-order (tutorial example) | https://www.w3schools.com/xml/schema_example.asp | local compact baseline | — |
| XSD | medium | EnzymeML v2 data model | https://raw.githubusercontent.com/EnzymeML/enzymeml-specifications/main/schemes/v2/enzymeml-v2.xsd | none | Lauterbach et al., *Nat. Methods* 20:400–402 (2023), doi:10.1038/s41592-022-01763-1 |
| XSD | complex | Apache Maven POM 4.0.0 model | https://maven.apache.org/xsd/maven-4.0.0.xsd | none | — |
| SHACL | simple | W3C property-shape example | https://www.w3.org/TR/shacl/#property-shapes | local compact baseline | — |
| SHACL | medium | EnzymeML v2 shapes graph | https://raw.githubusercontent.com/EnzymeML/enzymeml-specifications/main/schemes/v2/enzymeml-v2.ttl | added missing `md:` prefix so it parses as Turtle | Lauterbach et al., *Nat. Methods* 20:400–402 (2023), doi:10.1038/s41592-022-01763-1 |
| SHACL | complex | DCAT-AP 2.1.1 shapes (SEMIC) | https://raw.githubusercontent.com/SEMICeu/DCAT-AP/master/releases/2.1.1/dcat-ap_2.1.1_shacl_shapes.ttl | none | DCAT-AP specification (Publications Office of the EU); no journal paper |
| LinkML | simple | PersonInfo example | https://raw.githubusercontent.com/linkml/linkml/main/examples/PersonSchema/personinfo.yaml | none | — |
| LinkML | medium | EnzymeML v2 data model | https://raw.githubusercontent.com/EnzymeML/enzymeml-specifications/main/schemes/v2/enzymeml-v2-linkml.yaml | fixed invalid schema `name` (NCName) and removed `is_a` references to external CURIEs (see below) | Lauterbach et al., *Nat. Methods* 20:400–402 (2023), doi:10.1038/s41592-022-01763-1 |
| LinkML | complex | NMDC schema (materialized) | https://raw.githubusercontent.com/microbiomedata/nmdc-schema/main/nmdc_schema/nmdc_materialized_patterns.yaml | none | Eloe-Fadrosh et al., *Nucleic Acids Res.* 50(D1):D828–D836 (2022), doi:10.1093/nar/gkab990 |
| MD-Models | simple | Hello MD-Models example | https://fairchemistry.github.io/md-models/ | copied from the documented Hello MD-Models example | — |
| MD-Models | medium | EnzymeML v2 data model | https://github.com/EnzymeML/enzymeml-specifications/blob/main/specifications/v2.md | removed bold markup from required field names so the current `mdmodels-core` parser accepts the source | Lauterbach et al., *Nat. Methods* 20:400–402 (2023), doi:10.1038/s41592-022-01763-1 |
| MD-Models | complex | ThermoML model | provided locally; ThermoML standard: https://www.nist.gov/mml/acmd/trc/thermoml | source MD-Models file provided locally | Frenkel et al., *J. Chem. Eng. Data* 48(1):2–13 (2003), doi:10.1021/je025645o |

### Data-quality issues discovered during conversion

While running the evaluation we found several issues in real-world source schemas that prevented conversion. They are recorded here because they are findings in their own right (cross-conversion exercises the schemas more thoroughly than single-ecosystem use) and because they explain some of the local adaptations above.

- **EnzymeML, LinkML representation — invalid schema `name` (NCName).** The upstream file (`enzymeml-v2-linkml.yaml`) sets `name: EnzymeML V2`. LinkML requires the schema `name` to be a valid NCName, which may not contain spaces, so LinkML's *own* generators abort at load time with `Not a valid NCName`. This is present in the current upstream file, not introduced by us. Fixed locally to `name: EnzymeML-V2` (the human-readable `title` keeps "EnzymeML V2").
- **EnzymeML, LinkML representation — `is_a` pointing to external ontology terms.** Three classes (`Creator`, `Vessel`, `Protein`) declared both `class_uri:` and `is_a:` set to the same external CURIE (`schema:person`, `OBO:OBI_0400081`, `OBO:PR_000000001`). In LinkML, `is_a` must reference a class defined in the schema (inheritance), whereas the ontology mapping belongs in `class_uri`. The generators therefore fail with `No such class`. Fixed locally by removing the spurious `is_a` lines (keeping `class_uri`). After both fixes, the LinkML generators produce output for this input.
- **EnzymeML, SHACL/Turtle representation — missing prefix.** The upstream Turtle (`enzymeml-v2.ttl`) uses the `md:` prefix without declaring it, so it does not parse as Turtle. Fixed locally by adding `@prefix md: <http://www.enzymeml.org/v2/> .`.
- **EnzymeML, MD-Models representation — bold markup on required fields.** Required field names were wrapped in Markdown bold, which the current `mdmodels-core` parser rejects; removed locally.

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
eval/results/orchestrator_outputs/
  runs/<run_id>/
    review/final_outputs.csv
    review/edge_outputs.csv
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

- `G`: good, valid and practically usable overall; it may still miss minor details.
- `L`: lacking, valid and partially useful but missing important structure or constraints.
- `I`: invalid, failed, syntactically invalid, empty/trivial, wrong target language, or unusable.

The runner pre-fills `I` for failed or automatically invalid outputs. Valid outputs are left blank for inspection.

**What each output is judged against (important):**

- In `final_outputs.csv`, judge the final schema against the **original source schema / the modeling intent** — i.e. the end-to-end usefulness of the orchestrator's result.
- In `edge_outputs.csv`, judge each converter's output against its **direct input only**, given by the `input_step_index` / `input_path` columns (the original source for `step_index == 1`, otherwise the previous step's output). Ask *"given exactly this input, is this converter's direct output a mostly good, partially useful, or unusable target-language representation?"* — **not** how it compares to the original source. This isolates each converter's own fidelity: a converter is graded `G` when it carries its direct input across well enough to be practically useful, even if minor details are imperfect. A converter is graded `L` when the direct output is valid but misses important direct-input structure or constraints. No edge is penalized for information a previous step already lost.

The runs are deterministic, so on a re-run the runner **carries over** existing annotations from `results/orchestrator_outputs/review/*.csv`: you only need to (re-)annotate rows for inputs that changed. New or changed inputs leave their valid outputs blank for re-annotation.

You can annotate in a local browser UI instead of editing the CSVs directly:

```bash
PYTHONPATH=src python3 eval/annotate_outputs.py
```

The page shows the full final-output or edge-output table. Clicking a row opens
the relevant input and produced output side by side, with a `G`/`L`/`I` status
dropdown and a notes field. The `Next`, `Back`, and `Table` buttons support
sequential review and returning to the full table.

#### Re-annotating after a converter changed

Carry-over keys on the input and the conversion path, not on converter behaviour, so if a *converter* (rather than the input data) changed, its carried-over annotations may be stale (e.g. a path that used to fail now produces output, or vice versa). To force re-annotation of every path/edge that uses a given converter, pass `--reset-converter` (repeatable; matched as a substring of the converter name / path signature):

```bash
PYTHONPATH=src venv/bin/python eval/evaluate.py \
  --reset-converter shacl-bridge --reset-converter Jsonix
```

The runner reports how many final and edge annotations it dropped; those rows revert to the default (`I` for invalid output, blank for valid output needing a fresh judgement).

`final_outputs.csv` is used for the orchestrator-level matrix. Only the best-ranked path per `(source_language, target_language, input_file)` is counted there.

`edge_outputs.csv` is used for the edge-colored graph. It evaluates each converter edge on its own immediate output, judged against that edge's direct input (`input_path`) — not on downstream path success, and not against the original source schema.

### Plot

After annotation:

```bash
PYTHONPATH=src venv/bin/python eval/plot_orchestrator_evaluation.py
```

Generated plots:

```text
eval/results/orchestrator_outputs/plots/orchestrator_result_matrix.png
eval/results/orchestrator_outputs/plots/edge_robustness_matrix.png
eval/results/orchestrator_outputs/plots/conversion_graph_edge_robustness.png
eval/results/orchestrator_outputs/plots/conversion_graph_all_languages.png
eval/results/orchestrator_outputs/plots/graphical_abstract_conversion_graph.png
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

`conversion_graph_all_languages.png` shows the complete registered conversion graph with neutral edge coloring. It is topology-only, because the broad evaluation does not cover every registered language.

## Accuracy-Based Ranking Benchmarks

These benchmarks evaluate SHACL `->` JSON Schema and JSON Schema `->` SHACL paths against ground-truth test suites. Their per-path scores are persisted to `src/schema_conversion_orchestrator/data/accuracy_scores.json` for runtime ranking and copied to `eval/results/accuracy_scores.json` with the other generated evaluation results.

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
eval/results/benchmarks/benchmark_results_<task>.csv
eval/results/benchmarks/benchmark_accuracy_<task>.png
eval/results/accuracy_scores.json
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
PYTHONPATH=src python3 eval/cache_timing_analysis.py --output eval/results/cache_timing_results.csv
```

Generated outputs:

```text
eval/results/cache_timing_results.csv
eval/results/cache_timing_results.json
```

## Notes

- The broad orchestrator evaluation runs converters in-process and does not require the Flask service to be running.
- The accuracy benchmark and cache timing workflows use the HTTP API and do require the service.
- The broad orchestrator evaluation is intended for the paper's overall system evaluation.
- The SHACL/JSON accuracy benchmarks are intended for ranking and conversion-quality evaluation.
