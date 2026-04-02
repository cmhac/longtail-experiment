# Data Model: Current-State Multi-Lookback Trends

## Entity: LookbackDefinition

- Purpose: Canonical catalog entry for one supported lookback depth.
- Fields:
  - lookback_points (integer, PK-like logical key; one of 1,2,3,4,5,10,25,50,100,250,500,1000)
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
  - `trend_label/direction/strength` required when outcome is significant.
  - Deterministic output for identical ordered observations and analysis version.

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
  - `selected_lookback_points` must exist in LookbackDefinition when descriptor is available.
  - Unavailable descriptors must carry reason trace in `weighting_trace` or paired applicability rows.

## Entity: DatasetDetailCanonicalTrendPayload (Read Model)

- Purpose: Backend API projection for client-side chip rendering.
- Fields:
  - descriptor_state (available | unavailable)
  - trend_label (nullable)
  - direction (nullable)
  - strength (nullable)
  - selected_lookback_points (nullable)
  - observed_on (nullable)
  - reason_code (nullable)
- Validation rules:
  - Must be render-ready without client-side weighting/ranking logic.

## Relationships

- One DataSeries has many LookbackApplicabilityEvaluation rows.
- One DataSeries has many ObservationLookbackTrendSnapshot rows.
- One DataSeries has many CanonicalTrendDescriptorSnapshot rows.
- One observation context has at most one CanonicalTrendDescriptorSnapshot and up to N lookback snapshots.
- DatasetDetailCanonicalTrendPayload is derived from latest canonical descriptor snapshot for requested dataset.

## State Transitions

- Ingestion writes a new observation.
- Trend pipeline evaluates each lookback:
  - inapplicable -> applicability row only
  - applicable + no signal -> snapshot with `no_significant_trend`
  - applicable + signal -> snapshot with significant descriptor fields
- Weighted heuristic computes canonical descriptor:
  - if descriptor resolvable -> `available`
  - else -> `unavailable`
- Reprocessing same observation is idempotent via uniqueness constraints and deterministic recompute rules.

## Migration and Compatibility Notes

- Existing `trend_records` and `trend_transition_events` remain available for backward traceability during migration.
- Dataset detail product behavior is moved to canonical descriptor payload and no longer depends on `trend_spans` interval semantics.
- Reclassification jobs must recompute both lookback snapshots and canonical descriptor snapshots for historical observations when analysis version changes.
