# Dataset Detail Page Contract

## Scope

This contract defines expected page-level behavior and section semantics for the dataset detail page overhaul.

## Route Contract

- Route shape remains `/datasets/{id}`.
- Valid dataset identifiers render the overhauled detail experience.
- Unknown dataset identifiers render the existing not-found experience.
- Non-not-found retrieval failures render the existing generic error experience.

## Loaded-State Section Contract

A successful dataset detail render MUST include the following sections in order:

1. Dataset hero with source attribution, dataset title, and utility actions.
2. Insight summary rail with latest observation and comparative statistics.
3. Historical trend section with selectable time-window controls.
4. Observed-values section with tabular rows and directional movement semantics.

## Trend Interaction Contract

- A default time range is selected when the page loads with observation data.
- User can switch between available range controls (`1M`, `6M`, `1Y`, `ALL`).
- Trend visualization updates to reflect the selected range.
- Individual points remain inspectable in each range.
- If there are no observations, the trend section displays explicit no-data messaging.

## Observed Values Table Contract

- Rows are ordered by recency for human scanning.
- Each row includes observation date and value.
- Change indicator is shown when a comparable prior value exists.
- Movement state maps to change sign:
  - positive -> positive visual cue
  - negative -> negative visual cue
  - zero -> neutral visual cue
  - unavailable -> explicit fallback treatment
- Archive/load-more affordance appears only when rows exceed the default visible subset, and remains hidden otherwise.

## Safety and Fallback Contract

- Externally sourced text is rendered as escaped content.
- Partial metadata is tolerated with explicit fallback labels where needed.
- No-data, error, and not-found states are explicit and non-blank.

## Responsive Contract

- Desktop and mobile layouts preserve section order and readability.
- Utility actions remain discoverable and actionable across viewport sizes.
- No clipping or overlap of key values, controls, or section headings.
