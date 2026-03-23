# Feature Specification: Frontend Dataset Discovery UI

**Feature Branch**: `018-frontend-dataset-discovery`  
**Created**: 2026-03-23  
**Status**: Draft  
**Input**: User description: "Frontend UI for dataset discovery — landing page search, recent updates feed, full catalog list with source grouping, and per-dataset detail page with time series visualization"

## User Scenarios & Testing _(mandatory)_

### User Story 1 — Search for a Dataset from the Home Page (Priority: P1)

A visitor arrives at the site and sees a prominent search box. They type a keyword — such as a topic, geographic area, or source name — and are immediately presented with a ranked list of matching datasets. They can click any result to go to the dataset's detail page.

**Why this priority**: This is the primary entry point of the product. Without search, users have no way to find anything. It must work before any other page delivers value.

**Independent Test**: Can be tested by loading the home page, entering a search term, and verifying that matching dataset results appear and link correctly to detail pages.

**Acceptance Scenarios**:

1. **Given** a visitor loads the home page, **When** they see the page, **Then** a visible search input is present and clearly indicated as the primary action.
2. **Given** a visitor types a keyword matching a known dataset title, **When** they submit the search, **Then** a ranked list of matching datasets is returned and displayed.
3. **Given** a visitor searches using a term that appears in a description or geographic scope field (not just the title), **When** results are returned, **Then** the matching datasets are included in results.
4. **Given** a visitor searches using a topic tag name, **When** results are returned, **Then** datasets tagged with that topic appear in results.
5. **Given** a visitor submits a search that matches no datasets, **When** the result list is shown, **Then** an empty-state message is displayed rather than a blank screen.
6. **Given** a visitor submits an empty or whitespace-only search, **When** the result list is shown, **Then** either a prompt to enter a term is shown or all datasets are returned as defaults.

---

### User Story 2 — Browse Recently Updated Datasets (Priority: P2)

A returning user checks the home page to see what data is freshest. A "Recent Updates" section shows up to 5 datasets ordered by when they were last updated, most recent first. Each entry shows enough information (title, source, last-updated date) to decide whether to click through.

**Why this priority**: Recurring users need a quick at-a-glance feed of what is new without searching. This is secondary to search but critical for retention and trust.

**Independent Test**: Can be tested by loading the home page and verifying the displayed list is ordered by recency and capped at 5 entries.

**Acceptance Scenarios**:

1. **Given** there are datasets with different update timestamps, **When** the home page loads, **Then** the "Recent Updates" section shows up to 5 datasets ordered by most-recently-updated first.
2. **Given** the recent-updates section is visible, **When** a user inspects each entry, **Then** each entry shows the dataset title, the name of the source that provides it, and the date it was last updated.
3. **Given** fewer than 5 datasets exist, **When** the section renders, **Then** all available datasets are shown without padding or placeholder rows.
4. **Given** a user clicks an entry in the feed, **When** they are redirected, **Then** they land on the correct dataset detail page.

---

### User Story 3 — Browse the Full Dataset Catalog (Priority: P2)

A user navigates to the datasets list page to see everything available. They can scroll through all datasets, search within the list, and toggle a "group by source" view to see datasets organized under the provider that contributes them (e.g., FRED, BLS, Census).

**Why this priority**: Exploratory discovery requires a full catalog view. Users who do not know what to search for need to be able to browse. Source grouping adds meaningful structure without requiring extra navigation.

**Independent Test**: Can be tested by loading the catalog page, verifying all datasets appear, running a search, and toggling the group-by-source view.

**Acceptance Scenarios**:

1. **Given** a user navigates to the datasets list page, **When** the page loads, **Then** all datasets are shown with title, source name, and last-updated date.
2. **Given** a search box is on the catalog page, **When** a user enters a search term, **Then** the displayed list is filtered to matching datasets without a full page reload.
3. **Given** a "group by source" toggle or control is visible, **When** a user activates it, **Then** datasets are reorganized into labeled sections per data source.
4. **Given** the grouped view is active, **When** a user inspects a source group, **Then** all datasets belonging to that source are listed under its heading.
5. **Given** the grouped view is active and filtered by a search term, **When** results render, **Then** only source groups containing matching datasets are shown.
6. **Given** a user clicks any dataset in the list, **When** they navigate, **Then** they reach the correct detail page for that dataset.

---

### User Story 4 — View a Dataset Detail Page (Priority: P1)

A user clicks through to a specific dataset and sees its full profile: title, description, geographic scope, topic tags, source attribution, and the complete history of observations visualized as a time series chart. They have enough context to understand what the data represents and can inspect individual data points.

**Why this priority**: The detail page is the endpoint of all discovery flows. Without it, no upstream page has a meaningful destination. It must work end-to-end before the product is usable.

**Independent Test**: Can be tested by navigating directly to a known dataset URL and verifying that all metadata fields and observation data render correctly.

**Acceptance Scenarios**:

1. **Given** a user navigates to a dataset detail page with a valid dataset identifier, **When** the page loads, **Then** the title, description, geographic scope, topic tags, and source attribution are all displayed.
2. **Given** the dataset has observations, **When** the page loads, **Then** the observations are displayed as a time series visualization ordered chronologically.
3. **Given** the dataset has observations, **When** the chart section renders, **Then** individual data points are inspectable (e.g., via hover tooltip or a data table).
4. **Given** a user navigates to a dataset identifier that does not exist, **When** the page loads, **Then** a clear "not found" message is shown rather than a crash or blank page.
5. **Given** a dataset has no observations yet, **When** the page loads, **Then** the metadata is still shown and a message indicates no observation data is available.

---

### Edge Cases

- What happens when the API is unavailable or returns an error? Users should see a graceful error state, not a broken layout.
- What should display when a dataset has a very long description or many topic tags? Layout must not break or overflow uncontrollably.
- What if a dataset title is very short (1–2 characters) or very long (200+ characters)? Truncation or wrapping must handle both extremes.
- What should the time series chart show when there is only one data point? Single-point charts must render meaningfully.
- What happens when the search term contains special characters? Input must be rendered as escaped safe text to prevent XSS.

## Requirements _(mandatory)_

### Functional Requirements

- **FR-001**: The home page MUST display a prominently placed text search box that searches across dataset title, description, geographic scope, and topic tags.
- **FR-002**: The home page MUST display a "Recent Updates" section listing up to 5 datasets ordered by most-recently-updated first, each showing title, source name, and last-updated date.
- **FR-003**: The datasets list page MUST display all available datasets with title, source name, and last-updated date.
- **FR-004**: The datasets list page MUST include a search box that filters the visible list in real time or near-real time.
- **FR-005**: The datasets list page MUST provide a control to toggle grouping of datasets by their contributing source.
- **FR-006**: When grouped by source, each group heading MUST show the source name and all datasets that belong to it.
- **FR-007**: Every dataset entry in the home search results, recent updates feed, and catalog list MUST link to that dataset's detail page.
- **FR-008**: The dataset detail page MUST display the dataset's title, description, geographic scope, topic tags, and source attribution.
- **FR-009**: The dataset detail page MUST display a time series visualization of the dataset's observations ordered chronologically.
- **FR-010**: The dataset detail page MUST allow individual observation values to be inspected (hover tooltip, data table, or equivalent).
- **FR-011**: Any page that references a nonexistent resource MUST display a clear "not found" state rather than a crash or blank page.
- **FR-012**: All pages MUST display a graceful error state when the underlying data service is unavailable.
- **FR-013**: All user-visible text derived from external data MUST be rendered as escaped safe text to prevent cross-site scripting.

### Key Entities

- **Dataset**: A named time series from a specific source, with title, description, geographic scope, topic tags, source attribution, and an ordered collection of observations.
- **Observation**: A single data point in a dataset's time series, consisting of a date and a numeric value.
- **Source**: The data provider that contributes one or more datasets (e.g., "FRED", "BLS"). Has a display name and an identifier.
- **Topic Tag**: A short label categorizing a dataset by subject matter (e.g., "interest rates", "unemployment").

## Success Criteria _(mandatory)_

### Measurable Outcomes

- **SC-001**: A user can navigate from the home page to a specific dataset detail page in 3 clicks or fewer.
- **SC-002**: Search results appear within 2 seconds of a user submitting a query on any page with a search box.
- **SC-003**: All four core pages (home, catalog, dataset detail, not-found) are reachable and render without visual errors in a standard desktop browser.
- **SC-004**: The time series visualization on the detail page renders correctly for datasets with 1 observation, 10 observations, and 100+ observations.
- **SC-005**: A "not found" state is shown on the detail page when navigating to a nonexistent dataset identifier.
- **SC-006**: The grouped-by-source view on the catalog page correctly separates datasets under their respective source headings.
- **SC-007**: Frontend automated test coverage is at or above 90% for all new pages and components introduced by this feature.

## Assumptions

- The backend dataset discovery API from feature 017 is deployed and accessible to the frontend at a configurable base URL. No API gateway or auth layer is required for this feature.
- The API returns data in the contracts defined in feature 017 (search, recent, catalog, detail endpoints).
- Time series observations include a date and a numeric value sufficient for a line chart; no special chart type is required.
- The frontend does not need to support mobile-first or responsive breakpoints for this iteration; desktop layout is sufficient.
- No authentication, personalization, or user accounts are required for any page in this feature.
- The frontend build and quality toolchain is already established (Next.js App Router, HeroUI, Biome, Vitest, TypeScript strict).

## Dependencies

- Feature 017 backend API must be deployed and serving the four discovery endpoints.
- HeroUI component library must be available in the frontend project.
- A time series charting capability compatible with the existing frontend stack must be identified during planning.

## Constitution Alignment _(mandatory)_

- **CA-001 Quality Gates**: Feature can satisfy linting, formatting, type checking, and
  automated test gates without suppressions, bypasses, or workaround-only code. (Yes)
- **CA-002 Coverage**: Feature includes tests to keep backend/frontend coverage at or
  above 90% in affected projects. (Yes)
- **CA-003 Local Stack**: Feature is runnable in the unified local Docker Compose stack,
  or explicitly lists compose updates needed. (Yes — the backend API service from 017 is already present; this feature adds only frontend pages consumed via the browser.)
- **CA-004 Contracts and Data Integrity**: Data/interface contract changes,
  provenance/timestamp impacts, and trend-alert reliability safeguards are defined.
  (Yes — frontend consumes 017 contracts read-only; no new data contracts are introduced.)
- **CA-005 Documentation Fidelity**: Relevant documentation is identified and will be
  created or updated in the same change for any impacted behavior, contracts, setup, or
  runbooks, including AGENTS.md when repository structure/workflows/tooling change.
  (Yes)
