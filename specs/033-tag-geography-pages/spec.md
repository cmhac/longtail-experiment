# Feature Specification: Tag and Geography Discovery Pages

**Feature Branch**: `[033-tag-geography-pages]`  
**Created**: 2026-03-25  
**Status**: Draft  
**Input**: User description: "Create tag detail pages and geography detail pages so clicking dataset pills opens a dedicated page listing all datasets with that tag or in that geography, including any needed pipeline, backend, and frontend changes."

## User Scenarios & Testing _(mandatory)_

### User Story 1 - Open Topic Tag Pages (Priority: P1)

As a discovery visitor, I can click a topic tag pill on a dataset entry or dataset detail page and open a dedicated page showing all datasets with that topic so I can continue browsing by subject without starting a new search.

**Why this priority**: Topic tags already signal subject matter in the current experience, so making them navigable turns an existing discovery cue into a high-value browse path.

**Independent Test**: Open a known dataset with visible topic tags, click a tag pill, and verify the destination page shows the selected tag context plus only datasets carrying that tag.

**Acceptance Scenarios**:

1. **Given** a dataset row or dataset detail page displays a topic tag pill, **When** the visitor selects that pill, **Then** the app opens a dedicated page for that topic tag.
2. **Given** the topic tag page loads successfully, **When** the visitor reviews the page, **Then** they see the selected tag label and a list of datasets associated with that tag only.
3. **Given** the visitor inspects datasets on the topic tag page, **When** they select one, **Then** they are routed to the existing dataset detail experience.

---

### User Story 2 - Open Geography Pages (Priority: P2)

As a discovery visitor, I can click a geography pill on a dataset entry or dataset detail page and open a dedicated page showing all datasets associated with that geography so I can browse the catalog by place.

**Why this priority**: Geography is a major part of dataset meaning and already appears prominently in the UI, but it currently stops at display rather than navigation.

**Independent Test**: Open a known dataset with a geography pill, click it, and verify the destination page shows the selected geography context plus only datasets associated with that geography.

**Acceptance Scenarios**:

1. **Given** a dataset row or dataset detail page displays a geography pill, **When** the visitor selects that pill, **Then** the app opens a dedicated page for that geography.
2. **Given** the geography page loads successfully, **When** the visitor reviews the page, **Then** they see the selected geography label and a list of datasets associated with that geography only.
3. **Given** multiple datasets share the same geography, **When** the geography page renders, **Then** each qualifying dataset appears once in a stable browse order.

---

### User Story 3 - Recover Gracefully from Empty, Missing, or Failed Metadata Pages (Priority: P3)

As a discovery visitor, I can understand when a tag or geography page cannot be shown because it has no visible datasets, does not exist, or is temporarily unavailable so I do not get stuck in a broken navigation flow.

**Why this priority**: Metadata-driven navigation needs explicit fallback behavior to remain trustworthy when links are stale, metadata is sparse, or retrieval fails.

**Independent Test**: Attempt to open an unknown tag or geography page and simulate an unavailable response; verify that not-found, empty, and error states are explicit and non-breaking.

**Acceptance Scenarios**:

1. **Given** the visitor opens a tag or geography route that does not resolve to a known browse page, **When** the app handles the request, **Then** the visitor sees a clear not-found experience.
2. **Given** a valid tag or geography exists but has no currently visible datasets, **When** the page renders, **Then** the visitor sees the page context with an explicit empty state instead of a blank list.
3. **Given** a tag or geography page cannot load due to an upstream failure, **When** the request fails, **Then** the visitor sees a clear error state with shell navigation preserved.

### Edge Cases

- What happens when a dataset has duplicate or inconsistently cased topic labels from source metadata? The visitor should see one stable browse destination per visible topic label rather than fragmented duplicates.
- What happens when a topic tag or geography contains spaces, punctuation, or mixed case? Navigation should remain stable and route consistently to the intended metadata page.
- What happens when a dataset has no topic tags or no geography? The dataset still renders normally, but no broken or misleading metadata navigation affordance is shown for missing values.
- What happens when counts or memberships change between the originating dataset page and the destination metadata page? The destination page should render the current catalog state without showing unrelated datasets.
- What happens when a metadata page contains only one dataset? The page should still show full context and the single qualifying dataset entry.

## Requirements _(mandatory)_

### Functional Requirements

- **FR-001**: The system MUST make visible topic tag pills selectable from dataset list rows and dataset detail pages when topic tag metadata is present.
- **FR-002**: The system MUST provide a dedicated topic tag page for each selectable topic tag.
- **FR-003**: The topic tag page MUST display the selected topic label and the datasets associated with that topic.
- **FR-004**: The system MUST make visible geography pills selectable from dataset list rows and dataset detail pages when geography metadata is present.
- **FR-005**: The system MUST provide a dedicated geography page for each selectable geography value.
- **FR-006**: The geography page MUST display the selected geography label and the datasets associated with that geography.
- **FR-007**: Dataset listings on topic tag pages and geography pages MUST reuse the existing dataset browsing hierarchy so visitors can continue into the current dataset detail experience.
- **FR-008**: Topic tag pages MUST ensure displayed datasets belong only to the selected topic tag.
- **FR-009**: Geography pages MUST ensure displayed datasets belong only to the selected geography.
- **FR-010**: The system MUST provide stable navigation identifiers for topic tag pages and geography pages so pill selection resolves consistently across list and detail contexts.
- **FR-011**: The system MUST support any required metadata normalization, storage updates, or query-surface updates needed so topic tag and geography browsing reflect the current discoverable catalog state.
- **FR-012**: The system MUST preserve existing dataset search, catalog, source, and dataset-detail navigation behavior while adding metadata-page navigation.
- **FR-013**: Topic tag and geography pages MUST show an explicit empty state when the selected page is valid but has no visible datasets.
- **FR-014**: Topic tag and geography routes MUST preserve clear not-found handling for unknown metadata identifiers.
- **FR-015**: Topic tag and geography routes MUST preserve graceful error-state handling when data retrieval fails.
- **FR-016**: Metadata pages and metadata navigation affordances MUST remain readable and usable across common desktop and mobile viewport ranges.
- **FR-017**: All externally sourced labels, counts, and dataset metadata shown in metadata navigation flows MUST be rendered safely as escaped content.

### Key Entities _(include if feature involves data)_

- **Topic Tag Page**: A page-level representation of one selected topic label containing its display identity and the datasets associated with it.
- **Geography Page**: A page-level representation of one selected geography containing its display identity and the datasets associated with it.
- **Metadata Navigation Identifier**: The route-safe identifier used to open a topic tag page or geography page from a pill click.
- **Metadata Dataset Membership**: The relationship that determines which datasets appear on a given topic tag page or geography page.
- **Metadata Pill Action**: The selectable affordance attached to a visible topic tag or geography pill that launches metadata-based browsing.

## Success Criteria _(mandatory)_

### Measurable Outcomes

- **SC-001**: In metadata-navigation QA, 100% of sampled visible topic tag pills open the correct topic tag page.
- **SC-002**: In metadata-navigation QA, 100% of sampled visible geography pills open the correct geography page.
- **SC-003**: In detail-page QA, 100% of sampled topic tag pages and geography pages show only datasets belonging to the selected metadata value.
- **SC-004**: In fallback QA, 100% of tested empty, not-found, and load-error scenarios for topic tag and geography pages display explicit user-facing states rather than blank or broken pages.
- **SC-005**: In navigation QA, 100% of sampled datasets reached from a topic tag page or geography page open the correct existing dataset detail page.

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
  for any service that requires secrets. (N/A)

## Assumptions

- Metadata-page browsing will sit alongside the existing dataset and source discovery experiences rather than replace them.
- Existing dataset detail pages remain the destination after a visitor chooses a dataset from a topic tag page or geography page.
- Topic tag labels and geography labels currently visible in the discovery experience are the starting point for metadata identity unless supporting surfaces need to be expanded.
- No authentication, personalization, or role-based behavior is required for metadata-page browsing.

## Dependencies

- Existing discovery metadata that associates datasets with topic tags and geography values.
- Existing shell navigation, page layout, and dataset row presentation patterns.
- Backend discovery query surfaces and contracts that may need to be expanded to return first-class topic tag and geography records plus metadata-specific dataset listings.
- Pipeline and persistence behavior that determine how topic tag and geography values are named, normalized, and associated with discoverable datasets.
