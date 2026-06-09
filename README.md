# Schema Conversion Orchestrator

Schema Conversion Orchestrator is a Flask-based schema conversion service.
It builds a conversion graph across multiple schema languages and can route
conversions through built-in Python converters, external Java and Node.js
converter packages, and standalone executable tools such as ROBOT.

## Features

- Dynamic conversion graph and multi-hop path discovery
- Python, Java, Node.js, and standalone executable converter integrations
- HTTP API for schema conversion
- Evaluation plots for conversion coverage, robustness, and graph structure
- Unit tests that run without heavy external converter dependencies

## Repository Layout

```text
src/schema_conversion_orchestrator/   Python package
external_converters/                  Java, Node.js, and standalone executable assets
deploy/docker/                        Dockerfile and compose files
requirements/                         Python runtime and test requirements
scripts/                              Build, run, test, and utility scripts
tests/                                Pytest suite and fixtures
eval/                                 Evaluation schemas and generated eval outputs
```

## Setup

Install Python runtime dependencies:

```bash
pip install -r requirements/runtime.txt
```

Install lightweight test dependencies:

```bash
pip install -r requirements/dev.txt
```

## Build External Converters

Build all external converter subpackages:

```bash
scripts/build_subpackages.sh
```

Expected build outputs:

```text
external_converters/java/converter.jar
external_converters/node/dist/index.js
```

## Run Locally

```bash
scripts/run.sh
```

The service listens on `http://localhost:5002`.

Health check:

```bash
curl http://localhost:5002/health
```

## HTTP API

The service exposes a single conversion endpoint.

`POST /convert`

Request body:

```json
{
  "sourceLanguage": "SHACL_TTL",
  "targetLanguage": "JsonSchema",
  "schema": "<schema as a string>",
  "useCache": true
}
```

- `sourceLanguage` / `targetLanguage`: schema language enum values (see
  [Supported Formats](#supported-formats)).
- `schema`: the source schema, passed as a string (a JSON object is also
  accepted and serialized automatically).
- `useCache` (optional, default `true`): reuse cached results of shared
  intermediate sub-paths across the attempted paths.

The orchestrator discovers every feasible conversion path from the source to
the target language, executes them, ranks the results, and returns all
attempts (successful and failed):

```json
{
  "results": [
    {
      "success": true,
      "result": "<converted schema or error message>",
      "failedStepIndex": null,
      "conversionPath": [
        {
          "sourceLanguage": "SHACL_TTL",
          "targetLanguage": "JsonSchema",
          "serviceName": "node",
          "converterName": "shacl-bridge SHACL->JSON Schema",
          "library": "shacl-bridge",
          "libraryVersion": "x.y.z",
          "libraryUrl": "https://www.npmjs.com/package/shacl-bridge"
        }
      ]
    }
  ]
}
```

For a failed attempt, `success` is `false`, `result` carries the error
message, and `failedStepIndex` identifies the converter step that failed.
Each step reports the underlying library, its version, and a URL, so the exact
provenance of every result is traceable.

A ready-made example request is in `scripts/send_test_request.py`.

## Conversion Path Ranking

When several paths connect the source and target language, the returned
attempts are ranked so that the most faithful result surfaces first; failed
attempts are always sorted below successful ones. Two strategies are available:

- **Least character loss** (`LeastCharacterLoss`, default): a fallback that
  prefers the largest successful output, assuming dropped constraints tend to
  shorten a schema.
- **Accuracy-based** (`AccuracyBased`): ranks paths by benchmark-derived accuracy
  scores. Chosen automatically whenever offline scores exist for the requested
  source/target pair (currently the SHACL <-> JSON Schema conversions).

## Test

Run unit tests:

```bash
python3 -m pytest
```

Run a manual conversion request against a running local service:

```bash
python3 scripts/send_test_request.py
```

Run the local Docker integration check:

```bash
scripts/run_local_docker_test.sh --down
```

## Docker

Build and run with compose:

```bash
docker compose -f deploy/docker/docker-compose.yml up -d --build
```

Standalone HTTPS deployment is defined in:

```text
deploy/docker/docker-compose.https.yml
```

The Docker image uses the repo root as build context and
`deploy/docker/Dockerfile` as the Dockerfile.

## Generate Evaluation Plots

```bash
PYTHONPATH=src venv/bin/python eval/plot_orchestrator_evaluation.py
```

Generated files are written to:

```text
eval/results/orchestrator_outputs/plots/
```

## Supported Formats

Currently modeled schema language enum values include:

- `JsonSchema`
- `LinkMl`
- `MdModels`
- `Dtd`
- `Xsd`
- `SHACL_TTL`
- `SHACL_JSON_LD`
- `Owl_TTL`
- `Owl_XML`
- `Owl_OFN`
- `OWL_OBO`
- `OntologyRdf`
- `GraphQL`
- `Protobuf`
- `Shex`
- `Mermaid`
- `SqlAlchemy`

## Add a Converter

Python converters live under:

```text
src/schema_conversion_orchestrator/converters/python/
```

Register Python converters in:

```text
src/schema_conversion_orchestrator/converters/python_registry.py
```

External converter registration lives in:

```text
src/schema_conversion_orchestrator/converters/external_registry.py
```

External converter source/assets live under:

```text
external_converters/
```

## License

This project is licensed under [LICENSE](LICENSE).

Third-party bundled artifact notices are documented in
[THIRD_PARTY_NOTICES.md](THIRD_PARTY_NOTICES.md).
