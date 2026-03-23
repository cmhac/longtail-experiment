# Data Model: Initial Read-Only FastAPI API For Ingested Data

## Overview

This feature introduces API-layer response entities (Pydantic schemas) that project data from existing runtime ORM models into stable HTTP response shapes. No new database tables or ORM models are introduced. All entities map to existing `libs/db` ORM models.

## Entities

### 1) PaginatedResponse[T] (common envelope)

Generic pagination envelope returned by all list endpoints.

Fields:

- items: list[T] (required) — page of result objects
- total: int (required) — total matching record count (≥ 0)
- page: int (required) — current page number (≥ 1)
- page_size: int (required) — page size used for this response (1–200)

Validation rules:

- `total` must be non-negative.
- `page` must be ≥ 1.
- `page_size` must be between 1 and 200 inclusive.
- `len(items)` ≤ page_size.

Relationships:

- Used as the top-level response for: IngestionRunListResponse, SourceRunOutcomeListResponse, SourceEligibilityListResponse, ConflictRecordListResponse.

---

### 2) ErrorResponse (common error envelope)

Structured error body returned by 4xx and 5xx responses.

Fields:

- code: string (required) — machine-readable error code (e.g., `"not_found"`, `"validation_error"`, `"service_unavailable"`)
- message: string (required) — human-readable description
- details: object | null (optional) — structured error context (e.g., field-level validation errors)
- correlation_id: string | null (optional) — request correlation identifier for log tracing

Validation rules:

- `code` must be non-empty.
- `message` must be non-empty.

---

### 3) IngestionRunResponse

Projects an `IngestionRun` ORM row into the HTTP response shape for a single ingestion run.

Source ORM model: `libs/db/src/db/models/ingestion_runtime.IngestionRun`

Fields:

- run_id: string (required) — stable string run identifier (maps to `IngestionRun.run_id`)
- trigger_type: string (required) — how the run was triggered (e.g., `"scheduled"`, `"manual"`)
- lifecycle_state: string (required) — current run lifecycle state (e.g., `"completed"`, `"running"`)
- outcome_state: string (required) — aggregate outcome (e.g., `"succeeded"`, `"failed"`, `"partial"`)
- started_at: string (required) — ISO-8601 UTC timestamp
- completed_at: string | null (optional) — ISO-8601 UTC timestamp; null if run is in progress
- accepted_count: int (required)
- quarantined_count: int (required)
- failed_count: int (required)
- duplicate_no_op_count: int (required)
- conflict_count: int (required)
- due_source_count: int (required)
- executed_source_count: int (required)
- deferred_source_count: int (required)
- not_due_source_count: int (required)
- failed_source_count: int (required)
- trigger_origin: string | null (optional)

Validation rules:

- All count fields must be ≥ 0.
- `started_at` must be a valid ISO-8601 UTC string.
- `completed_at` must be a valid ISO-8601 UTC string or null.

Relationships:

- One IngestionRunResponse has zero or more SourceRunOutcomeResponse items.
- One IngestionRunResponse has zero or more SourceEligibilityResponse items.
- One IngestionRunResponse has zero or more ConflictRecordResponse items (via `run_id`).

---

### 4) SourceRunOutcomeResponse

Projects a `SourceRunOutcome` ORM row into the HTTP response shape.

Source ORM model: `libs/db/src/db/models/ingestion_runtime.SourceRunOutcome`

Fields:

- run_id: string (required)
- source_key: string (required)
- state: string (required) — outcome state from the stable value set: `succeeded`, `failed`, `not_due`, `deferred`, `conflict`
- accepted_count: int (required)
- quarantined_count: int (required)
- failed_count: int (required)
- duplicate_no_op_count: int (required)
- conflict_count: int (required)
- outcome_reason_code: string | null (optional)
- message: string | null (optional)

Validation rules:

- `state` must be one of the defined stable value set.
- All count fields must be ≥ 0.

---

### 5) SourceEligibilityResponse

Projects a `SourceEligibilitySnapshot` ORM row into the HTTP response shape.

Source ORM model: `libs/db/src/db/models/ingestion_runtime.SourceEligibilitySnapshot`

Fields:

- run_id: string (required)
- source_key: string (required)
- eligibility_state: string (required) — e.g., `"eligible"`, `"not_due"`, `"skipped"`
- reason_code: string (required) — machine-readable reason for eligibility decision
- evaluated_at: string (required) — ISO-8601 UTC timestamp
- due_at: string | null (optional) — ISO-8601 UTC timestamp; null if not applicable
- selected_for_execution: bool (required)

Validation rules:

- `evaluated_at` must be a valid ISO-8601 UTC string.
- `due_at` must be a valid ISO-8601 UTC string or null.

---

### 6) ConflictRecordResponse

Projects a `ConflictRecord` ORM row into the HTTP response shape.

Source ORM model: `libs/db/src/db/models/ingestion_runtime.ConflictRecord`

Fields:

- conflict_id: string (required) — stable string conflict identifier
- run_id: string (required)
- source_key: string (required)
- series_key: string (required)
- reference_period_key: string (required)
- existing_observation_ref: string (required)
- incoming_record_ref: string (required)
- conflict_type: string (required)
- conflict_state: string (required) — from the stable value set: `open`, `resolved`, `suppressed`
- created_at: string (required) — ISO-8601 UTC timestamp
- resolved_at: string | null (optional) — ISO-8601 UTC timestamp; null if not yet resolved

Validation rules:

- `conflict_state` must be one of the defined stable value set.
- `created_at` must be a valid ISO-8601 UTC string.
- `resolved_at` must be a valid ISO-8601 UTC string or null.

---

### 7) HealthResponse

Response shape for `GET /health`.

Fields:

- status: string (required) — `"ok"` when healthy, `"degraded"` or `"unavailable"` when unhealthy
- db: string (required) — `"reachable"` or `"unreachable"`

Validation rules:

- `status` must be non-empty.
- `db` must be one of `"reachable"`, `"unreachable"`.

## Enum / State Value Sets

These value sets are stable across Phase 1. Any extension requires a versioned contract update.

### outcome_state (SourceRunOutcomeResponse.state)

| Value       | Meaning                                   |
| ----------- | ----------------------------------------- |
| succeeded   | Source run completed without errors       |
| failed      | Source run encountered a terminal error   |
| not_due     | Source was not due for execution          |
| deferred    | Source was deferred for retry             |
| conflict    | Source produced one or more conflict records |

### conflict_state (ConflictRecordResponse.conflict_state)

| Value      | Meaning                                    |
| ---------- | ------------------------------------------ |
| open       | Conflict is unresolved                     |
| resolved   | Conflict was explicitly resolved           |
| suppressed | Conflict was suppressed without resolution |

### eligibility_state (SourceEligibilityResponse.eligibility_state)

| Value     | Meaning                                    |
| --------- | ------------------------------------------ |
| eligible  | Source was due and selected for execution  |
| not_due   | Source cadence not yet satisfied           |
| skipped   | Source was eligible but not executed       |

## Query Parameter Contracts

### Pagination (all list endpoints)

| Parameter | Type | Default | Min | Max | Description |
| --------- | ---- | ------- | --- | --- | ----------- |
| page | int | 1 | 1 | — | Page number (1-based) |
| page_size | int | 50 | 1 | 200 | Items per page |

### Conflict Filters (GET /api/conflicts)

| Parameter | Type | Required | Description |
| --------- | ---- | -------- | ----------- |
| run_id | string | No | Filter by run identifier |
| source_key | string | No | Filter by source key |
| series_key | string | No | Filter by series key |
| reference_period_key | string | No | Filter by reference period key |
| conflict_state | string | No | Filter by conflict state (open/resolved/suppressed) |
