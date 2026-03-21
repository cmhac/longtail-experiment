#!/usr/bin/env bash
set -euo pipefail

docker compose up -d
sleep 3
docker compose ps
pipeline_state=$(docker compose ps --format json | grep -c '"Service":"pipeline"' || true)
backend_state=$(docker compose ps --format json | grep -c '"Service":"backend"' || true)
frontend_state=$(docker compose ps --format json | grep -c '"Service":"frontend"' || true)
db_ps_json="$(docker compose ps db --format json || true)"
db_state=$(printf '%s\n' "$db_ps_json" | grep -c '"Service":"db"' || true)
db_healthy=0
for _ in $(seq 1 30); do
  db_ps_json="$(docker compose ps db --format json || true)"
  db_healthy=$(printf '%s\n' "$db_ps_json" | grep -c '"Health":"healthy"' || true)
  if [[ "$db_healthy" -gt 0 ]]; then
    break
  fi
  sleep 1
done
if [[ "$pipeline_state" -eq 0 || "$backend_state" -eq 0 || "$frontend_state" -eq 0 || "$db_state" -eq 0 ]]; then
  echo "Pipeline, backend, frontend, or db service is missing." >&2
  docker compose logs >&2 || true
  docker compose down
  exit 1
fi
if [[ "$db_healthy" -eq 0 ]]; then
  echo "DB service is not healthy." >&2
  docker compose logs >&2 || true
  docker compose down
  exit 1
fi
docker compose down
