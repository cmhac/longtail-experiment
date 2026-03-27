# Data Model: Filter UI Improvements

## Entity: FilterControlContainer

- Description: Visual wrapper that groups dataset-list filter controls and communicates hierarchy via shared surface styling.
- Fields:
  - `surface_style_variant` (enum): resolved visual surface style for filter container
  - `appearance_mode` (enum): active appearance context affecting token resolution
  - `layout_mode` (enum): responsive layout mode for control grouping/reflow
- Validation Rules:
  - `surface_style_variant` must map to approved shared filter/shell surface semantics.
  - Container styling must remain readable in each supported `appearance_mode`.

## Entity: FilterSelectorControl

- Description: Selector control used to choose filter values or sort options on the dataset list page.
- Fields:
  - `control_id` (enum): one of two filtering selectors or one sorting selector
  - `role` (enum): `filter` or `sort`
  - `selected_value` (string | null)
  - `available_options` (list)
  - `interaction_state` (enum): default, focused, expanded, selected, no-match
- Validation Rules:
  - Role assignments remain stable (`filter`, `filter`, `sort`).
  - Selection changes preserve existing query/filter/sort behavior semantics.
  - Keyboard interaction paths remain operable for open, navigate, and select actions.

## Entity: FilterControlLayoutGroup

- Description: Spatial grouping model for selector placement and spacing.
- Fields:
  - `left_group_controls` (list): exactly two filter selectors
  - `right_group_control` (single): sort selector
  - `inter_group_spacing` (design token or fixed spacing rule)
  - `control_width_cap` (size rule): maximum width per selector
  - `responsive_reflow_rule` (enum): stacking/reflow behavior on narrow viewports
- Validation Rules:
  - Left group contains only filtering selectors.
  - Right group contains only sorting selector.
  - Width caps prevent full-row stretching where horizontal space is available.
  - Reflow keeps grouping intent understandable on narrower layouts.

## Entity: FilterInteractionOutcome

- Description: Observable result after control selection changes.
- Fields:
  - `active_filter_values` (map)
  - `active_sort_value` (string)
  - `result_state` (enum): updated, empty, loading, error
- State Transitions:
  - On filter selection change: update `active_filter_values` and refresh list scope.
  - On sort selection change: update `active_sort_value` and refresh ordering.
  - On no-match condition: preserve selected-state clarity and explicit empty-result handling.
