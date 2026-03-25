# Data Model: Unified Dataset List Item

## Overview

This feature defines a shared presentation model for dataset entries used in both homepage recent updates and datasets listing flows.

## Entities

### 1. UnifiedDatasetRow

- Description: Shared renderable row representation for one dataset entry.
- Fields:
  - dataset_id (string, required)
  - destination_href (string, required)
  - source_label (string, required)
  - updated_label (string, required)
  - title (string, required)
  - summary_text (string, optional)
  - tag_pills (array<string>, optional)
  - emphasized_pills (array<string>, optional)
- Validation rules:
  - dataset_id, destination_href, source_label, updated_label, and title must be non-empty.
  - Missing optional summary and pills must not break row structure.
  - Pills are displayed in stable order provided by the owning page mapping.

### 2. HomepageRecentUpdatesListState

- Description: Home feed state controlling recent row visibility.
- Fields:
  - items (array<UnifiedDatasetRow>, required)
  - unavailable (boolean, required)
  - max_visible_items (number, required)
- Validation rules:
  - unavailable=true bypasses populated list rendering and shows fallback state.
  - max_visible_items limits rendered rows for home feed context.

### 3. DatasetsCatalogListState

- Description: Datasets page list state after filter/sort transformations.
- Fields:
  - items (array<UnifiedDatasetRow>, required)
  - source_filter (string, required)
  - category_filter (string, required)
  - sort_mode (string, required)
  - empty_message (string, required)
- Validation rules:
  - Filter/sort state updates visible items deterministically.
  - Empty result sets render explicit empty message while preserving control state.

### 4. RowRenderContext

- Description: Context flags that preserve page-specific interactions around shared row presentation.
- Fields:
  - context_key (enum: home_recent_updates | datasets_listing, required)
  - row_interaction_mode (enum: row_link | title_link, required)
- Validation rules:
  - context_key must be one of the supported row hosts.
  - row_interaction_mode must remain consistent with host-page behavior requirements.

## Relationships

- HomepageRecentUpdatesListState has zero-to-many UnifiedDatasetRow.
- DatasetsCatalogListState has zero-to-many UnifiedDatasetRow.
- UnifiedDatasetRow has exactly one RowRenderContext during rendering.

## State Transitions

1. home_loading -> home_populated when recent payload resolves with entries.
2. home_loading -> home_unavailable when recent payload retrieval fails.
3. datasets_loading -> datasets_populated when filtered catalog has visible entries.
4. datasets_loading -> datasets_empty when filtered catalog has zero visible entries.
5. datasets_populated -> datasets_empty when control changes remove all matches.
6. datasets_empty -> datasets_populated when control changes restore matches.
