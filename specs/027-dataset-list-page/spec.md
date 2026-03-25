# Feature Specification: Dataset List Page

**Feature Branch**: `[027-dataset-list-page]`  
**Created**: 2026-03-25  
**Status**: Draft  
**Input**: User description: "Create a frontend dataset list page based on provided screenshot with source/category filters, sorting, dataset cards, and request-new-dataset action"

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

### User Story 1 - Browse Available Datasets (Priority: P1)

As a dataset consumer, I can scan a structured list of datasets with clear metadata so I can quickly identify relevant series.

**Why this priority**: Core value comes from being able to discover and review datasets at a glance. Without this, filtering and sorting have no practical use.

**Independent Test**: Load the page and verify that a visible list of dataset cards appears with required metadata and readable hierarchy.

**Acceptance Scenarios**:

1. **Given** I open the datasets page, **When** initial content loads, **Then** I see a page title, a total-series summary, and a vertical list of dataset cards.
2. **Given** a dataset card is visible, **When** I review it, **Then** I can see the dataset source label, title, descriptive summary, topical tags, and last-updated context.
3. **Given** multiple cards are displayed, **When** I scroll through the list, **Then** each card preserves consistent information layout and visual hierarchy.

---

### User Story 2 - Refine and Sort Dataset Results (Priority: P2)

As a dataset consumer, I can narrow results by source and category and reorder results by a sort choice so I can find useful datasets faster.

**Why this priority**: Once baseline list visibility exists, filtering and sorting are the highest-impact controls for improving search efficiency.

**Independent Test**: Change source/category filters and sort choice, and verify result list updates to match selected controls.

**Acceptance Scenarios**:

1. **Given** the datasets list is visible, **When** I choose a specific source filter, **Then** displayed cards are limited to datasets from that source.
2. **Given** the datasets list is visible, **When** I choose a specific category filter, **Then** displayed cards are limited to datasets in that category.
3. **Given** filters are applied, **When** I clear or reset filters to all values, **Then** the full dataset set is restored.
4. **Given** the sort control is available, **When** I select a sort mode, **Then** the visible order updates to reflect that mode.

---

### User Story 3 - Take Action from the Listing Page (Priority: P3)

As a data requester, I can start a request for a new dataset from the listing page and access per-dataset action affordances so I can act without leaving discovery context.

**Why this priority**: Action pathways are important, but secondary to finding and evaluating datasets already in the catalog.

**Independent Test**: Click the primary request action and interact with card-level action affordances to verify they are consistently available and operable.

**Acceptance Scenarios**:

1. **Given** I am on the datasets page, **When** I click the primary request action, **Then** I am routed to or presented with the dataset request workflow entry point.
2. **Given** a dataset card is visible, **When** I inspect its action area, **Then** I see consistent per-item action affordances for saving and sharing.
3. **Given** I navigate between cards, **When** I interact with card actions, **Then** those interactions do not break page layout or reset unrelated filter controls.

---

### Edge Cases

- What happens when filters produce zero matches? The page should show a clear empty-results state and a direct way to reset filters.
- What happens when source/category metadata is missing for some datasets? Cards should still render and use fallback labels without breaking controls.
- What happens when dataset titles or summaries are unusually long? Card text should wrap or truncate predictably without overlapping action controls.
- What happens when last-updated values are unavailable or stale? The page should show a readable fallback timestamp state.
- What happens when dataset volume is high? The page should remain navigable with stable rendering and no visual jitter that blocks browsing.

## Requirements _(mandatory)_

### Functional Requirements

- **FR-001**: The system MUST provide a dedicated datasets page with a clear page heading and total-series summary near the top of the page.
- **FR-002**: The datasets page MUST provide a primary call-to-action to request a new dataset.
- **FR-003**: The system MUST display datasets in a vertically scannable card list where each card includes source, title, summary, tags, and last-updated context.
- **FR-004**: The system MUST provide a source filter control that includes an all-sources option and supports narrowing visible dataset cards.
- **FR-005**: The system MUST provide a category filter control that includes an all-categories option and supports narrowing visible dataset cards.
- **FR-006**: The system MUST provide a sort control with a default ordering focused on recency.
- **FR-007**: The system MUST update visible results whenever filter or sort selections change, and preserve selected control states while the user remains on the page.
- **FR-008**: The system MUST provide an explicit empty-results state when no datasets match the selected filters.
- **FR-009**: Each dataset card MUST include per-item action affordances for save and share interactions.
- **FR-010**: The page MUST maintain readable hierarchy and control usability on desktop and mobile viewport sizes.
- **FR-011**: The datasets list MUST avoid duplicate entries within the same visible result set.
- **FR-012**: The displayed total-series summary MUST represent the catalog total for the current dataset inventory, independent of temporary filter selections.
- **FR-013**: The system MUST allow backend discovery contract or query-surface updates when required to satisfy listing filters, sorting semantics, and metadata completeness.

### Key Entities _(include if feature involves data)_

- **Dataset Listing Item**: One discoverable dataset entry containing source label, title, descriptive summary, topical tags, and last-updated context.
- **Filter State**: User-selected source and category values that constrain the visible listing set.
- **Sort State**: User-selected ordering mode determining presentation order of dataset listing items.
- **Catalog Summary**: Aggregate total-series count displayed at page level.
- **Dataset Request Entry Point**: Primary page action that initiates a new-dataset request workflow.

## Success Criteria _(mandatory)_

### Measurable Outcomes

- **SC-001**: In usability testing, at least 90% of users can identify a relevant dataset using the listing page in under 90 seconds.
- **SC-002**: At least 95% of filter and sort interactions result in updated visible results in under 2 seconds under normal load conditions.
- **SC-003**: 100% of sampled dataset cards in QA include the required metadata fields (source, title, summary, tags, and last-updated context).
- **SC-004**: At least 85% of surveyed users report that the list hierarchy and controls are clear and easy to scan.
- **SC-005**: The request-new-dataset primary action is discoverable and successfully activated by at least 95% of users during first-pass task testing.

## Constitution Alignment _(mandatory)_

<!--
  ACTION REQUIRED: Confirm this feature complies with repository constitution rules.
  Any item marked "No" requires explicit owner-approved exception before implementation.
-->

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

- The provided screenshot defines the intended information architecture and visual hierarchy for this initial dataset listing experience.
- Save and share actions on cards are in scope as visible interactions on this page; downstream destinations or persistence behavior are outside this specification unless already defined elsewhere.
- The list page targets discovery and triage rather than full dataset detail exploration; full dataset detail pages remain out of scope.
- The total-series figure reflects overall catalog inventory and may differ from filtered result counts.

## Dependencies

- Existing dataset inventory and metadata feed that provides source, category, descriptive text, tags, and last-updated values.
- Existing request-new-dataset workflow destination for CTA handoff.
- Existing shell/navigation patterns that host page-level headings, controls, and list content consistently across viewports.
- Backend discovery API and query layers may require coordinated updates to provide complete category/filter/sort data guarantees for the frontend experience.
