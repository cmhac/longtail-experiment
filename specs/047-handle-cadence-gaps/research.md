# Research: Gap-Tolerant Cadence Inference

## Decision 1: Introduce ratio-based tolerance for off-cadence gaps

- Decision: Treat a series as cadence-valid when off-cadence intervals remain at or below a fixed irregular-gap ratio threshold, provided all cadence-valid intervals map to one dominant cadence family.
- Rationale: The current all-or-nothing cadence rule fails for long mostly-regular histories with rare historical discontinuities. A ratio-based policy accepts isolated data gaps while preserving explicit rejection for truly mixed spacing.
- Alternatives considered:
  - Keep strict single-cadence-only rule: rejected because it fails known valid long-running weekly series with one historical discontinuity.
  - Allow any number of off-cadence intervals: rejected because it weakens true-irregular guardrails.

## Decision 2: Set threshold to 0.20% irregular-gap ratio

- Decision: Set `MAX_IRREGULAR_GAP_RATIO = 0.002` (0.20% of adjacent intervals).
- Rationale: The observed reference EIA series (`ENERGY.US.RETAIL_GASOLINE.NUS`) has 1 irregular gap in 1852 intervals (0.0540%). A 0.20% threshold gives ~3.7x headroom over reference behavior while still requiring >99.8% cadence consistency.
- Alternatives considered:
  - 0.10%: rejected because it gives less room for slightly gappier but still practically regular series.
  - 0.50%+: rejected because tolerance becomes too permissive for mixed-spacing histories.

## Decision 3: Keep dominant-cadence uniqueness requirement

- Decision: Even with tolerated off-cadence intervals, all cadence-valid intervals must belong to exactly one cadence family (`daily`, `weekly`, or `monthly`).
- Rationale: This prevents blended weekly/monthly histories from being accepted as gap-tolerant when they are actually mixed cadence.
- Alternatives considered:
  - Pick most frequent cadence regardless of secondary cadence presence: rejected because it can hide genuinely mixed update behavior.

## Decision 4: Preserve existing hard-failure guards

- Decision: Keep explicit failures for fewer than minimum observations and non-increasing periods unchanged.
- Rationale: These are structural validity failures, not gap-tolerance candidates.
- Alternatives considered:
  - Soften these conditions with tolerance: rejected because trend windows become unreliable and non-deterministic.

## Decision 5: Emit cadence decision metadata for operations

- Decision: Include explicit cadence decision reason metadata in trend processing outcomes (`regular`, `gap_tolerant`, `irregular_rejected`) and include interval statistics needed for operator diagnosis.
- Rationale: The feature introduces a policy decision; operators need transparency to distinguish accepted gaps from rejected irregularity.
- Alternatives considered:
  - No metadata changes: rejected because run outcomes become harder to audit and explain.

## Decision 6: Apply same policy in backfill and incremental paths

- Decision: Use one cadence policy for every evaluation path in runtime processing (historical backfill and latest-only incremental processing).
- Rationale: Mixed policies would create non-deterministic historical outcomes across reruns.
- Alternatives considered:
  - Different tolerance by path: rejected due to deterministic reproducibility risk.

## Reference Measurement Used for Threshold

- Series measured: `ENERGY.US.RETAIL_GASOLINE.NUS`
- Interval count: 1852
- Irregular intervals: 1
- Observed irregular-gap ratio: 0.0540%
- Chosen threshold: 0.20% (allows up to 3 irregular intervals at this series length, still rejects materially mixed spacing)

## Repository Seams Confirmed

- Cadence logic: `libs/trend_analysis/src/trend_analysis/cadence.py`
- Cadence tests: `libs/trend_analysis/tests/test_cadence_and_failures.py`
- Runtime trend orchestration entry: `apps/pipeline/src/orchestration/jobs/trend_runtime_processor.py`
- Runtime processor tests: `apps/pipeline/tests/orchestration/test_trend_runtime_processor.py`
- Source-level failure mapping: `apps/pipeline/src/orchestration/jobs/parallel_source_executor.py`

## Planning Outcome

- All technical unknowns for thresholding and policy behavior are resolved.
- No `NEEDS CLARIFICATION` markers remain for planning.
- Phase 1 design artifacts can proceed with fixed threshold and validation expectations.

## Threshold rationale and deterministic decision notes

- Threshold remains fixed at `MAX_IRREGULAR_GAP_RATIO = 0.002` (0.20%).
- Dominant cadence requirement remains strict: exactly one supported cadence family (`daily`, `weekly`, `monthly`) must be present among cadence-valid intervals.
- Decision reason-code surface is deterministic for identical ordered inputs:
  - `regular_spacing`
  - `isolated_irregular_gaps_tolerated`
  - `irregular_gap_ratio_exceeds_threshold`
  - `mixed_cadence_families`
  - `no_supported_cadence_gaps`
  - `non_increasing_periods`
  - `insufficient_observations`
- Gap tolerance is bounded and explicit:
  - accepted only when a dominant cadence exists and irregular-gap ratio is `<= 0.002`
  - true irregular rejections still propagate as `trend_processing_failed` at source level
  - gap-tolerant and regular outcomes continue lookback/canonical persistence
