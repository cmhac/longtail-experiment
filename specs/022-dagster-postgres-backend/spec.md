# Feature Specification: Dagster Metadata Postgres Migration

**Feature Branch**: `022-dagster-postgres-backend`  
**Created**: 2026-03-24  
**Status**: Draft  
**Input**: User description: "Switch Dagster storage backend from default SQLite to PostgreSQL because concurrent runs for source onboarding are causing locking protocol errors; add a second PostgreSQL database in the local stack for Dagster metadata while keeping the existing output data store."

## User Scenarios & Testing _(mandatory)_

### User Story 1 - Run concurrent ingest jobs reliably (Priority: P1)

As a pipeline engineer onboarding or validating source providers, I need orchestration metadata writes to remain stable during concurrent asset/job execution so runs can complete without storage lock failures.

**Why this priority**: Current lock failures block onboarding and validation flows, preventing reliable execution of core pipeline work.

**Independent Test**: Can be fully tested by launching a representative concurrent ingest workload and verifying that run/event tracking remains available and no storage-lock execution failures occur.

**Acceptance Scenarios**:

1. **Given** the local orchestration stack is running, **When** a multi-asset or multi-source run executes with concurrent steps, **Then** orchestration metadata is persisted successfully without lock-related run failure.
2. **Given** repeated concurrent run launches in a single developer session, **When** run history and event logs are queried, **Then** all completed runs are visible and queryable.

---

### User Story 2 - Operate two database roles in local stack (Priority: P2)

As a local-stack maintainer, I need a clearly separated orchestration metadata database and canonical output-data database so each can be managed, reset, and validated independently.

**Why this priority**: Separation prevents cross-purpose coupling and reduces accidental impact on canonical dataset storage while maintaining orchestration stability.

**Independent Test**: Can be tested by standing up the compose stack from clean state and confirming both database roles initialize correctly and are reachable by their intended consumers.

**Acceptance Scenarios**:

1. **Given** a clean local environment, **When** the local compose stack is started, **Then** both database roles are provisioned and healthy with no manual post-start patching.
2. **Given** orchestration metadata and canonical output data coexist in local development, **When** one store is reset for troubleshooting, **Then** the other store remains unaffected unless intentionally reset.

---

### User Story 3 - Diagnose configuration failures quickly (Priority: P3)

As a developer, I need clear startup and runtime failure behavior when orchestration database connectivity is misconfigured so I can fix environment issues without ambiguous partial-success states.

**Why this priority**: Fast diagnosis reduces debugging time and prevents silent orchestration degradation.

**Independent Test**: Can be tested by intentionally supplying invalid orchestration database configuration and verifying explicit, actionable failure behavior.

**Acceptance Scenarios**:

1. **Given** invalid or missing orchestration database connection settings, **When** orchestration services start or runs are launched, **Then** the system fails explicitly with actionable diagnostics and does not report successful run handling.
2. **Given** corrected orchestration database settings, **When** services restart, **Then** orchestration operations recover without requiring ad hoc code edits.

### Edge Cases

- What happens when the orchestration database is temporarily unavailable during an active run?
- How does the system behave if the orchestration metadata schema is absent or behind expected revision on startup?
- What happens if local developers still have legacy SQLite metadata files from earlier runs?
- How does the stack behave if orchestration and output data stores are accidentally configured to the same target database?

## Requirements _(mandatory)_

### Functional Requirements

- **FR-001**: The system MUST use a dedicated PostgreSQL-backed metadata store for orchestration run, event, and schedule state in local development.
- **FR-002**: The system MUST provision and configure orchestration metadata storage as a separate database role from canonical output dataset storage.
- **FR-003**: The system MUST preserve existing canonical output dataset behavior while introducing orchestration metadata database changes.
- **FR-004**: The system MUST provide deterministic local startup behavior where orchestration services only enter ready state after their metadata store is reachable.
- **FR-005**: The system MUST fail fast with explicit diagnostics when orchestration metadata database configuration is missing, invalid, or unreachable.
- **FR-006**: The system MUST provide a documented local migration path from prior SQLite-based orchestration metadata to PostgreSQL-backed metadata operation.
- **FR-007**: The system MUST define verification steps that confirm concurrent run execution no longer fails due to SQLite locking behavior.
- **FR-008**: The system MUST document operational boundaries so developers can independently reset, inspect, and troubleshoot orchestration metadata storage and canonical output storage.
- **FR-009**: The system MUST ensure local automation and runbooks include the new orchestration metadata dependency and readiness checks.

### Key Entities _(include if feature involves data)_

- **Orchestration Metadata Store**: Persistence boundary for run records, event logs, schedule/sensor state, and related control-plane metadata.
- **Canonical Output Data Store**: Persistence boundary for business-domain datasets produced by ingestion and transformation workloads.
- **Local Stack Database Configuration**: Environment-specific configuration set that maps each consumer (orchestration vs output data) to the correct database role.
- **Concurrency Validation Run**: Repeatable local validation execution used to confirm run/event persistence reliability under concurrent workload conditions.

### Assumptions

- Local development will continue to use Docker Compose as the primary stack orchestration entry point.
- PostgreSQL remains the approved local relational store for both orchestration and canonical output roles, with separate logical boundaries.
- Existing source onboarding workflows rely on concurrent execution patterns and therefore must be supported without reducing workload concurrency as the primary mitigation.
- Historical local SQLite metadata may be disposable for some developers; when not disposable, migration guidance will describe preservation options.

### Dependencies

- Availability of a second PostgreSQL database target in local stack configuration.
- Alignment with existing local-stack runbooks and verification scripts that currently assume a single PostgreSQL role plus default orchestration metadata behavior.

## Success Criteria _(mandatory)_

### Measurable Outcomes

- **SC-001**: In local validation, 0 lock-protocol storage failures occur across 50 consecutive concurrent run launches of the representative source-onboarding workload.
- **SC-002**: At least 95% of concurrent validation runs reach terminal success state on first attempt when upstream source endpoints are available.
- **SC-003**: 100% of developers following the updated runbook can stand up the local stack with both database roles and successfully execute at least one concurrent ingest validation within 15 minutes.
- **SC-004**: 100% of local startup failures caused by orchestration database misconfiguration present explicit actionable diagnostics that identify missing/invalid connectivity inputs.

## Constitution Alignment _(mandatory)_

- **CA-001 Quality Gates**: Yes. Feature scope includes tests and config updates that must pass lint/format/typecheck/test stop gates without suppressions.
- **CA-002 Coverage**: Yes. Feature requires test additions/updates for orchestration storage configuration and local-stack verification to preserve coverage thresholds.
- **CA-003 Local Stack**: Yes. Feature explicitly updates unified Docker Compose behavior to introduce and validate orchestration metadata database support.
- **CA-004 Contracts and Data Integrity**: Yes. Specification defines the separation boundary between orchestration metadata and canonical output data and protects output-data integrity.
- **CA-005 Documentation Fidelity**: Yes. Feature includes runbook/onboarding updates for new database responsibilities and verification steps.
- **CA-006 Configuration Integrity**: N/A. No new external API credentials are introduced; however, required orchestration database configuration will fail fast when absent or invalid.
