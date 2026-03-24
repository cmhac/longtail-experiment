#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "${SCRIPT_DIR}/../../.." && pwd)"
STACK_ENV_FILE="${REPO_ROOT}/docker/compose/stack.env"
SECRETS_ENV_FILE="${REPO_ROOT}/docker/compose/local.secrets.env"

HOST="${DAGIT_HOST:-127.0.0.1}"
PORT="${DAGIT_PORT:-3001}"
ENDPOINT="${DAGIT_ENDPOINT:-http://${HOST}:${PORT}}"
RETRIES="${DAGIT_ENDPOINT_RETRIES:-20}"
DELAY_SECONDS="${DAGIT_ENDPOINT_DELAY_SECONDS:-1}"
VERIFY_WORKSPACE="${DAGIT_VERIFY_WORKSPACE:-1}"
MIN_LOCATION_ENTRIES="${DAGIT_MIN_LOCATION_ENTRIES:-1}"

# Preserve caller-provided metadata vars (including explicit empty values) so
# sourced env files do not override fail-fast test inputs.
CALLER_SET_METADATA_HOST="${DAGSTER_METADATA_DB_HOST+x}"
CALLER_SET_METADATA_PORT="${DAGSTER_METADATA_DB_PORT+x}"
CALLER_SET_METADATA_NAME="${DAGSTER_METADATA_DB_NAME+x}"
CALLER_SET_METADATA_USER="${DAGSTER_METADATA_DB_USER+x}"
CALLER_SET_METADATA_PASSWORD="${DAGSTER_METADATA_DB_PASSWORD+x}"
CALLER_METADATA_HOST="${DAGSTER_METADATA_DB_HOST-}"
CALLER_METADATA_PORT="${DAGSTER_METADATA_DB_PORT-}"
CALLER_METADATA_NAME="${DAGSTER_METADATA_DB_NAME-}"
CALLER_METADATA_USER="${DAGSTER_METADATA_DB_USER-}"
CALLER_METADATA_PASSWORD="${DAGSTER_METADATA_DB_PASSWORD-}"

if [[ -f "$STACK_ENV_FILE" ]]; then
  # shellcheck disable=SC1090
  source "$STACK_ENV_FILE"
fi

if [[ -f "$SECRETS_ENV_FILE" ]]; then
  # shellcheck disable=SC1090
  source "$SECRETS_ENV_FILE"
fi

if [[ -n "$CALLER_SET_METADATA_HOST" ]]; then
  export DAGSTER_METADATA_DB_HOST="$CALLER_METADATA_HOST"
fi
if [[ -n "$CALLER_SET_METADATA_PORT" ]]; then
  export DAGSTER_METADATA_DB_PORT="$CALLER_METADATA_PORT"
fi
if [[ -n "$CALLER_SET_METADATA_NAME" ]]; then
  export DAGSTER_METADATA_DB_NAME="$CALLER_METADATA_NAME"
fi
if [[ -n "$CALLER_SET_METADATA_USER" ]]; then
  export DAGSTER_METADATA_DB_USER="$CALLER_METADATA_USER"
fi
if [[ -n "$CALLER_SET_METADATA_PASSWORD" ]]; then
  export DAGSTER_METADATA_DB_PASSWORD="$CALLER_METADATA_PASSWORD"
fi

export DAGSTER_METADATA_DB_HOST="${DAGSTER_METADATA_DB_HOST:-127.0.0.1}"
export DAGSTER_METADATA_DB_PORT="${DAGSTER_METADATA_DB_PORT:-55433}"
export DAGSTER_METADATA_DB_NAME="${DAGSTER_METADATA_DB_NAME:-dagster_local}"
export DAGSTER_METADATA_DB_USER="${DAGSTER_METADATA_DB_USER:-dagster}"

print_failure() {
  local code="$1"
  local message="$2"
  local remediation_hint
  case "$code" in
    endpoint_unavailable)
      remediation_hint="Confirm Dagit is running and endpoint host/port are correct."
      ;;
    metadata_config_missing)
      remediation_hint="Export DAGSTER_METADATA_DB_* vars or source docker/compose env files before probing."
      ;;
    workspace_load_failed)
      remediation_hint="Confirm workspace definitions load and DAGIT_VERIFY_WORKSPACE settings are correct."
      ;;
    prerequisite_missing)
      remediation_hint="Run from repository root after local prerequisites are installed."
      ;;
    *)
      remediation_hint="Inspect Dagit logs and rerun endpoint check."
      ;;
  esac
  echo "DAGIT_HEALTH_STATUS=failure"
  echo "DAGIT_FAILURE_CATEGORY=${code}"
  echo "DAGIT_MESSAGE=${message}"
  echo "DAGIT_REMEDIATION_HINT=${remediation_hint}"
}

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

for _ in $(seq 1 "$RETRIES"); do
  if curl -fsS "$ENDPOINT" >/dev/null 2>&1; then
    break
  fi
  sleep "$DELAY_SECONDS"
done

if ! curl -fsS "$ENDPOINT" >/dev/null 2>&1; then
  print_failure "endpoint_unavailable" "Dagit endpoint unreachable at ${ENDPOINT}"
  exit 1
fi

if [[ "$VERIFY_WORKSPACE" == "0" ]]; then
  echo "DAGIT_HEALTH_STATUS=ready"
  echo "DAGIT_MESSAGE=Endpoint reachable"
  exit 0
fi

graphql_payload='{"query":"query LocalWorkspaceCheck { workspaceOrError { __typename ... on Workspace { locationEntries { id } } } }"}'
response="$(curl -fsS -X POST "${ENDPOINT}/graphql" -H "Content-Type: application/json" -d "$graphql_payload" 2>/dev/null || true)"

if [[ -z "$response" ]]; then
  print_failure "workspace_load_failed" "Endpoint is reachable, but workspace GraphQL query failed"
  exit 1
fi

if [[ "$response" != *"\"__typename\":\"Workspace\""* ]]; then
  print_failure "workspace_load_failed" "Workspace is not loaded in Dagit"
  exit 1
fi

if [[ "$response" != *"locationEntries"* ]]; then
  print_failure "workspace_load_failed" "Workspace response is missing location entries"
  exit 1
fi

location_entry_count="$(printf '%s' "$response" | (grep -o '"id"' || true) | wc -l | tr -d ' ')"
if [[ "$location_entry_count" -lt "$MIN_LOCATION_ENTRIES" ]]; then
  print_failure "workspace_load_failed" "Workspace location entries below threshold (${location_entry_count} < ${MIN_LOCATION_ENTRIES})"
  exit 1
fi

echo "DAGIT_HEALTH_STATUS=ready"
echo "DAGIT_LOCATION_ENTRIES=${location_entry_count}"
echo "DAGIT_SCHEDULE_MODEL=per_source"
echo "DAGIT_MESSAGE=Endpoint and workspace checks passed"
