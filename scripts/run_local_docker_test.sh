#!/usr/bin/env bash
# Build the schema-converter image, start it via docker-compose.yml, wait until
# it is healthy, then run the black-box integration tests (test_docker_service.py)
# against the running container.
#
# This is the one-command "does the image actually work on my machine?" check.
#
#   scripts/run_local_docker_test.sh           # build, test, leave container running
#   scripts/run_local_docker_test.sh --down    # build, test, then tear the container down
#
# Requires: docker (with compose), python3. No Python deps.

set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
COMPOSE_FILE="$ROOT_DIR/deploy/docker/docker-compose.yml"

PORT="${SCHEMA_CONVERTER_PORT:-5002}"
BASE_URL="http://localhost:${PORT}"
TEARDOWN=0
[ "${1:-}" = "--down" ] && TEARDOWN=1

cleanup() {
  if [ "$TEARDOWN" -eq 1 ]; then
    echo "Tearing down container..."
    docker compose -f "$COMPOSE_FILE" down
  fi
}
trap cleanup EXIT

echo "==> Building and starting schema-converter (port ${PORT})"
docker compose -f "$COMPOSE_FILE" up -d --build

echo "==> Waiting for service to become healthy (first start loads LinkML + discovers converters, up to 3 min)"
healthy=0
for i in $(seq 1 36); do
  if curl -sf "${BASE_URL}/health" >/dev/null 2>&1; then
    echo "    healthy after $((i * 5))s"
    healthy=1
    break
  fi
  echo "    attempt ${i}/36 — retrying in 5s"
  sleep 5
done

if [ "$healthy" -ne 1 ]; then
  echo "Service did not become healthy in time. Recent logs:"
  docker compose -f "$COMPOSE_FILE" logs --tail=80 schema-converter
  exit 1
fi

echo "==> Running integration tests against ${BASE_URL}"
BASE_URL="${BASE_URL}" python3 "$ROOT_DIR/scripts/test_docker_service.py"
