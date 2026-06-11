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

The conversion graph is built from converter registrations at service startup, so a new converter participates in path finding, execution, and ranking as soon as it is registered. No other part of the service needs to change. There are two integration routes: internal Python converters and external sub-process converters (Node.js, Java, or any standalone executable).

### Internal Python converter

1. **Add the dependency.** Add the underlying library to `requirements/runtime.txt`.
2. **Implement the converter.** Create a module under `src/schema_conversion_orchestrator/converters/python/` with a subclass of `ConverterInternal` (from `converters/base.py`). Declare the source and target language and the library metadata in `__init__`, and implement `converter_logic` (plus `validate_input` / `validate_output`, which may simply return `True`):

   ```python
   from schema_conversion_orchestrator.converters.base import ConverterInternal, get_package_version
   from schema_conversion_orchestrator.domain.schema_types import SchemaLanguage


   class ConverterMyLibrary(ConverterInternal):
       def __init__(self) -> None:
           super().__init__(
               name="my-library",
               service_address="internal",
               service_name="FlaskApp",
               source_language=SchemaLanguage.JsonSchema,
               target_language=SchemaLanguage.SHACL_TTL,
               library="my-library",
               library_version=get_package_version("my-library"),
               library_url="https://github.com/example/my-library",
           )

       def converter_logic(self, schema: str) -> str:
           ...  # call the library, return the converted schema as a string

       def validate_input(self, schema: str) -> bool:
           return True

       def validate_output(self, schema: str) -> bool:
           return True
   ```

   The `library`, `library_version`, and `library_url` values are what the API reports as per-step provenance, so fill them in accurately. `get_package_version` reads the installed package version, keeping the reported version in sync with the environment.
3. **Register it.** Add an instance to the list returned by `register_python_converters()` in `src/schema_conversion_orchestrator/converters/python_registry.py`.

### External converter (Node.js)

Node converters are auto-discovered: at startup the Python service runs `node external_converters/node/dist/index.js list` and registers every converter the bundle reports, so no Python code changes are needed.

1. **Add the dependency.** Add the npm package to `external_converters/node/package.json` and run `npm install` in that directory.
2. **Implement the converter.** Create `external_converters/node/src/converters/<name>.ts` exporting a `Converter` object (see `dataStructures.ts` for the interface):

   ```typescript
   import {Converter, SchemaLanguage} from "../dataStructures.js";

   export const converter: Converter = {
     name: "my-converter",
     sourceLanguage: SchemaLanguage.Xsd,
     targetLanguage: SchemaLanguage.JsonSchema,
     library: "my-npm-package",          // resolvable package name; its version is read from package.json
     libraryUrl: "https://www.npmjs.com/package/my-npm-package",

     async convert(schema: string): Promise<string> {
       ...  // call the library, return the converted schema as a string
     }
   };

   export default converter;
   ```

   Every file in `src/converters/` is loaded automatically; there is no separate Node-side registry.
3. **Build.** Run `npm run build` in `external_converters/node/`.

### External converter (Java or standalone executable)

Java converters live in `external_converters/java/` and are discovered the same way (the service runs `java -jar converter.jar list` at startup). Standalone executables that cannot report their own converters, such as ROBOT, are instead registered explicitly as `ConverterExternalGeneric` instances in `src/schema_conversion_orchestrator/converters/external_registry.py`, which specifies the command to run, the source and target languages, file suffixes, and the library metadata.

### Add a schema language

Add a value to the `SchemaLanguage` enum in `src/schema_conversion_orchestrator/domain/schema_types.py` (and, if Node converters use it, to the `SchemaLanguage` enum in `external_converters/node/src/dataStructures.ts`). The language appears as a node in the conversion graph as soon as a registered converter consumes or produces it.

### Verify

Start the service (`scripts/run.sh`) and check the startup log: every registered converter is printed there, and a `POST /convert` request for the new language pair exercises the new edge. Add a test in `tests/` (see `tests/test_logic.py` for converter-level examples). Optionally, add benchmark inputs and ground truths under `eval/benchmarks/` so the new conversion participates in accuracy-based ranking (see `eval/README.md`).

## License

This project is licensed under [LICENSE](LICENSE).

Third-party bundled artifact notices are documented in
[THIRD_PARTY_NOTICES.md](THIRD_PARTY_NOTICES.md).
