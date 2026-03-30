# Feature Specification: Relative Change Visualizations

**Feature Branch**: `[041-relative-change-visualization]`  
**Created**: 2026-03-30  
**Status**: Draft  
**Input**: User description: "we are going to create a new feature spec for a new feature: relative change visualizations. we will add the ability to, instead of showing a chart of the observed values, showing the chart with percentage change relative to some earlier value. we will enable users to visualize percentage change relative to some baseline in 2 ways. first we will allow visualizing the data as percentage change relative to some previous value on a rolling basis, so for example relative change compared to 1 observation ago, 2 observations ago, 3 observations ago, n observations ago. In addition, we will allow it to visualize the data compared to some constant baseline, e.g. comparing all values as percentage change relative to an observation 10 years ago. Please write a spec for this work"

## Clarifications

### Session 2026-03-30

- Q: How should users choose the fixed baseline reference for relative-change mode? → A: Both date selector and observation index/offset selector.
- Q: When a relative-change point cannot be computed, how should it be shown in the chart? → A: Keep points in timeline as gaps/unavailable values (no numeric value shown).
- Q: Which baseline setting behavior should be used when the user changes dataset chart time range or other chart filters? → A: Preserve user-selected baseline settings if still valid; otherwise keep settings and show unavailable state.
- Q: Which percentage-change definition should be the canonical calculation for relative-change visualizations? → A: Signed baseline-relative percent change ((current - baseline) / baseline × 100).
- Q: When a user selects a baseline date that does not exactly match an observation date, what rule should apply? → A: Exact-match-only date selection by showing only available observation dates in the UI.

## User Scenarios & Testing _(mandatory)_

### User Story 1 - Switch To Relative Change View (Priority: P1)

As a dataset viewer, I can switch from raw observed values to relative percentage change so I can quickly understand growth or decline without manually calculating differences.

**Why this priority**: The primary value of the feature is making relative change visible in the chart at all.

**Independent Test**: Open a dataset detail page with observations, switch chart mode to relative change, and verify the plotted values represent percentages relative to a selected baseline instead of raw values.

**Acceptance Scenarios**:

1. **Given** a dataset detail chart with observations, **When** the viewer selects relative change mode, **Then** the chart displays percentage-change values rather than raw observed values.
2. **Given** relative change mode is active, **When** the viewer returns to observed value mode, **Then** the chart displays the original raw-value view without losing chart usability.
3. **Given** relative change mode is active, **When** the viewer inspects axis labels and tooltip values, **Then** values are presented as percentages and are clearly distinguishable from raw-value formatting.

---

### User Story 2 - Compare Against Rolling Baseline (Priority: P2)

As a dataset viewer, I can visualize change relative to a rolling prior observation offset (for example 1, 2, 3, or n observations ago) so I can evaluate short- and medium-horizon momentum.

**Why this priority**: Rolling comparison is the first requested baseline mode and supports common trend-analysis workflows.

**Independent Test**: In relative change mode, choose multiple rolling offsets and verify each selection updates the chart to use percentage change versus the selected prior-observation offset.

**Acceptance Scenarios**:

1. **Given** relative change mode is active, **When** the viewer selects a rolling offset of 1 observation, **Then** each displayed point reflects percentage change relative to the immediately preceding observation.
2. **Given** relative change mode is active, **When** the viewer selects a rolling offset of 2 or 3 observations, **Then** each displayed point reflects percentage change relative to that chosen offset.
3. **Given** relative change mode is active, **When** the viewer selects a larger rolling offset n, **Then** only valid points with sufficient history are visualized and insufficient-history points are handled without breaking the chart.

---

### User Story 3 - Compare Against Fixed Baseline (Priority: P3)

As a dataset viewer, I can compare all points against one fixed historical baseline (for example 10 years ago) so I can understand long-term change from a constant reference point.

**Why this priority**: Fixed-baseline comparison is explicitly requested and offers a complementary long-horizon view to rolling comparisons.

**Independent Test**: In relative change mode, set a fixed historical baseline and verify the full visible series is expressed as percentage change relative to that single baseline reference.

**Acceptance Scenarios**:

1. **Given** relative change mode is active, **When** the viewer selects fixed baseline comparison, **Then** all eligible points are plotted as percentage change relative to one constant baseline observation.
2. **Given** fixed baseline comparison is active, **When** the viewer chooses a baseline by date or by observation index/offset and changes that reference, **Then** the chart recalculates using the newly selected constant baseline.
3. **Given** a fixed baseline reference is unavailable for the selected data scope, **When** the viewer attempts fixed baseline comparison, **Then** the interface provides a clear unavailable-state message and preserves a usable chart experience.

### Edge Cases

- What happens when a selected rolling offset is larger than available history? The interface keeps the chart stable and clearly indicates insufficient history for some or all points.
- What happens when the baseline observation value is zero? The interface avoids undefined percentage math and communicates an unavailable or non-computable result state.
- What happens when a dataset has very sparse or irregular observation cadence? Relative change calculations still respect observation order and avoid misleading interpolation assumptions.
- What happens when filters or time ranges change after selecting a baseline mode? The system preserves the user-selected baseline mode and parameters when still valid; if invalid in the new scope, it keeps those selections visible and shows an explicit unavailable state.
- What happens when a dataset has only one observation? Relative-change mode remains accessible but shows no computed series and an explicit no-data explanation for comparison output.
- What happens when only some points are non-computable in the visible range? Those positions remain in the timeline as unavailable gaps and do not render substitute numeric values.
- What happens when a fixed-baseline date is chosen? The date selector offers only observation dates available in the current scope so non-existent dates cannot be selected.

## Requirements _(mandatory)_

### Functional Requirements

- **FR-001**: The system MUST allow users to switch the dataset detail chart between observed-value mode and relative-change mode.
- **FR-002**: In relative-change mode, the system MUST express plotted values as percentage change relative to a chosen baseline definition.
- **FR-003**: The system MUST support rolling baseline comparison where each point is compared to a prior observation offset selected by the user.
- **FR-004**: The rolling baseline selector MUST support at minimum 1, 2, and 3 observations ago, and must allow selecting larger offsets up to the maximum valid history for the current scope.
- **FR-005**: The system MUST support fixed baseline comparison where all eligible points are compared to one constant baseline observation.
- **FR-006**: The system MUST allow users to set or change the fixed baseline reference while relative-change mode is active.
- **FR-007**: The fixed-baseline workflow MUST support selecting the baseline by date.
- **FR-008**: The fixed-baseline workflow MUST support selecting the baseline by observation index/offset.
- **FR-009**: The system MUST prevent invalid percentage-change rendering when a required baseline is missing or non-computable, and MUST communicate the unavailable condition clearly.
- **FR-010**: Non-computable relative-change points MUST remain in chronological timeline position as unavailable gaps and MUST NOT be coerced to fallback numeric values.
- **FR-011**: The system MUST preserve existing chart usability states (empty-data, loading, and error experiences) when relative-change mode or baseline settings are used.
- **FR-012**: The system MUST render relative-change axis and tooltip values in percentage format to avoid confusion with raw observed values.
- **FR-013**: The system MUST compute relative change using signed baseline-relative percent change: ((current value - baseline value) / baseline value) × 100.
- **FR-014**: The system MUST ensure relative-change calculations are based on chronological observation order.
- **FR-015**: Changing between baseline modes or baseline parameters MUST update the chart results immediately for the currently visible dataset scope.
- **FR-016**: When chart time range or filters change, the system MUST preserve user-selected baseline mode and parameters if they remain valid in the new scope.
- **FR-017**: If preserved baseline settings become invalid after a scope change, the system MUST keep those settings visible and present an explicit unavailable state instead of silently resetting or auto-adjusting.
- **FR-018**: The system MUST preserve compatibility with existing dataset detail navigation and chart interactions while adding relative-change options.
- **FR-019**: The feature MUST include automated and manual validation coverage for mode switching, rolling baseline offsets, fixed baseline comparisons, non-computable baseline handling, baseline persistence behavior across scope changes, and signed-percentage calculation correctness.
- **FR-020**: Fixed-baseline date selection MUST be exact-match only and MUST use available observation dates only.
- **FR-021**: The fixed-baseline date selector UI MUST present only selectable dates that exist in the currently active dataset scope.

### Key Entities _(include if feature involves data)_

- **Chart Value Mode**: The active visualization mode on the detail chart (observed values or relative percentage change).
- **Rolling Baseline Offset**: A user-selected integer indicating how many observations back each point should be compared against.
- **Fixed Baseline Reference**: A single observation chosen as the constant baseline for comparing all eligible points in view, selectable by exact available date or by observation index/offset.
- **Relative Change Point**: A computed signed baseline-relative percentage-change data point derived from an observation and its baseline value.
- **Computability State**: The status for whether a relative-change point or series can be calculated (valid, insufficient history, or undefined baseline), where non-computable points are represented as timeline gaps.

## Success Criteria _(mandatory)_

### Measurable Outcomes

- **SC-001**: In manual QA, 100% of audited dataset detail pages can switch between observed-value and relative-change modes without navigation errors or chart breakage.
- **SC-002**: In validation scenarios for rolling comparison, 100% of tested offsets (1, 2, 3, and one larger n value where history exists) produce expected percentage-change outputs for sampled points.
- **SC-003**: In validation scenarios for fixed-baseline comparison, 100% of tested baseline selections produce expected percentage-change outputs for sampled points in the active scope.
- **SC-004**: In non-computable baseline scenarios (insufficient history or zero baseline), 100% of audited interactions present a clear unavailable state and avoid misleading plotted values.
- **SC-005**: In user acceptance review, at least 90% of reviewers report that distinguishing long-term versus short-term relative movement is easier than in raw-value-only view.

## Constitution Alignment _(mandatory)_

- **CA-001 Quality Gates**: Feature can satisfy linting, formatting, type checking, and
  automated test gates without suppressions, bypasses, or workaround-only code, and the
  full-suite stop rule (`pnpm exec nx run-many -t test --all`) can be satisfied before
  commit and before AI agent handoff/end of work. (Yes)
- **CA-002 Coverage**: Feature includes tests to keep backend/frontend coverage at or
  above 90% in affected projects, and can satisfy the commit-time coverage stop rule
  (`pnpm exec nx run-many -t coverage --all`). (Yes)
- **CA-003 Local Stack**: Feature is runnable in the unified local Docker Compose stack,
  or explicitly lists compose updates needed. (Yes)
- **CA-004 Contracts and Data Integrity**: Data/interface contract changes,
  provenance/timestamp impacts, and trend-alert reliability safeguards are defined.
  (Yes)
- **CA-005 Documentation Fidelity**: Relevant documentation is identified and will be
  created or updated in the same change for any impacted behavior, contracts, setup, or
  runbooks, including AGENTS.md when repository structure/workflows/tooling change.
  (Yes)
- **CA-006 Configuration Integrity**: Any new service or pipeline component that requires
  credentials or external API keys will fail hard (exception/non-zero exit/job-level
  failure) when those variables are absent — no soft outcome recording, no silent
  swallowing. `docker/compose/local.secrets.env` is declared as an `env_file` source
  for any Docker Compose service that requires secrets. (N/A)
- **CA-007 Frontend UI System**: For frontend changes, the feature uses HeroUI
  components, Tailwind utilities, and shared abstractions in
  `apps/frontend/src/components` for repeated patterns; it does not introduce duplicate
  one-off component patterns or new local CSS without a documented exception.
  (Yes)

## Assumptions

- Relative-change visualization is introduced on existing dataset detail chart surfaces and does not create a separate analytics page.
- Percentage change uses a standard baseline-relative formula and follows existing observation ordering semantics.
- Existing chart time-range controls continue to apply and relative-change calculations operate within the currently active range scope.
- Users can access both baseline methods from the same relative-change workflow without leaving the detail page.
- The feature focuses on visualization behavior and does not alter source ingestion or canonical observation ownership.

## Dependencies

- Existing dataset detail payloads that provide chronological observation history.
- Existing chart controls and detail-page interaction patterns that this feature extends.
- Existing no-data, not-found, and error-state handling on dataset detail pages.
- Existing quality-gate and validation workflows used for discovery page changes.
