# Feature Specification: Unified Dataset List Item

**Feature Branch**: `[028-unify-dataset-list-item]`  
**Created**: 2026-03-25  
**Status**: Draft  
**Input**: User description: "Create a unified reusable dataset list item component for homepage recent updates feed and datasets list page, using the homepage visual layout as the standard; dropdown styling can remain different for now."

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

### User Story 1 - Read Consistent Dataset Entries (Priority: P1)

As a visitor, I can scan dataset entries with the same visual structure on the home page recent updates area and the datasets listing page, so I do not have to relearn two different content patterns.

**Why this priority**: Visual and structural consistency across primary dataset browsing surfaces is the core user value for this feature.

**Independent Test**: Open the home page and datasets page and verify dataset entries use the same row-level layout and hierarchy.

**Acceptance Scenarios**:

1. **Given** I view the home page recent updates section, **When** dataset rows render, **Then** each row uses the editorial list-item layout baseline.
2. **Given** I view the datasets listing page, **When** dataset rows render, **Then** each row follows the same layout baseline as the home page recent updates entries.
3. **Given** both pages render dataset rows, **When** I compare source/date/title/summary/tag placement, **Then** the information hierarchy appears consistent between pages.

---

### User Story 2 - Preserve Existing Page Workflows (Priority: P2)

As a visitor, I can continue to filter and sort datasets on the datasets page and continue to browse recent updates on the home page while seeing a unified list-item style.

**Why this priority**: Consistency should not disrupt existing page-level behavior that users already rely on.

**Independent Test**: Change filters and sort on datasets page and confirm rows remain visible/usable; verify home recent updates still displays recent entries.

**Acceptance Scenarios**:

1. **Given** the datasets page controls are available, **When** I change source/category/sort selections, **Then** result updates still work and rows remain in the unified visual pattern.
2. **Given** the home page recent updates section is visible, **When** recent entries load, **Then** the unified list-item pattern appears without breaking page navigation.
3. **Given** I use both pages in one session, **When** I move between them, **Then** entry styling remains consistent while each page keeps its own controls and surrounding content.

---

### User Story 3 - Keep Presentation Readable and Stable (Priority: P3)

As a visitor, I can read dataset entries comfortably in desktop and mobile views after unification.

**Why this priority**: Shared presentation needs to remain readable and robust once reused in multiple contexts.

**Independent Test**: Validate both pages at common desktop and mobile widths and confirm no clipping, overlap, or hierarchy loss in entry rows.

**Acceptance Scenarios**:

1. **Given** either page is rendered on desktop, **When** I scan entries, **Then** source/date/title/summary/tag content remains legible.
2. **Given** either page is rendered on mobile widths, **When** entries reflow, **Then** row content wraps cleanly without overlap.
3. **Given** entries have long titles or summaries, **When** they render, **Then** layout remains stable and readable.

---

### Edge Cases

- What happens when datasets page filters produce zero results? The page should keep its existing empty-results behavior while maintaining unified row styling for populated states.
- What happens when optional metadata (description, geography, tags) is missing? Rows should degrade gracefully without broken spacing.
- What happens when titles or summaries are unusually long? Row layout should preserve hierarchy without overlap.
- What happens when date values are malformed? Rows should display safe fallback date text.
- What happens when home recent-updates data is unavailable? Existing home fallback behavior should remain intact.

## Requirements _(mandatory)_

### Functional Requirements

- **FR-001**: The system MUST provide one reusable dataset list-item presentation pattern shared by the home page recent updates section and the datasets listing page.
- **FR-002**: The shared list-item pattern MUST follow the homepage editorial row visual hierarchy as the baseline.
- **FR-003**: The datasets listing page MUST render dataset entries using the same shared list-item pattern instead of a distinct card-like row format.
- **FR-004**: The shared list-item pattern MUST display source attribution, update date context, title, summary text, and tag pills when available.
- **FR-005**: The system MUST preserve page-specific behaviors outside the list item pattern, including datasets page filtering/sorting controls and home page recent-updates section placement.
- **FR-006**: The system MUST preserve existing row navigation behavior for each page context while using the shared presentation pattern.
- **FR-007**: The system MUST maintain existing empty/fallback behaviors for home and datasets pages.
- **FR-008**: The datasets page control strip (source/category/sort) MAY keep its current styling in this feature scope.
- **FR-009**: The unified list-item pattern MUST remain readable across desktop and mobile viewport sizes.
- **FR-010**: The system MUST avoid introducing new visual divergence between the two dataset row surfaces after unification.

### Key Entities _(include if feature involves data)_

- **Unified Dataset List Item**: Shared presentation unit for one dataset entry, containing source, date context, title, summary, and tags.
- **Homepage Recent Update Entry**: Dataset entry shown in home recent updates flow using the unified item pattern.
- **Datasets Page Listing Entry**: Dataset entry shown in the catalog listing flow using the same unified item pattern.
- **List Context State**: Page-level state that surrounds entries (home feed availability, datasets filters/sort, empty/fallback outcomes).

## Success Criteria _(mandatory)_

### Measurable Outcomes

- **SC-001**: In visual QA, 100% of sampled dataset rows on home recent updates and datasets listing use the same row hierarchy for source/date/title/summary/tags.
- **SC-002**: In UX validation, at least 85% of reviewers report that dataset entry presentation feels consistent between home and datasets pages.
- **SC-003**: In regression QA, 100% of existing home-feed fallback scenarios and datasets-page filter/sort interactions continue working after unification.
- **SC-004**: In responsive checks, 100% of tested desktop and mobile viewport snapshots show readable row content with no overlap or clipping.

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

- The homepage recent updates row style is the visual source of truth for the unified pattern.
- Datasets page filter/sort dropdown styling can remain as currently implemented in this feature scope.
- No new user roles or permissions are needed for this presentation unification.
- Existing dataset metadata contracts remain sufficient for unified row rendering.

## Dependencies

- Existing homepage recent updates data feed and fallback states.
- Existing datasets listing route with source/category/sort controls and list-state handling.
- Existing shared shell typography and spacing tokens used across frontend pages.
