# Data Model: Current-State Multi-Lookback Trends

## Entity: LookbackDefinition

- Purpose: Canonical catalog entry for one supported lookback depth.
- Fields:
  - lookback_points (integer, logical key; one of 1,2,3,4,5,10,25,50,100,250,500,1000)
  - display_label (string, required)
  - sort_order (integer, required)
  - is_enabled (boolean, required)
- Validation rules:
  - `lookback_points` must be unique and positive.
  - Catalog values are fixed by feature contract.

## Entity: LookbackApplicabilityEvaluation

- Purpose: Persist whether a lookback is applicable for a specific series/observation context.
- Fields:
  - id (uuid, PK)
  - data_series_id (uuid, FK -> data_series.id, required)
  - observation_id (uuid or composite key reference, required)
  - lookback_points (integer, required)
  - applicability_state (enum: applicable | inapplicable, required)
  - reason_code (string, required)
  - reason_detail (string, nullable)
  - created_at (timestamp, required)
- Validation rules:
  - Unique per `(data_series_id, observation_id, lookback_points)`.
  - Inapplicable rows must include `reason_code`.

## Entity: ObservationLookbackTrendSnapshot

- Purpose: Persist current trend outcome for one observation and one applicable lookback.
- Fields:
  - id (uuid, PK)
  - data_series_id (uuid, FK -> data_series.id, required)
  - observation_id (uuid or composite key reference, required)
  - observed_on (date/timestamp, required)
  - lookback_points (integer, required)
  - outcome_state (enum: significant_trend | no_significant_trend, required)
  - trend_label (string, nullable for no_significant_trend)
  - direction (enum: up | down, nullable)
  - strength (string/enum, nullable)
  - seasonality_classification (string/enum, nullable)
  - analysis_version (string, required)
  - created_at (timestamp, required)
- Validation rules:
  - Unique per `(data_series_id, observation_id, lookback_points)`.
  - `trend_label`, `direction`, and `strength` are required when outcome is `significant_trend`.
  - Deterministic output is required for identical ordered observations and analysis version.

## Entity: CanonicalTrendDescriptorSnapshot

- Purpose: Persist weighted canonical trend descriptor derived from applicable lookback snapshots for one observation context.
- Fields:
  - id (uuid, PK)
  - data_series_id (uuid, FK -> data_series.id, required)
  - observation_id (uuid or composite key reference, required)
  - observed_on (date/timestamp, required)
  - descriptor_state (enum: available | unavailable, required)
  - canonical_trend_label (string, nullable)
  - canonical_direction (enum: up | down, nullable)
  - canonical_strength (string/enum, nullable)
  - selected_lookback_points (integer, nullable)
  - weighting_version (string, required)
  - weighting_trace (json/object, nullable)
  - created_at (timestamp, required)
- Validation rules:
  - Unique per `(data_series_id, observation_id)`.
  - `selected_lookback_points` must exist in `LookbackDefinition` when descriptor is available.
  - Unavailable descriptors must carry a reason trace in `weighting_trace` or through paired applicability rows.

## Entity: CanonicalTrendDescriptorPayload (Read Model)

- Purpose: Shared API projection for direct list-row and detail rendering.
- Fields:
  - descriptor_state (available | unavailable)
  - trend_label (nullable)
  - direction (nullable)
  - strength (nullable)
  - selected_lookback_points (nullable)
  - observed_on (nullable)
  - reason_code (nullable)
- Validation rules:
  - Must be render-ready without client-side weighting or lookback ranking logic.
  - When `descriptor_state` is `available`, all semantic render fields required to interpret the current trend must be present.

## Entity: DatasetSummaryWithTrend (Read Model)

- Purpose: Dataset-summary projection used by all dataset list surfaces.
- Fields:
  - dataset_id (string, required)
  - source (object, required)
  - title (string, required)
  - description (nullable)
  - geographic_scope (nullable)
  - topic_tags (array, required)
  - latest_update_at (nullable string)
  - canonical_trend_descriptor (`CanonicalTrendDescriptorPayload`, required)
- Validation rules:
  - Every dataset-summary response must include `canonical_trend_descriptor`, even when the descriptor is unavailable.
  - The summary payload must be sufficient for row rendering without a follow-up detail request.

## Entity: DatasetTrendIndicatorModel (UI Read Model)

- Purpose: Frontend projection of the canonical descriptor into one shared indicator state used on list rows and the detail heading.
- Fields:
  - availability_state (available | unavailable)
  - direction (up | down | nullable)
  - strength (strong | mild | nullable)
  - visual_state (strong_up | mild_up | mild_down | strong_down | unavailable)
- Validation rules:
  - `visual_state` must be derived deterministically from canonical descriptor fields only.
  - Unsupported or incomplete descriptor combinations fall back to `unavailable` rather than heuristic client inference.

## Entity: DatasetDetailCanonicalTrendPayload (Read Model)

- Purpose: Dataset-detail projection for the primary current-trend indicator and supporting diagnostic views.
- Fields:
  - canonical_trend_descriptor (`CanonicalTrendDescriptorPayload`, required)
  - lookback_trend_snapshots (array, required)
- Validation rules:
  - The canonical descriptor remains the primary user-facing current-trend field.
  - Lookback snapshots remain available for explicit applicability and audit context.

## Relationships

- One `DataSeries` has many `LookbackApplicabilityEvaluation` rows.
- One `DataSeries` has many `ObservationLookbackTrendSnapshot` rows.
- One `DataSeries` has many `CanonicalTrendDescriptorSnapshot` rows.
- One observation context has at most one `CanonicalTrendDescriptorSnapshot` and up to N lookback snapshots.
- `DatasetSummaryWithTrend` and `DatasetDetailCanonicalTrendPayload` are both derived from the latest `CanonicalTrendDescriptorSnapshot` for a dataset.
- `DatasetTrendIndicatorModel` is a client-side projection of `CanonicalTrendDescriptorPayload`.

## State Transitions

- Ingestion writes a new observation.
- Trend processing evaluates each lookback:
  - inapplicable -> applicability row only
  - applicable + no signal -> snapshot with `no_significant_trend`
  - applicable + signal -> snapshot with significant descriptor fields
- Weighted heuristic computes canonical descriptor:
  - descriptor resolvable -> `available`
  - descriptor not resolvable -> `unavailable`
- Summary and detail read models both project the latest canonical descriptor:
  - available descriptor -> list/detail indicator can render one directional state
  - unavailable descriptor -> list/detail indicator renders the explicit unavailable state
- Reprocessing the same observation remains idempotent through uniqueness constraints and deterministic recompute rules.

## Migration and Compatibility Notes

- Existing `trend_records` and `trend_transition_events` remain available for backward traceability but are not the primary product read model in this feature scope.
- Dataset-summary contracts must expand to include the canonical current-trend descriptor without forcing endpoint-specific alternative schemas.
- Dataset-detail product behavior remains based on the canonical descriptor payload and no longer depends on trend-overlay interval semantics.
- Reclassification jobs must continue recomputing both lookback snapshots and canonical descriptor snapshots for historical observations when analysis behavior changes.
