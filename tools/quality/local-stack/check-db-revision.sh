#!/usr/bin/env bash
set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../../.." && pwd)"
ENV_FILE="$REPO_ROOT/docker/compose/stack.env"
ALEMBIC_INI="$REPO_ROOT/libs/db/alembic.ini"

if [[ ! -f "$ENV_FILE" ]]; then
  echo "Missing env file: $ENV_FILE" >&2
  exit 1
fi

set -a
source "$ENV_FILE"
set +a

: "${LOCAL_DB_HOST:?LOCAL_DB_HOST is required}"
: "${LOCAL_DB_PORT:?LOCAL_DB_PORT is required}"
: "${LOCAL_DB_NAME:?LOCAL_DB_NAME is required}"
: "${LOCAL_DB_USER:?LOCAL_DB_USER is required}"
: "${LOCAL_DB_PASSWORD:?LOCAL_DB_PASSWORD is required}"

DB_URL="postgresql+psycopg://${LOCAL_DB_USER}:${LOCAL_DB_PASSWORD}@${LOCAL_DB_HOST}:${LOCAL_DB_PORT}/${LOCAL_DB_NAME}"
EXPECTED_REVISION="${EXPECTED_DB_REVISION:-0008_dataset_discovery_indexes}"

cd "$REPO_ROOT"

db_ps_json="$(docker compose ps db --format json || true)"
if [[ "$(printf '%s\n' "$db_ps_json" | grep -c '"Service":"db"' || true)" -eq 0 ]]; then
  docker compose up -d db
fi

db_healthy=0
for _ in $(seq 1 30); do
  db_ps_json="$(docker compose ps db --format json || true)"
  db_healthy=$(printf '%s\n' "$db_ps_json" | grep -c '"Health":"healthy"' || true)
  if [[ "$db_healthy" -gt 0 ]]; then
    break
  fi
  sleep 1
done

if [[ "$db_healthy" -eq 0 ]]; then
  echo "DB service is not healthy; cannot verify revision." >&2
  docker compose logs db >&2 || true
  exit 1
fi

if ! current_output="$(
  PYTHONPATH="$REPO_ROOT/libs/db/src" \
  ALEMBIC_CONFIG="$ALEMBIC_INI" \
  DATABASE_URL="$DB_URL" \
  uv run --project apps/backend alembic -c "$ALEMBIC_INI" current
)"; then
  echo "Unable to read current Alembic revision for local DB." >&2
  exit 1
fi

current_revision="$(printf '%s\n' "$current_output" | awk '/^[0-9][0-9A-Za-z_]+/ {print $1}' | tail -n 1)"

if [[ -z "$current_revision" ]]; then
  echo "Could not parse current revision from Alembic output:" >&2
  printf '%s\n' "$current_output" >&2
  exit 1
fi

if [[ "$current_revision" != "$EXPECTED_REVISION" ]]; then
  echo "Revision mismatch: expected '$EXPECTED_REVISION' but got '$current_revision'." >&2
  printf '%s\n' "$current_output" >&2
  exit 1
fi

echo "Revision OK: $current_revision"
