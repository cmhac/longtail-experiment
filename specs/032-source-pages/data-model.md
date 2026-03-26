# Data Model: Source Discovery Pages

## Entity: Source Summary

- Purpose: Represents one source entry on the sources directory page.
- Fields:
  - source_id: Route-safe source identifier used in navigation.
  - source_name: Human-readable source display name.
  - dataset_count: Total number of discoverable datasets attributed to the source.
  - source_type: Optional descriptive source classification when available.
- Validation Rules:
  - source_id and source_name must be non-empty.
  - dataset_count must be zero or greater.
  - source_id must map deterministically to the source shown in source detail views.

## Entity: Source Detail

- Purpose: Represents the page-level state for one selected source.
- Fields:
  - source_id: Route-safe source identifier.
  - source_name: Human-readable source name.
  - dataset_count: Total number of datasets currently associated with the source.
  - datasets: Ordered list of datasets attributed to the source.
- Validation Rules:
  - source_id and source_name must match the selected source route.
  - dataset_count must equal the number of visible datasets in the returned source detail payload.
  - datasets must not include entries from other sources.

## Entity: Source Dataset Summary

- Purpose: Represents one dataset entry inside a source detail page.
- Fields:
  - dataset_id: Canonical dataset identifier used by existing dataset detail routes.
  - title: Dataset display title.
  - description: Optional summary text.
  - geographic_scope: Optional geography label.
  - topic_tags: Optional topical labels.
  - latest_update_at: Optional latest update context.
  - source_ref: Source attribution for membership verification.
- Validation Rules:
  - dataset_id and title must be non-empty.
  - source_ref must match the parent source detail source.
  - latest_update_at may be empty but must remain safely renderable when present.

## Entity: Source List View State

- Purpose: Represents the user-facing state of the sources directory page.
- Fields:
  - items: Ordered collection of source summaries.
  - total_sources: Total number of discoverable sources.
  - render_state: Loaded, empty, or error.
- Validation Rules:
  - Loaded state requires a concrete source summary list.
  - Empty state is used when total_sources is zero.
  - Error state must preserve shell navigation and avoid partial misleading content.

## Entity: Source Detail View State

- Purpose: Represents the user-facing state of the source detail route.
- Fields:
  - source_detail: Source detail payload when found.
  - render_state: Loaded, empty-datasets, not-found, or error.
  - dataset_navigation_targets: Existing dataset detail destinations for child dataset entries.
- Validation Rules:
  - Not-found state is used only when the source identifier cannot be resolved.
  - Empty-datasets state is used only when the source exists but has zero datasets.
  - Error state is reserved for retrieval or runtime failures unrelated to source existence.

## Relationships

- One Source Summary corresponds to one Source Detail.
- One Source Detail owns zero or more Source Dataset Summary records.
- Source List View State contains zero or more Source Summary records.
- Source Detail View State contains exactly one Source Detail when loaded successfully.
- Each Source Dataset Summary links onward to an existing dataset detail route through its dataset_id.
