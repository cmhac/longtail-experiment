#!/usr/bin/env bash
set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
DB_USER="${LOCAL_DB_USER:-longtail}"
DB_NAME="${LOCAL_DB_NAME:-longtail_local}"
RESET_INGEST_COMMAND="${SPEC050_RESET_INGEST_COMMAND:-}"

cd "$REPO_ROOT"

run_psql_scalar() {
  local sql="$1"
  docker compose exec -T db psql -U "$DB_USER" -d "$DB_NAME" -At -c "$sql"
}

echo "[spec050] hard cutover reset validation starting"
echo "[spec050] stopping stack"
docker compose down

echo "[spec050] removing volumes for clean baseline"
docker compose down -v

echo "[spec050] starting db and backend"
docker compose up -d db backend

echo "[spec050] waiting for backend health"
for _ in $(seq 1 60); do
  if curl -fsS "http://127.0.0.1:18081/api/health" >/dev/null 2>&1; then
    break
  fi
  sleep 2
done
curl -fsS "http://127.0.0.1:18081/api/health" >/dev/null

reset_started_at="$(date -u +"%Y-%m-%dT%H:%M:%SZ")"
echo "[spec050] reset baseline timestamp: ${reset_started_at}"

if [[ -n "$RESET_INGEST_COMMAND" ]]; then
  echo "[spec050] running custom post-reset ingest command"
  eval "$RESET_INGEST_COMMAND"
else
  echo "[spec050] running default post-reset ingest smoke command"
  uv run --project apps/pipeline pytest --no-cov apps/pipeline/tests/orchestration/test_trend_runtime_processor_notification_events.py
fi

echo "[spec050] verifying post-reset rows in trend/event/notification tables"

canon_total="$(run_psql_scalar "SELECT COUNT(*) FROM trend_canonical_descriptors;")"
canon_old="$(run_psql_scalar "SELECT COUNT(*) FROM trend_canonical_descriptors WHERE created_at < '${reset_started_at}'::timestamptz;")"

events_total="$(run_psql_scalar "SELECT COUNT(*) FROM trend_change_events;")"
events_old="$(run_psql_scalar "SELECT COUNT(*) FROM trend_change_events WHERE emitted_at < '${reset_started_at}'::timestamptz;")"

notif_total="$(run_psql_scalar "SELECT COUNT(*) FROM user_trend_notifications;")"
notif_old="$(run_psql_scalar "SELECT COUNT(*) FROM user_trend_notifications WHERE delivered_at < '${reset_started_at}'::timestamptz;")"

echo "[spec050] trend_canonical_descriptors total=${canon_total} old=${canon_old}"
echo "[spec050] trend_change_events total=${events_total} old=${events_old}"
echo "[spec050] user_trend_notifications total=${notif_total} old=${notif_old}"

if [[ "$canon_old" != "0" ]]; then
  echo "[spec050] ERROR: found pre-reset rows in trend_canonical_descriptors" >&2
  exit 1
fi

if [[ "$events_old" != "0" ]]; then
  echo "[spec050] ERROR: found pre-reset rows in trend_change_events" >&2
  exit 1
fi

if [[ "$notif_old" != "0" ]]; then
  echo "[spec050] ERROR: found pre-reset rows in user_trend_notifications" >&2
  exit 1
fi

echo "[spec050] reset validation passed"
