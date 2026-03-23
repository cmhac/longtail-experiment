# Feature Specification: Multi-Series Source Adapter Model

**Feature Branch**: `012-multi-series-adapters`  
**Created**: 2026-03-22  
**Status**: Draft  
**Input**: User description: "Enable one source adapter to ingest multiple series while allowing optional split adapters when cadence or operational needs differ"

## User Scenarios & Testing _(mandatory)_

### User Story 1 - Ingest Multiple Series from One Source Adapter (Priority: P1)

As a pipeline operator, I can configure one source adapter to ingest multiple observation series from the same provider so onboarding similar datasets does not require creating unnecessary duplicate adapters.

**Why this priority**: This is the immediate business need and unlocks faster source expansion with less operational and maintenance overhead.

**Independent Test**: Configure one source adapter with at least two series, run it once, and verify both series produce new observations with distinct identities.

**Acceptance Scenarios**:

1. **Given** a source adapter includes multiple configured series, **When** an operator runs that adapter, **Then** all configured series are ingested in the same run and recorded separately.
2. **Given** one series has no new data while another does, **When** the adapter runs, **Then** only the series with new data adds observations and the run still completes.
3. **Given** one configured series fails provider retrieval, **When** the adapter runs, **Then** the failure is visible and does not hide successful ingestion results from other configured series.

---

### User Story 2 - Operate Series as Separate Dagit Items (Priority: P2)

As an operator, I can view and trigger series-level items separately in orchestration so troubleshooting and ad-hoc backfills can target one dataset without rerunning unrelated datasets.

**Why this priority**: Independent operability reduces incident scope and improves debugging speed as source coverage grows.

**Independent Test**: Trigger one series item from orchestration and verify only that series is executed while other series from the same provider remain idle.

**Acceptance Scenarios**:

1. **Given** multiple series exist under one provider grouping, **When** an operator selects one series item in orchestration, **Then** only that series executes.
2. **Given** an operator inspects orchestration catalog entries, **When** viewing series items, **Then** each item clearly shows its provider grouping and its own run history.
3. **Given** a series-level run fails, **When** an operator reviews the run, **Then** failure details identify the impacted series without ambiguity.

---

### User Story 3 - Choose Grouped or Split Adapter Strategy (Priority: P3)

As a platform owner, I can choose between grouping multiple series in one adapter or splitting series into separate adapters when cadence or operational requirements diverge.

**Why this priority**: This preserves long-term flexibility so the platform can optimize for simplicity now and operational control later.

**Independent Test**: Define one provider with grouped series and another provider area with split adapters; validate both models are accepted and schedulable.

**Acceptance Scenarios**:

1. **Given** grouped-series adapters are used, **When** cadence is shared, **Then** one adapter can remain the authoritative execution path for those series.
2. **Given** a series later requires faster cadence, **When** owners move that series to a dedicated adapter, **Then** the system supports the split without requiring a redesign of other adapters.
3. **Given** both grouped and split models are active, **When** operators inspect scheduling behavior, **Then** schedule ownership is clear for each item and duplicate-trigger ambiguity is prevented.

### Edge Cases

- A grouped adapter contains series with different natural publication frequencies.
- A new series is added to a grouped adapter after previous runs already exist.
- A series is moved from a grouped adapter to a split adapter and must avoid duplicate ingestion in overlap windows.
- A grouped run succeeds for some series and fails for others in the same execution window.
- A series item is manually triggered while a grouped schedule run is also due.
- A provider temporarily disables one series endpoint while others remain available.

## Requirements _(mandatory)_

### Functional Requirements

- **FR-001**: The system MUST allow one source adapter to ingest multiple distinct series from the same provider in a single execution path.
- **FR-002**: The system MUST preserve separate series identity and traceability for all ingested observations, including when series share one adapter run.
- **FR-003**: The system MUST support operator-visible series-level items in orchestration that can be run independently.
- **FR-004**: The system MUST allow platform owners to choose either grouped-series adapters or split adapters for the same provider domain.
- **FR-005**: The system MUST support shared cadence for grouped series by default in initial rollout.
- **FR-006**: The system MUST allow later migration of a series from grouped to split adapter ownership without requiring global scheduling redesign.
- **FR-007**: The system MUST prevent duplicate scheduled execution when grouped and split adapter models coexist.
- **FR-008**: The system MUST preserve source-level and series-level operational visibility for success, partial success, and failure outcomes.
- **FR-009**: The system MUST keep on-demand triggering available for both grouped and split operational models.
- **FR-010**: The system MUST define operator guidance for deciding when to keep series grouped versus when to split into separate adapters.
- **FR-011**: The system MUST include regression coverage for grouped execution, series-level independent triggers, cadence ownership, and split-model coexistence.
- **FR-012**: The system MUST update onboarding and runbook documentation for multi-series adapter onboarding, operation, and troubleshooting.

### Assumptions

- Initial rollout will use shared cadence for grouped series unless an explicit faster/slower cadence requirement exists.
- A provider may expose many topics, and not all topics require separate operational ownership from day one.
- Operators need to run and inspect series independently, even when underlying ingestion code is reused within one adapter grouping.
- Splitting series into separate adapters remains an allowed strategy, not a mandatory default.

### Dependencies

- A maintained inventory of provider series and their intended ownership model (grouped or split).
- Operational naming conventions that make provider grouping and series identity clear in orchestration views.
- Updated runbooks describing migration safeguards when series move between grouped and split ownership.

### Key Entities _(include if feature involves data)_

- **Provider Group**: A logical grouping that represents one external provider domain and can own one or more ingest series.
- **Series Item**: A separately identifiable dataset within a provider group, with its own triggerability, visibility, and run history.
- **Adapter Ownership Mode**: A policy choice defining whether series are executed by a grouped adapter or by dedicated split adapters.
- **Series Execution Outcome**: A result record that captures series-level status, counts, and diagnostics for operator triage.

## Success Criteria _(mandatory)_

### Measurable Outcomes

- **SC-001**: At least one provider group can ingest two or more series through a single adapter path with 100% distinct series traceability in validation runs.
- **SC-002**: Operators can trigger an individual series item without executing unrelated series in at least 95% of targeted test runs.
- **SC-003**: For mixed grouped and split models in validation, 100% of scheduled runs have unambiguous ownership attribution and zero duplicate schedule triggers.
- **SC-004**: In release qualification, grouped-run scenarios and split-run scenarios both pass with 100% success across defined regression suites.
- **SC-005**: Platform owners can complete a documented grouped-to-split migration procedure for one series without loss of visibility or auditability.

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
