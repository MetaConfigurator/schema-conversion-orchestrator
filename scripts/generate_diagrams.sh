#!/bin/bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

PYTHONPATH="$ROOT_DIR/src" python3 -m schema_conversion_orchestrator.reporting.generate_diagrams
