# Data Model: Historical As-Of Trend Tooltips

## Entity: ObservationAsOfTrendDescriptor (Read Model)

- Purpose: Canonical trend descriptor resolved for one specific dataset observation in detail payloads.
- Fields:
  - descriptor_state (enum: `available` | `unavailable`, required)
  - trend_label (string | null)
  - direction (enum: `up` | `down` | null)
  - strength (string | null)
  - selected_lookback_points (integer | null)
  - observed_on (date string | null)
  - reason_code (string | null)
- Validation rules:
  - `descriptor_state` is always present.
  - When `descriptor_state=available`, `trend_label`, `direction`, `strength`, `selected_lookback_points`, and `observed_on` are required.
  - When `descriptor_state=unavailable`, semantic fields may be null and `reason_code` should explain unavailability.

## Entity: DatasetDetailObservationPoint (Contract Extension)

- Purpose: Detail response observation point enriched with as-of trend state for tooltip rendering.
- Fields:
  - observed_on (date string, required)
  - value (number, required)
  - reported_at (date-time string, required)
  - attributes (object, required)
  - as_of_trend_descriptor (`ObservationAsOfTrendDescriptor`, required)
- Validation rules:
  - Observation ordering remains unchanged from existing detail response behavior.
  - `as_of_trend_descriptor` must be present for every observation.
  - Missing as-of matches must emit explicit `descriptor_state=unavailable` rather than omitting the field.

## Entity: DatasetDetailAsOfTrendEnvelope (Read Model)

- Purpose: End-to-end detail payload carrying both dataset-level and observation-level trend state.
- Fields:
  - canonical_trend_descriptor (existing dataset-level descriptor, required)
  - lookback_trend_snapshots (existing dataset-level diagnostic snapshots, required array)
  - observations (array of `DatasetDetailObservationPoint`, required)
- Validation rules:
  - Existing dataset-level fields remain backward compatible.
  - Observation-level as-of descriptors are additive and required for each observation.

## Entity: ObservationTooltipTrendViewModel (UI Read Model)

- Purpose: Tooltip-ready projection for one hovered chart point.
- Fields:
  - date_label (string)
  - value_label (string)
  - movement_label (string | null)
  - as_of_trend_descriptor (`ObservationAsOfTrendDescriptor`)
  - trend_indicator_state (derived enum: `strong_up` | `mild_up` | `mild_down` | `strong_down` | `unavailable`)
- Validation rules:
  - `trend_indicator_state` is derived only from API descriptor fields.
  - Tooltip always renders one chip row at the bottom, including unavailable state.

## Relationships

- One dataset detail response has many `DatasetDetailObservationPoint` records.
- Each `DatasetDetailObservationPoint` has exactly one `ObservationAsOfTrendDescriptor`.
- Each observation-level descriptor is resolved from persisted canonical trend descriptors for that observation context.
- Dataset-level canonical descriptor remains independent and continues to represent the latest state, not per-observation state.

## Deterministic Resolution Rules

- For each observation in the detail payload:
  - resolve descriptor candidate(s) for that observation context
  - apply deterministic tie-break order when candidates compete
  - emit explicit unavailable descriptor when no candidate exists
- Determinism requirements:
  - identical dataset and observation windows must produce identical as-of descriptor outputs
  - tie-break implementation must be order-stable and test-covered

## State Transitions

- Observation included in detail payload -> backend attempts as-of descriptor resolution.
- Resolution succeeds -> observation emits `descriptor_state=available` descriptor.
- Resolution absent/invalid context -> observation emits `descriptor_state=unavailable` descriptor.
- Frontend tooltip hover -> chart point maps directly to observation descriptor and renders chip.

## Compatibility Notes

- Feature is additive to existing dataset detail contract.
- Existing consumers reading top-level canonical descriptor remain compatible.
- Tooltips become observation-time-aware without requiring additional fetches.
