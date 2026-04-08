# Data Model: Trend Analysis Upgrade (Spec 050)

## Entity: ObservationSeriesWindow

- Purpose: Ordered windowed series input per dataset metric and lookback horizon for trend evidence computation.
- Fields:
  - data_series_id (string, required)
  - canonical_series_key (string, required)
  - as_of_observed_on (date, required)
  - lookback_points (integer, required)
  - values (array<number>, required)
  - observed_on (array<date>, required)
  - reported_at (array<datetime>, required)
  - cadence_label (enum, required)
  - cadence_regularity_state (enum: `regular` | `irregular`, required)
- Validation rules:
  - Window ordering is deterministic by `(observed_on, reported_at)`.
  - `values`, `observed_on`, and `reported_at` lengths must match.

## Entity: LookbackApplicabilityRecord

- Purpose: Per-observation per-lookback applicability and reason tracking.
- Fields:
  - data_series_id (string, required)
  - as_of_observed_on (date, required)
  - lookback_points (integer, required)
  - applicability_state (enum: `applicable` | `inapplicable`, required)
  - reason_code (string | null)
  - evaluated_at (datetime, required)
- Validation rules:
  - Every configured lookback must have exactly one applicability record.
  - Inapplicable windows must include explicit `reason_code`.

## Entity: PreprocessingMetadata

- Purpose: Traceable metadata describing smoothing/seasonal adjustment behavior used before scoring.
- Fields:
  - applied (boolean, required)
  - smoothing_method (enum: `ewma` | `none`, required)
  - smoothing_params (object, required)
  - seasonal_adjustment_method (enum: `stl` | `mstl` | `none`, required)
  - seasonal_periods (array<integer>, required)
  - seasonal_reliability_state (enum: `reliable` | `fallback_non_adjusted` | `not_applicable`, required)
  - warmup_points (integer, required)
  - missing_input_points (integer, required)
  - preprocess_version (string, required)
- Validation rules:
  - `smoothing_method=ewma` requires populated EWMA parameters.
  - `seasonal_adjustment_method=stl|mstl` requires cadence eligibility and reliability checks.

## Entity: LookbackTrendSnapshotV2

- Purpose: Versioned per-lookback trend evidence payload.
- Fields:
  - data_series_id (string, required)
  - as_of_observed_on (date, required)
  - lookback_points (integer, required)
  - applicability_state (enum, required)
  - descriptor_state (enum: `available` | `unavailable`, required)
  - direction (enum: `up` | `down` | `flat` | null)
  - confidence_score (number | null, range 0..1)
  - trend_label (string | null)
  - dominant_measure_family (enum: `theil_sen` | `mixed` | `none`, required)
  - theil_sen_slope (number | null)
  - theil_sen_low_slope (number | null)
  - theil_sen_high_slope (number | null)
  - kendall_tau (number | null)
  - kendall_pvalue (number | null)
  - ols_slope (number | null)
  - ols_intercept (number | null)
  - ols_r_squared (number | null)
  - ols_pvalue (number | null)
  - preprocessing (PreprocessingMetadata, required)
  - reason_code (string | null)
- Validation rules:
  - `descriptor_state=unavailable` requires `direction=null` and `confidence_score=null`.
  - Applicable lookbacks with `descriptor_state=available` must include Theil-Sen slope.
  - OLS fields are supplementary and may be null when unavailable.

## Entity: CanonicalTrendDescriptorV2

- Purpose: Single canonical descriptor selected from applicable lookback evidence.
- Fields:
  - data_series_id (string, required)
  - as_of_observed_on (date, required)
  - descriptor_version (string, required)
  - descriptor_state (enum: `available` | `unavailable`, required)
  - direction (enum: `up` | `down` | `flat` | null)
  - confidence_score (number | null, range 0..1)
  - trend_label (string | null)
  - selected_lookback_points (integer | null)
  - dominant_measure_family (enum: `theil_sen` | `mixed` | `none`, required)
  - medium_horizon_weight (number | null)
  - short_horizon_weight (number | null)
  - long_horizon_weight (number | null)
  - preprocessing (PreprocessingMetadata, required)
  - ols_slope (number | null)
  - ols_intercept (number | null)
  - ols_r_squared (number | null)
  - ols_pvalue (number | null)
  - reason_code (string | null)
- Validation rules:
  - Irregular-cadence rejection requires `descriptor_state=unavailable` and `reason_code=cadence_irregular_rejected`.
  - Only one canonical descriptor exists per `(data_series_id, as_of_observed_on, descriptor_version)`.
  - `flat` is valid available direction and does not create reversal events.

## Entity: ChangePointContextMetadata

- Purpose: Additive context metadata used only for tie-break/context modulation.
- Fields:
  - data_series_id (string, required)
  - as_of_observed_on (date, required)
  - detector (enum: `ruptures`, required)
  - cp_count_recent_window (integer, required)
  - distance_since_last_cp (integer | null)
  - cp_density (number | null)
  - context_score (number | null, range 0..1)
  - influencing_scope (enum: `none` | `tie_break_only`, required)
- Validation rules:
  - Must not override directional decision from primary evidence.
  - If absent, canonical computation still completes.

## Entity: TrendChangeEvent

- Purpose: Persisted directional transition event for notification fan-out and audit.
- Fields:
  - event_id (UUID, required)
  - data_series_id (string, required)
  - previous_direction (enum: `up` | `down`, required)
  - current_direction (enum: `up` | `down`, required)
  - effective_observed_on (date, required)
  - processing_context (enum: `incremental` | `historical_reprocessing`, required)
  - visibility_classification (enum: `user_visible` | `audit_only`, required)
  - idempotency_fingerprint (string, required)
- Validation rules:
  - Events are created only for `up <-> down` transitions.
  - Transitions involving `flat` or unavailable descriptors are non-event transitions.

## Relationships

- One `ObservationSeriesWindow` yields one `LookbackApplicabilityRecord` and at most one `LookbackTrendSnapshotV2` per configured lookback.
- Multiple `LookbackTrendSnapshotV2` records feed one `CanonicalTrendDescriptorV2` for the same as-of point.
- `ChangePointContextMetadata` can decorate canonical arbitration but cannot replace it.
- `CanonicalTrendDescriptorV2` transitions may yield `TrendChangeEvent` only when directional eligibility rules pass.

## State Transitions

- Applicability determination -> inapplicable windows persist reason only.
- Applicable windows -> preprocessing -> Theil-Sen + Kendall + OLS snapshot evidence.
- Canonical arbitration combines applicable snapshots with weighted horizons and confidence modifiers.
- Rejection precedence check can force unavailable canonical descriptor.
- Canonical change detection:
  - `up <-> down`: eligible event
  - `flat` transitions: descriptive only, no reversal event
  - unavailable transitions: non-directional

## Determinism and Idempotency Rules

- As-of ordering uses deterministic `(observed_on, reported_at)` tie-breaks.
- Snapshot/canonical recomputation for unchanged data must be reproducible.
- Event idempotency is enforced with deterministic fingerprint boundaries.
- Contract versioning is explicit; only one active version is served after cutover.
