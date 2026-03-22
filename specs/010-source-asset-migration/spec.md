# Feature Specification: Migrate Ingestion to Source-Per-Asset Architecture

**Feature Branch**: `010-source-asset-migration`  
**Created**: 2026-03-22  
**Status**: Draft  
**Input**: User description: "read issue 5 of this repo and create a spec to implement this change"

## Clarifications

### Session 2026-03-22

- Q: For initial delivery, which sources must be migrated to source-as-asset and covered by acceptance tests? -> A: Migrate all current and any new source added during the implementation window.
- Q: What cutover strategy should migration use? -> A: One-time big-bang cutover for all sources in one release window, acceptable due early greenfield stage and minimal data preservation burden.
- Q: What should happen if a subset of sources fails validation in the release window? -> A: Proceed with full cutover and accept temporary failures for broken sources.
- Q: What is the maximum acceptable time to recover a source that fails during cutover? -> A: No explicit recovery target for this early greenfield stage.

## User Scenarios & Testing _(mandatory)_

### User Story 1 - Operators run one source at a time (Priority: P1)

As an operations user, I can trigger ingestion for one selected source without running unrelated sources so I can handle source-specific incidents and backfills quickly.

**Why this priority**: Source-level control is the primary operational gap and the direct reason for this migration.

**Independent Test**: Launch a run for one valid source from the operations UI and verify only that source runs while all other sources remain idle.

**Acceptance Scenarios**:

1. **Given** multiple sources are configured, **When** an operator requests a run for source A, **Then** the system executes source A only and records a run for source A.
2. **Given** an invalid or unknown source is requested, **When** the request is submitted, **Then** the system rejects the request with a clear validation message and no source run starts.

---

### User Story 2 - Operators monitor source outcomes directly (Priority: P2)

As an operations user, I can see source-level execution outcomes and metadata directly in the orchestration UI so I can triage failures without relying on hidden internal coordinator details.

**Why this priority**: Visibility is required to make source-level control trustworthy and actionable.

**Independent Test**: Execute a source run and verify source-level status, run outcome, and key metadata are visible in the orchestration UI and traceable to persistence records.

**Acceptance Scenarios**:

1. **Given** a source run completes successfully, **When** the operator opens the run details, **Then** source-level materialization and run metadata are visible and identifiable.
2. **Given** a source run fails, **When** the operator inspects the failed run, **Then** failure state and diagnostic metadata are visible at source level.

---

### User Story 3 - Platform owners keep scheduling authority centralized (Priority: P3)

As a platform owner, I can rely on the orchestration platform as the only ingest scheduling authority so cadence control is consistent and legacy competing schedulers cannot trigger duplicate runs.

**Why this priority**: Single scheduling authority is critical for long-term reliability and architecture consistency.

**Independent Test**: Enable all source schedules in the orchestration platform, run cadence windows, and confirm no non-platform scheduling path can initiate ingest.

**Acceptance Scenarios**:

1. **Given** cadence schedules are configured for active sources, **When** schedule windows arrive, **Then** runs are launched only through the platform scheduler.
2. **Given** legacy scheduling entrypoints are disabled, **When** old scheduling commands are attempted, **Then** they do not create ingest runs and the system reports they are retired.

### Edge Cases

- A source definition exists but violates required registration or execution contract.
- Two source definitions resolve to the same source key.
- Big-bang cutover fails for a subset of sources during the release window.
- A source is locked or deferred at schedule time and must preserve current defer semantics.
- Schedule cutover is performed in an environment with in-flight runs.

## Requirements _(mandatory)_

### Functional Requirements

- **FR-001**: The system MUST represent every supported ingest source as a distinct first-class source asset in orchestration definitions.
- **FR-002**: The system MUST allow operators to run a single selected source without executing unrelated sources.
- **FR-003**: The system MUST expose source-level materialization status and run metadata in the orchestration UI.
- **FR-004**: The system MUST enforce deterministic registration and load order for source assets.
- **FR-005**: The system MUST fail fast with actionable error messaging when a source module violates the required source-asset contract.
- **FR-006**: The system MUST prevent duplicate source key registration during source-asset discovery and startup.
- **FR-007**: The system MUST keep run summaries and source outcomes available after cutover, without requiring strict historical parity guarantees for pre-cutover data in this greenfield phase.
- **FR-008**: The system MUST preserve existing behavioral semantics for deferred, locked, scheduled, and manual run paths.
- **FR-009**: The system MUST retire non-platform scheduling paths so ingest cadence is decided only by orchestration-native scheduling.
- **FR-010**: The system MUST perform a single release-window cutover that disables legacy scheduling/coordinator paths and enables source-asset execution as the default path.
- **FR-011**: The system MUST provide regression coverage for source selection, scheduling, lock handling, deferred handling, retries, and forward persistence integrity after cutover.
- **FR-012**: The system MUST update operational documentation to describe source-as-asset onboarding, scheduling, and troubleshooting flows.
- **FR-013**: The migration scope for initial delivery MUST include all currently supported sources and any new source onboarded during the implementation window.
- **FR-014**: If a subset of sources fails during big-bang cutover, the system MUST keep source-asset scheduling as the active path and allow operators to recover failing sources post-cutover without re-enabling legacy scheduling.
- **FR-015**: The initial greenfield rollout MUST NOT enforce a fixed recovery-time SLA for post-cutover source failures; recovery is tracked operationally without a hard time commitment.

### Key Entities _(include if feature involves data)_

- **Source Asset Definition**: Canonical representation of one ingest source as an independently executable, schedulable, observable asset identified by a unique source key.
- **Source Run Outcome**: Per-source execution result record that includes run identity, execution status, timing/provenance metadata, and outcome details.
- **Ingestion Run Summary**: Aggregate record for an ingest invocation used for historical traceability and parity checks during migration.
- **Scheduling Authority State**: Runtime state indicating that cadence decisions are owned only by orchestration-native schedules and automation.
- **Cutover Readiness Gate**: Explicit decision checkpoint capturing readiness evidence before executing the one-time cutover.

## Assumptions

- Existing supported sources at migration start and any new source onboarded during implementation are in scope and must retain equivalent operational behavior.
- Source-specific manual triggers and schedule automation are both required in the initial migrated operating model.
- Legacy coordinator and scheduling paths are retired in one cutover event rather than phased coexistence.
- Because this is an early greenfield phase, strict historical data parity/backfill obligations are not required beyond maintaining forward run visibility after cutover.
- Because this is an early greenfield phase, post-cutover source recovery does not require a fixed time-bound SLA.
- Operational users continue to use current orchestration UI access patterns and do not require new role models for this phase.

## Success Criteria _(mandatory)_

### Measurable Outcomes

- **SC-001**: 100% of supported ingest sources can be targeted and executed independently as source-level assets.
- **SC-002**: In operator validation runs, at least 95% of source-specific manual triggers complete without launching any unrelated source.
- **SC-003**: 100% of source runs expose source-level status and required metadata in the orchestration UI during acceptance testing.
- **SC-004**: 0 production ingest runs are initiated by non-platform scheduling paths after cutover completion.
- **SC-005**: After cutover, 100% of newly executed source runs produce accessible run summary and source outcome records for operational review.
- **SC-006**: Regression suite coverage includes scheduled, manual, deferred, and locked-source scenarios with 100% pass rate in release qualification runs.
- **SC-007**: Operations onboarding/troubleshooting documentation for source-as-asset workflows is updated and accepted by platform owners before release.
- **SC-008**: When partial source failures occur during cutover, source-level failure visibility remains available for 100% of failed sources so operators can triage and recover post-cutover.

## Constitution Alignment _(mandatory)_

- **CA-001 Quality Gates**: Feature can satisfy linting, formatting, type checking, and automated test gates without suppressions, bypasses, or workaround-only code. (Yes)
- **CA-002 Coverage**: Feature includes tests to keep backend/frontend coverage at or above 90% in affected projects. (Yes)
- **CA-003 Local Stack**: Feature is runnable in the unified local Docker Compose stack, or explicitly lists compose updates needed. (Yes)
- **CA-004 Contracts and Data Integrity**: Data/interface contract changes, provenance/timestamp impacts, and trend-alert reliability safeguards are defined. (Yes)
- **CA-005 Documentation Fidelity**: Relevant documentation is identified and will be created or updated in the same change for any impacted behavior, contracts, setup, or runbooks, including AGENTS.md when repository structure/workflows/tooling change. (Yes)
