# Data Model: Dataset Comparison Overlay

## Entity: ComparisonSelectionState

- Purpose: Persist and restore user-selected comparison datasets and related view settings.
- Fields:
  - selected_dataset_ids: ordered list of unique dataset identifiers.
  - selected_count: derived integer count (`0..MAX_COMPARISON_DATASETS`).
  - last_updated_at: timestamp for state mutation tracking.
  - version: schema version for persisted payload validation.
- Validation:
  - IDs are unique.
  - Count never exceeds configured max.
  - Invalid/corrupted payload is treated as hard failure state requiring manual reset.
- State transitions:
  - Empty -> Populated: first add action.
  - Populated -> Populated: add/remove reorder preserving uniqueness.
  - Populated -> Empty: remove all or reset action.
  - Any -> Invalid: payload parse/shape/version failure.

## Entity: ComparisonDatasetView

- Purpose: Runtime projection of one selected dataset for charting and list management.
- Fields:
  - dataset_id
  - title
  - unit_type
  - unit_label
  - observations: chronological raw observations from detail payload.
  - line_color: stable color token scoped to active selection.
- Validation:
  - unit_type may be null/unknown for compatibility checks until resolved from detail metadata.
  - observation dates are used as source truth; no synthetic values introduced.

## Entity: ComparisonModeState

- Purpose: Shared chart display mode and compatibility gating controls.
- Fields:
  - value_mode: `observed | relative`.
  - absolute_mode_enabled: boolean gate derived from selection compatibility.
  - mode_lock_reason: user-facing explanation when observed mode is disabled.
- Validation rules:
  - observed mode allowed only when all selected datasets are unit-compatible.
  - when incompatibility is detected while observed mode active, state auto-transitions to relative mode.

## Entity: RelativeBaselineState

- Purpose: Define one shared relative baseline configuration across all compared series.
- Fields:
  - baseline_mode: `rolling | fixed`.
  - rolling_offset: integer >= 1.
  - fixed_baseline_date: nullable date selector value.
- Validation rules:
  - one shared configuration applied to all series.
  - in fixed mode per-series baseline resolution order:
    1. exact selected date
    2. nearest prior observation
    3. nearest available observation

## Entity: ComparisonTimelineProjection

- Purpose: Multi-series chart data on unified timeline.
- Fields:
  - timeline_dates: sorted union of all selected-series observation dates.
  - series_points: mapping of dataset_id -> date-indexed points.
  - point_value: numeric or null for gap.
  - computability_state: computed/unavailable with reason.
- Validation rules:
  - timeline uses union, not intersection.
  - missing date value for a series is represented as gap (null), never fabricated.

## Entity: ComparisonPageViewState

- Purpose: Page-level UI behavior for dedicated comparison route.
- Fields:
  - eligibility_state: insufficient-selection (`<2`) or ready.
  - selected_items: removable dataset list.
  - chart_visible: boolean (true only when eligibility met and state valid).
  - table_visible: always false in this feature scope.
  - detail_sidebar_visible: always false in this feature scope.
- Validation rules:
  - less than 2 selected datasets shows instructional empty state.
  - invalid persisted state blocks comparison until reset.

## Constants

- MAX_COMPARISON_DATASETS
  - Purpose: single authoritative selection cap.
  - Initial value: `5`.
  - Requirement linkage: FR-009 / FR-010.
