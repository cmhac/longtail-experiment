# Phase 1 API Contract: Read-Only FastAPI Endpoints

**Version**: 1.0.0
**Branch**: `014-read-only-fastapi-api`
**Date**: 2026-03-23
**Status**: Draft

## Overview

This document defines the stable HTTP API contract for Phase 1 read-only endpoints. Frontend clients MUST consume this contract to generate typed client interfaces. Any change to paths, field names, status codes, or value sets in this document constitutes a breaking change requiring a versioned update.

## General Conventions

| Convention | Value |
| ---------- | ----- |
| Base URL (local dev) | `http://localhost:8080` |
| Path prefix | `/api/` (unversioned Phase 1) |
| Content-Type | `application/json` |
| Field naming | snake_case throughout |
| Timestamp format | ISO-8601 UTC (e.g., `"2026-03-23T03:47:22Z"`) |
| Pagination style | Page-number (`page`, `page_size`) |

## Common Response Envelopes

### List Response Envelope

All list endpoints return:

```json
{
  "items": [ /* array of resource objects */ ],
  "total": 42,
  "page": 1,
  "page_size": 50
}
```

### Error Response Envelope

All 4xx and 5xx responses return:

```json
{
  "code": "not_found",
  "message": "Ingestion run 'abc123' was not found.",
  "details": null,
  "correlation_id": null
}
```

| Field | Type | Required | Description |
| ----- | ---- | -------- | ----------- |
| code | string | yes | Machine-readable error code |
| message | string | yes | Human-readable description |
| details | object or null | no | Structured context (e.g., field validation errors) |
| correlation_id | string or null | no | Request correlation ID for log tracing |

### Standard Error Codes

| HTTP Status | code value | When Used |
| ----------- | ---------- | --------- |
| 404 | `not_found` | Requested single resource does not exist |
| 422 | `validation_error` | Invalid query parameter or path parameter |
| 503 | `service_unavailable` | Database is unreachable |
| 500 | `internal_error` | Unexpected server error |

---

## Endpoints

### GET /health

Check service health and database reachability.

**Response 200 — Healthy**:

```json
{
  "status": "ok",
  "db": "reachable"
}
```

**Response 503 — Unhealthy**:

```json
{
  "status": "unavailable",
  "db": "unreachable"
}
```

---

### GET /api/runs

List ingestion runs ordered by `started_at` descending.

**Query Parameters**:

| Parameter | Type | Default | Min | Max | Description |
| --------- | ---- | ------- | --- | --- | ----------- |
| page | int | 1 | 1 | — | Page number |
| page_size | int | 50 | 1 | 200 | Items per page |

**Response 200**:

```json
{
  "items": [
    {
      "run_id": "run-20260323-abc",
      "trigger_type": "scheduled",
      "lifecycle_state": "completed",
      "outcome_state": "success",
      "started_at": "2026-03-23T03:00:00Z",
      "completed_at": "2026-03-23T03:02:15Z",
      "accepted_count": 120,
      "quarantined_count": 0,
      "failed_count": 0,
      "duplicate_no_op_count": 2,
      "conflict_count": 0,
      "due_source_count": 3,
      "executed_source_count": 3,
      "deferred_source_count": 0,
      "not_due_source_count": 1,
      "failed_source_count": 0,
      "trigger_origin": null
    }
  ],
  "total": 1,
  "page": 1,
  "page_size": 50
}
```

---

### GET /api/runs/{run_id}

Get a single ingestion run by its string run identifier.

**Path Parameters**:

| Parameter | Type | Description |
| --------- | ---- | ----------- |
| run_id | string | String run identifier |

**Response 200**: Single `IngestionRunResponse` object (same fields as items in list above).

**Response 404**:

```json
{
  "code": "not_found",
  "message": "Ingestion run 'run-xyz' was not found.",
  "details": null,
  "correlation_id": null
}
```

---

### GET /api/runs/{run_id}/outcomes

List source run outcomes for a specific ingestion run.

**Path Parameters**:

| Parameter | Type | Description |
| --------- | ---- | ----------- |
| run_id | string | String run identifier |

**Response 200**:

```json
{
  "items": [
    {
      "run_id": "run-20260323-abc",
      "source_key": "fred.fedfunds",
      "state": "success",
      "accepted_count": 60,
      "quarantined_count": 0,
      "failed_count": 0,
      "duplicate_no_op_count": 0,
      "conflict_count": 0,
      "outcome_reason_code": null,
      "message": null
    }
  ],
  "total": 1,
  "page": 1,
  "page_size": 50
}
```

**Stable `state` values**: `success`, `partial_success`, `failure`, `not_due`, `deferred`, `conflict`

**Response 404**: Run not found (same envelope as above).

---

### GET /api/runs/{run_id}/eligibility

List source eligibility snapshots for a specific ingestion run.

**Path Parameters**:

| Parameter | Type | Description |
| --------- | ---- | ----------- |
| run_id | string | String run identifier |

**Response 200**:

```json
{
  "items": [
    {
      "run_id": "run-20260323-abc",
      "source_key": "fred.fedfunds",
      "eligibility_state": "due",
      "reason_code": "due_for_execution",
      "evaluated_at": "2026-03-23T03:00:01Z",
      "due_at": "2026-03-23T03:00:00Z",
      "selected_for_execution": true
    }
  ],
  "total": 1,
  "page": 1,
  "page_size": 50
}
```

**Stable `eligibility_state` values**: `due`, `not_due`, `skipped_inactive`, `skipped_invalid_policy`

**Response 404**: Run not found.

---

### GET /api/conflicts

List conflict records with optional filters.

**Query Parameters**:

| Parameter | Type | Required | Description |
| --------- | ---- | -------- | ----------- |
| page | int | No (default 1) | Page number |
| page_size | int | No (default 50) | Items per page (max 200) |
| run_id | string | No | Filter by run identifier |
| source_key | string | No | Filter by source key |
| series_key | string | No | Filter by series key |
| reference_period_key | string | No | Filter by reference period key |
| conflict_state | string | No | Filter by state (open/resolved/suppressed) |

**Response 200**:

```json
{
  "items": [
    {
      "conflict_id": "conflict-001",
      "run_id": "run-20260323-abc",
      "source_key": "fred.fedfunds",
      "series_key": "FEDFUNDS",
      "reference_period_key": "2026-02",
      "existing_observation_ref": "obs-aaa",
      "incoming_record_ref": "obs-bbb",
      "conflict_type": "value_drift",
      "conflict_state": "open",
      "created_at": "2026-03-23T03:01:00Z",
      "resolved_at": null
    }
  ],
  "total": 1,
  "page": 1,
  "page_size": 50
}
```

**Stable `conflict_state` values**: `open`, `resolved`, `suppressed`

**Response 422** (invalid `conflict_state` value):

```json
{
  "code": "validation_error",
  "message": "Invalid value for 'conflict_state': 'unknown'. Must be one of: open, resolved, suppressed.",
  "details": {
    "field": "conflict_state",
    "provided": "unknown",
    "allowed": ["open", "resolved", "suppressed"]
  },
  "correlation_id": null
}
```

---

## OpenAPI Snapshot

The authoritative machine-readable contract is at:

```
specs/contracts/openapi-phase1-snapshot.json
```

This file is generated from the running FastAPI application and checked in. A test in `apps/backend/tests/api/test_openapi_snapshot.py` asserts consistency between the live `/openapi.json` response and the snapshot. Any PR that changes the API surface MUST regenerate this file.

To regenerate:

```bash
uv run --project apps/backend python -c "
import json
from src.api.app import create_app
app = create_app()
print(json.dumps(app.openapi(), indent=2))
" > specs/contracts/openapi-phase1-snapshot.json
```
