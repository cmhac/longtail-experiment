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
STACK_ENV_FILE="${REPO_ROOT}/docker/compose/stack.env"
SECRETS_ENV_FILE="${REPO_ROOT}/docker/compose/local.secrets.env"

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
    metadata_config_missing)
      remediation_hint="Set DAGSTER_METADATA_DB_* vars (host, port, name, user, password), then retry."
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

if [[ -f "$STACK_ENV_FILE" ]]; then
  # shellcheck disable=SC1090
  source "$STACK_ENV_FILE"
fi

if [[ -f "$SECRETS_ENV_FILE" ]]; then
  # shellcheck disable=SC1090
  source "$SECRETS_ENV_FILE"
fi

export DAGSTER_METADATA_DB_HOST="${DAGSTER_METADATA_DB_HOST:-127.0.0.1}"
export DAGSTER_METADATA_DB_PORT="${DAGSTER_METADATA_DB_PORT:-55433}"
export DAGSTER_METADATA_DB_NAME="${DAGSTER_METADATA_DB_NAME:-dagster_local}"
export DAGSTER_METADATA_DB_USER="${DAGSTER_METADATA_DB_USER:-dagster}"

missing_vars=()
for required_var in DAGSTER_METADATA_DB_HOST DAGSTER_METADATA_DB_PORT DAGSTER_METADATA_DB_NAME DAGSTER_METADATA_DB_USER DAGSTER_METADATA_DB_PASSWORD; do
  if [[ -z "${!required_var:-}" ]]; then
    missing_vars+=("${required_var}")
  fi
done

if [[ "${#missing_vars[@]}" -gt 0 ]]; then
  print_failure "metadata_config_missing" "Missing required metadata DB vars: ${missing_vars[*]}"
  exit 1
fi

if ! command -v uv >/dev/null 2>&1; then
  print_failure "prerequisite_missing" "uv is required to launch Dagit locally"
  exit 1
fi

set +e
nohup env \
  DAGSTER_HOME="${LOCAL_DAGSTER_HOME}" \
  DAGSTER_METADATA_ENFORCE="1" \
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
