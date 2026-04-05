# Data Model: Gap-Tolerant Cadence Inference

## Entity: ObservationSpacingProfile

- Purpose: Ordered interval profile derived from one series' chronological observations.
- Fields:
  - series_key (string, required)
  - total_intervals (integer, required, >= 0)
  - interval_days (ordered list of integers, required)
  - cadence_class_counts (object, required)
    - daily_count (integer, >= 0)
    - weekly_count (integer, >= 0)
    - monthly_count (integer, >= 0)
    - irregular_count (integer, >= 0)
- Validation rules:
  - Intervals are computed only from strictly increasing observation dates.
  - `daily_count + weekly_count + monthly_count + irregular_count == total_intervals`.

## Entity: GapTolerancePolicy

- Purpose: Policy envelope that defines when off-cadence intervals are treated as tolerated gaps.
- Fields:
  - min_observations_for_cadence (integer, required)
  - supported_cadence_families (set: daily/weekly/monthly, required)
  - max_irregular_gap_ratio (decimal, required)
  - dominant_cadence_required (boolean, required)
- Validation rules:
  - `max_irregular_gap_ratio` is between 0 and 1.
  - Dominant cadence must be unique among cadence-valid intervals.

## Entity: CadenceDecisionOutcome

- Purpose: Deterministic decision record for one series cadence evaluation.
- Fields:
  - series_key (string, required)
  - cadence_state (enum: `regular` | `gap_tolerant` | `irregular_rejected`, required)
  - inferred_cadence (enum: `daily` | `weekly` | `monthly` | null)
  - irregular_gap_count (integer, required)
  - total_interval_count (integer, required)
  - irregular_gap_ratio (decimal, required)
  - reason_code (string, required)
  - reason_detail (string | null)
- Validation rules:
  - `inferred_cadence` is required for `regular` and `gap_tolerant`.
  - `inferred_cadence` is null for `irregular_rejected`.
  - `reason_code` is always present and deterministic for identical inputs.

## Entity: TrendProcessingSeriesOutcome (Extended)

- Purpose: Series-level runtime outcome surfaced to source execution aggregation.
- Fields:
  - series_key (string, required)
  - execution_state (existing outcome state, required)
  - outcome_reason_code (existing reason code, required)
  - cadence_decision (CadenceDecisionOutcome summary, optional but present when cadence evaluation executed)
- Validation rules:
  - Cadence decision metadata is present when cadence inference was attempted.
  - Source-level failure semantics remain unchanged for truly rejected irregular cadence.

## Relationships

- One `ObservationSpacingProfile` is generated from one series observation stream.
- One `GapTolerancePolicy` is applied to one `ObservationSpacingProfile` to produce one `CadenceDecisionOutcome`.
- One `CadenceDecisionOutcome` is embedded in one `TrendProcessingSeriesOutcome` during runtime processing.
- Source-level workflow outcomes aggregate many `TrendProcessingSeriesOutcome` records.

## State Transitions

- Observations loaded -> spacing profile computed.
- Profile evaluated against policy:
  - dominant single cadence + zero irregular ratio -> `regular`
  - dominant single cadence + irregular ratio <= threshold -> `gap_tolerant`
  - otherwise -> `irregular_rejected`
- Runtime trend evaluation:
  - `regular` or `gap_tolerant` -> continue lookback evaluation/persistence.
  - `irregular_rejected` -> surface explicit cadence irregular failure.

## Determinism Rules

- Identical ordered observations MUST produce identical interval counts and cadence decisions.
- Threshold comparison MUST be stable and not sensitive to non-deterministic ordering.
- Backfill and incremental execution paths MUST use identical policy constants and decision rules.
