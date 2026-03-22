# Feature Specification: Per-Source Asset Cadence

**Feature Branch**: `011-source-asset-cadence`  
**Created**: 2026-03-22  
**Status**: Draft  
**Input**: User description: "Replace shared ingest scheduling with per-source Dagster asset cadences"

## User Scenarios & Testing _(mandatory)_

### User Story 1 - Schedule Each Source Independently (Priority: P1)

As a pipeline operator, I need each source asset to run on its own cadence so that one source's timing does not control or delay another source.

**Why this priority**: This is the core behavior change and the primary value of the feature.

**Independent Test**: Configure distinct cadences for at least three source assets and verify each asset triggers according to its own schedule window without requiring a shared "run all sources" trigger.

**Acceptance Scenarios**:

1. **Given** multiple active source assets with different cadences, **When** the scheduling system evaluates upcoming runs, **Then** each asset receives run requests on its own cadence.
2. **Given** one source asset has no schedule due yet, **When** another source asset is due, **Then** only the due asset is triggered.
3. **Given** an operator views the orchestration catalog, **When** they inspect source assets, **Then** each source shows its own schedule association.

---

### User Story 2 - Simplify Scheduling Operations (Priority: P2)

As an operator, I need scheduling behavior to be managed in one place at the asset level so run timing is easier to reason about and troubleshoot.

**Why this priority**: Operational clarity and lower cognitive load are key outcomes of the architecture shift.

**Independent Test**: Remove legacy shared cadence routing and confirm run behavior can be explained entirely through source asset schedules and schedule metadata.

**Acceptance Scenarios**:

1. **Given** a source asset schedule is updated, **When** the next run window arrives, **Then** run timing follows the updated asset schedule without requiring separate policy state updates.
2. **Given** a run occurs from an asset schedule, **When** run records are reviewed, **Then** the trigger is attributable to the source asset schedule that initiated it.

---

### User Story 3 - Perform a Safe Hard Cutover (Priority: P3)

As a maintainer, I need legacy shared-schedule behavior removed cleanly so there is no ambiguity about which scheduling model is active.

**Why this priority**: The user requested a hard break; ambiguity would create duplicate triggers and operational risk.

**Independent Test**: Validate there is no active shared "all-sources" schedule path and no legacy due-filtering requirement for normal scheduled execution.

**Acceptance Scenarios**:

1. **Given** the cutover release is active, **When** scheduled runs are generated, **Then** they originate from source-specific asset schedules only.
2. **Given** legacy shared cadence artifacts exist in historical records, **When** operators view current scheduling behavior, **Then** current cadence decisions depend only on the source asset schedule model.

---

### Edge Cases

- A source asset schedule is paused while other source schedules remain active.
- Two source assets are due at the same timestamp.
- A source asset misses one or more schedule windows due to downtime.
- A source is temporarily disabled and later re-enabled.
- A source asset exists in the catalog but has no configured cadence.
- A source run triggered by schedule overlaps with a manually triggered run.

## Requirements _(mandatory)_

### Functional Requirements

- **FR-001**: The system MUST provide an independent schedule for each active source asset used by ingestion operations.
- **FR-002**: The system MUST allow different cadences across source assets without requiring a shared parent schedule.
- **FR-003**: The system MUST remove the shared scheduled-trigger path that executes all sources through one cadence gate.
- **FR-004**: The system MUST ensure scheduled source execution eligibility is determined by each source asset schedule rather than a separate due-filtering subsystem.
- **FR-005**: The system MUST preserve on-demand source execution as an operator capability independent of scheduled cadence.
- **FR-006**: The system MUST prevent duplicate scheduled execution for a source asset within the same cadence window.
- **FR-007**: The system MUST provide operator-visible schedule metadata per source asset, including cadence and activation status.
- **FR-008**: The system MUST emit run records that identify which source asset schedule triggered each scheduled execution.
- **FR-009**: The system MUST define and document hard-cutover behavior so only one scheduling model is authoritative after release.
- **FR-010**: The system MUST preserve source-level outcome visibility and existing run-audit traceability expectations after cutover.
- **FR-011**: The system MUST define behavior for sources without an active cadence (for example: paused, disabled, or unconfigured) and ensure they are not triggered by scheduled runs.
- **FR-012**: The system MUST provide migration guidance for legacy schedule-policy and eligibility artifacts so operators can interpret historical records correctly post-cutover.

### Assumptions

- Source assets already exist in the orchestration catalog and remain the unit of scheduled execution.
- The release is allowed to be a hard break with no requirement for dual-run compatibility.
- Existing on-demand triggering remains in scope and should continue to work for source-specific execution.
- Historical run records remain queryable for audit and troubleshooting.

### Dependencies

- A maintained list of in-scope source assets that require independent cadences.
- Local stack verification workflows that can validate schedule registration and source-level run visibility.
- Updated operator documentation for schedule ownership, cadence updates, and troubleshooting.

### Key Entities _(include if feature involves data)_

- **Source Asset**: A discrete ingestable source with identity, activation status, and observable run history.
- **Asset Schedule**: A cadence assignment linked to one source asset, including cadence, active/paused state, and effective window.
- **Scheduled Run Record**: A run event with trigger origin, timestamps, source identity, and outcome summary.
- **Scheduling Migration State**: A cutover interpretation context that distinguishes historical legacy cadence artifacts from the active asset-schedule model.

## Success Criteria _(mandatory)_

### Measurable Outcomes

- **SC-001**: 100% of active source assets in scope have explicitly defined independent cadences and no dependency on a shared all-source schedule.
- **SC-002**: In a 24-hour validation window, each source asset executes only during its own scheduled windows, with zero executions attributable to legacy shared cadence logic.
- **SC-003**: For a test set of at least three source assets with mixed cadences, operators can correctly predict and verify scheduled execution timing for each source with at least 95% accuracy.
- **SC-004**: For scheduled runs sampled during validation, 100% of run records include source-level trigger attribution identifying the originating source asset schedule.
- **SC-005**: Post-cutover verification confirms zero active shared scheduled-trigger definitions for all-source execution.

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
