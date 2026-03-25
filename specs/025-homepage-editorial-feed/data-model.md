# Data Model: Home Page Editorial Feed

## Overview

This feature defines a homepage editorial feed presentation model layered on top of the existing recent-updates data source.

## Entities

### 1. EditorialFeedSection

- Description: Home page section container for recent updates heading, recency label, and ordered entry rows.
- Fields:
  - heading_text (string, required)
  - sort_label (string, required)
  - entries (array<EditorialFeedEntry>, required)
  - state (enum: populated | empty | fallback, required)
- Validation rules:
  - Heading and sort label are always present when section renders.
  - Section remains visible and structurally stable across all state values.

### 2. EditorialFeedEntry

- Description: One recent update row rendered in editorial format.
- Fields:
  - dataset_id (string, required)
  - source_id (string, required)
  - source_name (string, required)
  - latest_update_at (string timestamp, required)
  - title (string, required)
  - summary_text (string, optional)
  - geography_text (string, optional)
  - view_table_href (string, required)
  - download_csv_href (string, required)
- Validation rules:
  - Required identifiers and action destinations must be non-empty.
  - Entries are displayed in descending recency order.
  - Missing optional summary/geography does not break row rendering.

### 3. FeedActionLink

- Description: Canonical row action representation used by the editorial entry.
- Fields:
  - label (enum: View Table | Download CSV, required)
  - href (string, required)
- Validation rules:
  - Each editorial row contains both required action links.
  - Action labels are consistent for all entries.

### 4. FeedPresentationState

- Description: Rendering mode for editorial feed behavior.
- Fields:
  - mode (enum: populated | empty | fallback, required)
  - message (string, optional)
- Validation rules:
  - Empty mode provides explicit user feedback.
  - Fallback mode preserves page usability and does not block search interactions.

## Relationships

- EditorialFeedSection has one-to-many EditorialFeedEntry.
- EditorialFeedEntry has exactly two FeedActionLink records.
- EditorialFeedSection has exactly one FeedPresentationState.

## State Transitions

1. loading -> populated when recent payload is valid and non-empty.
2. loading -> empty when recent payload is valid with zero entries.
3. loading -> fallback when payload retrieval or mapping fails.
4. populated remains stable during theme/viewport changes.
5. populated -> fallback only when subsequent refresh yields invalid data.
