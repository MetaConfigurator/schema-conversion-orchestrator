#!/bin/bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

# Build sub-packages
echo "Building sub-packages..."
"$ROOT_DIR/scripts/build_subpackages.sh"

# Build the main application
echo "Installing main application dependencies..."
pip install -r "$ROOT_DIR/requirements/runtime.txt"
