# Contract: Series Ownership and Triggering

## Purpose

Define behavioral contracts for grouped and split series ownership, including independent operator triggering and schedule-attribution guarantees.

## Scope

- Series-level operability under grouped provider adapters.
- Split-adapter ownership support for cadence divergence.
- Trigger-attribution and duplicate-prevention expectations.

## Contract Definitions

### 1) Series Registration Contract

Requirements:

- Each series item must have a stable series identity.
- Each active series item must declare one active ownership mode.
- Grouped ownership must declare provider grouping metadata visible to operators.

Validation outcomes:

- Invalid when series identity is missing or duplicated.
- Invalid when ownership mode is missing for an active series.
- Invalid when ownership references an unknown adapter key.

### 2) Execution Selection Contract

Requirements:

- Operators must be able to trigger one series item without forcing unrelated series execution.
- Grouped adapter runs may execute multiple series in one run when requested by grouped ownership semantics.
- Split adapter runs must execute only the dedicated owned series unless an explicit multi-series selection is requested.

Validation outcomes:

- Invalid selection requests must fail fast with actionable diagnostics.
- Selection must always report the final resolved series set.

### 3) Schedule Ownership Contract

Requirements:

- Every scheduled execution must identify the owning schedule and ownership mode.
- Coexisting grouped and split models must not trigger duplicate scheduled executions for the same series in the same cadence window.
- Ownership transitions must define an effective boundary where only one schedule path is authoritative.

Validation outcomes:

- Duplicate ownership windows are invalid.
- Missing schedule attribution metadata is invalid for scheduled runs.

### 4) Outcome Visibility Contract

Requirements:

- Each run must preserve per-series outcome visibility with status and counters.
- Grouped runs must not collapse series outcomes into untraceable aggregate-only records.
- Failure diagnostics must identify impacted series explicitly.

Validation outcomes:

- Missing series-level outcome records are invalid.
- Ambiguous failure attribution is invalid.

### 5) Ownership Transition Contract

Requirements:

- Transition from grouped to split (or reverse) must include duplicate-trigger prevention and explicit operational guidance.
- Historical outcome traceability must remain intact across ownership transitions.

Validation outcomes:

- Transition is invalid if overlapping active ownership causes duplicate schedule authority.
- Transition is invalid if historical traceability for moved series is lost.

## Non-Goals

- Forcing all providers into a single ownership strategy.
- Reintroducing shared all-source schedule authority.

## Evidence Expectations

Acceptance evidence should include:

- Grouped run with two series and distinct outcomes.
- Independent series trigger showing isolated execution.
- Mixed grouped/split schedule validation with zero duplicate triggers.
- One ownership transition simulation demonstrating preserved traceability.
