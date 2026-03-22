# Contract: Source-Asset Orchestration Cutover

**Feature**: 010-source-asset-migration  
**Audience**: Platform engineers and operators responsible for ingest orchestration

## Purpose

Define required behavior for source-per-asset registration, trigger flow, scheduling authority, and post-cutover failure handling.

## Source Registration Contract

1. Each source module exposes the required registration contract for source-asset loading.
2. Registration is deterministic across runs.
3. Duplicate source keys are rejected at startup with actionable validation errors.
4. Invalid modules fail startup validation with module-specific failure details.

## Triggering Contract

1. Operators can trigger a single source without running unrelated sources.
2. Invalid source keys are rejected before execution.
3. Trigger outcome includes source-level status and run metadata visibility.

## Scheduling Authority Contract

1. After cutover, Dagster-native schedules and automation are the sole cadence authority.
2. Legacy non-Dagster scheduling/coordinator cadence paths remain disabled.
3. Any attempt to invoke retired cadence paths does not create ingest runs.

## Big-Bang Cutover Contract

1. Cutover is executed in one release window after readiness gate checks pass.
2. If a subset of sources fails during cutover, scheduling authority still remains Dagster-only.
3. Failing sources are recovered through source-asset operational paths, not legacy scheduling fallback.

## Outcome Visibility Contract

1. Post-cutover runs emit source-level outcomes for both successful and failed executions.
2. Run summary and source outcome records remain accessible for operator triage.
3. Failure records include enough context for remediation workflows.

## Verification Contract

A release is acceptable only when all outcomes are true:

1. All in-scope sources are represented as source assets.
2. Source-level manual trigger succeeds for valid keys and rejects invalid keys.
3. No non-Dagster scheduling path initiates production cadence runs.
4. Regression tests for scheduled, manual, deferred, and locked scenarios pass.
5. Runbook and onboarding docs describe the source-as-asset operating model.

## Out-of-Scope Contract

This feature does not define:

1. Historical data parity/backfill SLA for pre-cutover records.
2. Legacy scheduler rollback as a normal operational recovery path.
3. New backend public API surface unrelated to orchestration migration behavior.
