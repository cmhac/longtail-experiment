#!/usr/bin/env bash
set -euo pipefail

HOST="${DAGIT_HOST:-127.0.0.1}"
PORT="${DAGIT_PORT:-3001}"
ENDPOINT="${DAGIT_ENDPOINT:-http://${HOST}:${PORT}}"
RETRIES="${DAGIT_ENDPOINT_RETRIES:-20}"
DELAY_SECONDS="${DAGIT_ENDPOINT_DELAY_SECONDS:-1}"
VERIFY_WORKSPACE="${DAGIT_VERIFY_WORKSPACE:-1}"
MIN_LOCATION_ENTRIES="${DAGIT_MIN_LOCATION_ENTRIES:-1}"

print_failure() {
  local code="$1"
  local message="$2"
  local remediation_hint
  case "$code" in
    endpoint_unavailable)
      remediation_hint="Confirm Dagit is running and endpoint host/port are correct."
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
