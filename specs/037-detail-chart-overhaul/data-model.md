# Data Model: Dataset Detail Chart Overhaul

## Entity: Historical Trend Panel

- Purpose: The chart-focused analysis surface on the dataset detail page.
- Fields:
  - title: Trend section heading shown above the chart.
  - chart_surface_state: Layout and visual treatment state for the chart area.
  - control_group_state: Visibility and ordering state for time-filter controls.
  - empty_state_message: Explicit fallback message shown when observations are absent.
- Validation Rules:
  - chart_surface_state must fill the available trend-panel width.
  - empty_state_message is required when no observations are available.
  - control_group_state is omitted when no meaningful preset filters are available.

## Entity: Chart Surface State

- Purpose: Visual presentation rules for the rendered trend line and axes.
- Fields:
  - width_behavior: Full-width behavior within the trend section.
  - height_alignment: Vertical alignment target relative to the adjacent metadata column.
  - border_state: Removed or absent chart border.
  - footnote_state: Removed or absent observation-count footnote.
  - line_marker_state: Hidden point markers in the default trend render.
  - x_axis_label_spacing: Increased visual separation of axis labels.
- Validation Rules:
  - border_state must remain absent in the loaded chart state.
  - footnote_state must remain absent in the loaded chart state.
  - line_marker_state must remain hidden unless a future explicit inspection mode requires otherwise.

## Entity: Time Filter Control Set

- Purpose: Ordered range controls used to change the visible history window.
- Fields:
  - selected_range: Active range shown in the chart.
  - available_ranges: Ordered list of visible filter options.
  - default_range: Initial selected range for loaded datasets.
  - pointer_affordance: Clickable cursor behavior for visible controls.
- Validation Rules:
  - default_range must be all-history whenever observations exist.
  - available_ranges must be ordered from longest visible range to shortest visible range.
  - pointer_affordance applies to every visible filter control.

## Entity: Time Filter Option

- Purpose: One chart lookback option offered to the visitor.
- Fields:
  - key: Stable range identifier such as all-history, 5-year, 1-year, 6-month, or 1-month.
  - label: Visitor-facing control text.
  - support_state: Visible only when meaningful for the available history.
  - relative_order: Position within the visible control sequence.
- Validation Rules:
  - key must be unique within one control set.
  - support_state determines whether the control is rendered at all.
  - 5-year may appear only when the dataset history meaningfully supports it.

## Entity: Supported History Window

- Purpose: Derived determination of which lookback windows are meaningful for one dataset.
- Fields:
  - dataset_history_span: Effective chronological coverage of the observation history.
  - supported_range_keys: Range keys that produce distinct useful chart views.
  - filtered_observation_subset: Observations included for a chosen supported range.
- Validation Rules:
  - filtered_observation_subset must remain in chronological order.
  - supported_range_keys must always include all-history when at least one observation exists.
  - unsupported range keys must not appear in the visible control set.

## Relationships

- Historical Trend Panel contains one Chart Surface State and, when observations are present, zero or one Time Filter Control Set.
- Time Filter Control Set contains one or more Time Filter Options.
- Supported History Window determines which Time Filter Options are included in the Time Filter Control Set.
- Chart Surface State and Supported History Window both derive from the same observation history in the dataset detail payload.
