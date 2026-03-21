# Feature Specification: Orchestrated Time-Series Ingestion

**Feature Branch**: `005-dagster-ingest-pipeline`  
**Created**: 2026-03-21  
**Status**: Draft  
**Input**: User description: "Set up a Dagster-orchestrated pipeline that ingests any time series source into the database through source-specific pipeline scripts."

## Clarifications

### Session 2026-03-21

- Q: When one source workflow fails during a run that includes multiple sources, what should the orchestration do for the remaining sources? → A: Continue other sources; report overall run as partial success.
- Q: Should this phase require only scheduled runs, or both scheduled and on-demand runs? → A: Scheduled plus manual on-demand triggers.
- Q: If a new trigger arrives while the same source is already running, what should happen? → A: Queue one pending run per source (deduplicated).
- Q: When a source sends a duplicate record for the same series and reference period, how should ingestion treat it? → A: If the new record matches the existing record, do not write again and safely exit; if values differ, record both as a data-quality conflict with database-identifiable conflict metadata.

## User Scenarios & Testing _(mandatory)_

### User Story 1 - Onboard a New Source Quickly (Priority: P1)

As a data platform maintainer, I can add a new source-specific ingest workflow without changing core orchestration behavior so that new time-series sources can be onboarded rapidly.

**Why this priority**: The primary business value is reducing onboarding effort for new datasets while keeping a consistent ingestion lifecycle.

**Independent Test**: Can be fully tested by adding one new source ingest workflow, running one ingestion cycle, and confirming accepted records and failure outcomes are both reported.

**Acceptance Scenarios**:

1. **Given** a source with valid sample observations, **When** its ingest workflow is registered and run, **Then** observations are ingested using the shared canonical contract and completion is reported.
2. **Given** a source with records that violate mandatory contract rules, **When** ingest runs, **Then** invalid records are quarantined with explicit reasons and valid records are still processed.

---

### User Story 2 - Run Standardized Ingestion Operations (Priority: P2)

As an operator, I can run ingestion through one standardized orchestration entry point so that scheduling, reruns, and monitoring follow a single predictable workflow.

**Why this priority**: Operational consistency lowers troubleshooting time and avoids one-off run paths per source.

**Independent Test**: Can be tested by triggering a run through the orchestration entry point and validating run status, ingest counts, and per-source outcomes are available from one place.

**Acceptance Scenarios**:

1. **Given** one or more registered source workflows, **When** an ingestion run is triggered, **Then** each source workflow executes under the same run lifecycle and status model.
2. **Given** a transient source retrieval failure, **When** the operator reruns ingestion, **Then** rerun behavior is deterministic and produces clear success/failure outcome reporting.

---

### User Story 3 - Preserve Auditability During Ingestion (Priority: P3)

As a governance or analytics stakeholder, I can trace ingested data to source and run context so that trust and reproducibility are maintained.

**Why this priority**: Time-series decisions depend on provenance and revision confidence, even when ingest orchestration grows.

**Independent Test**: Can be tested by selecting ingested observations from one run and confirming provenance attributes, revision relationships, and run context can be retrieved without external notes.

**Acceptance Scenarios**:

1. **Given** accepted observations from an ingest run, **When** audit information is requested, **Then** source context and run context are available for each accepted observation.
2. **Given** a corrected source publication for an existing reference period, **When** ingest processes the update, **Then** revision lineage between prior and current observations remains traceable.

### Edge Cases

- A source returns an empty dataset for a scheduled period.
- A source returns a mix of valid, duplicate, and malformed rows in one batch.
- A source returns a duplicate row with matching values for an already stored series-period record.
- A source returns a duplicate row with a different value for an already stored series-period record.
- A source changes field names or value formatting without notice.
- One source workflow fails while other source workflows in the same run are healthy.
- A rerun receives overlapping records for periods that were previously ingested.
- Ingest is triggered while an earlier run for the same source is still in progress; only one pending run is queued for that source.

## Requirements _(mandatory)_

### Functional Requirements

- **FR-001**: System MUST provide one orchestration entry point that executes source-specific ingestion workflows through a shared run lifecycle and supports both scheduled and manual on-demand triggers.
- **FR-002**: System MUST allow new source ingestion workflows to be added through a bounded registration pattern without requiring changes to existing source workflows.
- **FR-003**: System MUST process each source workflow through shared canonical validation rules before persistence.
- **FR-004**: System MUST support mixed outcomes within a run, where valid records are accepted and invalid records are quarantined with explicit reasons.
- **FR-005**: System MUST persist accepted observations with required provenance and run-context metadata.
- **FR-006**: System MUST preserve revision lineage when updated values supersede previously accepted observations for the same series and reference period.
- **FR-007**: System MUST expose per-run and per-source operational outcomes including counts of accepted, quarantined, failed, duplicate no-op, and data-quality conflict records.
- **FR-008**: System MUST support deterministic rerun behavior for the same source and reference period boundaries.
- **FR-009**: System MUST prevent concurrent conflicting execution for the same source workflow within the same ingestion scope by enforcing at most one active run and one deduplicated queued pending run per source.
- **FR-010**: System MUST continue processing unaffected source workflows when one source workflow fails and MUST report the overall run outcome as partial success.
- **FR-011**: System MUST ensure ingestion operations can be executed in local development workflows using documented commands and expected environment defaults.
- **FR-012**: System MUST define documentation updates for onboarding a new source workflow, operating ingestion runs, and interpreting ingest outcomes.
- **FR-014**: System MUST perform drift checks for duplicate series-period records such that exact-value duplicates are treated as idempotent no-ops and are not rewritten.
- **FR-015**: System MUST classify non-matching duplicates for the same series-period record as data-quality conflicts, preserve both record contexts, and persist conflict identifiers that are queryable in the database.

### Key Entities _(include if feature involves data)_

- **Ingestion Workflow Definition**: A registered source-specific ingest workflow with source identity, ownership, expected cadence, and run inputs.
- **Ingestion Run**: A single orchestrated execution event containing run context, trigger metadata, lifecycle status, and aggregated outcomes.
- **Ingestion Record Outcome**: Per-record classification including accepted, quarantined, failed, duplicate no-op, or data-quality conflict status and associated reason metadata.
- **Canonical Observation Version**: A persisted observation linked to series identity, reference period, normalized value semantics, and revision state.
- **Provenance Context**: Source and acquisition attributes that allow an accepted observation to be traced to publication and retrieval context.
- **Conflict Record**: A persisted conflict artifact that links incompatible records for the same series and reference period, includes conflict identifiers, and supports downstream review.

### Assumptions

- Existing canonical contract rules remain the governing validation standard for accepted observations.
- Source-specific workflows are authored and maintained by platform developers.
- Initial phase scope focuses on ingestion orchestration and persistence integrity, not user-facing analytics features.
- Default local operational behavior prioritizes repeatability and explicit reruns over implicit automatic recovery.

### Dependencies

- Existing canonical schema, normalization, and validation definitions.
- Existing shared persistence models and migration authority.
- Existing local environment profiles and operational runbooks.
- Existing quality gate expectations for linting, formatting, type checking, test coverage, and contract tests.

## Success Criteria _(mandatory)_

### Measurable Outcomes

- **SC-001**: A new source workflow can be onboarded from definition to first successful ingestion run in under 1 business day without modifying existing source workflows.
- **SC-002**: At least 95% of valid records in onboarding test datasets are accepted in a single run while 100% of invalid records are quarantined with explicit reasons.
- **SC-003**: Operators can determine final run status and per-source record outcomes in under 5 minutes from run completion.
- **SC-004**: For sampled revised publications, 100% of superseded observations maintain traceable lineage to their replacement observations.
- **SC-005**: In repeated local validation runs, ingestion outcomes are consistent for identical inputs across at least 3 consecutive reruns.
- **SC-006**: 100% of non-matching duplicate records for the same series and reference period are surfaced as database-queryable conflict records.

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
