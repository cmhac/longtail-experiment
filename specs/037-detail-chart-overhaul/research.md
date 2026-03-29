# Research: Dataset Detail Chart Overhaul

## Decision 1: Keep the existing dataset detail API contract and compute chart range availability in the frontend

- Decision: Reuse the current `DatasetDetail.observations` payload and derive supported chart ranges, default selection, and filtered chart points entirely in the frontend view-model layer.
- Rationale: The feature changes chart behavior and presentation only; the existing payload already provides ordered observations and enough history information to decide which windows are meaningful.
- Alternatives considered:
  - Add backend-computed chart-range metadata: rejected because it expands backend scope and contract surface without adding product value for this UI-only change.
  - Hardcode all chart filters regardless of available history: rejected because it violates the requirement to avoid dead-end or duplicate controls.

## Decision 2: Treat all-history as the default selected state and hide unsupported windows rather than disabling them

- Decision: Make all-history the default selected chart state and show only the subset of preset ranges that the dataset history meaningfully supports.
- Rationale: This preserves the most complete first view while ensuring every visible control can produce a distinct, useful chart state.
- Alternatives considered:
  - Keep a shorter default such as 1Y: rejected because it hides long-term context on first load.
  - Show unsupported ranges in a disabled state: rejected because it adds visual noise and still advertises unavailable actions.

## Decision 3: Define support for preset windows in terms of meaningful distinct history, not merely control availability

- Decision: A preset range is considered supported only when the available observation history is sufficient for that range to represent a distinct charted view compared with broader ranges or all-history.
- Rationale: The spec emphasizes eliminating misleading controls, so the support rule must prevent duplicate or nearly identical range outcomes from being shown as separate options.
- Alternatives considered:
  - Show a preset as soon as any observations exist inside that nominal time span: rejected because short histories would expose multiple controls that all resolve to the same result.
  - Base support only on raw observation count labels: rejected because the product requirement is meaningful user-facing history coverage, not an internal count threshold by itself.

## Decision 4: Keep layout changes inside the existing trend panel and chart component boundaries

- Decision: Achieve the expanded chart footprint, border removal, and footnote removal by refining the existing detail analysis layout and chart wrapper rather than restructuring the route or creating a new panel system.
- Rationale: The current detail-page architecture already isolates the chart in a dedicated trend section, so the requested visual changes can be implemented with lower risk inside the existing component boundaries.
- Alternatives considered:
  - Rebuild the entire detail analysis section around a new layout abstraction: rejected because it increases scope beyond the chart overhaul.
  - Push chart sizing concerns into page-level route composition only: rejected because part of the change belongs to the chart container itself.

## Decision 5: Improve x-axis readability through chart configuration and spacing behavior, not through external explanatory text

- Decision: Increase perceived x-axis label separation through chart spacing/tick presentation changes while removing the observation-count footnote entirely.
- Rationale: The requirement is to make the chart itself clearer and less cluttered, not to compensate with additional supporting copy.
- Alternatives considered:
  - Keep the footnote to explain dataset density: rejected because the spec explicitly removes it.
  - Add a second explanatory label row beneath the chart: rejected because it adds new visual clutter instead of reducing it.
