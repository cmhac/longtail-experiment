# Data Model: Dataset List Page

## Overview

This feature defines the presentation and interaction model for the datasets listing page.

## Entities

### 1. DatasetListView

- Description: Page-level composition containing heading, catalog summary, listing controls, and result list.
- Fields:
  - heading_text (string, required)
  - total_series_text (string, required)
  - request_action (DatasetRequestAction, required)
  - controls (DatasetListControlsState, required)
  - state (enum: populated | empty | fallback, required)
- Validation rules:
  - Heading and total-series summary are always visible when the page renders.
  - Controls are present in all page states.

### 2. DatasetListItem

- Description: One row/card representation of a discoverable dataset entry.
- Fields:
  - dataset_id (string, required)
  - source_id (string, required)
  - source_label (string, required)
  - title (string, required)
  - summary_text (string, optional)
  - tags (array<string>, optional)
  - last_updated_label (string, required)
  - actions (DatasetItemActions, required)
- Validation rules:
  - Required identifiers and title must be non-empty.
  - Missing optional summary/tags does not break card rendering.

### 3. DatasetListControlsState

- Description: User-selected control values that drive list visibility and ordering.
- Fields:
  - source_filter (string, required)
  - category_filter (string, required)
  - sort_mode (string, required)
- Validation rules:
  - Source filter includes an all-sources state.
  - Category filter includes an all-categories state.
  - Sort mode includes a recency-first default.

### 4. DatasetItemActions

- Description: Per-item user actions displayed on each dataset card.
- Fields:
  - can_save (boolean, required)
  - can_share (boolean, required)
- Validation rules:
  - Both save and share affordances are consistently rendered.

### 5. DatasetRequestAction

- Description: Primary page-level action for requesting a new dataset.
- Fields:
  - label (string, required)
  - destination (string, required)
- Validation rules:
  - Label is visible near page header region.
  - Destination remains valid across page states.

## Relationships

- DatasetListView has exactly one DatasetListControlsState.
- DatasetListView has zero-to-many DatasetListItem.
- DatasetListItem has exactly one DatasetItemActions group.
- DatasetListView has exactly one DatasetRequestAction.

## State Transitions

1. loading -> populated when catalog payload resolves with at least one item.
2. loading -> empty when payload resolves with zero visible items after active filters.
3. loading -> fallback when payload retrieval or mapping fails.
4. populated -> empty when control updates remove all visible matches.
5. empty -> populated when control reset restores visible matches.
