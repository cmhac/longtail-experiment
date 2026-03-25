# Feature Specification: Homepage Search Bar Experience

**Feature Branch**: `[024-home-search-bar]`  
**Created**: 2026-03-24  
**Status**: Draft  
**Input**: User description: "create a spec for the design of the home page's main search bar. It should be prominently in the middle of the page. Under the search bar in minimla text should be the text 'Searching TK active datasets from TK sources.' The TKs should be treated as placeholders, and in the final design they should actually render real values. this will likely require additional changes to the api routes to do this aggregation, too. When we do searches, we should display a drop down with likely matches using postgres trigram. changes can be made across both the frontend and backend app. write a spec"

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

### User Story 1 - Discover Search Entry Point (Priority: P1)

As a visitor, I can immediately see and use a prominent search bar in the center of the home page so I can begin dataset discovery without scanning the page.

**Why this priority**: The centered search entry point is the core interaction for discovery and must be obvious on first load.

**Independent Test**: Open the home page and confirm a visually dominant centered search field is present and accepts text input.

**Acceptance Scenarios**:

1. **Given** a visitor loads the home page, **When** the page renders, **Then** the main search bar appears centered and visually emphasized relative to surrounding content.
2. **Given** the search bar is visible, **When** the visitor focuses and types, **Then** input is accepted without navigation away from the page.

---

### User Story 2 - Understand Search Scope at a Glance (Priority: P2)

As a visitor, I can see a minimal context line under the search bar showing active dataset and source totals so I know the breadth of searchable content.

**Why this priority**: Scope context builds trust in discovery coverage and improves confidence before searching.

**Independent Test**: Load the home page and verify the context line appears under the search field with real numeric values in place of placeholders.

**Acceptance Scenarios**:

1. **Given** the home page is loaded, **When** the context line renders, **Then** it displays the sentence pattern "Searching [dataset count] active datasets from [source count] sources." with numeric values.
2. **Given** underlying totals change, **When** the page is refreshed, **Then** the displayed counts reflect the latest available aggregate values.

---

### User Story 3 - Get Likely Matches While Typing (Priority: P3)

As a visitor, I can see likely dataset matches in a dropdown while typing so I can quickly identify the intended dataset without completing a full page search flow.

**Why this priority**: Suggestive results reduce search friction and help users converge on target datasets faster.

**Independent Test**: Enter a partial query and verify a dropdown of likely matches appears and updates as input changes.

**Acceptance Scenarios**:

1. **Given** the visitor types at least one character in the search bar, **When** likely matches exist, **Then** a dropdown appears with relevant suggestions.
2. **Given** the visitor changes the query text, **When** suggestions are recalculated, **Then** the dropdown content updates to match the new input.
3. **Given** no likely matches are found, **When** the dropdown would otherwise open, **Then** no misleading suggestions are shown.

---

### Edge Cases

- What happens when aggregate totals are temporarily unavailable? The context line should remain readable and fall back to a safe placeholder state without breaking the page layout.
- What happens when the user enters very short, very long, or special-character queries? The dropdown should remain stable and avoid duplicate or malformed suggestion entries.
- What happens when the user types quickly? Suggestion updates should remain responsive and display the latest relevant result set.
- What happens when no suggestions are found? The UI should avoid presenting stale suggestions from a previous query.
- What happens when search services are unavailable? The page should preserve the core search input experience and present a graceful non-blocking fallback state.

## Requirements _(mandatory)_

### Functional Requirements

- **FR-001**: The system MUST render a prominent primary search bar centered in the home page hero area.
- **FR-002**: The system MUST display a minimal context line directly beneath the search bar using this sentence pattern: "Searching [dataset count] active datasets from [source count] sources."
- **FR-003**: The system MUST replace both count placeholders with real aggregated values at runtime.
- **FR-004**: The system MUST source the aggregated counts from backend-provided data and keep the displayed values synchronized with current available totals.
- **FR-005**: The system MUST display a likely-match suggestion dropdown as a user types in the search bar.
- **FR-006**: The suggestion dropdown MUST prioritize likely textual matches and refresh based on the current query.
- **FR-007**: The system MUST avoid showing stale suggestions that do not correspond to the current query text.
- **FR-008**: The system MUST support frontend and backend changes required to deliver both aggregate counts and likely-match suggestions in one cohesive search experience.
- **FR-009**: The search bar, context line, and suggestion dropdown MUST remain legible and usable across supported appearance modes and common viewport sizes.
- **FR-010**: If aggregate counts or suggestions are temporarily unavailable, the system MUST degrade gracefully without blocking typing or breaking layout.

### Key Entities

- **Homepage Search Surface**: The centered search input area and its immediate contextual content.
- **Search Scope Summary**: Aggregate metadata containing active dataset count and active source count for the context line.
- **Suggestion Item**: A single likely dataset match shown in the dropdown, including identifying label and selection target.
- **Suggestion Result Set**: Ordered collection of suggestion items associated with the current query text.

## Success Criteria _(mandatory)_

### Measurable Outcomes

- **SC-001**: At least 95% of home page loads show a centered, clearly visible primary search bar without layout overlap.
- **SC-002**: 100% of home page loads that receive aggregate metadata render numeric values for both active dataset and source counts in the context line.
- **SC-003**: For representative discovery queries, at least 90% of typed queries display likely-match suggestions within one second of input stabilization.
- **SC-004**: In usability validation, at least 85% of users can identify and start a relevant search from the home page without additional navigation.

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

- "Prominently in the middle" means the search surface is visually centered in the primary above-the-fold content area.
- Aggregate counts represent currently active, searchable records and are supplied by authoritative backend aggregation logic.
- Suggestion dropdown behavior is discoverability-focused and does not require introducing advanced personalization in this feature slice.
- Existing homepage content remains below the search surface and is not removed by this feature.

## Dependencies

- Backend query capabilities for active dataset and active source aggregates.
- Backend search-suggestion capabilities for likely-match responses from partial query text.
- Frontend integration surfaces for homepage search rendering and suggestion dropdown behavior.
