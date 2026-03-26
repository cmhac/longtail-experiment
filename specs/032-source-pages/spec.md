# Feature Specification: Source Discovery Pages

**Feature Branch**: `[032-source-pages]`  
**Created**: 2026-03-25  
**Status**: Complete  
**Input**: User description: "Build a source list page in the frontend that shows all sources and, when clicked, a detail page with that source's datasets. Gather and support any needed pipeline, backend, and frontend changes for this flow."

## User Scenarios & Testing _(mandatory)_

### User Story 1 - Browse Available Sources (Priority: P1)

As a discovery visitor, I can open a dedicated sources page and scan all available data sources so I can understand which publishers are represented in the catalog.

**Why this priority**: A browsable source directory is the minimum viable entry point for source-based navigation. Without it, users cannot discover sources at all.

**Independent Test**: Open the sources page and verify it shows a complete, readable list of sources with enough summary context to choose one.

**Acceptance Scenarios**:

1. **Given** the visitor opens the sources page, **When** source data is available, **Then** the page shows a list of all available sources with source names and dataset counts.
2. **Given** multiple sources are available, **When** the visitor scans the page, **Then** each source entry uses a consistent hierarchy and clearly indicates it can be opened.
3. **Given** the sources inventory is empty, **When** the page loads, **Then** the visitor sees an explicit empty state instead of a blank screen.

---

### User Story 2 - Open a Source Detail Page (Priority: P2)

As a discovery visitor, I can open a specific source page and see the datasets published by that source so I can evaluate its coverage without running a text search.

**Why this priority**: Source-level dataset browsing is the core follow-on action after finding a source and is the main value of the detail page.

**Independent Test**: Open a known source from the sources page and verify the detail page shows source context plus only datasets belonging to that source.

**Acceptance Scenarios**:

1. **Given** the visitor selects a source from the sources page, **When** the source exists, **Then** the app opens a dedicated source detail page for that source.
2. **Given** the source detail page loads successfully, **When** the visitor reviews the page, **Then** they see the source name, total dataset count, and a list of datasets from that source only.
3. **Given** the visitor uses a dataset link on the source detail page, **When** they select a dataset, **Then** they are routed to the existing dataset detail experience.

---

### User Story 3 - Recover Gracefully from Missing or Failed Source Views (Priority: P3)

As a discovery visitor, I can understand when a source page cannot be shown because the source is unknown or source data is temporarily unavailable so I do not get stuck in a broken navigation flow.

**Why this priority**: Clear fallback behavior preserves trust and keeps navigation usable when source-level requests fail or a stale link is opened.

**Independent Test**: Attempt to open an unknown source and simulate an unavailable source response; verify that not-found and error states are explicit and non-breaking.

**Acceptance Scenarios**:

1. **Given** the visitor opens a source detail route for a non-existent source, **When** the app resolves the request, **Then** the visitor sees a clear not-found experience.
2. **Given** the sources page or a source detail page cannot load due to an upstream failure, **When** the request fails, **Then** the visitor sees a clear error state with shell navigation preserved.
3. **Given** a source exists but has no visible datasets, **When** the detail page renders, **Then** the visitor sees source context with an explicit no-datasets state.

### Edge Cases

- What happens when multiple datasets share the same source name but differ in other metadata? They should still appear under one source entry and one source detail page.
- What happens when a source has only one dataset? The source detail page should still show the full source context and the single dataset entry.
- What happens when source names contain spaces, punctuation, or mixed case? Source navigation should remain stable and route consistently to the intended source.
- What happens when a source is present in source metadata but has no currently discoverable datasets? The sources page and source detail page should show a clear zero-dataset state.
- What happens when source counts or listings change between the list view and detail view? The detail page should render the current source state without showing unrelated datasets.

## Requirements _(mandatory)_

### Functional Requirements

- **FR-001**: The system MUST provide a dedicated sources page that lists all discoverable data sources.
- **FR-002**: The sources page MUST show each source with its display name and total dataset count.
- **FR-003**: The system MUST allow a visitor to open a dedicated detail page for a selected source.
- **FR-004**: The source detail page MUST show the selected source name and the datasets associated with that source.
- **FR-005**: The source detail page MUST reuse the existing dataset browsing hierarchy so visitors can continue from source browsing into dataset detail pages.
- **FR-006**: The system MUST ensure datasets shown on a source detail page belong only to the selected source.
- **FR-007**: The system MUST provide a clear empty state when no sources are available on the sources page.
- **FR-008**: The system MUST provide a clear empty state when a valid source has no datasets to display.
- **FR-009**: The system MUST preserve clear not-found handling for unknown source identifiers.
- **FR-010**: The system MUST preserve graceful error-state handling when source list or source detail data retrieval fails.
- **FR-011**: Source names, dataset counts, and dataset listings shown in source views MUST reflect the current discoverable catalog state.
- **FR-012**: The source browsing experience MUST remain readable and usable across common desktop and mobile viewport ranges.
- **FR-013**: All source-facing text and values MUST be rendered safely as escaped content.
- **FR-014**: The system MUST support any required query, contract, or metadata-surface updates across frontend, backend, and pipeline layers when existing discovery responses do not fully support source browsing.

### Key Entities _(include if feature involves data)_

- **Source Listing Entry**: One discoverable source item containing a source identifier, source display name, and dataset count.
- **Source Detail View**: A page-level representation of one source containing its source context and the datasets associated with it.
- **Source Dataset Membership**: The relationship that determines which datasets appear under a given source.
- **Source Navigation Identifier**: The route-safe identifier used to open a source detail page from the sources list.

## Success Criteria _(mandatory)_

### Measurable Outcomes

- **SC-001**: In source-directory QA, 100% of sampled active sources appear on the sources page exactly once.
- **SC-002**: In navigation QA, 100% of sampled source selections from the sources page open the correct source detail page.
- **SC-003**: In detail-page QA, 100% of sampled source detail pages show only datasets belonging to the selected source.
- **SC-004**: In fallback QA, 100% of tested empty, no-dataset, not-found, and load-error scenarios display explicit user-facing states rather than blank or broken pages.

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

- The source browsing experience will sit alongside the existing dataset discovery experience rather than replace it.
- Existing dataset detail pages remain the destination after a visitor chooses a dataset from a source detail page.
- Existing source attribution in the discovery catalog is the starting point for source identity unless supporting contracts need to be expanded.
- No new authentication or role-based access behavior is required for source browsing.

## Dependencies

- Existing discovery catalog metadata that attributes datasets to a source.
- Existing shell navigation, page layout, and dataset row presentation patterns.
- Backend discovery query surfaces and contracts that may need expansion to return first-class source records and source-specific dataset listings.
- Pipeline and persistence metadata that determine how sources are named and associated with datasets in the discoverable catalog.
