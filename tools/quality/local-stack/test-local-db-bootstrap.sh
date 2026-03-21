#!/usr/bin/env bash
set -euo pipefail

docker compose up -d db
ps_json="$(docker compose ps db --format json || true)"
db_present=$(printf '%s\n' "$ps_json" | grep -c '"Service":"db"' || true)
db_healthy=0

for _ in $(seq 1 30); do
  ps_json="$(docker compose ps db --format json || true)"
  db_healthy=$(printf '%s\n' "$ps_json" | grep -c '"Health":"healthy"' || true)
  if [[ "$db_healthy" -gt 0 ]]; then
    break
  fi
  sleep 1
done

if [[ "$db_present" -eq 0 || "$db_healthy" -eq 0 ]]; then
  echo "Local DB bootstrap verification failed." >&2
  docker compose logs db >&2 || true
  docker compose down
  exit 1
fi

docker compose down
