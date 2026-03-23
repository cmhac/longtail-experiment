# Feature Specification: Initial Read-Only FastAPI API For Ingested Data

**Feature Branch**: `014-read-only-fastapi-api`
**Created**: 2026-03-23
**Status**: Draft
**Input**: User description: "Initial Read-Only FastAPI API For Ingested Data"

## User Scenarios & Testing _(mandatory)_

### User Story 1 - Check API Health (Priority: P1)

A frontend client or operator needs to confirm the backend API is reachable and healthy before making data requests.

**Why this priority**: Health checks are the foundation of any API integration. Frontend clients must know the service is available before issuing data reads. This is the minimum viable API surface.

**Independent Test**: Can be fully tested by sending an HTTP GET to `/health` and verifying a JSON response with a `status` field indicating the service is operational.

**Acceptance Scenarios**:

1. **Given** the backend service is running, **When** a client sends `GET /health`, **Then** the response has HTTP 200 with a JSON body containing `{"status": "ok"}` (or equivalent healthy state indicator).
2. **Given** the backend service cannot reach the database, **When** a client sends `GET /health`, **Then** the response returns HTTP 503 with a body indicating the dependency is unavailable.

---

### User Story 2 - List Ingestion Runs (Priority: P1)

A frontend operator or developer wants to see all recorded ingestion runs to understand when data was collected and whether those runs succeeded.

**Why this priority**: Ingestion runs are the top-level operational record. Without this endpoint, frontend clients have no entry point into the ingestion audit trail.

**Independent Test**: Can be fully tested by seeding the database with ingestion run records and sending `GET /api/runs`, then verifying the returned list matches the expected records.

**Acceptance Scenarios**:

1. **Given** multiple ingestion runs are persisted, **When** a client sends `GET /api/runs`, **Then** the response has HTTP 200 with a JSON list of runs ordered by descending start time, each with stable field names (id, status, started_at, finished_at).
2. **Given** no ingestion runs are persisted, **When** a client sends `GET /api/runs`, **Then** the response has HTTP 200 with an empty list.
3. **Given** a page size limit is in effect, **When** a client sends `GET /api/runs` with pagination parameters, **Then** the response includes the requested page of results plus pagination metadata.

---

### User Story 3 - Retrieve a Single Ingestion Run (Priority: P2)

A frontend developer or operator wants to view the details of a specific ingestion run by its identifier.

**Why this priority**: Detail views require a single-run endpoint. Needed for drill-down UX and API correctness validation.

**Independent Test**: Can be fully tested by seeding a known run and issuing `GET /api/runs/{run_id}`, verifying the returned object matches the seeded data.

**Acceptance Scenarios**:

1. **Given** an ingestion run with `run_id` exists, **When** a client sends `GET /api/runs/{run_id}`, **Then** the response has HTTP 200 with the run's full detail record.
2. **Given** no ingestion run with `run_id` exists, **When** a client sends `GET /api/runs/{run_id}`, **Then** the response has HTTP 404 with a JSON error body including a `code` and `message` field.

---

### User Story 4 - List Source Run Outcomes For a Run (Priority: P2)

A frontend client needs to see the per-source outcomes for a specific ingestion run to understand which sources succeeded, failed, were deferred, or had conflicts.

**Why this priority**: Outcomes are the core operational audit record that diagnose data quality. Needed before conflict drill-down makes sense.

**Independent Test**: Can be fully tested by seeding a run with associated source outcomes and sending `GET /api/runs/{run_id}/outcomes`, verifying all outcomes are returned with their correct status values.

**Acceptance Scenarios**:

1. **Given** a run with source outcomes exists, **When** a client sends `GET /api/runs/{run_id}/outcomes`, **Then** the response has HTTP 200 with a list of source outcomes, each with a stable `state` value from the known set (`success`, `partial_success`, `failure`, `not_due`, `deferred`, `conflict`).
2. **Given** the run exists but has no outcomes, **When** a client sends `GET /api/runs/{run_id}/outcomes`, **Then** the response has HTTP 200 with an empty list.
3. **Given** `run_id` does not match any run, **When** a client sends `GET /api/runs/{run_id}/outcomes`, **Then** the response has HTTP 404 with a structured error body.

---

### User Story 5 - List Eligibility Records For a Run (Priority: P3)

A developer or operator wants to inspect which sources were evaluated for eligibility during a specific run, including their eligibility reason and cadence information.

**Why this priority**: Eligibility data is operational diagnostic information. Needed to understand scheduling decisions but lower urgency than outcomes for end-to-end validation.

**Independent Test**: Can be fully tested by seeding a run with eligibility records and issuing `GET /api/runs/{run_id}/eligibility`, verifying the returned list matches the seeded records.

**Acceptance Scenarios**:

1. **Given** eligibility records exist for a run, **When** a client sends `GET /api/runs/{run_id}/eligibility`, **Then** the response has HTTP 200 with a list of eligibility records including `source_key`, `eligibility_state` (one of `due`, `not_due`, `skipped_inactive`, `skipped_invalid_policy`), and `reason_code` fields.
2. **Given** `run_id` does not match any run, **When** a client sends `GET /api/runs/{run_id}/eligibility`, **Then** the response has HTTP 404 with a structured error body.

---

### User Story 6 - List Conflicts With Filters (Priority: P3)

A data quality reviewer or operator wants to browse conflicts across ingestion runs, optionally filtered by run, source, series, period, or conflict state.

**Why this priority**: Conflict visibility is essential for data quality review workflows. Filtering ensures the endpoint remains usable with large data volumes.

**Independent Test**: Can be fully tested by seeding conflicts with varying attributes and issuing `GET /api/conflicts` with each supported filter parameter, verifying only matching records are returned.

**Acceptance Scenarios**:

1. **Given** conflicts are persisted, **When** a client sends `GET /api/conflicts` with no filters, **Then** the response has HTTP 200 with all conflicts in a paginated list.
2. **Given** conflicts exist for multiple sources, **When** a client sends `GET /api/conflicts?source_key=X`, **Then** only conflicts matching `source_key=X` are returned.
3. **Given** an unsupported filter parameter is provided, **When** a client sends `GET /api/conflicts?unsupported=foo`, **Then** the response has HTTP 422 with a structured validation error body.
4. **Given** a filter with no matching records, **When** a client sends `GET /api/conflicts?run_id=nonexistent`, **Then** the response has HTTP 200 with an empty list.

---

### Edge Cases

- What happens when a `run_id` path parameter is not a valid integer or UUID format? The API must return HTTP 422 with a structured validation error.
- What happens when the database is unreachable at request time? The API must return HTTP 503 with a structured error body; it must not expose internal stack traces.
- What happens when a filter parameter value is an empty string? The API must treat it as absent or return a 422 validation error.
- What happens when pagination parameters (e.g., `page`, `limit`) are out of valid range? The API must return HTTP 422 with a descriptive validation error.
- What happens when a list endpoint returns zero results? The API must return HTTP 200 with an empty `items` list, not a 404.

## Requirements _(mandatory)_

### Functional Requirements

- **FR-001**: The backend MUST expose a `/health` endpoint that returns the service's operational status and reachability of its database dependency.
- **FR-002**: The backend MUST expose `GET /api/runs` returning a paginated, ordered list of ingestion run records with stable field names.
- **FR-003**: The backend MUST expose `GET /api/runs/{run_id}` returning the full detail record for a single run or HTTP 404 if not found.
- **FR-004**: The backend MUST expose `GET /api/runs/{run_id}/outcomes` returning the list of source run outcome records for the specified run.
- **FR-005**: The backend MUST expose `GET /api/runs/{run_id}/eligibility` returning the list of source eligibility records for the specified run.
- **FR-006**: The backend MUST expose `GET /api/conflicts` returning a paginated list of conflict records, supporting filter parameters: `run_id`, `source_key`, `series_key`, `reference_period_key`, and `conflict_state`.
- **FR-007**: All list endpoints MUST support pagination and return a response envelope with an `items` array and pagination metadata (`total`, `page`, `page_size`).
- **FR-008**: All endpoints MUST return responses using a consistent JSON envelope with explicit, stable field names in snake_case.
- **FR-009**: All timestamps in responses MUST be formatted as ISO-8601 UTC strings.
- **FR-010**: All enum/state values (`state` on source outcomes, `eligibility_state` on eligibility records, `conflict_state` on conflict records) MUST use lowercase snake_case string literals from a defined, stable value set. The stable sets are: source outcome `state` = `success` | `partial_success` | `failure` | `not_due` | `deferred` | `conflict`; eligibility `eligibility_state` = `due` | `not_due` | `skipped_inactive` | `skipped_invalid_policy`; conflict `conflict_state` = `open` | `resolved` | `suppressed`.
- **FR-011**: The backend MUST return HTTP 404 with a structured JSON error body (`code`, `message`) for any single-resource endpoint where the resource is not found.
- **FR-012**: The backend MUST return HTTP 422 with a structured JSON error body for invalid filter parameters or malformed path parameters.
- **FR-013**: The backend MUST return HTTP 503 with a structured JSON error body when a downstream dependency (database) is unavailable.
- **FR-014**: The API MUST be read-only; no create, update, or delete endpoints are in scope.
- **FR-015**: The backend MUST generate and expose an OpenAPI schema document, and a checked-in snapshot of the schema MUST be maintained under `specs/contracts/`.
- **FR-016**: The API path structure MUST support a versioning decision; Phase 1 endpoints are served under `/api/` (unversioned) with the option to add `/api/v1/` later without breaking existing paths.
- **FR-017**: The backend MUST include an error response envelope with at minimum: `code` (string), `message` (string), and optionally `details` (object) and `correlation_id` (string).

### Key Entities

- **IngestionRun**: A single execution of the ingestion pipeline; has an identifier, start time, finish time, status, and summary counts.
- **SourceRunOutcome**: A per-source result record within an ingestion run; has source key, outcome state (`success`, `partial_success`, `failure`, `not_due`, `deferred`, or `conflict`), observation counts, and an optional reason code.
- **SourceEligibility**: A record of a source's cadence evaluation within a run; has source key, eligibility state string (`due`, `not_due`, `skipped_inactive`, or `skipped_invalid_policy`), machine-readable reason code, evaluation timestamp, and a flag indicating whether the source was selected for execution.
- **ConflictRecord**: A data conflict recorded during ingestion; has run reference, source key, series key, reference period key, conflict state, and timestamps.

## Success Criteria _(mandatory)_

### Measurable Outcomes

- **SC-001**: All six Phase 1 endpoints respond within 500 ms for typical database sizes used in local development.
- **SC-002**: 100% of Phase 1 endpoints have automated contract tests and integration tests that pass in CI.
- **SC-003**: Backend test coverage for affected modules remains at or above 90% after this feature is merged.
- **SC-004**: The OpenAPI contract snapshot is checked in and remains consistent with the running application (validated by a test).
- **SC-005**: Developers can start the backend API locally with a single documented command and confirm all endpoints via a health check within 2 minutes.
- **SC-006**: All error responses use a consistent envelope so frontend clients can handle errors uniformly without special-casing each endpoint.
- **SC-007**: The Phase 1 API surface is independent of canonical observation persistence; all Phase 1 endpoints return data without requiring canonical wiring.

## Assumptions

- Phase 1 endpoints depend only on runtime ingestion tables (`ingestion_runs`, `source_run_outcomes`, `source_eligibility_snapshots`, and `conflict_records`) that are already persisted by the pipeline.
- Phase 2 endpoints (observations, audit, hierarchy) are explicitly out of scope for this feature and will be addressed in a follow-up issue after canonical persistence is wired.
- Path versioning starts as unversioned `/api/` for Phase 1; a `/api/v1/` migration path may be introduced later without requiring changes to this spec.
- Frontend clients will consume the OpenAPI contract snapshot to generate typed client interfaces (FR-015); this contract acts as the shared interface boundary.
- Authentication and authorization are out of scope; all Phase 1 endpoints are unauthenticated reads.
- Pagination uses page-number style (`page`, `page_size`) as a reasonable default; cursor-based pagination may be introduced in a later phase.
- The pipeline writes `partial_success` as a distinct source-level outcome state (a source that ingested some records successfully but also encountered some failures). Frontend clients MUST handle this value; it is not an error but a degraded-success condition.
- Query-support indexes on `conflict_records` filter columns and `ingestion_runs.started_at` are required for SC-001 to hold at scale. These are delivered by database migration `0008_query_support_indexes` and MUST be applied before the API is exercised against a populated database.

## Constitution Alignment _(mandatory)_

- **CA-001 Quality Gates**: Yes — all endpoints will have ruff, ty, and pytest gates passing without suppressions.
- **CA-002 Coverage**: Yes — new backend modules will include tests targeting ≥ 90% coverage for affected scope.
- **CA-003 Local Stack**: Yes — backend API will be runnable against the existing Docker Compose local stack; compose updates will be listed if needed.
- **CA-004 Contracts and Data Integrity**: Yes — OpenAPI contract snapshot is checked in and validated; response envelopes define stable field names and value sets; no write paths introduced.
- **CA-005 Documentation Fidelity**: Yes — local run/test commands will be documented in a runbook; AGENTS.md will be updated if repository structure or tooling changes.
