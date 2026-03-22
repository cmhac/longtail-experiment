# Feature Specification: Parallel Source Scheduling

**Feature Branch**: `[006-parallel-source-scheduling]`  
**Created**: 2026-03-21  
**Status**: Draft  
**Input**: User description: "Add bounded parallel source execution and explicit per-source scheduling cadences to orchestration"

## Clarifications

### Session 2026-03-21

- Q: When an operator triggers an on-demand run for specific sources, should those sources run even if they are not currently due by cadence? -> A: On-demand runs execute explicitly selected sources regardless of due-state.
- Q: If due sources exceed parallel capacity for extended periods, which fairness rule should govern deferred source selection across subsequent runs? -> A: Strict FIFO by earliest due timestamp only.
- Q: If source X is due in a new run but already actively executing in another run, how should the new run classify X? -> A: Wait for the active run to finish and do not execute a duplicate run.
- Q: If a single scheduled run cannot finish all due sources before the next scheduler tick, what should happen at the run boundary? -> A: Let active work finish and carry remaining due sources forward as deferred, with warnings logged for scaling visibility.
- Q: When a source has malformed or missing cadence policy metadata, what should scheduled execution do? -> A: Skip source, mark skipped_invalid_policy, and emit warning.

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

### User Story 1 - Control Run Throughput (Priority: P1)

As a pipeline operator, I need source ingestion work to run with bounded parallelism so
that hourly or daily orchestrator runs do not stall or create an unbounded backlog as
the number of sources grows.

**Why this priority**: Throughput protection is required to keep ingestion reliable as
source count increases. Without it, queue growth can prevent timely data freshness.

**Independent Test**: Configure more sources than the allowed concurrency, start one
orchestration run, and verify that active source executions never exceed the configured
parallelism ceiling while all eligible sources still complete.

**Acceptance Scenarios**:

1. **Given** a configured source-execution parallelism limit and more due sources than
   available slots, **When** an orchestration run starts, **Then** sources are launched
   up to the limit and remaining due sources wait until slots are free.
2. **Given** one source fails during a bounded-parallel run, **When** the run continues,
   **Then** other due sources continue processing and the run summary reports both
   successful and failed outcomes.

---

### User Story 2 - Schedule Sources by Cadence (Priority: P2)

As a data operations owner, I need each source to declare its own update cadence so
that sources only run when due (hourly, daily, weekly, monthly, or less frequent).

**Why this priority**: A single global hourly schedule over-processes low-frequency
sources and wastes resources that should be reserved for high-priority updates.

**Independent Test**: Register multiple sources with different cadences and last-run
timestamps, trigger a schedule tick, and verify that only due sources are selected.

**Acceptance Scenarios**:

1. **Given** sources with mixed cadences and different last-success timestamps,
   **When** a scheduler tick is evaluated, **Then** only sources due at that point in
   time are included in the run request.
2. **Given** a source with a weekly cadence that was successfully processed less than
   one week ago, **When** hourly scheduler ticks continue, **Then** that source is
   excluded until it becomes due again.

---

### User Story 3 - Operate with Predictable Visibility (Priority: P3)

As an on-call operator, I need run metadata to show what was due, what ran, and what
was deferred by cadence or parallelism so that I can diagnose delays without reading
application internals.

**Why this priority**: Operational transparency reduces incident triage time and helps
teams trust source-specific scheduling decisions.

**Independent Test**: Trigger runs under mixed cadence and contention conditions and
verify run records expose source eligibility and final outcomes clearly.

**Acceptance Scenarios**:

1. **Given** a run where some sources are due and others are not,
   **When** the run completes, **Then** persisted run records distinguish executed,
   skipped-not-due, and failed sources.
2. **Given** a run where parallelism gates launch order,
   **When** the run completes, **Then** run metadata shows all due sources were either
   completed or explicitly reported as failed.

---

### Edge Cases

<!--
  ACTION REQUIRED: The content in this section represents placeholders.
  Fill them out with the right edge cases.
-->

- What happens when many sources become due at the same tick and the parallelism limit
  is much smaller than the due count?
- How does the scheduler behave when cadence metadata is missing, malformed, or points
  to a timestamp in the future?
- What happens when a run starts with a source marked due, but another run has already
  acquired execution rights for that same source?
- How are failed sources retried relative to cadence rules, and how is immediate retry
  bounded to avoid starvation of other due sources?

## Requirements _(mandatory)_

<!--
  ACTION REQUIRED: The content in this section represents placeholders.
  Fill them out with the right functional requirements.
-->

### Functional Requirements

- **FR-001**: System MUST support a configurable maximum number of concurrently active
  source executions per orchestration run.
- **FR-002**: System MUST prevent active source executions from exceeding the configured
  concurrency limit at any time during a run.
- **FR-003**: System MUST continue processing remaining due sources when an individual
  source fails, unless an explicit operator stop action is requested.
- **FR-004**: Each source MUST define an explicit scheduling cadence and eligibility
  metadata that determines when it is due to run.
- **FR-005**: Scheduler evaluation MUST select only sources that are due at evaluation
  time and MUST exclude not-due sources.
- **FR-006**: System MUST persist per-run source eligibility and outcome states,
  including executed, not-due, succeeded, failed, and skipped-by-policy conditions.
- **FR-007**: Operators MUST be able to trigger on-demand execution for a selected
  subset of sources regardless of due-state, without modifying cadence metadata.
- **FR-008**: System MUST keep source-level coordination rules that prevent duplicate
  execution of the same source in overlapping runs.
- **FR-009**: System MUST expose run-level summaries that report counts for due,
  executed, succeeded, failed, and deferred sources.
- **FR-010**: System MUST apply deterministic source selection and launch behavior so
  repeated runs with identical eligibility state produce the same launch ordering.
- **FR-011**: When due sources exceed execution capacity, system MUST defer and later
  schedule sources using strict FIFO order by earliest due timestamp.
- **FR-012**: If a source is already active in another run, system MUST wait for that
  active run to finish and MUST NOT launch a duplicate execution for the same source.
- **FR-013**: If a scheduled run reaches the next scheduler tick with due work
  remaining, system MUST allow active executions to finish and carry remaining due
  sources forward as deferred for subsequent runs.
- **FR-014**: System MUST emit warning-level operational signals whenever due sources
  are carried forward because run capacity or run duration was insufficient.
- **FR-015**: If cadence policy metadata is missing or malformed, system MUST skip
  source execution, classify the source as `skipped_invalid_policy`, and emit
  warning-level operational signals for operator follow-up.

### Key Entities _(include if feature involves data)_

- **Source Schedule Policy**: Defines one source's cadence, due-window rules,
  activation status, and last successful execution reference used for eligibility.
- **Source Eligibility Snapshot**: Captures per-source due/not-due evaluation at run
  creation time with reason codes for operator visibility.
- **Run Concurrency Policy**: Represents bounded-parallel execution constraints used to
  gate active source launches within a run.
- **Source Execution Outcome**: Stores each source's terminal state for a run,
  including success, failure, deferred, and policy-skipped classifications.

## Assumptions

- Existing source workflow registration remains the source of truth for available
  sources, and schedule metadata will be attached to those registrations.
- One global scheduler tick remains acceptable as long as per-source eligibility
  determines which sources are selected.
- Source failures are isolated and should not cancel unrelated due sources by default.
- Operators require persisted auditability of eligibility and execution outcomes for
  troubleshooting and capacity planning.

## Success Criteria _(mandatory)_

<!--
  ACTION REQUIRED: Define measurable success criteria.
  These must be technology-agnostic and measurable.
-->

### Measurable Outcomes

- **SC-001**: During runs with at least 2x more due sources than concurrency capacity,
  observed active source executions remain at or below configured parallelism in 100%
  of sampled runs.
- **SC-002**: For mixed-cadence source portfolios, at least 95% of sampled scheduler
  ticks execute only sources that are due at evaluation time.
- **SC-003**: For daily operations over a two-week observation window, no source with
  hourly or daily cadence misses two consecutive due windows due to queue saturation.
- **SC-004**: Operators can identify the reason a source did or did not execute for a
  run from persisted run records in under 5 minutes for 95% of triage checks.

## Constitution Alignment _(mandatory)_

<!--
  ACTION REQUIRED: Confirm this feature complies with repository constitution rules.
  Any item marked "No" requires explicit owner-approved exception before implementation.
-->

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
