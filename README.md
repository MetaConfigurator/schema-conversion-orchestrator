# Schema Conversion Orchestrator

Schema Conversion Orchestrator is a Flask-based schema conversion service.
It builds a conversion graph across multiple schema languages and can route
conversions through built-in Python converters plus external Java, Node.js, and
ROBOT converter subprocesses.

## Features

- Dynamic conversion graph and multi-hop path discovery
- Python, Java, Node.js, and ROBOT-based converters
- HTTP API for schema conversion
- Diagram/report generation for available conversion paths
- Unit tests that run without heavy external converter dependencies

## Repository Layout

```text
src/schema_conversion_orchestrator/   Python package
external_converters/                  Java, Node.js, and ROBOT converter assets
deploy/docker/                        Dockerfile and compose files
requirements/                         Python runtime and test requirements
scripts/                              Build, run, test, and utility scripts
tests/                                Pytest suite and fixtures
eval/                                 Evaluation schemas and generated eval outputs
artifacts/                            Ignored generated diagrams/reports
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

## Generate Diagrams

```bash
scripts/generate_diagrams.sh
```

Generated files are written to ignored artifact directories:

```text
artifacts/diagrams/core/
artifacts/diagrams/full/
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
