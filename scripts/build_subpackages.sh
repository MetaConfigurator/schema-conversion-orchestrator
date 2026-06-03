#!/bin/bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

# Build the Java Package
echo "Building Java package..."
mvn -f "$ROOT_DIR/external_converters/java/pom.xml" clean package

# Build the TypeScript Package
echo "Building TypeScript package..."
npm --prefix "$ROOT_DIR/external_converters/node" install
npm --prefix "$ROOT_DIR/external_converters/node" run build
