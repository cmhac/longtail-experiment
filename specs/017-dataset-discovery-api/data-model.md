# Data Model: Dataset Discovery Backend API

## Overview

This feature defines read-optimized backend models that project canonical dataset and observation tables into discovery and detail payloads. These models are API-facing contracts and do not replace canonical persistence entities.

## Entities

### 1) DatasetSearchRequest

Represents request context for landing search and catalog search.

Fields:

- query_text: string (optional, trimmed)
- source_ids: list[string] (optional)
- page: integer (required, >= 1)
- page_size: integer (required, >= 1 and <= max configured size)
- include_recent_hint: boolean (optional)

Validation rules:

- Empty or whitespace-only query_text is treated as no query.
- source_ids must reference known source keys when provided.
- page and page_size must remain within configured bounds.

Relationships:

- One DatasetSearchRequest yields one paginated DatasetSummaryPage.

### 2) DatasetSummary

Represents a lightweight discovery record for search, catalog, and recent-updates cards.

Fields:

- dataset_id: string (required; canonical series key)
- source_id: string (required)
- source_name: string (required)
- title: string (required)
- description: string (optional)
- geographic_scope: string (optional)
- topic_tags: list[string] (required; can be empty)
- latest_update_at: datetime (optional)

Validation rules:

- dataset_id must be unique within a result set.
- title and source attribution are mandatory for rendering cards.
- topic_tags list is always present, even if empty.

Relationships:

- Many DatasetSummary records belong to one SourceGroup.
- DatasetSummary corresponds to one DatasetDetail via dataset_id.

### 3) DatasetSummaryPage

Represents paginated discovery results.

Fields:

- items: list[DatasetSummary] (required)
- page: integer (required)
- page_size: integer (required)
- total_items: integer (required)
- total_pages: integer (required)
- sort_key: string (required)

Validation rules:

- sort_key describes deterministic ordering applied to items.
- total_pages must be consistent with total_items and page_size.

Relationships:

- One DatasetSummaryPage is produced from one DatasetSearchRequest.

### 4) SourceGroup

Represents source-oriented grouping in all-datasets browsing.

Fields:

- source_id: string (required)
- source_name: string (required)
- dataset_count: integer (required)
- datasets: list[DatasetSummary] (required)

Validation rules:

- All datasets in the group must share source_id.
- dataset_count must equal len(datasets) within the returned page/group scope.

Relationships:

- One SourceGroup contains many DatasetSummary records.

### 5) DatasetDetail

Represents full dataset metadata plus associated observations.

Fields:

- dataset_id: string (required)
- source_id: string (required)
- source_name: string (required)
- title: string (required)
- description: string (optional)
- geographic_scope: string (optional)
- topic_tags: list[string] (required)
- metadata: map[string, string | number | boolean | null] (optional)
- observations: list[ObservationPoint] (required)

Validation rules:

- Unknown dataset_id returns not-found rather than empty DatasetDetail.
- observations list can be empty for a valid dataset with no points.
- observations must be ordered chronologically.

Relationships:

- One DatasetDetail contains many ObservationPoint records.

### 6) ObservationPoint

Represents one time-series record for detail charting.

Fields:

- observed_on: date (required)
- value: decimal (required)
- reported_at: datetime (required)
- attributes: map[string, string | number | boolean | null] (optional)

Validation rules:

- observed_on and reported_at must preserve canonical source semantics.
- value must be parseable into the declared numeric precision used by canonical storage.

Relationships:

- Many ObservationPoint records belong to one DatasetDetail.

## State Transitions

### Discovery Request Lifecycle

1. requested: input accepted and validated.
2. resolved: query returns deterministic ordered rows.
3. paginated: response metadata computed and attached.
4. delivered: payload returned to caller.

Transition constraints:

- Invalid pagination/search input blocks transition from requested to resolved.
- Missing deterministic ordering blocks transition from resolved to paginated.

### Detail Request Lifecycle

1. requested: dataset_id (and optional range) received.
2. identified: dataset metadata located.
3. hydrated: observations loaded and chronologically ordered.
4. delivered: detail payload returned.

Transition constraints:

- Unknown dataset_id transitions to not-found terminal state.
- Known dataset_id with zero observations still reaches delivered with empty observations list.

## Invariants

- Dataset identifiers are canonical and stable across discovery and detail surfaces.
- Every DatasetSummary includes source attribution.
- Discovery responses provide deterministic ordering for repeated identical inputs.
- Detail observations are chronological by observed_on with stable tie-break rules.
- Optional metadata and tags never cause request failure when absent.
