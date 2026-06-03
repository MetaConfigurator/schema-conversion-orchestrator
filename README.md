# Schema Conversion Orchestrator

This project provides a schema conversion platform that supports converting between various data modeling formats (like JSON Schema, LinkML, XSD, DTD, RDF, etc.) using a software architecture that supports different programming languages due to subprocess calling. It consists of:

* 🐍 A central **Flask Orchestrator** (main API + smart pathfinding + schema feature matching + converters in Python)
* ☕ **Java** converters
* 🪦 **Node.js TypeScript** converters


## Features

* Builds a dynamic conversion graph
* Smartly selects the best conversion path based on schema features
* Supports recursive multi-step conversions (e.g. JSONSchema → LinkML → RDF)
* Easily extendable: add new converters in any language

---

## 🔧 Setup and Run

### 1. Clone the repo

```bash
git clone https://github.com/Logende/schema-conversion-orchestrator.git
cd universal-schema-converter
```

### 2. Build the sub-packages

#### Java

```bash
mvn -f external_converters/java/pom.xml clean package
```

Result: `target/converter.jar`

#### Node

```bash
npm --prefix external_converters/node install
npm --prefix external_converters/node run build
```

Result: `dist/index.js`

### 3. Build and Run the Orchestrator

```bash
pip install -r requirements/runtime.txt
PYTHONPATH=src python3 -m schema_conversion_orchestrator.app
```

From the repository root, use:

```bash
scripts/build.sh
scripts/run.sh
```

### 3. Test the System

Run the included client test script:

```bash
python3 test_clients.py
```

This will:

* Register multiple converters with the orchestrator
* Request a full conversion from JSON Schema to RDF
* Print the converted result

---

## 🪩 Supported Formats (Enum)

* `JsonSchema`
* `LinkMl`
* `MdModels`
* `Xsd`
* `Dtd`
* `OntologyRdf`

## 🧮 Supported Features (Enum)

* `Comments`
* `Hierarchy`
* `References`
* `Conditions`
* `Constraints`
* `Properties`
* `Attributes`
* `Composition`
* `Negation`

---

## 🔌 Add Your Own Converter

TODO

## TODO

If a path fails due to a certain edge, remove all paths which include this edge as an optimization.

---

## 📜 License

MIT License — feel free to use, contribute, and share.

Third-party dependency and bundled converter notices are documented in
[THIRD_PARTY_NOTICES.md](THIRD_PARTY_NOTICES.md).
