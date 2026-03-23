# Tasks: Frontend Dataset Discovery UI (018)

**Input**: Design documents from `/specs/018-frontend-dataset-discovery/`  
**Prerequisites**: plan.md ✅, spec.md ✅, research.md ✅, data-model.md ✅, contracts/ ✅

**Tests**: Test tasks are REQUIRED. Every user story and foundational component MUST
include automated test coverage sufficient to maintain >= 90% coverage in `apps/frontend/`.

**Organization**: Tasks are grouped by user story to enable independent implementation
and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to
- Paths are relative to `apps/frontend/`

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Install the charting library dependency, create the API types and client
module, configure environment variables, and confirm existing quality gates still pass.

- [x] T001 Add `recharts` to dependencies in `apps/frontend/package.json` and run `pnpm install`
- [x] T002 [P] Create `src/lib/api/discovery-types.ts` with all TypeScript interface types from `specs/018-frontend-dataset-discovery/data-model.md` (SourceRef, DatasetSummary, DatasetRecentItem, DatasetSourceGroup, ObservationPoint, DatasetDetail, all response envelopes, ApiErrorEnvelope, CatalogViewMode, ChartDataPoint)
- [x] T003 Create `src/lib/api/discovery-client.ts` with typed fetch wrappers: `fetchDatasetSearch`, `fetchRecentDatasets`, `fetchDatasetCatalog`, `fetchDatasetDetail`; reads `DISCOVERY_API_BASE_URL` from `process.env`; URL-encodes all query params via `URLSearchParams`; throws typed error on non-200
- [x] T004 Document `DISCOVERY_API_BASE_URL` usage in `apps/frontend/.env.local.example` (server-side only, no `NEXT_PUBLIC_` prefix)
- [x] T005 Write `tests/discovery-types.test.ts` — validates TypeScript type shape invariants (optional fields nullable, arrays always present, correct field names)
- [x] T006 Write `tests/discovery-client.test.ts` — tests all four fetch functions with mocked `fetch`: correct URL construction, param encoding, error throw on non-200, typed response return
- [x] T007 Run `pnpm --dir apps/frontend typecheck` and `pnpm --dir apps/frontend test` — confirm both pass with no regressions

**Checkpoint**: Types and API client are in place; existing test suite passes.

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Build the shared leaf components that every user story page and phase
depends on. No user story phase can begin until these components exist.

**⚠️ CRITICAL**: No user story work can begin until this phase is complete.

- [x] T008 [P] Create `src/components/discovery/EmptyState.tsx` — accepts optional `message?: string`; defaults to "No results found."; renders `<div role="status">` with message text
- [x] T009 [P] Create `src/components/discovery/ErrorState.tsx` — accepts optional `message?: string`; defaults to "Unable to load data. Please try again."; renders `<div role="alert">` with message text
- [x] T010 [P] Create `src/components/discovery/DatasetCard.tsx` — accepts `dataset_id`, `title`, `source`, `latest_update_at`; renders as a Next.js `<Link href="/datasets/{dataset_id}">` card with title, source name badge, and formatted last-updated date
- [x] T011 Create `src/components/discovery/DatasetDetailHeader.tsx` — accepts `DatasetDetail`; renders title, description (or "No description available" if null), geographic scope (omit section if null), topic tags as inline badge chips, source attribution with source name
- [x] T012 Create `src/components/discovery/ObservationsTable.tsx` — accepts `observations: ObservationPoint[]`; if empty renders `<EmptyState message="No observation data available" />`; otherwise renders `<table>` with `observed_on` and `value` columns, `<caption>` for accessibility
- [x] T013 [P] Write `tests/EmptyState.test.tsx` — renders default message; renders custom message; has correct ARIA role
- [x] T014 [P] Write `tests/ErrorState.test.tsx` — renders default message; renders custom message; has correct ARIA `role="alert"`
- [x] T015 [P] Write `tests/DatasetCard.test.tsx` — renders title, source name, formatted date; link href points to correct `/datasets/{dataset_id}` path
- [x] T016 [P] Write `tests/DatasetDetailHeader.test.tsx` — renders all metadata fields; handles null description; handles null geographic_scope; handles empty topic_tags
- [x] T017 [P] Write `tests/ObservationsTable.test.tsx` — renders table with data rows; renders EmptyState when observations is empty
- [x] T018 Run `pnpm --dir apps/frontend test` and `pnpm --dir apps/frontend typecheck` — all tests pass, no type errors

**Checkpoint**: Shared leaf components present and tested. User story phases can begin.

---

## Phase 3: User Story 4 — Dataset Detail Page (Priority: P1) 🎯 MVP Core

**Goal**: Deliver the per-dataset detail page — the destination for all discovery flows.
Build the time series chart, wire the detail page, and add not-found handling.

**Independent Test**: Navigate to `/datasets/FEDFUNDS`; verify title, description, tags,
source, and a Recharts line chart all render. Navigate to `/datasets/UNKNOWN`; verify
not-found page shown.

### Tests for User Story 4 ⚠️

- [x] T019 [P] [US4] Write `tests/ObservationsChart.test.tsx` — renders Recharts `LineChart` for 1+ observations; renders `<EmptyState>` for empty observations; does not crash with single data point; has `aria-label`
- [x] T020 [P] [US4] Write `tests/detail-page.test.tsx` — renders `DatasetDetailHeader` + `ObservationsChart` with fixture data; calls `fetchDatasetDetail` with correct `dataset_id`; renders `ErrorState` when fetch throws; calls `notFound()` when API returns 404

### Implementation for User Story 4

- [x] T021 [US4] Create `src/components/discovery/ObservationsChart.tsx` — `"use client"` component; accepts `observations: ObservationPoint[]`; projects to `ChartDataPoint[]` (date string → formatted, value); renders Recharts `<LineChart>` with `<XAxis dataKey="date">`, `<YAxis>`, `<Line dataKey="value">`, `<Tooltip>`; adds `aria-label="Time series chart"`; renders `<EmptyState message="No observation data available" />` when observations is empty
- [x] T022 [US4] Create `src/app/datasets/[id]/not-found.tsx` — renders "Dataset not found" heading with `<Link href="/datasets">` back to catalog
- [x] T023 [US4] Create `src/app/datasets/[id]/page.tsx` — async Server Component; calls `fetchDatasetDetail(params.id)`; if API throws a 404 error calls Next.js `notFound()`; if API throws other error renders `<ErrorState />`; otherwise renders `<DatasetDetailHeader data={detail} />`, `<ObservationsChart observations={detail.observations} />`, `<ObservationsTable observations={detail.observations} />`
- [x] T024 [US4] Verify `pnpm --dir apps/frontend test` passes with ≥90% coverage including new component and page files

**Checkpoint**: Detail page fully functional. Navigate directly to `/datasets/FEDFUNDS`
to verify. US4 complete independently.

---

## Phase 4: User Story 1 — Home Page Search (Priority: P1) 🎯 MVP

**Goal**: Deliver the home page with a prominent search box that searches across
title, description, geographic scope, and tags, displaying ranked results.

**Independent Test**: Load `/`; type "federal" in the search box and submit; verify
matching datasets appear. Submit empty search; verify default state (recent feed)
shown without error.

### Tests for User Story 1 ⚠️

- [x] T025 [P] [US1] Write `tests/DatasetSearchBox.test.tsx` — renders search input; pre-populates from `?q` URL param; on submit pushes `?q=<value>` to router; does not submit with blank input
- [x] T026 [P] [US1] Write `tests/DatasetSearchResults.test.tsx` — renders a `DatasetCard` per item; renders `<EmptyState>` when items array is empty; passes correct `dataset_id` to each card
- [x] T027 [P] [US1] Write `tests/home-page.test.tsx` — renders search box; renders RecentUpdatesFeed when no `?q`; renders DatasetSearchResults when `?q` present; renders `<ErrorState>` when fetchDatasetSearch throws

### Implementation for User Story 1

- [x] T028 [US1] Create `src/components/discovery/DatasetSearchBox.tsx` — `"use client"` component; controlled text input pre-populated from `useSearchParams().get("q")`; on form submit calls `router.push` with `?q=<value>` appended to current path; has visible `<label>` and accessible button with "Search" text
- [x] T029 [US1] Create `src/components/discovery/DatasetSearchResults.tsx` — accepts `items: DatasetSummary[]` and `query: string`; renders heading "Results for '{query}'" if query non-empty; renders `<DatasetCard>` per item; renders `<EmptyState message="No datasets matched your search." />` when items is empty
- [x] T030 [US1] Update `src/app/page.tsx` — async Server Component; reads `q` from `searchParams`; if `q` present calls `fetchDatasetSearch({ q })` and renders `<DatasetSearchBox />` + `<DatasetSearchResults />`; always fetches `fetchRecentDatasets()` for recent feed; wraps all fetches in try/catch rendering `<ErrorState />` on failure; renders `<DatasetSearchBox />` as prominently placed primary action
- [x] T031 [US1] Verify `pnpm --dir apps/frontend test` passes with ≥90% coverage including new component files

**Checkpoint**: Home page search functional. Load `/` and search "unemployment" to
verify. US1 complete independently.

---

## Phase 5: User Story 2 — Recent Updates Feed (Priority: P2)

**Goal**: Display a "Recent Updates" section on the home page showing up to 5 datasets
ordered by most-recently-updated, with title, source, and last-updated date, each
linking to the detail page.

**Independent Test**: Load `/`; verify "Recent Updates" section shows ≤5 entries ordered
by recency; click an entry and verify it navigates to the correct detail page.

### Tests for User Story 2 ⚠️

- [x] T032 [P] [US2] Write `tests/RecentUpdatesFeed.test.tsx` — renders at most 5 items; renders each as a `DatasetCard` with title, source name, and last-updated date; renders no padding/placeholder rows when fewer than 5 items supplied; renders correctly when 0 items (no crash)

### Implementation for User Story 2

- [x] T033 [US2] Create `src/components/discovery/RecentUpdatesFeed.tsx` — accepts `items: DatasetRecentItem[]`; renders section heading "Recent Updates"; renders `<DatasetCard>` for each of up to 5 items (slice to first 5 as safety); if `items` is empty renders nothing (section hidden) or `<EmptyState message="No recent updates." />`
- [x] T034 [US2] Confirm `src/app/page.tsx` already calls `fetchRecentDatasets()` and passes result to `<RecentUpdatesFeed items={recent.items} />` (wired in T030); add the call and render if not already present
- [x] T035 [US2] Verify `pnpm --dir apps/frontend test` passes with ≥90% coverage including RecentUpdatesFeed

**Checkpoint**: Recent updates feed live on home page. Both US1 (search) and US2
(recent feed) work independently and together on `/`.

---

## Phase 6: User Story 3 — Dataset Catalog Page (Priority: P2)

**Goal**: Deliver the full catalog list page with inline search filtering and a
group-by-source toggle that reorganizes datasets under labeled source sections.

**Independent Test**: Load `/datasets`; verify all datasets shown. Enter search term "rate";
verify list filters. Toggle "Group by Source"; verify datasets reorganized into source
sections. Click a dataset; verify navigation to correct detail page.

### Tests for User Story 3 ⚠️

- [x] T036 [P] [US3] Write `tests/GroupBySourceToggle.test.tsx` — renders toggle control; reads `?group` URL param to set initial state; on change pushes `?group=source` when enabling and removes param when disabling
- [x] T037 [P] [US3] Write `tests/DatasetCatalogList.test.tsx` — flat mode renders one `DatasetCard` per item; grouped mode renders one section per source group with heading and member cards; grouped mode with search-filtered groups only shows non-empty source sections; renders `<EmptyState>` when items is empty
- [x] T038 [P] [US3] Write `tests/catalog-page.test.tsx` — renders search box and group toggle; passes `?q` param to `fetchDatasetCatalog`; passes `group_by_source=true` when `?group=source` present; renders `<DatasetCatalogList>` with results; renders `<ErrorState>` when fetch throws

### Implementation for User Story 3

- [x] T039 [US3] Create `src/components/discovery/GroupBySourceToggle.tsx` — `"use client"` component; reads `useSearchParams().get("group")`; renders a toggle button/checkbox labeled "Group by source"; on change pushes `?group=source` (enable) or removes `group` param (disable) via `router.push`; has accessible `aria-pressed` or equivalent
- [x] T040 [US3] Create `src/components/discovery/DatasetCatalogList.tsx` — accepts `items: DatasetSummary[]`, `groups: DatasetSourceGroup[] | null`, `viewMode: CatalogViewMode`; if `viewMode === "flat"` renders `<DatasetCard>` per item; if `viewMode === "grouped"` and `groups` non-null renders one `<section>` per group with `<h2>` source heading and member cards (matched by `dataset_id`); renders `<EmptyState>` when items is empty
- [x] T041 [US3] Create `src/app/datasets/page.tsx` — async Server Component; reads `q` and `group` from `searchParams`; calls `fetchDatasetCatalog({ q, groupBySource: group === "source" })`; renders `<DatasetSearchBox />`, `<GroupBySourceToggle />`, `<DatasetCatalogList items={result.items} groups={result.groups} viewMode={group === "source" ? "grouped" : "flat"} />`; wraps fetch in try/catch rendering `<ErrorState />`
- [x] T042 [US3] Verify `pnpm --dir apps/frontend test` passes with ≥90% coverage including new component and page files

**Checkpoint**: Full catalog page functional. All four pages (home, catalog, detail,
not-found) are complete. All four user stories independently tested.

---

## Phase 7: Polish & Cross-Cutting Concerns

**Purpose**: Final quality gate pass, documentation updates, and end-to-end local
stack verification.

- [x] T043 [P] Run full frontend quality suite: `pnpm --dir apps/frontend lint`, `pnpm --dir apps/frontend exec biome check .`, `pnpm --dir apps/frontend typecheck`, `pnpm --dir apps/frontend test`, `pnpm --dir apps/frontend coverage` — all pass, coverage reports ≥90%
- [ ] T044 [P] Run `pnpm run affected:lint && pnpm run affected:format && pnpm run affected:typecheck && pnpm run affected:test && pnpm run affected:coverage` — blocked by pre-existing backend/pipeline coverage deficits outside this feature branch
- [x] T045 Add `test:discovery-pages` Nx run-commands target to `apps/frontend/project.json` that runs Vitest filtered to `tests/home-page.test.tsx`, `tests/catalog-page.test.tsx`, `tests/detail-page.test.tsx`
- [x] T046 [P] Update `AGENTS.md` — add `recharts` under frontend dependencies; add `/datasets` and `/datasets/[id]` routes to the active page surface; add `DISCOVERY_API_BASE_URL` env var note; update "Recent Changes" entry for 018
- [x] T047 [P] Update `docs/runbooks/provider-onboarding.md` — add note that new data providers will automatically surface in frontend catalog, recent feed, and detail pages once ingested
- [x] T048 Update `specs/018-frontend-dataset-discovery/quickstart.md` — fill in the "Execution Evidence" section with actual command outputs after manual verification
- [x] T049 Start Docker Compose stack (`docker compose up -d db backend`) and verify all four pages end-to-end: `/`, `/?q=federal`, `/datasets`, `/datasets?group=source`, `/datasets/FEDFUNDS`, `/datasets/UNKNOWN`

---

## Dependencies & Execution Order

### Phase Dependencies

- **Phase 1 (Setup)**: No dependencies — begin immediately
- **Phase 2 (Foundational)**: Depends on Phase 1 completion — BLOCKS all user story phases
- **Phase 3 (US4 — Detail Page)**: Depends on Phase 2 completion — can start independently
- **Phase 4 (US1 — Home Search)**: Depends on Phase 2 completion — can start independently
- **Phase 5 (US2 — Recent Feed)**: Depends on Phase 4 (T030 home page wiring) — or can be partially prepared in parallel
- **Phase 6 (US3 — Catalog)**: Depends on Phase 2 completion — can start in parallel with US4/US1
- **Phase 7 (Polish)**: Depends on all user story phases complete

### User Story Dependencies

- **US4 (P1 — Detail)**: Starts after Foundational — independent of other stories
- **US1 (P1 — Home Search)**: Starts after Foundational — independent of other stories
- **US2 (P2 — Recent Feed)**: Shares the home page (`page.tsx`) with US1; best started after US1 wires the page shell (T030)
- **US3 (P2 — Catalog)**: Starts after Foundational — fully independent of US1/US2/US4

### Within Each Phase

- Test tasks written before/alongside implementation
- Client Components (DatasetSearchBox, GroupBySourceToggle) independent from Server Component pages
- All `[P]` tasks within a phase can be launched simultaneously

---

## Parallel Execution Examples

### Phase 2 — Foundational (all parallelizable)

```text
Parallel batch:
  T008: EmptyState.tsx
  T009: ErrorState.tsx
  T010: DatasetCard.tsx
  T013: tests/EmptyState.test.tsx
  T014: tests/ErrorState.test.tsx
  T015: tests/DatasetCard.test.tsx
Then sequential:
  T011: DatasetDetailHeader.tsx (uses EmptyState indirectly)
  T012: ObservationsTable.tsx (uses EmptyState)
  T016: tests/DatasetDetailHeader.test.tsx
  T017: tests/ObservationsTable.test.tsx
```

### Phase 3 — US4 Detail Page (tests then impl)

```text
Parallel batch:
  T019: tests/ObservationsChart.test.tsx
  T020: tests/detail-page.test.tsx
Then sequential:
  T021: ObservationsChart.tsx
  T022: not-found.tsx
  T023: datasets/[id]/page.tsx
```

### Phase 4 — US1 Home Search (tests then impl)

```text
Parallel batch:
  T025: tests/DatasetSearchBox.test.tsx
  T026: tests/DatasetSearchResults.test.tsx
  T027: tests/home-page.test.tsx
Then sequential:
  T028: DatasetSearchBox.tsx
  T029: DatasetSearchResults.tsx
  T030: app/page.tsx update
```

### Phase 6 — US3 Catalog (tests then impl)

```text
Parallel batch:
  T036: tests/GroupBySourceToggle.test.tsx
  T037: tests/DatasetCatalogList.test.tsx
  T038: tests/catalog-page.test.tsx
Then sequential:
  T039: GroupBySourceToggle.tsx
  T040: DatasetCatalogList.tsx
  T041: datasets/page.tsx
```

---

## Implementation Strategy

### MVP First (US4 + US1 minimum)

1. Complete Phase 1 (Setup)
2. Complete Phase 2 (Foundational) — CRITICAL
3. Complete Phase 3 (US4 — Detail Page) — enables navigation destination
4. Complete Phase 4 (US1 — Home Search) — enables discovery entry point
5. **STOP and VALIDATE**: Both pages functional end-to-end
6. Demo: Search → click result → see detail with chart

### Incremental Delivery

1. Phase 1 + Phase 2 → Foundation ready
2. Phase 3 (US4) → Detail page live
3. Phase 4 (US1) + Phase 5 (US2) → Home page complete
4. Phase 6 (US3) → Catalog page complete
5. Phase 7 (Polish) → All quality gates confirmed, docs updated

### Parallel Team Strategy (2 developers)

Once Phase 1 + 2 complete:

- **Dev A**: Phase 3 (US4 — Detail + Chart) + Phase 5 (US2 — Recent Feed component)
- **Dev B**: Phase 4 (US1 — Home Search) + Phase 6 (US3 — Catalog page)
- Both: Phase 7 (Polish + docs)
