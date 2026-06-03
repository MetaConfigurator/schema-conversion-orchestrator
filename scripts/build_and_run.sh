#!/bin/bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

# Build the whole project
echo "Building the project..."
"$ROOT_DIR/scripts/build.sh"

# Run the conversion service
echo "Running the conversion service..."
"$ROOT_DIR/scripts/run.sh"
