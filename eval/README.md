# Evaluation Workflows

Three independent workflows live here:

1. Broad orchestrator evaluation over real-world schemas.
2. SHACL/JSON Schema accuracy benchmarks (used for accuracy-based ranking).
3. Cache timing analysis.

Run everything from the repository root.

## Broad orchestrator evaluation

This measures the orchestrator as a whole system. For every input schema it tries each evaluated target language and every discovered path, then stores the final outputs, the intermediate step outputs, the path metadata, and review CSVs for annotation.

### Input corpus

Drop real-world schemas under:

```text
eval/real_world_inputs/{JsonSchema,Xsd,SHACL_TTL,LinkMl,MdModels}/
```

Aim for three files per source language: one simple, one medium, one complex. The evaluated languages are JSON Schema, XSD, SHACL TTL, LinkML, and MD-Models; OWL and the generated targets (GraphQL, Protobuf, and so on) are left out of this matrix because the corpus does not connect them well enough. Where a language has an EnzymeML version, it is used as the medium-complexity anchor.

The corpus is self-contained: the runner reads local files and downloads nothing. If you refresh a source schema, update the local file and its row in `real_world_inputs/example_manifest.csv`.

### Source schema provenance

The inputs and any local adaptations are listed below. This table is the citable record the paper points to instead of repeating every URL inline. The "Reference" column names the peer-reviewed paper for the schema or standard where one exists; the rest are documentation examples, tutorials, or tooling registries.

| Source language | Tier | Input schema (origin) | Source URL / origin | Local change | Reference |
| --- | --- | --- | --- | --- | --- |
| JSON Schema | simple | Address example (json-schema.org) | https://json-schema.org/learn/miscellaneous-examples#address | local compact baseline | none |
| JSON Schema | medium | EnzymeML v2 data model | https://raw.githubusercontent.com/EnzymeML/enzymeml-specifications/main/schemes/v2/enzymeml-v2.json | none | Lauterbach et al., *Nat. Methods* 20:400–402 (2023), doi:10.1038/s41592-022-01763-1 |
| JSON Schema | complex | GitHub Workflow (SchemaStore) | https://json.schemastore.org/github-workflow.json | none | none |
| XSD | simple | Ship-order (tutorial example) | https://www.w3schools.com/xml/schema_example.asp | local compact baseline | none |
| XSD | medium | EnzymeML v2 data model | https://raw.githubusercontent.com/EnzymeML/enzymeml-specifications/main/schemes/v2/enzymeml-v2.xsd | none | Lauterbach et al., *Nat. Methods* 20:400–402 (2023), doi:10.1038/s41592-022-01763-1 |
| XSD | complex | Apache Maven POM 4.0.0 model | https://maven.apache.org/xsd/maven-4.0.0.xsd | none | none |
| SHACL | simple | W3C property-shape example | https://www.w3.org/TR/shacl/#property-shapes | local compact baseline | none |
| SHACL | medium | EnzymeML v2 shapes graph | https://raw.githubusercontent.com/EnzymeML/enzymeml-specifications/main/schemes/v2/enzymeml-v2.ttl | added missing `md:` prefix so it parses as Turtle | Lauterbach et al., *Nat. Methods* 20:400–402 (2023), doi:10.1038/s41592-022-01763-1 |
| SHACL | complex | DCAT-AP 2.1.1 shapes (SEMIC) | https://raw.githubusercontent.com/SEMICeu/DCAT-AP/master/releases/2.1.1/dcat-ap_2.1.1_shacl_shapes.ttl | none | DCAT-AP specification (Publications Office of the EU); no journal paper |
| LinkML | simple | PersonInfo example | https://raw.githubusercontent.com/linkml/linkml/main/examples/PersonSchema/personinfo.yaml | none | none |
| LinkML | medium | EnzymeML v2 data model | https://raw.githubusercontent.com/EnzymeML/enzymeml-specifications/main/schemes/v2/enzymeml-v2-linkml.yaml | fixed invalid schema `name` (NCName) and removed `is_a` references to external CURIEs (see below) | Lauterbach et al., *Nat. Methods* 20:400–402 (2023), doi:10.1038/s41592-022-01763-1 |
| LinkML | complex | NMDC schema (materialized) | https://raw.githubusercontent.com/microbiomedata/nmdc-schema/main/nmdc_schema/nmdc_materialized_patterns.yaml | none | Eloe-Fadrosh et al., *Nucleic Acids Res.* 50(D1):D828–D836 (2022), doi:10.1093/nar/gkab990 |
| MD-Models | simple | Hello MD-Models example | https://fairchemistry.github.io/md-models/ | copied from the documented Hello MD-Models example | none |
| MD-Models | medium | EnzymeML v2 data model | https://github.com/EnzymeML/enzymeml-specifications/blob/main/specifications/v2.md | removed bold markup from required field names so the current `mdmodels-core` parser accepts the source | Lauterbach et al., *Nat. Methods* 20:400–402 (2023), doi:10.1038/s41592-022-01763-1 |
| MD-Models | complex | ThermoML model | provided locally; ThermoML standard: https://www.nist.gov/mml/acmd/trc/thermoml | source MD-Models file provided locally | Frenkel et al., *J. Chem. Eng. Data* 48(1):2–13 (2003), doi:10.1021/je025645o |

### Data-quality issues found during conversion

Running the same models through several ecosystems surfaced bugs in otherwise valid-looking source schemas. They are worth recording in their own right (cross-conversion exercises a schema far harder than single-ecosystem use), and they explain some of the local adaptations above.

- **EnzymeML, LinkML: invalid schema `name`.** The upstream `enzymeml-v2-linkml.yaml` sets `name: EnzymeML V2`, but a LinkML schema `name` must be a valid NCName (no spaces), so LinkML's own generators abort with `Not a valid NCName`. Fixed locally to `EnzymeML-V2`; the `title` still reads "EnzymeML V2".
- **EnzymeML, LinkML: `is_a` pointing at external terms.** `Creator`, `Vessel`, and `Protein` set both `class_uri` and `is_a` to the same external CURIE. In LinkML `is_a` must reference a class defined in the schema, so the generators fail with `No such class`. Fixed by dropping the `is_a` lines and keeping `class_uri`.
- **EnzymeML, SHACL/Turtle: missing prefix.** `enzymeml-v2.ttl` uses the `md:` prefix without declaring it, so it does not parse as Turtle. Fixed by adding `@prefix md: <http://www.enzymeml.org/v2/> .`.
- **EnzymeML, MD-Models: bold on required fields.** Required field names were wrapped in Markdown bold, which the current `mdmodels-core` parser rejects. Removed locally.

### Run

```bash
PYTHONPATH=src venv/bin/python eval/evaluate.py                 # core languages only
PYTHONPATH=src venv/bin/python eval/evaluate.py --full-graph    # all registered converters
```

Outputs go to `eval/results/orchestrator_outputs/`: the per-run `runs/<run_id>/...`, plus the top-level `review/final_outputs.csv` and `review/edge_outputs.csv`. Each attempt keeps its `metadata.json`, a `final_output.<ext>` (or `error.txt`), and per-step outputs under `steps/`.

### Annotation

The `status` column in `final_outputs.csv` is filled in two passes: a coding agent (Claude Code running Claude Sonnet 4.6) performs the first annotation pass following [ANNOTATION_INSTRUCTIONS.md](ANNOTATION_INSTRUCTIONS.md), and a human then reviews every label with the interactive viewer below. Disagreements are usually corrected directly in review; where they reveal an unclear criterion, the instructions are refined and the agent is re-run on the affected rows.

The labels:

- `G` good: valid and practically usable; minor gaps are fine.
- `L` lacking: valid but missing important structure or constraints.
- `I` invalid: failed, malformed, empty, wrong target language, or unusable.

The runner pre-fills `I` for failed or automatically invalid outputs and leaves valid ones blank.

What to compare each output against:

- `final_outputs.csv`: judge the final schema against the original source and modeling intent, i.e. the end-to-end usefulness of the orchestrator's result.
- `edge_outputs.csv`: deprecated optional diagnostic table for intermediate-step annotations. It is not used by the default paper-facing edge reliability scores because the intermediate rows are much more expensive to annotate and depend on upstream converter outputs.

Runs are deterministic, so a re-run carries over existing annotations from `results/orchestrator_outputs/review/*.csv`; only new or changed rows come back blank.

You can annotate in a browser instead of editing the CSVs:

```bash
PYTHONPATH=src python3 eval/annotate_outputs.py
```

It shows the input and produced output side by side with a `G`/`L`/`I` dropdown and a notes field, plus `Next`, `Back`, and `Table` navigation.

#### After a converter changes

Carry-over keys on the input and the path, not on converter behaviour, so a changed converter can leave stale annotations (a path that used to fail might now produce output). Force re-annotation of every path and edge that uses a converter with `--reset-converter` (repeatable, matched as a substring of the converter name or path signature):

```bash
PYTHONPATH=src venv/bin/python eval/evaluate.py \
  --reset-converter shacl-bridge --reset-converter xsd2jsonschema
```

Dropped rows revert to the default: `I` for invalid output, blank for valid output that needs a fresh judgement.

`final_outputs.csv` drives both the orchestrator-level matrix and the default edge reliability scores. The matrix counts only the best-ranked path per source/target/input. Edge reliability is estimated from direct one-step rows in `final_outputs.csv`, where the path has exactly one converter and the final output is therefore that converter's direct output on a real source-language schema. Edge scores separate syntactic robustness from quality: robustness is the fraction of reviewed direct outputs with automatically valid output; quality is `(G + 0.5L) / total` over those automatically valid direct outputs; reliability is `robustness * quality` and is used for edge coloring. The orchestrator ranks paths by the product of edge quality scores (syntactic failures are already known at ranking time and sort last, so only the expected quality of successful output matters).

Intermediate-step annotations in `edge_outputs.csv` are still supported for diagnostics with `eval/plot_orchestrator_evaluation.py --edge-score-source intermediate-edge`, but this mode is deprecated and is not used for the paper figures by default.

### Plot

```bash
PYTHONPATH=src venv/bin/python eval/plot_orchestrator_evaluation.py
```

Plots are written to `eval/results/orchestrator_outputs/plots/`:

```text
orchestrator_result_matrix.png
edge_robustness_matrix.png
conversion_graph_edge_robustness.png
conversion_graph_all_languages.png
graphical_abstract_conversion_graph.png
```

A matrix cell reads:

```text
4P
2G 2L 1I
```

`4P` is the number of discovered paths for the source-target pair; `2G 2L 1I` summarises the best-ranked result over the input files. The orchestrator matrix uses the red-yellow-green scale `(G + 0.5L) / total` over best-ranked final outputs. The edge graph colors direct converter edges by combined reliability (`robustness * quality`) from one-step final outputs and labels evaluated edges with both components (`R` for syntactic robustness, `Q` for conditional quality). `conversion_graph_all_languages.png` shows the full registered graph with neutral edges (topology only, since the broad evaluation does not cover every language).

## Accuracy benchmarks

These score SHACL `->` JSON Schema and JSON Schema `->` SHACL paths against ground-truth test suites. The per-path scores are written to `src/schema_conversion_orchestrator/data/accuracy_scores.json` for runtime ranking and mirrored to `eval/results/accuracy_scores.json`.

Start the service, then run the benchmarks:

```bash
scripts/run.sh
PYTHONPATH=src python3 eval/benchmark_runner.py                       # all
PYTHONPATH=src python3 eval/benchmark_runner.py "SHACL_TTL -> JsonSchema"
PYTHONPATH=src python3 eval/benchmark_runner.py "JsonSchema -> SHACL_TTL"
```

Override the endpoint with `ORCHESTRATOR_URL=http://localhost:5002/convert`.

Outputs: `eval/results/benchmarks/benchmark_results_<task>.csv` and `benchmark_accuracy_<task>.png`, plus the two `accuracy_scores.json` files. Benchmark definitions are in `eval/benchmarks/`; the comparison helpers are `eval/compare_json_schemas.py` and `eval/compare_shacl.py`.

## Cache timing

This times a full benchmark run with request-level sub-path caching on and off. The service must be running:

```bash
scripts/run.sh
PYTHONPATH=src python3 eval/cache_timing_analysis.py                  # all tasks
PYTHONPATH=src python3 eval/cache_timing_analysis.py "SHACL_TTL -> JsonSchema"
```

Outputs: `eval/results/cache_timing_results.csv` and `.json` (override the path with `--output`).

## Notes

- The broad evaluation runs converters in-process and does not need the Flask service.
- The accuracy benchmarks and cache timing use the HTTP API, so they do.
