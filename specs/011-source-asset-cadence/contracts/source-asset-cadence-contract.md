# Contract: Source Asset Cadence Ownership

## Status

- Feature: 011-source-asset-cadence
- Contract Type: Orchestration runtime and operator behavior contract
- Scope: Scheduled and on-demand source execution behavior after hard cutover

## 1. Scheduling Authority Contract

1. Each active source asset has independent schedule ownership.
2. Shared all-source scheduled execution authority is not active post-cutover.
3. Scheduled execution decisions are derived from source-owned schedule definitions.

## 2. Trigger Contract

### Scheduled Trigger

- Input Conditions:
- Source asset schedule is active.
- Current window matches source cadence.
- Expected Behavior:
- Create a run request attributable to the source schedule.
- Execute source-specific ingestion path.
- Emit run visibility records with source and trigger attribution.

### On-Demand Trigger

- Input Conditions:
- Operator requests source-specific execution.
- Expected Behavior:
- Execute selected source regardless of current scheduled due window.
- Preserve source-level run visibility and trigger attribution.

## 3. Run Attribution Contract

Every run record emitted from scheduled execution must include:

- source_key
- trigger_type
- trigger_origin
- outcome_state
- source-level outcome details

## 4. Legacy Coexistence Contract

1. Pre-cutover schedule-policy and eligibility artifacts are historical-only.
2. Legacy artifacts remain queryable according to retention expectations.
3. Legacy artifacts must not influence active post-cutover schedule decisions.

## 5. Failure and Concurrency Contract

1. Failure of one source schedule run must not block unrelated source schedules from their own windows.
2. Concurrent or overlapping source runs must preserve source-level lock and safety behavior.
3. Duplicate scheduled execution for the same source and cadence window is prohibited.

## 6. Operator Visibility Contract

1. Operator interfaces must expose source assets and their schedule associations.
2. Operators must be able to identify scheduled versus on-demand trigger origin per source run.
3. Troubleshooting workflows must remain supported through source-level outcomes and run history.

## 7. Verification Contract

A release satisfies this contract when:

1. All active source assets have independent schedule ownership.
2. No shared all-source schedule is active.
3. Scheduled and on-demand runs both maintain source-level attribution and outcomes.
4. Quality and local-stack verification workflows pass with no bypasses.
