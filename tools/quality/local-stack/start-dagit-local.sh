#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "${SCRIPT_DIR}/../../.." && pwd)"
PID_FILE="${REPO_ROOT}/.tmp/dagit-local.pid"
LOG_FILE="${REPO_ROOT}/.tmp/dagit-local.log"
LOCAL_DAGSTER_HOME="${REPO_ROOT}/.tmp/dagster_home"
PIPELINE_WORKDIR="apps/pipeline"
PIPELINE_PYTHONPATH="${REPO_ROOT}/apps/pipeline"
HOST="${DAGIT_HOST:-127.0.0.1}"
PORT="${DAGIT_PORT:-3001}"
ENDPOINT="http://${HOST}:${PORT}"

print_failure() {
  local code="$1"
  local message="$2"
  local remediation_hint
  case "$code" in
    prerequisite_missing)
      remediation_hint="Confirm uv is installed and run from repository root."
      ;;
    endpoint_unavailable)
      remediation_hint="Check ${LOG_FILE} for startup errors and port conflicts, then retry."
      ;;
    workspace_load_failed)
      remediation_hint="Inspect definitions module loading in apps/pipeline/src/orchestration/definitions.py."
      ;;
    *)
      remediation_hint="Verify local stack prerequisites and rerun startup helper."
      ;;
  esac
  echo "DAGIT_START_STATUS=failure"
  echo "DAGIT_FAILURE_CATEGORY=${code}"
  echo "DAGIT_MESSAGE=${message}"
  echo "DAGIT_REMEDIATION_HINT=${remediation_hint}"
}

if [[ "$PWD" != "$REPO_ROOT" ]]; then
  print_failure "prerequisite_missing" "Run this command from repository root: ${REPO_ROOT}"
  exit 1
fi

if ! command -v uv >/dev/null 2>&1; then
  print_failure "prerequisite_missing" "uv is required to launch Dagit locally"
  exit 1
fi

mkdir -p "${REPO_ROOT}/.tmp" "${LOCAL_DAGSTER_HOME}"

if [[ -f "$PID_FILE" ]]; then
  existing_pid="$(cat "$PID_FILE" 2>/dev/null || true)"
  if [[ -n "$existing_pid" ]] && kill -0 "$existing_pid" 2>/dev/null; then
    echo "DAGIT_START_STATUS=ready"
    echo "DAGIT_ENDPOINT=${ENDPOINT}"
    echo "DAGIT_MESSAGE=Dagit already running (pid=${existing_pid})"
    exit 0
  fi
  rm -f "$PID_FILE"
fi

set +e
nohup env \
  DAGSTER_HOME="${LOCAL_DAGSTER_HOME}" \
  PYTHONPATH="${PIPELINE_PYTHONPATH}${PYTHONPATH:+:${PYTHONPATH}}" \
  uv run --project apps/pipeline dagster dev \
    -d "${PIPELINE_WORKDIR}" \
    -m src.orchestration.definitions \
    --host "$HOST" \
    --port "$PORT" >"$LOG_FILE" 2>&1 &
pid=$!
set -e

echo "$pid" >"$PID_FILE"

if ! kill -0 "$pid" 2>/dev/null; then
  rm -f "$PID_FILE"
  print_failure "partial_environment" "Dagit process failed to start; check ${LOG_FILE}"
  exit 1
fi

for _ in $(seq 1 30); do
  if curl -fsS "$ENDPOINT" >/dev/null 2>&1; then
    echo "DAGIT_START_STATUS=ready"
    echo "DAGIT_ENDPOINT=${ENDPOINT}"
    echo "DAGIT_PID=${pid}"
    echo "DAGIT_MESSAGE=Dagit started successfully"
    exit 0
  fi
  if ! kill -0 "$pid" 2>/dev/null; then
    rm -f "$PID_FILE"
    print_failure "workspace_load_failed" "Dagit exited during startup; check ${LOG_FILE}"
    exit 1
  fi
  sleep 1
done

print_failure "endpoint_unavailable" "Dagit started but endpoint ${ENDPOINT} is not reachable"
exit 1
