# Relative Change Visualization Contract

## Scope

This contract governs dataset-detail chart behavior when users switch from observed values to relative-change visualization.

It covers:

- relative-change mode switching
- rolling baseline offset behavior
- fixed baseline behavior (date and index/offset)
- formula semantics
- non-computable point handling
- baseline persistence across scope changes

## Mode Contract

- Users can switch between observed-value mode and relative-change mode.
- Relative-change mode presents percentage outputs, not raw-value outputs.
- Mode switching preserves chart usability and existing detail-page fallback states.

## Computation Contract

- Relative change uses signed baseline-relative percentage:
  - ((current value - baseline value) / baseline value) \* 100
- Computation order follows chronological observation sequence.
- Formula semantics are identical across rolling and fixed baseline workflows; only baseline selection differs.

## Rolling Baseline Contract

- Rolling baseline mode compares each point with a prior observation at user-selected offset.
- Offset options include at least 1, 2, and 3 and may include larger values when history allows.
- Points lacking sufficient history are non-computable and rendered as gaps.

## Fixed Baseline Contract

- Fixed baseline mode compares all eligible points against one constant baseline observation.
- Baseline can be selected by:
  - exact available observation date
  - observation index/offset
- Date-mode baseline selection is exact-match only.
- Date selector offers only observation dates available in active scope.

## Non-Computable Contract

- Non-computable points remain in timeline position as unavailable gaps.
- Non-computable points are not coerced to fallback numeric values (for example 0% or carry-forward).
- The UI communicates unavailable conditions explicitly.

## Scope-Change Persistence Contract

- On chart time-range or filter changes, baseline mode/parameters are preserved when valid.
- If preserved settings become invalid, settings stay visible and the chart presents explicit unavailable state.
- The system does not silently reset or auto-adjust baseline selections.

## Regression Contract

- Relative-change additions must not break existing dataset-detail navigation, error states, empty states, or observed-value chart behavior.
- Tests and manual verification must cover:
  - formula correctness and sign behavior
  - rolling/fixed baseline behavior
  - non-computable gap rendering
  - baseline persistence and invalidation behavior
  - exact available-date selection behavior
