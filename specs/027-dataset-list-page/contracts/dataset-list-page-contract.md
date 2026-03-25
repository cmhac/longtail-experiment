# Contract: Dataset List Page Discovery Experience

## Interface Summary

- Interface type: Frontend page contract for dataset list discovery behavior
- Consumer: Users navigating to the datasets listing route
- Provider: Frontend datasets page and discovery component composition over existing catalog payload

## Route

- Primary page: `/datasets`

## Query Parameter Contract

- `source` (optional): selected source filter value; omit or `all` means no source constraint.
- `category` (optional): selected category/tag filter value; omit or `all` means no category constraint.
- `sort` (optional): supported values `recency`, `title_asc`, `title_desc`; unsupported values fall back to `recency`.

## Page-Level Contract

### Required page regions

1. Page heading region with "Datasets" title and total-series summary.
2. Primary request action region with a visible request-new-dataset control.
3. Listing controls region containing source filter, category filter, and sort controls.
4. Results region rendering dataset cards in deterministic order.

### Listing controls contract

- Source filter includes an all-sources option and source-specific options.
- Category filter includes an all-categories option and category-specific options.
- Sort control exposes recency-first default ordering.
- Control changes update visible results while preserving selected control values.
- Control selection state is represented in URL query parameters for deep-link/shareable list views.

### Dataset card contract

Each visible card includes:

- source label
- title
- summary text (when available)
- tag chips (when available)
- last-updated context
- save action affordance
- share action affordance

### State contract

- Populated state: one or more cards visible.
- Empty state: no cards visible plus explicit no-results guidance.
- Fallback state: non-blocking error-safe rendering preserving page controls/navigation.

## Behavioral Guarantees

1. Request-new-dataset action is visible and operable from the listing page.
2. Visible result order follows active sort mode.
3. Duplicate dataset entries are not shown in the same visible result set.
4. Missing optional metadata does not break card layout.
5. Desktop and mobile layouts preserve readability and control usability.
6. Catalog total-series summary reflects catalog inventory total and remains independent of temporary source/category filter selection.
7. When no entries match active controls, the page renders explicit reset guidance instead of an empty container.

## Versioning

- Contract version: 1.0
- Breaking changes require synchronized updates to page/component tests and spec artifacts.
