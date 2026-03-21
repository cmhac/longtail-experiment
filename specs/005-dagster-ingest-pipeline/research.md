# Research: Dagster-Orchestrated Time-Series Ingestion

## Orchestration Trigger Model

- Decision: Support both scheduled and manual on-demand ingestion triggers in the same orchestration entry point.
- Rationale: Scheduled runs cover baseline freshness, while on-demand runs support operator reruns and incident recovery without waiting for the next schedule tick.
- Alternatives considered:
  - Scheduled-only operation: rejected because recovery latency is too high after upstream failures.
  - On-demand-only operation: rejected because routine ingestion reliability and cadence discipline degrade.

## Mixed Outcome Run Semantics

- Decision: Continue unaffected source workflows when one source fails and classify the overall run as partial success.
- Rationale: Source-level isolation preserves data freshness for healthy sources while exposing failure clearly for remediation.
- Alternatives considered:
  - Fail fast across all sources: rejected because it creates unnecessary freshness gaps.
  - Report run success if any source succeeds: rejected because it obscures failure severity.

## Per-Source Concurrency Policy

- Decision: Enforce one active run plus one deduplicated queued run per source workflow.
- Rationale: Prevents conflicting overlap while preserving one pending trigger for eventual consistency.
- Alternatives considered:
  - Allow unrestricted overlap: rejected due to duplicate write and race risk.
  - Reject all concurrent triggers: rejected because ingestion intent can be lost.
  - Cancel in-flight run with newer trigger: rejected because in-progress work is discarded unpredictably.

## Duplicate Drift and Conflict Handling

- Decision: Apply deterministic drift checks for same series-period records: exact-match duplicates are no-op; non-matching duplicates are persisted as queryable conflict records with both record contexts.
- Rationale: Avoids redundant writes while preserving auditability and triage visibility when source values conflict.
- Alternatives considered:
  - Overwrite existing values automatically: rejected due to data loss risk and hidden quality issues.
  - Quarantine conflicting duplicate only: rejected because operators need both record contexts for investigation.
  - Fail entire source workflow on conflict: rejected because one conflict should not block all other valid records.

## Dagster Integration Pattern

- Decision: Use a modular orchestration package with definitions, jobs, schedules, sensors, and resources; source adapters register into a bounded workflow registry.
- Rationale: Keeps source-specific logic isolated while maintaining one operational run lifecycle.
- Alternatives considered:
  - Monolithic single-job code path: rejected due to poor extensibility for many sources.
  - Separate orchestrator per source: rejected because operational consistency and maintainability degrade.

## Persistence Strategy for Runtime Writes

- Decision: Implement concrete shared DB repository adapters for ingestion outcomes and conflict persistence under `libs/db/src/db/repositories` while retaining `libs/db/alembic` as migration authority.
- Rationale: Existing in-memory adapters are insufficient for operational ingestion and audit persistence.
- Alternatives considered:
  - Keep in-memory repositories for runtime: rejected because data is not durable.
  - Pipeline-local DB logic: rejected because it violates shared persistence boundaries.

## Observability and Operational Signals

- Decision: Require structured run-level and source-level signals for accepted, quarantined, failed, duplicate no-op, and conflict records.
- Rationale: Operators need explicit status and count visibility to diagnose partial-success runs quickly.
- Alternatives considered:
  - Coarse pass/fail only: rejected because conflict and no-op outcomes become invisible.

## Verification Scope

- Decision: Add orchestration tests for trigger modes, partial-success semantics, concurrency queue behavior, and duplicate conflict classification alongside existing contract tests.
- Rationale: Clarified requirements directly affect operational correctness and should be guarded by automated tests.
- Alternatives considered:
  - Manual verification only: rejected due to repeatability and regression risk.

## Clarification Resolution Checklist

- Scheduled and manual trigger support: Resolved
- Partial-success run behavior: Resolved
- Per-source active/queued concurrency policy: Resolved
- Duplicate no-op and conflict persistence policy: Resolved
