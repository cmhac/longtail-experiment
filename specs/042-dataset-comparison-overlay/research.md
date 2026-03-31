# Research: Dataset Comparison Overlay

## Decision 1: Comparison State Persistence Scope

- Decision: Persist comparison selections and chart settings in browser-local storage only.
- Rationale: The spec requires continuity across refresh/navigation in the same browser without expanding scope to account-level synchronization.
- Alternatives considered:
  - Session-only in-memory state: rejected because it loses state on refresh and conflicts with clarified requirements.
  - Server/user-profile persistence: rejected because it introduces auth/profile coupling outside this feature scope.

## Decision 2: Selection Capacity Enforcement

- Decision: Enforce a hard maximum of 5 selected datasets using a single centralized constant.
- Rationale: The spec explicitly fixes the limit to 5 and requires easy future change through one configurable value.
- Alternatives considered:
  - No limit: rejected due to readability/performance risks for multi-series charts.
  - Dynamic limit by viewport/device: rejected as unnecessary complexity for initial rollout.

## Decision 3: Absolute vs Relative Compatibility Behavior

- Decision: Allow observed-value mode only when all selected datasets are unit-compatible; auto-switch to relative mode and disable absolute mode when incompatible.
- Rationale: Aligns with clarified behavior and avoids misleading absolute comparisons while preserving usable comparisons.
- Alternatives considered:
  - Block incompatible datasets at add-time: rejected because spec allows mixed-unit sets for relative comparison.
  - Keep absolute mode enabled with warning only: rejected due to risk of incorrect interpretation.

## Decision 4: Multi-Series Timeline Alignment

- Decision: Use union-of-dates alignment across selected datasets and render missing points as gaps.
- Rationale: Preserves each series' true history while avoiding fabricated interpolations.
- Alternatives considered:
  - Intersection-only dates: rejected because it can discard large portions of valid data.
  - Global resampling/interpolation: rejected because it introduces synthetic values and semantic drift.

## Decision 5: Relative Fixed-Baseline Fallback

- Decision: For each series in fixed-baseline mode, choose nearest prior observation to baseline date; if unavailable, use nearest observation of any kind.
- Rationale: Implements the clarified fallback order with deterministic behavior across irregular cadences.
- Alternatives considered:
  - Exact-match-only baseline: rejected because mixed cadence datasets would frequently become non-comparable.
  - Nearest absolute only: rejected because it can prefer future points over prior context.

## Decision 6: Color Mapping Semantics

- Decision: Keep stable dataset-to-color mapping within the current comparison selection only.
- Rationale: Prevents color churn during interaction while avoiding global color identity commitments.
- Alternatives considered:
  - Positional colors only: rejected due to instability when datasets are added/removed.
  - Global database-wide fixed colors: rejected as out of scope and not required by spec.

## Decision 7: Corrupted Local State Handling

- Decision: Fail hard on invalid/corrupted comparison local state and require explicit user reset.
- Rationale: Directly reflects clarified requirement for strict failure handling over silent recovery.
- Alternatives considered:
  - Auto-reset with notification: rejected because user selected fail-hard behavior.
  - Partial salvage: rejected because it can hide integrity issues in persisted state.

## Decision 8: Existing Code Path Integration Strategy

- Decision: Implement as frontend-first extensions to existing discovery detail/chart modules (`DatasetDetailAnalysis`, `ObservationsChart`, `dataset-detail-view-model`, detail route and shell navigation) while keeping backend detail contract as the source for per-dataset unit metadata.
- Rationale: Current repository patterns already centralize chart behavior and unit inference in detail payloads, enabling incremental adoption with minimal backend surface changes.
- Alternatives considered:
  - New backend compare endpoint first: rejected for initial rollout because frontend can compose from existing detail fetches and avoid contract expansion.
  - Entirely separate chart stack for comparison page: rejected because it duplicates existing chart logic and increases drift risk.
