# Data Model: Tag and Geography Discovery Pages

## Entity: Topic Detail

- Purpose: Represents the page-level state for one selected topic tag.
- Fields:
  - topic_id: Route-safe topic identifier used in navigation.
  - topic_label: Human-readable topic label shown in the UI.
  - dataset_count: Total number of visible datasets associated with the topic.
  - datasets: Ordered list of datasets associated with the topic.
- Validation Rules:
  - topic_id and topic_label must be non-empty.
  - dataset_count must equal the number of visible datasets returned in the detail payload.
  - datasets must not include entries that do not carry the selected topic.

## Entity: Geography Detail

- Purpose: Represents the page-level state for one selected geography value.
- Fields:
  - geography_id: Route-safe geography identifier used in navigation.
  - geography_label: Human-readable geography label shown in the UI.
  - dataset_count: Total number of visible datasets associated with the geography.
  - datasets: Ordered list of datasets associated with the geography.
- Validation Rules:
  - geography_id and geography_label must be non-empty.
  - dataset_count must equal the number of visible datasets returned in the detail payload.
  - datasets must not include entries that do not belong to the selected geography.

## Entity: Metadata Dataset Summary

- Purpose: Represents one dataset entry inside a topic detail page or geography detail page.
- Fields:
  - dataset_id: Canonical dataset identifier used by existing dataset detail routes.
  - title: Dataset display title.
  - description: Optional summary text.
  - geographic_scope: Optional geography label.
  - topic_tags: Optional topical labels.
  - latest_update_at: Optional latest update context.
  - source_ref: Existing source attribution used for browse consistency.
- Validation Rules:
  - dataset_id and title must be non-empty.
  - topic detail datasets must include the selected topic label.
  - geography detail datasets must match the selected geography label.
  - latest_update_at may be empty but must remain safely renderable when present.

## Entity: Metadata Navigation Target

- Purpose: Represents a route destination derived from a visible topic tag or geography value.
- Fields:
  - kind: Topic or geography.
  - slug: Route-safe path segment.
  - label: Human-readable metadata label.
- Validation Rules:
  - kind must be one of the supported metadata browse types.
  - slug must be stable for the same visible metadata label.
  - label must remain safely renderable as escaped content.

## Entity: Metadata Detail View State

- Purpose: Represents the user-facing state of a topic or geography detail page.
- Fields:
  - metadata_detail: Topic detail or geography detail payload when found.
  - render_state: Loaded, empty-datasets, not-found, or error.
  - dataset_navigation_targets: Existing dataset detail destinations for child dataset entries.
- Validation Rules:
  - Not-found state is used only when the selected metadata identifier cannot be resolved.
  - Empty-datasets state is used only when the metadata value is valid but has zero visible datasets.
  - Error state is reserved for retrieval or runtime failures unrelated to metadata existence.

## Relationships

- One Topic Detail owns zero or more Metadata Dataset Summary records.
- One Geography Detail owns zero or more Metadata Dataset Summary records.
- One Metadata Dataset Summary can appear in multiple Topic Detail pages when it has multiple topic tags.
- One Metadata Dataset Summary can appear in at most one Geography Detail page under the current discovery-facing geography label model.
- Each Metadata Navigation Target resolves to either one Topic Detail page or one Geography Detail page.
