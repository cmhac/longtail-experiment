# Feature Specification: Dataset Discovery Backend API

**Feature Branch**: `017-dataset-discovery-api`  
**Created**: 2026-03-23  
**Status**: Draft  
**Input**: User description: "Build out backend API support for dataset discovery and detail pages: homepage search across title/description/geographic scope/tags, recent updates feed, all-datasets listing with source organization and search, and dataset detail responses with metadata plus full time-series data. Backend-only scope, including any required database additions."

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

### User Story 1 - Search and Recent Updates for Landing Page (Priority: P1)

As a visitor, I can search datasets from the landing page and see recently updated datasets so I can immediately discover relevant data without browsing the entire catalog.

**Why this priority**: This is the primary discovery entry point and provides immediate value even before full catalog browsing is used.

**Independent Test**: Can be fully tested by submitting search terms and verifying results include matches across title/description/geographic scope/tags, plus verifying the recent updates feed returns up to five datasets sorted by latest update timestamp.

**Acceptance Scenarios**:

1. **Given** a search term that appears in dataset metadata, **When** the landing-page search is executed, **Then** matching datasets are returned with enough summary information to render result cards.
2. **Given** datasets with different update timestamps, **When** recent updates are requested, **Then** the response contains at most five datasets ordered by most recent dataset update first.
3. **Given** an empty search term, **When** search is executed, **Then** the system returns a deterministic default response suitable for landing-page rendering.

---

### User Story 2 - Browse Full Dataset Catalog by Source (Priority: P2)

As a visitor, I can browse all datasets, filter or organize by source, and search within the catalog so I can find the right dataset even when I do not know the exact title.

**Why this priority**: This supports complete catalog discovery and source-oriented exploration once users move beyond landing-page shortcuts.

**Independent Test**: Can be independently tested by requesting catalog pages with and without source filtering/search terms and verifying all datasets are represented in stable ordering.

**Acceptance Scenarios**:

1. **Given** datasets from multiple sources, **When** the catalog endpoint is requested, **Then** all datasets are returned with source attribution suitable for grouped or filtered rendering.
2. **Given** a source filter and search term, **When** the catalog endpoint is requested, **Then** returned datasets satisfy both the source and text criteria.
3. **Given** a paginated catalog request, **When** the response is returned, **Then** paging metadata is included and stable across repeated calls for the same inputs.

---

### User Story 3 - View Dataset Detail and Full Time Series (Priority: P3)

As a visitor, I can open a specific dataset and receive its full metadata and full observation history so the frontend can render a complete detail experience and chart.

**Why this priority**: Dataset detail is essential for analysis workflows after discovery, but depends on discovery routes to reach a dataset.

**Independent Test**: Can be independently tested by requesting a dataset by key and verifying both metadata and chronological time-series observations are returned in one detail workflow.

**Acceptance Scenarios**:

1. **Given** a valid dataset identifier, **When** the detail endpoint is requested, **Then** title, description, geographic scope, tags, source attribution, and related metadata are returned.
2. **Given** a valid dataset identifier with observations, **When** the detail endpoint is requested, **Then** observations are returned in chronological order with reported timestamp and attributes for visualization.
3. **Given** an unknown dataset identifier, **When** the detail endpoint is requested, **Then** a clear not-found response is returned without exposing internal errors.

---

### Edge Cases

- Search term matches only tags but not title/description/geographic scope.
- Dataset has missing optional metadata fields (for example description or geographic scope).
- Dataset has no tags.
- Dataset has no observations yet.
- Multiple datasets share identical latest update timestamps.
- Catalog request asks for a page beyond available dataset count.
- Detail request includes observation ranges that return no points.

## Requirements _(mandatory)_

### Functional Requirements

- **FR-001**: The backend MUST provide a landing-page dataset search response that matches across dataset title, description, geographic scope, and topic tags.
- **FR-002**: The backend MUST provide a recent-updates response containing at most five datasets sorted by most recent dataset update timestamp descending.
- **FR-003**: The backend MUST provide a full catalog response that returns all datasets with source attribution and supports text search using the same metadata fields as landing search.
- **FR-004**: The backend MUST support source-based organization for catalog responses so datasets can be grouped or filtered by source.
- **FR-005**: The backend MUST provide dataset detail responses keyed by canonical dataset identifier.
- **FR-006**: Dataset detail responses MUST include dataset metadata needed by the frontend: title, description, geographic scope, tags, source attribution, and existing series metadata.
- **FR-007**: Dataset detail responses MUST include observation records for visualization, including observed date, value, reported timestamp, and available attributes.
- **FR-008**: Observation records in detail responses MUST be ordered chronologically by observed date.
- **FR-009**: Search and catalog responses MUST include deterministic ordering rules when records tie on recency or title.
- **FR-010**: Backend responses for search and catalog MUST include pagination inputs and outputs suitable for incremental loading.
- **FR-011**: The backend MUST return explicit not-found behavior for unknown dataset identifiers.
- **FR-012**: If current database fields or indexes are insufficient to satisfy required search, recency, or listing behavior at target scale, the feature MUST define and include additive database changes.

### Assumptions

- Initial release is read-only discovery/detail API behavior; write or admin workflows are out of scope.
- Dataset identifier exposed externally is the canonical series key.
- Missing optional metadata (description, geographic scope, tags) is represented as empty or null-safe values rather than request failure.
- Observation range filtering may be included when useful but full-series retrieval remains available.

### Dependencies

- Shared DB schema and migrations under `libs/db/alembic` remain the source of truth.
- Backend contract/query modules can be extended for new discovery/detail read models.
- Local Docker Compose database remains available for integration verification.

### Key Entities

- **Dataset Summary**: Lightweight dataset projection for landing and catalog views including identifier, title, source, recency marker, and discovery metadata.
- **Dataset Detail**: Full dataset projection with descriptive metadata, source metadata, tags, and canonical dataset attributes.
- **Observation Point**: Time-series record containing observed date, value, reported timestamp, and observation attributes.
- **Source Group**: Source-level grouping structure linking one source to many datasets for list-page organization.
- **Search Query Context**: Request context containing text term, source filters, and paging settings that drive deterministic result sets.

## Success Criteria _(mandatory)_

### Measurable Outcomes

- **SC-001**: 100% of sampled search requests return only datasets matching at least one configured search field (title, description, geographic scope, or tags).
- **SC-002**: 100% of sampled recent-updates requests return at most five datasets ordered by descending dataset update recency.
- **SC-003**: 100% of sampled catalog requests provide source attribution for every returned dataset and deterministic ordering across repeated identical requests.
- **SC-004**: 100% of sampled valid dataset-detail requests return both metadata and chronological observation data suitable for direct chart rendering.
- **SC-005**: 100% of sampled unknown dataset-detail requests return the defined not-found behavior.

## Constitution Alignment _(mandatory)_

- **CA-001 Quality Gates**: Feature can satisfy linting, formatting, type checking, and
  automated test gates without suppressions, bypasses, or workaround-only code. (Yes)
- **CA-002 Coverage**: Feature includes tests to keep backend/frontend coverage at or
  above 90% in affected projects. (Yes)
- **CA-003 Local Stack**: Feature is runnable in the unified local Docker Compose stack,
  or explicitly lists compose updates needed. (Yes)
- **CA-004 Contracts and Data Integrity**: Data/interface contract changes,
  provenance/timestamp impacts, and trend-alert reliability safeguards are defined.
  (Yes)
- **CA-005 Documentation Fidelity**: Relevant documentation is identified and will be
  created or updated in the same change for any impacted behavior, contracts, setup, or
  runbooks, including AGENTS.md when repository structure/workflows/tooling change.
  (Yes)
