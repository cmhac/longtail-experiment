# Data Model: Relative Change Visualizations

## Entities

### Chart Value Mode

- Purpose: Defines whether the dataset detail chart renders raw observed values or relative percentage change.
- Values:
  - observed-value mode
  - relative-change mode
- Rules:
  - Mode switching must not break existing dataset-detail chart behavior.
  - Relative-change formatting must be visually distinguishable from observed-value formatting.

### Rolling Baseline Offset

- Purpose: Selects prior-observation distance for rolling relative-change computation.
- Fields:
  - offset_value (positive integer)
  - supported_flag (whether offset can compute within current scope)
- Rules:
  - Must support 1, 2, and 3 at minimum.
  - Larger n offsets must be bounded by available observation history.

### Fixed Baseline Reference

- Purpose: Identifies a single constant baseline observation for fixed-baseline comparison.
- Fields:
  - reference_mode (date or observation index/offset)
  - reference_date (exact available observation date when date mode is used)
  - reference_index_offset (integer offset when index/offset mode is used)
- Rules:
  - Date mode is exact-match only.
  - Date selector options are limited to available observation dates in active scope.
  - Reference remains visible if it becomes invalid after scope change.

### Relative Change Point

- Purpose: Represents a computed chart point in relative-change mode.
- Fields:
  - observed_on
  - baseline_observed_on
  - relative_change_percent
  - computability_state
- Rules:
  - Formula: ((current - baseline) / baseline) \* 100.
  - Computation follows chronological observation ordering.

### Computability State

- Purpose: Distinguishes computable and non-computable points in transformed chart output.
- Values:
  - valid
  - insufficient_history
  - undefined_baseline (for example baseline value is zero)
- Rules:
  - Non-computable points are rendered as timeline gaps.
  - Non-computable points must not be replaced with fallback numeric values.

## Relationships

- Chart Value Mode governs whether Relative Change Point entities are used in rendering.
- Rolling Baseline Offset determines baseline lookup for each Relative Change Point in rolling mode.
- Fixed Baseline Reference determines a shared baseline for Relative Change Point computation in fixed mode.
- Computability State is attached to each Relative Change Point and drives gap/unavailable rendering behavior.

## State Transitions

### Mode Transition

1. User switches from observed-value mode to relative-change mode.
2. Baseline configuration is evaluated.
3. Relative change series is computed and rendered.

### Rolling Baseline Transition

1. User selects rolling offset.
2. Series recomputes per-point baseline using selected offset.
3. Points without sufficient history transition to non-computable gap state.

### Fixed Baseline Transition

1. User chooses fixed baseline via exact available date or index/offset.
2. Series recomputes against constant baseline reference.
3. Non-computable points transition to gap state when baseline rules cannot compute.

### Scope Change Transition

1. User changes time range or filter context.
2. Existing baseline settings are preserved if valid.
3. If invalid, settings remain visible and series enters explicit unavailable state until reconfigured.
