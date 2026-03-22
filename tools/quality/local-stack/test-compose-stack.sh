#!/usr/bin/env bash
set -euo pipefail

docker compose up -d
sleep 3
docker compose ps
pipeline_state=$(docker compose ps --format json | grep -c '"Service":"pipeline"' || true)
backend_state=$(docker compose ps --format json | grep -c '"Service":"backend"' || true)
frontend_state=$(docker compose ps --format json | grep -c '"Service":"frontend"' || true)
dagit_state=$(docker compose ps --format json | grep -c '"Service":"dagit"' || true)
db_ps_json="$(docker compose ps db --format json || true)"
db_state=$(printf '%s\n' "$db_ps_json" | grep -c '"Service":"db"' || true)
db_healthy=0
dagit_healthy=0
health_wait_seconds="${LOCAL_STACK_HEALTH_WAIT_SECONDS:-240}"
last_report_second=0
for _ in $(seq 1 "$health_wait_seconds"); do
  elapsed_seconds=$((last_report_second + 1))
  db_ps_json="$(docker compose ps db --format json || true)"
  db_healthy=$(printf '%s\n' "$db_ps_json" | grep -c '"Health":"healthy"' || true)
  dagit_ps_json="$(docker compose ps dagit --format json || true)"
  dagit_healthy=$(printf '%s\n' "$dagit_ps_json" | grep -c '"Health":"healthy"' || true)
  if [[ "$db_healthy" -gt 0 && "$dagit_healthy" -gt 0 ]]; then
    echo "Local stack health checks passed after ${elapsed_seconds}s."
    break
  fi
  if (( elapsed_seconds == 1 || elapsed_seconds % 15 == 0 )); then
    dagit_status="$(printf '%s\n' "$dagit_ps_json" | grep -o '"Status":"[^"]*"' | head -n 1 | cut -d '"' -f 4 || true)"
    if [[ -z "$dagit_status" ]]; then
      dagit_status="starting"
    fi
    echo "Waiting for health: elapsed=${elapsed_seconds}s/${health_wait_seconds}s db_healthy=${db_healthy} dagit_healthy=${dagit_healthy} dagit_status=${dagit_status}"
  fi
  last_report_second="$elapsed_seconds"
  sleep 1
done
if [[ "$pipeline_state" -eq 0 || "$backend_state" -eq 0 || "$frontend_state" -eq 0 || "$dagit_state" -eq 0 || "$db_state" -eq 0 ]]; then
  echo "Pipeline, backend, frontend, dagit, or db service is missing." >&2
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
if [[ "$dagit_healthy" -eq 0 ]]; then
  echo "Dagit service is not healthy." >&2
  echo "Timed out after ${health_wait_seconds}s waiting for Dagit health." >&2
  echo "Recent Dagit logs:" >&2
  docker compose logs dagit >&2 || true
  docker compose down
  exit 1
fi

if [[ "${VERIFY_DAGIT_ENDPOINT:-0}" == "1" ]]; then
  dagit_port="${DAGIT_PORT:-3001}"
  DAGIT_ENDPOINT="http://127.0.0.1:${dagit_port}" bash tools/quality/local-stack/test-dagit-endpoint.sh
fi

docker compose down
