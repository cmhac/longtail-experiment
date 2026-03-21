# Contract: Ingest Orchestration

## Purpose

Define orchestration lifecycle, trigger handling, and run outcome semantics for multi-source time-series ingestion.

## Version

- Contract: ingest-orchestration
- Version: v1
- Status: Draft for implementation planning

## Trigger Contract

- Supported trigger modes:
  - scheduled
  - on_demand
- Every triggered run MUST include:
  - runId
  - triggerType
  - requestedAt
  - requestedBy (system or operator identity)

## Run Lifecycle Contract

- Allowed lifecycle states:
  - queued
  - running
  - completed
  - failed
- Allowed outcome states:
  - success
  - partial_success
  - failure

## Outcome Semantics

- `success`: all source workflows completed with no source-level failure.
- `partial_success`: one or more source workflows failed and one or more source workflows succeeded.
- `failure`: all source workflows failed or run infrastructure failed before any source succeeded.

## Source Failure Policy

- A source workflow failure MUST NOT stop unaffected source workflows in the same run.
- Run summary MUST include source-level status and count metrics for accepted, quarantined, failed, duplicate no-op, and conflict outcomes.

## Concurrency Policy

- Per source workflow:
  - at most one active run
  - at most one deduplicated queued trigger
- New triggers while active + queued already exist MUST be deduplicated into the existing queued token.

## Validation Rules

- Every completed run MUST have an outcome state.
- Every source workflow executed in a run MUST produce one source-level outcome record.
- Partial-success runs MUST include both success and failure source-level outcomes.

## Compatibility and Evolution

- New outcome counters are additive.
- Breaking lifecycle or outcome semantic changes require version bump and migration notes.
