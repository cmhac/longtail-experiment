#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "${SCRIPT_DIR}/../../.." && pwd)"
PID_FILE="${REPO_ROOT}/.tmp/dagit-local.pid"

if [[ ! -f "$PID_FILE" ]]; then
  echo "DAGIT_STOP_STATUS=not_running"
  exit 0
fi

pid="$(cat "$PID_FILE" 2>/dev/null || true)"
if [[ -z "$pid" ]]; then
  rm -f "$PID_FILE"
  echo "DAGIT_STOP_STATUS=stale_pid_file_removed"
  exit 0
fi

if ! kill -0 "$pid" 2>/dev/null; then
  rm -f "$PID_FILE"
  echo "DAGIT_STOP_STATUS=already_stopped"
  exit 0
fi

kill "$pid" 2>/dev/null || true
for _ in $(seq 1 20); do
  if ! kill -0 "$pid" 2>/dev/null; then
    rm -f "$PID_FILE"
    echo "DAGIT_STOP_STATUS=stopped"
    exit 0
  fi
  sleep 1
done

kill -9 "$pid" 2>/dev/null || true
rm -f "$PID_FILE"
echo "DAGIT_STOP_STATUS=stopped_forced"
