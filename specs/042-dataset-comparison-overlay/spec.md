# Feature Specification: Dataset Comparison Overlay

**Feature Branch**: `042-dataset-comparison-overlay`  
**Created**: 2026-03-31  
**Status**: Draft  
**Input**: User description: "Dataset comparison on detail charts: allow users to overlay multiple datasets on the same chart, permit absolute-value comparison when units are compatible, and permit broader comparison in relative-change mode."

## Clarifications

### Session 2026-03-31

- Q: How should the comparison chart align datasets that have different observation dates? → A: Use a union of all dates from selected datasets and render missing values as gaps.
- Q: When users leave and return to the comparison page, should chart mode/baseline settings be restored from browser-local state or reset to defaults? → A: Persist and restore chart mode and baseline settings in browser-local state.
- Q: How should the comparison page assign line colors when datasets are added/removed over time? → A: Use stable dataset-to-color mapping within the current comparison selection only; do not define or persist database-wide constant colors.
- Q: In relative fixed-baseline mode, how should each dataset choose a baseline when the exact selected baseline date is missing? → A: Use the nearest prior observation; if none exists, fall back to the nearest observation of any kind.
- Q: If browser-local comparison state is invalid or corrupted, what should the system do? → A: Fail hard and block comparison until manual reset.

## User Scenarios & Testing _(mandatory)_

<!--
  IMPORTANT: User stories should be PRIORITIZED as user journeys ordered by importance.
  Each user story/journey must be INDEPENDENTLY TESTABLE - meaning if you implement just ONE of them,
  you should still have a viable MVP (Minimum Viable Product) that delivers value.

  Assign priorities (P1, P2, P3, etc.) to each story, where P1 is the most critical.
  Think of each story as a standalone slice of functionality that can be:
  - Developed independently
  - Tested independently
  - Deployed independently
  - Demonstrated to users independently
-->

### User Story 1 - Build A Comparison Set (Priority: P1)

As a dataset viewer, I can add datasets from detail pages into a comparison set, see how many are selected, and open a dedicated comparison page from the top navigation.

**Why this priority**: Without a reliable way to collect and review selected datasets, comparison cannot happen at all.

**Independent Test**: Open multiple dataset detail pages, add/remove items, verify count indicator updates in navigation, refresh, and confirm selections persist and can be opened in the comparison page.

**Acceptance Scenarios**:

1. **Given** I am on a dataset detail page, **When** I click "Add to comparison", **Then** that dataset is added to my comparison set and the top-nav comparison count increments.
2. **Given** I already added a dataset, **When** I remove it from the detail page, **Then** it is removed from the comparison set and the top-nav comparison count decrements.
3. **Given** I have one or more datasets in my comparison set, **When** I refresh or navigate to another page, **Then** my selection remains available in the same browser.
4. **Given** I have reached the maximum of 5 selected datasets, **When** I try to add another, **Then** the system prevents the addition and shows a clear maximum-selection message.

---

### User Story 2 - Compare Trends On A Dedicated Page (Priority: P2)

As a dataset viewer, I can open a dedicated comparison page that focuses on a full-width chart of selected datasets without extra detail-page side content.

**Why this priority**: A dedicated comparison surface improves trend analysis clarity and avoids visual clutter.

**Independent Test**: Add at least two datasets and open the comparison page from top navigation; verify chart-focused layout appears, with no metadata rail and no observation table.

**Acceptance Scenarios**:

1. **Given** I have selected at least 2 datasets, **When** I open the comparison page via the top-nav comparison icon, **Then** I see a chart-focused page with a full-width comparison chart.
2. **Given** I am on the comparison page, **When** the page renders, **Then** the left-side metrics/metadata rail is not shown.
3. **Given** I am on the comparison page, **When** the page renders, **Then** no observation table is shown.
4. **Given** I have fewer than 2 selected datasets, **When** I open the comparison page, **Then** I see a clear instruction to select at least 2 datasets before comparison is available.

---

### User Story 3 - Safe Mode Handling For Unit Compatibility (Priority: P3)

As a dataset viewer, I can compare observed values only when units are compatible, and when they are not, the chart automatically switches to relative change with clear guidance.

**Why this priority**: It prevents misleading absolute-value comparisons while still allowing meaningful cross-series analysis.

**Independent Test**: Build a mixed-unit selection, attempt absolute mode, and verify the experience auto-switches to relative mode, displays explicit messaging, and prevents switching back to absolute until compatibility is restored.

**Acceptance Scenarios**:

1. **Given** all selected datasets have matching units, **When** I choose observed-value mode, **Then** the chart displays absolute values for all selected datasets.
2. **Given** selected datasets have incompatible units, **When** absolute mode would apply, **Then** the system automatically switches to relative mode and informs me why.
3. **Given** selected datasets have incompatible units, **When** I view mode controls, **Then** absolute mode is visibly disabled.
4. **Given** relative mode is active for multiple selected datasets, **When** I choose rolling or fixed baseline comparison, **Then** all series use the same selected offset or baseline reference.

---

### Edge Cases

- What happens when a user adds the same dataset multiple times from different pages? The comparison set must remain unique and count it only once.
- What happens when a selected dataset becomes unavailable before rendering comparison? The page must show a clear unavailable-state message for that dataset and continue rendering remaining valid datasets.
- What happens when all selected datasets are removed on the comparison page? The page must show an empty-state prompt to add datasets and must not show a broken chart.
- What happens when a user selection stored in-browser exceeds the current maximum after a future policy change? The system must apply the current maximum safely and guide the user to resolve overflow.
- What happens when incompatible units become compatible after removals? Absolute mode must become available again without requiring a full page reload.
- What happens when compared datasets do not share all observation dates? The chart must include the union of dates and display missing points as gaps rather than fabricating values.
- What happens when a fixed baseline date is missing for one or more selected datasets? Each series must first use the nearest prior observation; if none exists, it must use the nearest available observation.
- What happens when browser-local comparison state is invalid or corrupted? The comparison experience must fail hard, block comparison rendering, and require user-triggered reset before continuing.

## Requirements _(mandatory)_

### Functional Requirements

- **FR-001**: The system MUST replace the dataset detail page primary export action with an "Add to comparison" action.
- **FR-002**: The system MUST support removing a dataset from the comparison set from both the dataset detail page and the comparison page.
- **FR-003**: The system MUST show a comparison indicator in top navigation between search and user controls, with a numeric count of selected datasets.
- **FR-004**: The system MUST open a dedicated comparison page when the comparison navigation indicator is activated.
- **FR-005**: The comparison page MUST present a full-width comparison chart and MUST NOT display the dataset detail metadata/metrics side rail.
- **FR-006**: The comparison page MUST NOT display an observation table in this feature scope.
- **FR-007**: The system MUST require a minimum of 2 selected datasets for chart comparison and MUST present a clear prompt when fewer than 2 are selected.
- **FR-008**: The system MUST persist the comparison set in browser-local storage so selections remain available after refresh and navigation on the same browser.
- **FR-009**: The system MUST enforce a maximum of 5 selected datasets using a single centralized configuration value for the limit.
- **FR-010**: The system MUST block additions beyond the maximum and MUST keep the existing selection unchanged.
- **FR-011**: The system MUST allow observed-value comparison only when all selected datasets have compatible units.
- **FR-012**: If selected datasets are not unit-compatible, the system MUST allow comparison only in relative-change mode.
- **FR-013**: When incompatible units are present and absolute mode would otherwise be active, the system MUST automatically switch to relative mode and provide clear user-facing explanation.
- **FR-014**: While incompatible units remain in the selected set, the system MUST disable the control for switching to absolute mode.
- **FR-015**: For multi-dataset relative comparison, the system MUST apply one shared baseline configuration across all compared series.
- **FR-016**: Shared relative baseline configuration MUST support a rolling offset reference applied uniformly across all compared series.
- **FR-017**: Shared relative baseline configuration MUST support a fixed baseline reference applied uniformly across all compared series.
- **FR-018**: The system MUST ensure each selected dataset appears at most once in the comparison set.
- **FR-019**: The top-nav comparison count MUST update immediately when datasets are added or removed from any supported surface.
- **FR-020**: The system MUST provide user-visible feedback when add, remove, limit, or mode-auto-switch events occur.
- **FR-021**: The comparison chart timeline MUST use the union of observation dates across selected datasets.
- **FR-022**: When a selected dataset has no value for a date on the shared chart timeline, the chart MUST render a gap for that series at that date.
- **FR-023**: The system MUST persist and restore comparison chart display settings in browser-local state, including observed-versus-relative mode and relative baseline configuration.
- **FR-024**: Within a current comparison selection, each dataset MUST keep a stable line color for that visualization, and color assignment MUST NOT be treated as a database-wide or globally constant dataset attribute.
- **FR-025**: In fixed-baseline relative comparison, when a series lacks the exact selected baseline date, the system MUST select that series baseline from the nearest prior observation; if no prior observation exists, the system MUST use the nearest available observation.
- **FR-026**: If browser-local comparison state is invalid or corrupted, the system MUST block comparison until the user performs a manual reset of comparison state.

### Key Entities _(include if feature involves data)_

- **Comparison Selection Set**: User-managed set of selected datasets for comparison; includes unique dataset identifiers, display labels, unit metadata required for compatibility checks, selection order, and persisted browser-local state.
- **Comparison Mode State**: Shared display mode for the comparison chart; includes observed-value mode versus relative-change mode, mode availability flags, and user-facing reason messaging when absolute mode is disabled.
- **Relative Baseline Configuration**: Shared relative reference used across all compared series; includes baseline type (rolling or fixed) and one common reference value (offset or fixed baseline selector).
- **Comparison Page View**: Dedicated chart-focused experience for selected datasets; includes selected dataset list for management, full-width chart area, and comparison eligibility/empty-state guidance.
- **Visualization Color Mapping**: Per-selection mapping of dataset identity to chart line color, stable within the active comparison selection and independent from any global metadata.

### Assumptions

- Comparison selections are scoped to one browser context and are not synchronized across devices or accounts in this feature.
- Persisted comparison state in browser-local storage includes both selected datasets and comparison chart settings for continuity across revisit and refresh.
- Replacing the detail-page CSV action with "Add to comparison" is acceptable for this phase.
- Users need clear status messaging for auto-mode transitions and selection-limit enforcement, but detailed export and tabular comparison are out of scope.

## Success Criteria _(mandatory)_

### Measurable Outcomes

- **SC-001**: 95% of users in validation can add two datasets and reach the comparison page in 60 seconds or less.
- **SC-002**: 100% of incompatible-unit validation scenarios prevent absolute observed-value comparison and present clear explanatory messaging.
- **SC-003**: 100% of relative-mode validation scenarios with multiple compared datasets apply one shared baseline configuration consistently across rendered series.
- **SC-004**: 100% of limit-enforcement validation scenarios prevent selection counts from exceeding 5 and preserve existing selections without unintended replacements.
- **SC-005**: 95% of users in validation can remove one or more selected datasets from either the detail page or comparison page on first attempt.

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
