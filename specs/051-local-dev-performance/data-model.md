# Data Model: Local Development Performance Stabilization (Spec 051)

## Entity: DatasetDetailRequest

- Purpose: Represents a single dataset detail page request in local development.
- Fields:
  - dataset_id (string, required)
  - from_date (date | null)
  - to_date (date | null)
  - request_context (enum: `server_render` | `api_proxy`, required)
- Validation rules:
  - `dataset_id` must be non-empty and canonical.
  - `from_date` must be <= `to_date` when both are provided.

## Entity: DatasetMetadataProjection

- Purpose: Dataset-specific metadata needed to render detail header and contextual fields.
- Fields:
  - dataset_id (string, required)
  - source (object: id, name, required)
  - title (string, required)
  - description (string | null)
  - geographic_scope (string | null)
  - topic_tags (array<string>, required)
  - latest_update_at (datetime | null)
  - has_recent_notification (boolean, required)
  - metadata (object, required)
- Validation rules:
  - Shape must remain compatible with existing detail response consumers.
  - Not-found behavior for unknown `dataset_id` remains unchanged.

## Entity: ObservationDetailSet

- Purpose: Ordered observation points for one dataset detail response.
- Fields:
  - dataset_id (string, required)
  - observations (array<ObservationPoint>, required)
  - observation_sort (string, required)

### ObservationPoint

- observed_on (date, required)
- value (number, required)
- reported_at (datetime, required)
- attributes (object, required)
- as_of_trend_descriptor (object | null)
- as_of_trend_candidates (array<object>, optional internal projection)

- Validation rules:
  - Ordering remains deterministic by observation/report timestamps as currently defined.
  - As-of descriptor values remain behaviorally consistent with existing contract tests.

## Entity: TrendDetailEvidence

- Purpose: Trend evidence payload attached to dataset detail response.
- Fields:
  - canonical_trend_descriptor (object, required)
  - lookback_trend_evidence (array<object>, required)
- Validation rules:
  - Evidence fields stay available and semantically consistent after performance changes.
  - Missing evidence degrades gracefully to existing unavailable/default semantics.

## Entity: LocalRequestExecutionProfile

- Purpose: Non-functional profile for work performed to satisfy one local dataset detail request.
- Fields:
  - retrieval_scope (enum: `dataset_scoped` | `catalog_scoped`, required target: `dataset_scoped`)
  - setup_overhead_state (enum: `bounded` | `repeated_full_setup`, required target: `bounded`)
  - response_latency_ms (number, measured)
  - sample_run_id (string, required for measurement sets)
- Validation rules:
  - Detail requests must execute in dataset-scoped mode after implementation.
  - Repeated refresh measurements must satisfy spec success criteria.

## Relationships

- One `DatasetDetailRequest` produces one `DatasetMetadataProjection` or a not-found/validation error outcome.
- One `DatasetDetailRequest` produces one `ObservationDetailSet` bound to the same dataset.
- One `DatasetDetailRequest` produces one `TrendDetailEvidence` bundle.
- Each completed request records/participates in one `LocalRequestExecutionProfile` during validation runs.

## State Transitions

- Request received -> request validated -> dataset metadata resolved.
- If dataset not found: return existing not-found behavior.
- If dataset found: observations and trend evidence resolved -> detail response assembled.
- Execution profile measured for baseline/after comparison in local runs.

## Invariants

- Detail endpoint output contract remains stable while performance characteristics improve.
- Error handling contract remains stable for invalid input and missing dataset IDs.
- Related discovery endpoints remain functionally unaffected by this feature.
