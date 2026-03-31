# Comparison Overlay Contract

## Scope

Defines externally visible behavior for comparison selection, compatibility gating, timeline projection, and comparison-page rendering.

## Contract Rules

### 1. Selection Lifecycle

- Dataset detail surfaces expose add/remove comparison action.
- Selection set is unique by dataset identifier.
- Maximum selections are capped by `MAX_COMPARISON_DATASETS` (initially 5).
- Add attempts beyond the cap are rejected without mutating existing selection.
- Selection count indicator reflects latest set size across supported surfaces.

### 2. Persistence and Integrity

- Comparison state persists in browser-local storage.
- Persisted state includes:
  - selected dataset identifiers
  - chart mode
  - relative baseline settings
- If persisted state is invalid/corrupted, comparison experience enters blocked state until manual reset.

### 3. Comparison Page Eligibility

- Comparison chart requires at least 2 selected datasets.
- With fewer than 2 selected datasets, page renders instructional empty state.
- Comparison page omits:
  - detail metadata/metrics side rail
  - observation table

### 4. Mode Compatibility Rules

- Observed-value mode is valid only when all selected datasets are unit-compatible.
- If incompatibility is present while observed mode is active:
  - system auto-switches to relative mode
  - user receives clear explanation
  - observed-mode control remains disabled until compatibility restored

### 5. Relative Baseline Rules

- Relative mode uses one shared baseline configuration for all compared datasets.
- Rolling baseline uses one shared offset.
- Fixed baseline resolution per series uses fallback sequence:
  1. nearest prior observation to selected date
  2. if none exists, nearest observation of any kind

### 6. Timeline Projection Rules

- Unified chart timeline uses union of all selected-series observation dates.
- Missing series value on a timeline date renders as gap (null), not interpolated value.

### 7. Color Mapping Rules

- Dataset line colors are stable within the current comparison selection.
- Color identity is not a global/database-wide dataset attribute.

## Validation Signals

- Selection cap enforcement and uniqueness are observable in UI behavior tests.
- Compatibility transitions are observable in mode toggles and messaging.
- Timeline and gap rules are observable in chart data projection tests.
- Corrupted-state fail-hard behavior is observable in persistence/state initialization tests.
