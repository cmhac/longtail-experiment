# Contract: Unified Dataset Row Presentation

## Interface Summary

- Interface type: Frontend UI composition contract
- Consumer surfaces: Homepage recent updates section and datasets listing page
- Provider: Shared dataset row component and host-page mappers

## Purpose

Define one reusable row presentation contract for dataset entries while preserving each host page’s surrounding workflow behavior.

## Required Row Content

Each rendered row includes:

1. Source attribution label
2. Update date context label
3. Dataset title
4. Summary text when available
5. Tag pills when available

## Host Context Contract

### Home recent updates context

- Uses shared row presentation.
- Keeps home feed fallback behavior for unavailable/no-data states.
- Keeps home feed recency ordering and max-visible-item policy.
- Uses row-level interaction mode where the full row is the navigable dataset link.

### Datasets listing context

- Uses the same shared row presentation.
- Keeps datasets page controls and list-state transitions (source/category/sort).
- Keeps datasets empty-results behavior when active filters return no items.
- Uses title-link interaction mode while preserving surrounding row hierarchy.

## Interaction Contract

- Row navigation destination remains the dataset detail route for rendered entries.
- Shared row adoption must not break existing host-level navigation and state behavior.
- Shared row test marker `data-testid="unified-dataset-row"` is present for both host contexts.

## Styling Contract

- Shared row visual hierarchy follows homepage editorial row baseline.
- Datasets filter/sort control styling is explicitly out of scope for this feature.
- Responsive readability must be maintained on desktop and mobile.

## Fallback and Missing Data Contract

- Missing optional summary and pills do not break row layout.
- Malformed date values render a readable fallback label.
- Host-page fallback states (home unavailable, datasets empty) remain intact.

## Versioning

- Contract version: 1.0
- Breaking changes require synchronized updates to affected page tests and spec artifacts.
