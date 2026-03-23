# Feature Specification: Real Backend Discovery API Runtime

**Feature Branch**: `019-real-backend-api`  
**Created**: 2026-03-23  
**Status**: Draft  
**Input**: User description: "Correctly implement backend dataset discovery API using real persisted data instead of seed-backed local HTTP responses"

## User Scenarios & Testing _(mandatory)_

<!--
  IMPORTANT: User stories should be PRIORITIZED as user journeys ordered by importance.
  Each user story/journey must be INDEPENDENTLY TESTABLE - meaning if you implement just ONE of them,
  you should still have a viable MVP (Minimum Viable Product) that delivers value.

  Assign priorities (P1, P2, P3, etc.) to each story, where P1 is the most critical.
  Think of each story as a standalone slice of functionality that can be:
  - Developed independently
  - Tested independently
  - Deployed independently
  - Demonstrated to users independently
-->

### User Story 1 - Trustworthy Discovery Data (Priority: P1)

As a user, I receive discovery and detail responses that reflect currently persisted dataset records so the UI shows real values instead of static fixture values.

**Why this priority**: This is the core correctness requirement; discovery pages are not trustworthy until API responses match persisted data.

**Independent Test**: Ingest a known dataset update in local runtime, request discovery/detail endpoints, and verify response values match newly persisted records.

**Acceptance Scenarios**:

1. **Given** new observations are persisted for an existing dataset, **When** detail data is requested for that dataset, **Then** the response includes those persisted observations in chronological order.
2. **Given** newly ingested datasets or updated timestamps exist, **When** search, recent, or catalog endpoints are requested, **Then** responses reflect the persisted dataset metadata and recency values.

---

### User Story 2 - Reliable Local Validation Loop (Priority: P2)

As a developer, I can run the local stack and validate backend discovery behavior against real persisted records so integration checks catch true regressions.

**Why this priority**: Local verification is the primary development safety loop and must represent production-intent data behavior.

**Independent Test**: Start local stack, run an ingest flow, and verify that API responses change based on persisted records without modifying seed fixtures.

**Acceptance Scenarios**:

1. **Given** the local stack is freshly started, **When** an ingest run writes records, **Then** discovery API responses use those records without requiring seed-file edits.
2. **Given** no matching dataset exists in persisted records, **When** detail is requested for an unknown identifier, **Then** explicit not-found behavior remains unchanged.

---

### User Story 3 - Accurate Operational Documentation (Priority: P3)

As an operator, I can follow runbooks and feature quickstarts that describe real backend behavior so operational checks and incident triage are consistent with runtime.

**Why this priority**: Documentation mismatch causes repeated false assumptions, delayed triage, and invalid release confidence.

**Independent Test**: Execute documented local-stack and verification commands from updated docs and confirm observed API behavior matches documented expectations.

**Acceptance Scenarios**:

1. **Given** current backend runtime behavior, **When** developers execute documented verification steps, **Then** they receive responses consistent with persisted data rather than static fixtures.
2. **Given** migration-head and runtime expectations are documented, **When** checks are run, **Then** docs report current expected outputs with no stale revision claims.

---

### Edge Cases

- Persisted dataset exists with metadata but zero observations.
- Persisted observations exist with multiple updates for the same observed date (revision history).
- Ingest writes records for one dataset while other datasets remain unchanged; unchanged datasets must retain prior response values.
- Local stack starts before migration application; API behavior must fail clearly or block until required schema is available.
- Recency ordering ties across datasets with identical latest update timestamps.
- Any runtime startup mode, environment switch, or fallback path attempts to serve discovery data from static fixtures instead of persisted records.

## Requirements _(mandatory)_

### Functional Requirements

- **FR-001**: The backend discovery API MUST source search, recent, catalog, and detail responses from persisted dataset and observation records.
- **FR-002**: The backend MUST NOT rely on static hardcoded fixture datasets for any runtime discovery API response path in local development, CI verification, or production-like execution; fixture datasets MAY be used only in automated test contexts and MUST NOT be wired into runtime startup or runtime fallback behavior.
- **FR-003**: Dataset detail responses MUST include all available persisted observations for the requested dataset within any requested date range, ordered chronologically.
- **FR-004**: Search and catalog responses MUST use persisted metadata fields (title, description, geographic scope, tags, source) and persisted recency values.
- **FR-005**: Recent-updates responses MUST reflect persisted dataset recency and maintain deterministic ordering and configured limit behavior.
- **FR-006**: Unknown dataset identifiers MUST continue returning explicit not-found responses.
- **FR-007**: A local end-to-end verification workflow MUST prove that after an ingest run, at least one discovery endpoint response changes to reflect newly persisted records.
- **FR-008**: Automated tests MUST include at least one integration path that validates parity between ingest-produced records and discovery API responses.
- **FR-009**: Documentation for local stack startup, migration checks, and backend discovery verification MUST describe the persisted-data runtime behavior and expected outcomes.
- **FR-010**: Runtime and documentation MUST use the current expected migration head and avoid stale revision assertions.
- **FR-011**: Any seed-backed or fixture-backed discovery runtime wiring, startup path, or fallback behavior MUST be removed from active runtime execution paths and MUST be excluded from default local stack startup.

### Assumptions

- Local development and CI environments have access to the same persistence schema used by ingestion and discovery workflows.
- Discovery APIs remain read-only in this feature scope.
- Existing endpoint shapes and error contracts remain stable unless explicitly versioned.
- Deterministic ordering rules from prior discovery contract remain in force.

### Dependencies

- Ingestion pipeline must continue persisting canonical dataset and observation records.
- Shared migration workflow remains authoritative for schema readiness in local stack.
- Existing frontend discovery pages depend on these backend endpoint contracts.

### Key Entities _(include if feature involves data)_

- **Persisted Dataset Record**: Discovery-level dataset representation containing identifier, source attribution, descriptive metadata, tags, and recency marker.
- **Persisted Observation Record**: Time-series record for a dataset containing observed date, value, reported timestamp, and optional attributes.
- **Discovery Response Projection**: Deterministic read model assembled from persisted records for search, catalog, recent-updates, and detail surfaces.
- **Verification Run Evidence**: Captured command outputs that prove API responses changed based on newly ingested persisted records.

## Success Criteria _(mandatory)_

### Measurable Outcomes

- **SC-001**: In a local verification run, 100% of sampled datasets with newly ingested observations show increased or changed observation payloads in detail responses without seed-file edits.
- **SC-002**: 100% of sampled search/recent/catalog responses are reproducibly derived from persisted records across repeated identical requests.
- **SC-003**: End-to-end verification runbook can be executed by a developer with no undocumented steps and yields expected outputs in one pass.
- **SC-004**: Contract and integration tests for discovery APIs pass with at least one test explicitly asserting ingest-to-API data parity.
- **SC-005**: During local-stack runtime verification, zero discovery responses are served from fixture-backed sources, and parity checks pass without enabling any fixture fallback mode.

## Constitution Alignment _(mandatory)_

- **CA-001 Quality Gates**: Feature can satisfy linting, formatting, type checking, and
  automated test gates without suppressions, bypasses, or workaround-only code. (Yes)
- **CA-002 Coverage**: Feature includes tests to keep backend/frontend coverage at or
  above 90% in affected projects. (Yes)
- **CA-003 Local Stack**: Feature is runnable in the unified local Docker Compose stack,
  or explicitly lists compose updates needed. (Yes)
- **CA-004 Contracts and Data Integrity**: Data/interface contract changes,
  provenance/timestamp impacts, and trend-alert reliability safeguards are defined.
  (Yes)
- **CA-005 Documentation Fidelity**: Relevant documentation is identified and will be
  created or updated in the same change for any impacted behavior, contracts, setup, or
  runbooks, including AGENTS.md when repository structure/workflows/tooling change.
  (Yes)
