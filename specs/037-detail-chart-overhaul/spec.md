# Feature Specification: Dataset Detail Chart Overhaul

**Feature Branch**: `[037-detail-chart-overhaul]`  
**Created**: 2026-03-29  
**Status**: Draft  
**Input**: User description: "Overhaul the frontend dataset detail page chart: make the chart fill available space down to the bottom of the metadata column, remove the chart border, remove the observations footnote text, default the chart to all-history view, add a 5Y time filter, order time filters from longest range on the left to shortest on the right, hide time filters that do not have enough data, remove point dots from the line chart, increase spacing between x-axis labels, and show a pointer cursor on time-filter buttons."

## User Scenarios & Testing _(mandatory)_

### User Story 1 - Read The Trend More Clearly (Priority: P1)

As a discovery visitor, I can view a larger, cleaner historical trend area on the dataset detail page so I can understand the shape of the data without visual clutter or wasted space.

**Why this priority**: The trend chart is the primary visual summary of the dataset, so readability and visual prominence have the highest user impact.

**Independent Test**: Open a dataset detail page with observation history and verify the chart expands to use the full available width, visually extends to the bottom of the adjacent metadata area, shows only the trend line without point markers, has no enclosing chart border, and no longer shows the prior observation-count footnote.

**Acceptance Scenarios**:

1. **Given** a dataset detail page with observations is loaded, **When** the visitor views the analysis section, **Then** the chart uses the full available horizontal space within its section and visually extends downward to align with the bottom of the adjacent metadata column.
2. **Given** the chart is visible, **When** the visitor scans the trend area, **Then** the chart appears without a surrounding border, without point dots along the line, and without the previous observation-count footnote text.
3. **Given** the chart contains dated points across the horizontal axis, **When** the axis labels are rendered, **Then** the label spacing is loose enough that adjacent labels are easier to distinguish at a glance.

---

### User Story 2 - Start With The Full Historical Picture (Priority: P2)

As a discovery visitor, I can land on the chart already showing the full history and then narrow the visible range only when shorter windows are meaningful for the available data.

**Why this priority**: Showing the full history by default prevents visitors from missing long-term context and reduces the risk of a misleading first impression.

**Independent Test**: Open dataset detail pages with long, medium, and short histories and verify the chart defaults to the all-history view, includes a 5-year option when enough history exists, orders visible filters from longest to shortest, hides options that extend beyond the available history, and shows a pointer cursor for visible time-filter buttons.

**Acceptance Scenarios**:

1. **Given** a dataset has observation history, **When** the detail page first loads, **Then** the chart defaults to the all-history view instead of a shorter preset window.
2. **Given** a dataset has enough historical coverage for multiple time windows, **When** the range controls are shown, **Then** the visible controls are ordered from longest range on the left to shortest on the right, with all-history first and the shortest visible option last.
3. **Given** a dataset does not have enough history to support one or more shorter or longer preset windows, **When** the chart renders, **Then** only the time filters supported by the available history are shown.
4. **Given** a dataset has at least five years of history, **When** the range controls are shown, **Then** a 5-year option is available as a selectable filter between all-history and shorter-range presets.
5. **Given** one or more time filters are visible, **When** the visitor hovers or targets a filter button with a pointing device, **Then** the control presents a pointer cursor to indicate clickability.

---

### User Story 3 - Avoid Dead-End Or Misleading Controls (Priority: P3)

As a discovery visitor, I can trust that every visible chart control represents a meaningful change in the trend view rather than a duplicate or unavailable state.

**Why this priority**: Removing non-meaningful options improves trust in the chart controls and keeps the page from presenting controls that do not actually help the visitor.

**Independent Test**: Compare chart controls across datasets with minimal, partial, and extensive history and verify that unavailable time windows are omitted, the remaining controls always produce meaningful range changes, and the no-data experience remains explicit.

**Acceptance Scenarios**:

1. **Given** a dataset has no observations, **When** the chart area renders, **Then** the page continues to show an explicit no-data message instead of empty controls or a blank plot.
2. **Given** a dataset has only limited history, **When** the visitor looks at the chart controls, **Then** no control is shown for a time span that the dataset cannot meaningfully support.
3. **Given** a visitor changes between the visible time filters, **When** the chart updates, **Then** each visible option presents a distinct historical view rather than repeating the same unsupported range state.

### Edge Cases

- What happens when a dataset has no observations? The trend area continues to show explicit no-data messaging and does not show time filters.
- What happens when a dataset has only enough history for the all-history view? The chart defaults to all-history and hides the time-filter control set entirely.
- What happens when a dataset supports some but not all preset windows? Only the supported windows are shown, preserving longest-to-shortest ordering among the visible options.
- What happens when a dataset has exactly five years of history? The 5-year option is shown and behaves as a distinct filter.
- What happens when x-axis labels would otherwise crowd together? The rendered spacing remains visibly looser than the current chart so labels are easier to scan.
- What happens when the chart is displayed on narrower viewports? The chart remains readable, preserves the same default all-history behavior, and avoids clipped controls or text.

## Requirements _(mandatory)_

### Functional Requirements

- **FR-001**: The system MUST render the dataset detail trend chart so it uses the full available horizontal space within the trend section.
- **FR-002**: The system MUST size and position the chart area so the plotted region visually extends downward to align with the bottom edge of the adjacent metadata column in the loaded detail-page layout.
- **FR-003**: The system MUST remove the visible border treatment that currently surrounds the chart plotting area.
- **FR-004**: The system MUST remove the observation-count footnote text that currently appears beneath the chart.
- **FR-005**: The system MUST default the chart to the all-history view whenever observation data is available.
- **FR-006**: The system MUST provide an additional 5-year time filter for datasets with enough historical coverage to support that view.
- **FR-007**: The system MUST order visible time filters from longest range on the left to shortest on the right.
- **FR-008**: The system MUST hide any preset time filter that the available dataset history does not meaningfully support.
- **FR-009**: The system MUST hide the time-filter control group entirely when no preset time filters beyond the active all-history view are available.
- **FR-010**: The system MUST render the chart trend as a line without point dots or equivalent point markers in the default loaded state.
- **FR-011**: Visible time-filter buttons MUST present a pointer cursor for pointer-device users.
- **FR-012**: The system MUST increase the visual separation of x-axis label text compared with the current chart so adjacent labels are easier to distinguish.
- **FR-013**: The system MUST preserve the explicit no-data chart state for datasets without observations.
- **FR-014**: The system MUST preserve safe rendering of externally sourced observation labels and values.
- **FR-015**: The chart overhaul MUST remain readable and usable across supported desktop and mobile detail-page layouts.

### Key Entities _(include if feature involves data)_

- **Historical Trend View**: The primary charted representation of one dataset's observation history within the detail page analysis section.
- **Time Filter Option**: A visitor-selectable historical range control representing all-history or a preset lookback window such as 5 years, 1 year, 6 months, or 1 month.
- **Supported History Window**: A time span that the dataset has enough observation history to display as a meaningful distinct chart view.
- **Trend Axis Label Set**: The visible x-axis date labels shown beneath the charted line.

## Success Criteria _(mandatory)_

### Measurable Outcomes

- **SC-001**: In dataset-detail QA review, 100% of sampled chart renders use the full available trend-section width and visually align downward with the bottom of the adjacent metadata column.
- **SC-002**: In visual regression review, 100% of sampled chart renders show no enclosing chart border, no observation-count footnote, and no point dots on the line.
- **SC-003**: In interaction QA, 100% of sampled dataset detail pages open with all-history selected by default whenever observations are present.
- **SC-004**: In control-availability QA, 100% of sampled datasets show only supported time filters, with visible filters ordered from longest to shortest and the 5-year filter present whenever five years of history are available.
- **SC-005**: In interaction QA, 100% of sampled visible time-filter buttons present a pointer cursor for pointer-device users.
- **SC-006**: In readability review across agreed desktop and mobile viewport samples, 100% of audited charts show clearer x-axis label separation with no clipped labels or overlapping controls.

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

- "All-history" remains available whenever the dataset has at least one observation and is treated as the default selected state.
- A preset time filter is considered supported only when the dataset has enough history for that filter to represent a meaningful view rather than duplicating a longer-range or all-history state.
- The chart continues to live within the existing dataset detail page structure, alongside the existing insight and metadata content, rather than moving to a different page section.
- This feature changes the chart presentation and control behavior only; it does not change the underlying dataset detail route, source data, or observed-values table scope.

## Dependencies

- Existing dataset detail pages that already render a historical trend area alongside summary and metadata content.
- Existing dataset detail payloads that provide chronological observation history for the chart.
- Existing detail-page no-data, error, and not-found states that remain authoritative for fallback behavior.
