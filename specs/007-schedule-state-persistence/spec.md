# Feature Specification: Schedule State Persistence

**Feature Branch**: `[007-schedule-state-persistence]`
**Created**: 2026-03-22
**Status**: Draft
**Input**: User description: "Wire the existing source_schedule_policies table so that per-source cadence enforcement is backed by durable run history rather than in-memory state that resets on every pipeline restart"

## Clarifications

### Session 2026-03-22

- Q: Should the scheduler write a policy record for a source that fails, or only for success? -> A: Only successful runs update the schedule state. Failed and not-due outcomes leave the timestamp unchanged so the source will be retried on the next trigger.
- Q: Should on-demand runs also update last_successful_at? -> A: Yes — on-demand runs should update the schedule record if the source succeeds, since the data was genuinely refreshed regardless of trigger type.
- Q: If a source has no schedule policy attached at registration time, should a default be synthesized and persisted? -> A: No. The write path should only upsert when a registration has an explicit schedule policy; unregistered sources continue using the in-memory fallback silently.

## User Scenarios & Testing _(mandatory)_

### User Story 1 - Enforce Per-Source Cadence Across Runs (Priority: P1)

As a data operations owner, I need each source to only re-run after its declared
cadence has fully elapsed since its last successful execution so that hourly
orchestrator ticks do not cause redundant re-fetches for daily or weekly sources.

**Why this priority**: Without cadence enforcement backed by real run history, every
orchestrator tick executes every source, wasting resources and over-calling external
data providers.

**Independent Test**: Run the pipeline with all sources succeeding, then immediately
trigger a second run. Verify that all sources are classified as not-due in the second
run and no source executions are attempted.

**Acceptance Scenarios**:

1. **Given** sources with daily cadence that just ran successfully, **When** the
   orchestrator fires again before a full day has passed, **Then** all such sources
   are marked not-due and skipped without executing.
2. **Given** a source with daily cadence whose last successful run was more than one
   day ago, **When** the orchestrator fires, **Then** that source is marked due and
   executes while other recently-run sources remain skipped.
3. **Given** a source with hourly cadence and a source with daily cadence, both just
   run, **When** the orchestrator fires 90 minutes later, **Then** only the hourly
   source is due; the daily source is still skipped.

---

### User Story 2 - Preserve Schedule State Across Restarts (Priority: P2)

As a pipeline operator, I need the last-successful-run timestamp for each source to
survive pipeline restarts and redeployments so that a service restart does not cause
all sources to appear due simultaneously.

**Why this priority**: In-memory state that resets on restart means any deployment
causes a burst of all-source execution, which can overload external APIs and produce
duplicate observations.

**Independent Test**: Run the pipeline so all sources succeed. Restart the pipeline
process. Trigger the orchestrator again and verify sources are still not-due, with no
burst execution.

**Acceptance Scenarios**:

1. **Given** all sources ran successfully before a pipeline restart, **When** the
   pipeline restarts and the orchestrator fires, **Then** sources that are not yet due
   remain not-due and are not re-executed.
2. **Given** a source that was due at the time of restart, **When** the pipeline
   restarts and the orchestrator fires, **Then** that source is correctly identified
   as due and executes normally.

---

### User Story 3 - Inspect and Reset Source Schedule State (Priority: P3)

As a pipeline operator, I need to inspect each source's current schedule record and
manually reset it when necessary so that I can force a specific source to re-run
immediately or recover from a stuck/misconfigured schedule entry.

**Why this priority**: Operational hygiene — operators need a reliable recovery path
when a source appears stuck or when a manual re-baseline is required after data
correction.

**Independent Test**: Artificially advance a source's last-successful-at timestamp to
two days in the past. Trigger the orchestrator. Verify the source is classified as due
and executes while other sources remain not-due.

**Acceptance Scenarios**:

1. **Given** a source whose last-successful-at is backdated by more than its cadence
   interval, **When** the orchestrator fires, **Then** the source is selected as due
   and executes as if it had not run recently.
2. **Given** a cleared schedule state for all sources (empty table), **When** the
   orchestrator fires, **Then** all sources are treated as never-run and execute as
   due regardless of their cadence.

---

### Edge Cases

- What happens when a source's cadence is changed in code between runs? The DB row
  stores the cadence that was active when the last upsert happened; the code value
  overrides it on the next successful run.
- What happens if the DB is unavailable when the coordinator tries to read schedule
  policies? The read is best-effort via duck-typed getattr; if not callable, sources
  default to always-due (safe fail-open that matches prior behavior).
- What happens if a source succeeds but the upsert fails? The source ran successfully;
  on the next trigger it will appear due again and re-execute (safe duplicate risk,
  not data loss).
- What happens when a brand-new source is registered with no prior DB entry? It has no
  row, so `last_successful_at` is None, causing `resolve_due_at` to return the current
  evaluation time — the source is always due on first run.

## Requirements _(mandatory)_

### Functional Requirements

- **FR-001**: After a source executes successfully, the system MUST persist the
  completion timestamp as `last_successful_at` for that source in durable storage.
- **FR-002**: Before evaluating which sources are due for a scheduled run, the system
  MUST read persisted `last_successful_at` values and apply them to each source's
  cadence policy before computing due-state.
- **FR-003**: Schedule state MUST survive pipeline process restarts; cadence enforcement
  MUST produce the same outcomes before and after a process restart given identical
  persisted state.
- **FR-004**: Sources with no persisted schedule record MUST be treated as never-run
  and considered immediately due regardless of cadence.
- **FR-005**: Only successful source outcomes MUST update the schedule record; failed,
  deferred, and not-due outcomes MUST leave the existing record unchanged.
- **FR-006**: Schedule state reads and writes MUST be scoped per source by source key
  so each source's cadence is evaluated and updated independently.
- **FR-007**: Operators MUST be able to manipulate schedule state directly (reset,
  backdate, clear) to force specific re-run behavior without modifying source code.
- **FR-008**: The system MUST update the cadence type in the schedule record whenever
  it upserts, so stored cadence reflects the currently registered value.

### Key Entities _(include if feature involves data)_

- **Source Schedule Policy** (persisted): Durable record of one source's cadence type,
  last successful execution time, and metadata required to compute the next due window.
- **Schedule Hydration Context**: The in-memory policy state built by merging the
  registered in-code cadence type with the DB-persisted `last_successful_at` before
  eligibility evaluation on each run.

## Assumptions

- The `source_schedule_policies` table already exists in the database (created by
  migration 0003) with the required columns; no new migration is needed.
- Sources are identified by a stable `source_key` string that matches across code
  registration and DB records.
- Run completion timestamp (`completed_at`) is an acceptable and sufficiently precise
  proxy for `last_successful_at`; sub-second accuracy is not required.
- The coordinator's run repository is accessed via duck-typed optional methods
  (`getattr`), preserving the existing integration pattern with no new protocols needed.
- On-demand runs that succeed should also update schedule state, since data was
  genuinely refreshed.

## Success Criteria _(mandatory)_

### Measurable Outcomes

- **SC-001**: After any run where all sources succeed, a subsequent immediate run
  reports 0 executed sources and all sources as not-due in 100% of observations.
- **SC-002**: Following a pipeline process restart, source due-state matches the
  pre-restart state within a single orchestrator tick in 100% of observations.
- **SC-003**: Manually backdating a source's schedule record by more than its cadence
  interval causes that source to be selected as due on the next run in 100% of trials.
- **SC-004**: Over a two-week observation window, no source with daily cadence executes
  more than once per 23-hour window under normal operating conditions.

## Constitution Alignment _(mandatory)_

- **Monorepo cohesion**: Changes are confined to the pipeline orchestration app and
  shared DB runtime persistence; no cross-boundary contracts are broken.
- **Quality gates**: All lint, format, typecheck, test, and coverage gates remain
  mandatory with no suppressions introduced.
- **Test and coverage discipline**: New persistence behavior is covered by both unit
  tests (in-memory mocks) and integration tests (live DB) maintaining ≥90% coverage.
- **Local-first parity**: Full behavior is exercisable via local Docker Compose DB
  and the existing local run harness without any cloud dependency.
- **Data integrity**: DB write uses `ON CONFLICT (source_key) DO UPDATE` to prevent
  duplicate rows and ensure atomicity of each policy update.
- **Documentation fidelity**: Quickstart and runbook are updated to include schedule
  state verification and manual reset procedures.
