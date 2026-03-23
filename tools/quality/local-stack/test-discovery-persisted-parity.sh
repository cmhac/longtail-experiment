#!/usr/bin/env bash
set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../../.." && pwd)"
API_BASE_URL="${DISCOVERY_API_BASE_URL:-http://localhost:8000}"
DATASET_ID="${DISCOVERY_PARITY_DATASET_ID:-}"
REQUIRE_DELTA="${DISCOVERY_PARITY_REQUIRE_DELTA:-1}"
INGEST_COMMAND="${DISCOVERY_PARITY_INGEST_COMMAND:-}"

cd "$REPO_ROOT"

echo "[parity] checking health endpoint at ${API_BASE_URL}"
curl -fsS "${API_BASE_URL}/api/health" >/dev/null

echo "[parity] capturing recent datasets payload"
baseline_recent_payload="$(curl -fsS "${API_BASE_URL}/api/datasets/recent")"

if echo "${baseline_recent_payload}" | grep -q '"dataset_id"'; then
  echo "[parity] recent payload contains dataset_id values"
else
  echo "[parity] ERROR: recent payload did not include dataset entries" >&2
  exit 1
fi

if [[ -z "${DATASET_ID}" ]]; then
  DATASET_ID="$(
    printf '%s' "${baseline_recent_payload}" \
      | python3 -c 'import json,sys; payload=json.load(sys.stdin); print((payload.get("items") or [{}])[0].get("dataset_id", ""))'
  )"
fi

if [[ -z "${DATASET_ID}" ]]; then
  echo "[parity] ERROR: unable to determine dataset_id from recent payload" >&2
  exit 1
fi

echo "[parity] fetching dataset detail for ${DATASET_ID}"
baseline_detail_payload="$(curl -fsS "${API_BASE_URL}/api/datasets/${DATASET_ID}")"

if echo "${baseline_detail_payload}" | grep -q '"observations"'; then
  echo "[parity] detail payload includes observations key"
else
  echo "[parity] ERROR: detail payload missing observations key" >&2
  exit 1
fi

if [[ -n "${INGEST_COMMAND}" ]]; then
  echo "[parity] running ingest command for parity validation"
  eval "${INGEST_COMMAND}"
fi

post_recent_payload="$(curl -fsS "${API_BASE_URL}/api/datasets/recent")"
post_detail_payload="$(curl -fsS "${API_BASE_URL}/api/datasets/${DATASET_ID}")"

if [[ "${REQUIRE_DELTA}" == "1" ]]; then
  if [[ "${baseline_recent_payload}" == "${post_recent_payload}" && "${baseline_detail_payload}" == "${post_detail_payload}" ]]; then
    echo "[parity] ERROR: no discovery response delta detected after parity flow" >&2
    exit 1
  fi
  echo "[parity] response delta detected between baseline and post-ingest checks"
fi

echo "[parity] parity scaffold check completed"
