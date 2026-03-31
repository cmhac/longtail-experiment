# Data Model: End-to-End Trend Detection

## Entity: TrendRecord

- Purpose: Persist one time-bounded trend segment for a series.
- Fields:
  - id (uuid, PK)
  - data_series_id (uuid, FK -> data_series.id, required)
  - trend_label (enum/string, required)
  - direction (enum: up|down|flat, required)
  - strength (enum/string, required)
  - seasonality_classification (enum: seasonal|non_seasonal, required)
  - start_period (date/timestamp, required)
  - end_period (date/timestamp, nullable)
  - is_ongoing (boolean, required)
  - created_at (timestamp, required)
  - ended_at (timestamp, nullable)
- Validation rules:
  - start_period <= end_period when end_period is present.
  - Exactly one ongoing record per series at a time.
  - Ongoing record must have null end_period.
  - Non-ongoing record must have non-null end_period.
- State transitions:
  - ongoing -> ended when no significant trend or materially different signature is detected.
  - ongoing -> ongoing (no write) when signature unchanged.
  - no ongoing -> ongoing when new significant trend detected.

## Entity: TrendSignature

- Purpose: Canonical comparison key for continuity decision.
- Fields:
  - trend_label
  - direction
  - strength
  - seasonality_classification
- Validation rules:
  - Any field-level change marks signature as materially different.

## Entity: TrendTransitionEvent

- Purpose: Auditable event for trend lifecycle decisions.
- Fields:
  - id (uuid, PK)
  - data_series_id (uuid, required)
  - transition_type (enum: created|continued|ended|no_op, required)
  - prior_trend_record_id (uuid, nullable)
  - new_trend_record_id (uuid, nullable)
  - trigger_observation_at (timestamp/date, required)
  - reason (string/enum, required)
  - created_at (timestamp, required)
- Validation rules:
  - `continued` and `no_op` do not create new TrendRecord rows.
  - `ended` must reference prior trend row and include boundary period.

## Entity: TrendAnalysisResult

- Purpose: Pure library output consumed by pipeline/application layers.
- Fields:
  - outcome (enum: significant_trend|no_significant_trend|insufficient_data|error)
  - signature (TrendSignature, nullable for non-significant/insufficient outcomes)
  - start_period (date/timestamp, nullable)
  - end_period (date/timestamp, nullable)
  - confidence_metrics (object/map, optional)
  - error_code (string, nullable)
  - error_message (string, nullable)
- Validation rules:
  - Deterministic output for identical ordered input under identical library version.
  - `error` used for invalid cadence/seasonality mismatch cases.

## Entity: TrendFeedItem

- Purpose: Unified recent updates feed item for trend events.
- Fields:
  - item_type (literal: trend_event)
  - data_series_id
  - dataset_slug/dataset_id
  - event_timestamp (trend start period per clarification)
  - direction
  - strength
  - start_period
  - end_period (nullable)
  - is_ongoing
- Validation rules:
  - Feed sort key uses event_timestamp consistently with dataset updates ordering model.

## Entity: TrendVisualizationSpan

- Purpose: Dataset detail UI contract for chart overlays.
- Fields:
  - span_id
  - start_x
  - end_x
  - direction
  - color_token
  - pattern_token
  - direction_icon
  - tooltip_payload
- Validation rules:
  - Spans must be non-overlapping before rendering.
  - At most one tooltip active in UI interaction state.
  - Touch + desktop interaction parity for detail access.

## Relationships

- One DataSeries has many TrendRecords.
- One DataSeries has many TrendTransitionEvents.
- TrendFeedItem references one DataSeries and optional TrendRecord snapshot.
- TrendVisualizationSpan is derived from TrendRecord/transition data for client display.

## Scale Considerations

- Trend processing executes per updated series.
- Historical backfill only for series with sufficient history and no existing trend records.
- Idempotent retry behavior required for unchanged persisted observation states.
