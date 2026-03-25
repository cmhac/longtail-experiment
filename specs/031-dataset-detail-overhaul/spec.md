# Feature Specification: Dataset Detail Page Overhaul

**Feature Branch**: `[031-dataset-detail-overhaul]`  
**Created**: 2026-03-25  
**Status**: Draft  
**Input**: User description: "Overhaul dataset detail page based on attached mockup"

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

### User Story 1 - Understand Dataset At A Glance (Priority: P1)

As a visitor, I can open a dataset page and immediately understand what the dataset is, who provides it, the latest value context, and the broad direction of recent movement.

**Why this priority**: Fast comprehension at first glance is the primary purpose of the detail page and the highest-value outcome for discovery users.

**Independent Test**: Open a known dataset detail page and verify that source, title, latest observation summary, key comparison statistics, and trend visualization are all visible without extra navigation.

**Acceptance Scenarios**:

1. **Given** a visitor lands on a valid dataset detail page, **When** the page loads, **Then** the page presents clear source attribution, dataset title, and a high-visibility summary region.
2. **Given** the dataset has observation history, **When** the page renders, **Then** the page shows a historical trend section with chronological data and a visible time-range control.
3. **Given** the dataset includes supporting metadata, **When** the summary region is shown, **Then** key metadata values appear in a readable key-value format.

---

### User Story 2 - Inspect Recent Observation History (Priority: P2)

As a visitor, I can review recent observation rows beneath the chart so I can validate point-in-time values and recent changes without leaving the page.

**Why this priority**: The observations table supports trust and analysis by exposing exact values behind the trend.

**Independent Test**: Load a dataset with observations and verify the observed-values section shows date, value, and movement indicators in descending recency with a clear archive action.

**Acceptance Scenarios**:

1. **Given** a dataset has multiple observations, **When** the table section loads, **Then** recent rows display observation date and numeric value in a consistent format.
2. **Given** sequential observations are available, **When** weekly or period-over-period movement is rendered, **Then** positive, negative, and unchanged values are visually distinguishable.
3. **Given** there are more rows than the default visible set, **When** a visitor reaches the end of the visible rows, **Then** a clear action is shown to access additional historical rows.

---

### User Story 3 - Use Utility Actions Without Friction (Priority: P3)

As a visitor, I can use quick page actions (such as export and sharing entry points) from the dataset header so I can continue analysis or distribute findings.

**Why this priority**: Utility actions are important but secondary to understanding and inspection workflows.

**Independent Test**: Open a dataset detail page and verify utility controls are discoverable in the hero region and remain usable across desktop and mobile layouts.

**Acceptance Scenarios**:

1. **Given** the detail page hero is visible, **When** the visitor scans the header controls, **Then** export and sharing actions are clearly presented and distinct from informational content.
2. **Given** the visitor is on a narrow viewport, **When** the hero region reflows, **Then** utility controls remain visible and usable without overlap or clipping.

---

### Edge Cases

- What happens when a dataset has no observations? The page still shows metadata/summary context and a clear no-data message for trend and table sections.
- What happens when a dataset has only one observation? The trend section renders a meaningful single-point state and table remains readable.
- What happens when source-provided metadata is partially missing? The page renders available metadata and uses explicit fallback labels for missing fields.
- What happens when value changes are exactly zero? Movement indicators show a neutral state, not positive or negative cues.
- What happens when the page cannot load data due to upstream failure? The page shows a clear non-blocking error state that preserves shell navigation.
- What happens when a dataset identifier is invalid or missing? The visitor is shown the existing clear not-found experience.

## Requirements _(mandatory)_

### Functional Requirements

- **FR-001**: The system MUST present dataset source attribution and dataset title in a high-prominence hero region at the top of the detail page.
- **FR-002**: The system MUST provide utility actions in the hero region for dataset-level export and sharing entry points.
- **FR-003**: The system MUST display a summary rail that includes the latest observation value and at least two comparative contextual statistics derived from available history.
- **FR-004**: The system MUST display core metadata in a structured key-value format in the summary area.
- **FR-005**: The system MUST provide a historical trend section that visualizes observations in chronological order.
- **FR-006**: The historical trend section MUST provide user-selectable time-window controls including 1M, 6M, 1Y, and all-history views.
- **FR-007**: The trend section MUST allow inspection of individual observations through an interactive affordance or equivalent explicit value display.
- **FR-008**: The system MUST provide an observed-values section beneath the trend section that lists recent observations in tabular form.
- **FR-009**: Each observed-values row MUST include observation date, observed value, and period-over-period change when comparable prior values exist.
- **FR-010**: The observed-values section MUST provide clear visual distinction between positive, negative, and neutral movement states.
- **FR-011**: The observed-values section MUST support access to additional historical rows beyond the default visible subset and hide archive controls when no additional rows exist.
- **FR-012**: The page MUST preserve existing not-found handling for unknown dataset identifiers.
- **FR-013**: The page MUST preserve existing graceful error-state behavior when data retrieval fails.
- **FR-014**: The overhauled detail page MUST remain readable and usable across common desktop and mobile viewport ranges.
- **FR-015**: All externally sourced text and values displayed on the detail page MUST be rendered safely as escaped content.

### Key Entities _(include if feature involves data)_

- **Dataset Hero Summary**: Top-of-page information block containing source attribution, dataset title, and page utility actions.
- **Observation Insight Rail**: At-a-glance statistics area containing latest value and comparison metrics derived from observation history.
- **Historical Trend View**: Visual representation of chronological observations with user-selectable time windows.
- **Observed Value Record**: One table row containing observation date, numeric value, and directional period-over-period change.
- **Metadata Attribute Set**: Structured dataset descriptors (such as cadence, unit, and value context) shown in key-value format.

## Success Criteria _(mandatory)_

### Measurable Outcomes

- **SC-001**: In dataset-detail QA walkthroughs, 100% of sampled pages display source, title, latest value summary, trend section, and observed-values section on initial load.
- **SC-002**: In interaction QA, 95% of sampled visitors can identify the latest value and its recent directional change within 10 seconds of landing on the page.
- **SC-003**: In responsiveness QA across agreed desktop and mobile viewport samples, 100% of audited screens show no clipped controls, overlapping text, or inaccessible actions.
- **SC-004**: In data-fallback QA, 100% of tested no-data, partial-metadata, not-found, and load-error cases display explicit user-facing states rather than blank sections.

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

## Assumptions

- The current dataset detail route and backend contract remain the canonical source for detail data.
- Existing not-found and generic error handling patterns remain in scope and should be preserved in the overhaul.
- Export and sharing controls are treated as discoverable entry points in this phase, with no new authentication requirements.
- The page should prioritize desktop readability while maintaining fully usable mobile behavior.

## Dependencies

- Existing dataset detail payloads that provide metadata and chronological observations.
- Existing shell page layout, typography system, and global spacing conventions.
- Existing discovery navigation flows that route users from search/listing surfaces to dataset detail pages.
