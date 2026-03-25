# Data Model: Dataset Detail Page Overhaul

## Entity: Dataset Detail Hero

- Purpose: Top-level identity and action region for one dataset detail page.
- Fields:
  - source_label: Human-readable provider attribution text.
  - dataset_title: Primary dataset name used as page heading.
  - utility_actions: Set of action entries exposed in hero (export/share entry points).
- Validation Rules:
  - source_label and dataset_title must be non-empty display strings.
  - utility_actions must include at least one actionable item when detail payload is loaded.

## Entity: Observation Insight Summary

- Purpose: At-a-glance quantitative context derived from available observations.
- Fields:
  - latest_value: Most recent observation value.
  - latest_observed_on: Date associated with latest_value.
  - comparison_metrics: At least two comparative metrics (for example high/low windows or period comparison).
  - movement_summary: Direction and magnitude label relative to prior comparable value.
- Validation Rules:
  - latest_value requires at least one observation.
  - movement_summary is optional when there is no prior comparable point.
  - comparison_metrics must degrade gracefully when insufficient history exists.

## Entity: Historical Trend State

- Purpose: Interaction state for trend visualization and range filtering.
- Fields:
  - selected_range: Active time-window key (short-range, mid-range, annual, all-history).
  - available_ranges: Ordered list of selectable time-window keys.
  - visible_points: Observation points included for current range.
  - inspection_point: Optional currently inspected point.
- Validation Rules:
  - selected_range must always be one of available_ranges.
  - visible_points must be chronological.
  - inspection_point, when present, must map to a point in visible_points.

## Entity: Observed Value Row

- Purpose: One row in the observed-values table.
- Fields:
  - observed_on: Observation date label.
  - value_display: Formatted numeric value.
  - period_change_value: Signed change versus prior comparable row.
  - movement_state: Positive, negative, neutral, or unavailable.
- Validation Rules:
  - observed_on and value_display are required.
  - movement_state must correspond to the sign of period_change_value when a change exists.
  - unavailable movement state is used when no comparable prior value exists.

## Entity: Observation Archive State

- Purpose: Controls disclosure of rows beyond the default visible subset.
- Fields:
  - default_row_count: Number of rows shown initially.
  - total_row_count: Total rows available from payload.
  - reveal_mode: collapsed or expanded.
  - reveal_action_label: User-facing archive/disclosure call-to-action text.
- Validation Rules:
  - total_row_count must be greater than or equal to default_row_count.
  - reveal action is shown only when total_row_count exceeds default_row_count.

## Relationships

- Dataset Detail Hero and Observation Insight Summary are both scoped to one loaded dataset payload.
- Historical Trend State and Observed Value Rows derive from the same chronological observation set.
- Observation Archive State governs how many Observed Value Rows are visible at any time.
- Movement semantics in Observation Insight Summary and Observed Value Row must use the same directional classification rules.
