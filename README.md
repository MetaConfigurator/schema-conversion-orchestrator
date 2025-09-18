# 😍 Universal Schema Converter

This project provides a schema conversion platform that supports converting between various data modeling formats (like JSON Schema, LinkML, XSD, DTD, RDF, etc.) using a microservice-based architecture. It consists of:

* 🐍 A central **Flask Orchestrator** (main API + smart pathfinding + schema feature matching)
* ☕ A **Java Spring Boot** microservice (dummy schema converter)
* 🪦 A **Node.js TypeScript** microservice (dummy schema converter)

---

## 📁 Folder Structure

```
schema-converter/
│
├── flask-backend/          # Central orchestrator with REST API and real converters
│   ├── main.py
│   └── ...
│
├── java-converter/         # Java Spring Boot dummy converter
│   ├── Dockerfile
│   └── ...
│
├── node-converter/         # Node.js TypeScript dummy converter
│   ├── Dockerfile
│   ├── package.json
│   ├── tsconfig.json
│   └── src/
│       └── index.ts
│
├── test_clients.py         # Script to register converters and trigger a conversion
│
├── docker-compose.yml      # Spins up all services together
│
└── README.md               # This file
```

---

## 🚀 Features

* Auto-register schema converters (via REST)
* Builds a dynamic conversion graph
* Smartly selects the best conversion path based on schema features
* Supports recursive multi-step conversions (e.g. JSONSchema → LinkML → RDF)
* Easily extendable: add new converters in any language via Docker/microservices

---

## 🔧 Setup and Run

### 1. Clone the repo

```bash
git clone https://github.com/Logende/universal-schema-converter.git
cd universal-schema-converter
```

### 2. Build and start with Docker

```bash
docker-compose up --build
```

This will:

* Start the Flask orchestrator on `http://localhost:5000`
* Start the Java Spring Boot dummy converter on `http://localhost:8080`
* Start the Node.js TypeScript converter on `http://localhost:3001`

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

1. Create a service that exposes a `POST /convert` endpoint.
2. Register it with the orchestrator via `/registerConversion`.
3. Done! The orchestrator will use your converter automatically when needed.

---

## 📜 License

MIT License — feel free to use, contribute, and share.


## ToDOs

- Use ZooKeeper for Service Registry