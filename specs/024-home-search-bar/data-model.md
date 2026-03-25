# Data Model: Homepage Search Bar Experience

## Overview

This feature introduces homepage search-focused response entities for scope summary and likely-match suggestions. No user-auth identity model changes are involved.

## Entities

### 1. HomepageSearchSurface

- Description: Home hero search presentation entity combining input, summary line, and suggestion state.
- Fields:
  - query_text (string, required)
  - is_focused (boolean, required)
  - suggestions_visible (boolean, required)
  - summary_line (string, required)
- Validation rules:
  - Search surface remains centered and visually prominent on home page.
  - Summary line always follows expected sentence pattern when data exists.

### 2. SearchScopeSummary

- Description: Aggregated scope metadata rendered below the search input.
- Fields:
  - active_dataset_count (integer, required, >= 0)
  - active_source_count (integer, required, >= 0)
  - generated_at (string datetime, optional)
- Validation rules:
  - Counts must be numeric and non-negative.
  - Frontend must render real runtime values, not static placeholders.

### 3. SuggestionItem

- Description: One likely-match candidate for typed query input.
- Fields:
  - dataset_id (string, required)
  - title (string, required)
  - source_id (string, required)
  - source_name (string, required)
  - rank_score (number, required)
- Validation rules:
  - Items correspond to current query text.
  - Ordering is deterministic by matching relevance then stable tiebreakers.

### 4. SuggestionResultSet

- Description: Bounded ordered suggestions for current query.
- Fields:
  - query (string, required)
  - items (array<SuggestionItem>, required)
  - limit (integer, required, > 0)
- Validation rules:
  - Result set must not exceed configured limit.
  - Stale results for previous query must not be displayed after new input resolution.

## Relationships

- HomepageSearchSurface 1-to-1 SearchScopeSummary.
- HomepageSearchSurface 1-to-many SuggestionItem (via SuggestionResultSet).
- SuggestionResultSet belongs to exactly one current query value.

## State Transitions

### Search surface lifecycle

1. idle: centered search visible, no suggestions open.
2. summary_loaded: aggregate counts displayed in summary line.
3. typing: user updates query text.
4. suggestions_loaded: likely matches for latest query displayed in dropdown.
5. empty_suggestions: no matches found for latest query.
6. degraded_fallback: summary or suggestions unavailable; input remains usable with fallback UI.
