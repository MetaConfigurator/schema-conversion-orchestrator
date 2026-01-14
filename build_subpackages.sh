#!/bin/bash

# Build the Java Package
echo "Building Java package..."
mvn -f schema-conversion-orchestrator/external_converters/java/pom.xml clean package

# Build the TypeScript Package
echo "Building TypeScript package..."
npm --prefix schema-conversion-orchestrator/external_converters/node install
npm --prefix schema-conversion-orchestrator/external_converters/node run build