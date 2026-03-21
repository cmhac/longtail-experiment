#!/usr/bin/env bash
set -euo pipefail

docker compose up -d
sleep 3
docker compose ps
backend_state=$(docker compose ps --format json | grep -c '"Service":"backend"' || true)
frontend_state=$(docker compose ps --format json | grep -c '"Service":"frontend"' || true)
if [[ "$backend_state" -eq 0 || "$frontend_state" -eq 0 ]]; then
  echo "Backend or frontend service is missing." >&2
  docker compose logs >&2 || true
  docker compose down
  exit 1
fi
docker compose down
