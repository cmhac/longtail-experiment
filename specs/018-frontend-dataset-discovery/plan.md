# Implementation Plan: Frontend Dataset Discovery UI

**Branch**: `018-frontend-dataset-discovery` | **Date**: 2026-03-23 | **Spec**: [spec.md](spec.md)  
**Input**: Feature specification from `/specs/018-frontend-dataset-discovery/spec.md`

## Summary

Build a Next.js App Router frontend that exposes four dataset discovery surfaces:
a home page with keyword search and a "Recent Updates" feed, a full catalog list
page with inline search and group-by-source toggle, and a per-dataset detail page
with metadata and a Recharts time series visualization. All data is fetched from
the 017 backend `DatasetDiscoveryService` via a typed fetch-wrapper client. State
is URL-driven for shareability. No DB migrations; no backend changes.

## Technical Context

**Language/Version**: TypeScript 5.x with strict mode; Node.js 22 LTS  
**Primary Dependencies**: Next.js 15 (App Router), React 19, HeroUI 3, Recharts (new), Vitest 2, Biome  
**Storage**: N/A — read-only consumer of the 017 backend API  
**Testing**: Vitest + `react-dom/server` renderToStaticMarkup; `@vitest/coverage-v8` ≥ 90%  
**Target Platform**: Desktop browser (web application)  
**Project Type**: Next.js App Router web application  
**Performance Goals**: Search results visible within 2 seconds of query submission  
**Constraints**: No client-side secrets; `DISCOVERY_API_BASE_URL` server-side only; no `dangerouslySetInnerHTML`  
**Scale/Scope**: 4 new pages, ~10 new components, 1 API client module

## Constitution Check

_GATE: Must pass before Phase 0 research. Re-check after Phase 1 design._

- **Monorepo cohesion**: ✅ All changes are confined to `apps/frontend/` (Nx project
  boundary). The new `recharts` dependency is added to `apps/frontend/package.json`.
  The `DISCOVERY_API_BASE_URL` environment variable is documented in quickstart.md.
  No cross-project imports are introduced.
- **Quality gate enforcement**: ✅ Biome lint/format, `tsc --noEmit`, and Vitest are
  enforced via existing Nx targets and pre-commit hooks. No suppressions or bypasses
  are planned. Recharts has complete TypeScript types included.
- **Test and coverage discipline**: ✅ All new components and the API client module are
  covered by Vitest tests. The 90% coverage floor is maintained in `apps/frontend/`.
  TDD approach: tests written before or alongside component implementation.
- **Local-first parity**: ✅ The 017 backend API service is already in `docker-compose.yml`.
  This feature adds frontend-only pages reachable via `pnpm --dir apps/frontend dev`.
  The `DISCOVERY_API_BASE_URL` environment variable is documented in quickstart.md.
  Optional Compose frontend service pattern is documented but not required for dev.
- **Data integrity and reliability**: ✅ No data mutations. Frontend is a read-only
  consumer. All API response data is treated as potentially null/empty for optional
  fields. No schema migrations are involved.
- **Documentation fidelity**: ✅ `AGENTS.md` is updated to reflect the new recharts
  dependency and frontend page structure. `quickstart.md` covers local setup.
  `contracts/frontend-discovery-ui-contract.md` documents all component/URL/env contracts.

## Project Structure

### Documentation (this feature)

```text
specs/[###-feature]/
├── plan.md              # This file (/speckit.plan command output)
├── research.md          # Phase 0 output (/speckit.plan command)
├── data-model.md        # Phase 1 output (/speckit.plan command)
├── quickstart.md        # Phase 1 output (/speckit.plan command)
├── contracts/           # Phase 1 output (/speckit.plan command)
└── tasks.md             # Phase 2 output (/speckit.tasks command - NOT created by /speckit.plan)
```

### Source Code (repository root)

```text
apps/frontend/
├── src/
│   ├── app/
│   │   ├── page.tsx                         # Home page (Server Component)
│   │   ├── layout.tsx                       # Root layout (existing, no change)
│   │   └── datasets/
│   │       ├── page.tsx                     # Catalog page (Server Component)
│   │       └── [id]/
│   │           ├── page.tsx                 # Detail page (Server Component)
│   │           └── not-found.tsx            # Not-found boundary
│   ├── lib/
│   │   └── api/
│   │       ├── discovery-types.ts           # TypeScript types for API responses
│   │       └── discovery-client.ts          # Typed fetch wrappers (4 functions)
│   └── components/
│       └── discovery/
│           ├── DatasetSearchBox.tsx         # "use client" — search input
│           ├── DatasetSearchResults.tsx     # Search result cards list
│           ├── RecentUpdatesFeed.tsx        # Recent 5 datasets feed
│           ├── DatasetCatalogList.tsx       # Flat/grouped catalog renderer
│           ├── GroupBySourceToggle.tsx      # "use client" — group toggle
│           ├── DatasetCard.tsx              # Shared list-view card
│           ├── DatasetDetailHeader.tsx      # Metadata display block
│           ├── ObservationsChart.tsx        # Recharts LineChart wrapper
│           ├── ObservationsTable.tsx        # Tabular fallback / a11y companion
│           ├── EmptyState.tsx               # No-results display
│           └── ErrorState.tsx              # API error display
└── tests/
    ├── discovery-types.test.ts              # Type shape validation
    ├── discovery-client.test.ts             # API client fetch logic
    ├── DatasetSearchBox.test.tsx
    ├── DatasetSearchResults.test.tsx
    ├── RecentUpdatesFeed.test.tsx
    ├── DatasetCatalogList.test.tsx
    ├── GroupBySourceToggle.test.tsx
    ├── DatasetCard.test.tsx
    ├── DatasetDetailHeader.test.tsx
    ├── ObservationsChart.test.tsx
    ├── ObservationsTable.test.tsx
    ├── EmptyState.test.tsx
    ├── ErrorState.test.tsx
    ├── home-page.test.tsx
    ├── catalog-page.test.tsx
    └── detail-page.test.tsx
```

**Structure Decision**: The App Router page tree maps directly to the four URL routes
defined in the frontend contract. All new components are scoped to
`src/components/discovery/` for clear ownership. The API client lives in `src/lib/api/`
following the established `src/server/` utility pattern already in the project.

## Complexity Tracking

> No constitution violations. No complexity justification required.

---

## Implementation Phases

### Phase 1 — Dependency & Foundation

**Goal**: Install recharts, create the API client module and TypeScript types,
verify the type-checker is clean, and confirm the existing test suite still passes.

**Deliverables**:

1. Add `recharts` to `apps/frontend/package.json` dependencies; run `pnpm install`.
2. Create `src/lib/api/discovery-types.ts` with all TypeScript types from data-model.md.
3. Create `src/lib/api/discovery-client.ts` with four typed fetch functions;
   reads `DISCOVERY_API_BASE_URL` from `process.env`; URL-encodes all params.
4. Write `tests/discovery-types.test.ts` — validates type structure invariants.
5. Write `tests/discovery-client.test.ts` — tests fetch logic with mocked `fetch`.
6. Run `pnpm --dir apps/frontend typecheck` and `pnpm --dir apps/frontend test` — both pass.

**Quality gates**: typecheck clean, existing tests pass, coverage ≥ 90%.

---

### Phase 2 — Shared Discovery Components

**Goal**: Build the reusable leaf components that are used across all pages.

**Deliverables**:

1. `EmptyState.tsx` — accepts optional `message` prop; renders ARIA `role="status"`.
2. `ErrorState.tsx` — accepts optional `message` prop; renders ARIA `role="alert"`.
3. `DatasetCard.tsx` — accepts `DatasetSummary | DatasetRecentItem`; renders title,
   source name, last-updated date, and a Next.js `<Link>` to `/datasets/<dataset_id>`.
4. `DatasetDetailHeader.tsx` — accepts `DatasetDetail`; renders all metadata fields;
   handles null description/geographic_scope gracefully; renders topic_tags as badges.
5. `ObservationsTable.tsx` — accepts `observations: ObservationPoint[]`; renders a
   `<table>` with date and value columns; empty → `<EmptyState />`.
6. Tests for all five components.

**Quality gates**: all component tests pass, typecheck clean.

---

### Phase 3 — Search & Recent Updates (Home Page)

**Goal**: Build the home page with search and recent updates.

**Deliverables**:

1. `DatasetSearchBox.tsx` — `"use client"` component; pre-populates from `?q` URL param;
   on submit pushes `?q=<value>` to router.
2. `DatasetSearchResults.tsx` — accepts `items: DatasetSummary[]` and `query: string`;
   renders `<DatasetCard />` per item; empty → `<EmptyState />`.
3. `RecentUpdatesFeed.tsx` — accepts `items: DatasetRecentItem[]`; renders up to 5
   `<DatasetCard />` rows.
4. Update `src/app/page.tsx` — Server Component: reads `?q` from `searchParams`;
   calls `fetchDatasetSearch` (if q present) or `fetchRecentDatasets` for the feed;
   renders `<DatasetSearchBox />`, search results section (if q), and
   `<RecentUpdatesFeed />`; wraps fetch in try/catch → `<ErrorState />` on failure.
5. Tests for search box, results, feed, and home page rendering.

**Quality gates**: home page renders for empty q and with q; error state renders
on API failure; all tests pass.

---

### Phase 4 — Catalog Page

**Goal**: Build the full catalog list page with search and group-by-source.

**Deliverables**:

1. `GroupBySourceToggle.tsx` — `"use client"` component; reads `?group` URL param;
   toggles `?group=source` on/off via router push.
2. `DatasetCatalogList.tsx` — accepts `items`, `groups`, `viewMode`; flat mode renders
   `<DatasetCard />` list; grouped mode renders source sections with member cards.
3. Create `src/app/datasets/page.tsx` — Server Component: reads `?q` and `?group`
   from `searchParams`; calls `fetchDatasetCatalog`; renders `<DatasetSearchBox />`,
   `<GroupBySourceToggle />`, `<DatasetCatalogList />`; error → `<ErrorState />`.
4. Tests for toggle, catalog list (flat and grouped modes), and catalog page.

**Quality gates**: catalog shows all datasets; group toggle reorganizes view;
search filter applies; all tests pass.

---

### Phase 5 — Detail Page & Not-Found

**Goal**: Build the dataset detail page with the time series chart and not-found handling.

**Deliverables**:

1. `ObservationsChart.tsx` — accepts `observations: ObservationPoint[]`; projects to
   `ChartDataPoint[]`; renders Recharts `LineChart` with `XAxis`, `YAxis`, `Line`,
   `Tooltip`; adds `aria-label`; single point renders without crash; empty →
   `<EmptyState message="No observation data available" />`.
2. Create `src/app/datasets/[id]/page.tsx` — Server Component: calls
   `fetchDatasetDetail(params.id)`; on 404 error calls Next.js `notFound()`;
   on other errors renders `<ErrorState />`; renders `<DatasetDetailHeader />`,
   `<ObservationsChart />`, `<ObservationsTable />`.
3. Create `src/app/datasets/[id]/not-found.tsx` — renders a friendly "Dataset not found"
   message with a link back to `/datasets`.
4. Tests for chart (empty, 1 point, many points), detail page, not-found page.

**Quality gates**: detail page renders all metadata; chart renders for all data sizes;
not-found renders on unknown ID; all tests pass.

---

### Phase 6 — Quality Gates & Documentation

**Goal**: Confirm all quality gates pass and update all required documentation.

**Deliverables**:

1. Run full frontend quality suite: lint, format, typecheck, test, coverage — all pass.
2. Run `pnpm run affected:lint/format/typecheck/test/coverage` — no regressions.
3. Update `AGENTS.md` — add `recharts` to frontend dependencies, add new page routes
   and Nx targets if any are added to `apps/frontend/project.json`.
4. Update `docs/runbooks/provider-onboarding.md` — note that frontend pages will
   display datasets for any provider whose data appears in the backend.
5. Add `test:discovery-pages` Nx target to `apps/frontend/project.json` for focused
   discovery page test runs.
6. Update `specs/018-frontend-dataset-discovery/quickstart.md` with execution evidence.

**Quality gates**: ≥ 90% coverage across `src/`; all affected gates green; docs updated.

---

## Key Design Decisions

| Decision           | Choice                                          | Rationale                                                            |
| ------------------ | ----------------------------------------------- | -------------------------------------------------------------------- |
| Charting library   | `recharts`                                      | React-native, TypeScript-first, minimal bundle, no D3 peer conflicts |
| Data fetching      | Server Components + typed `discovery-client.ts` | No client-side fetch weight; URL-driven re-renders                   |
| Filter state       | URL search params                               | Bookmarkable, shareable, App Router native                           |
| Not-found handling | `notFound()` + `not-found.tsx`                  | App Router standard; no custom error boundary needed                 |
| XSS safety         | React JSX escaping + `URLSearchParams`          | React default; no extra library                                      |
| Component scope    | `src/components/discovery/` flat module         | Clear feature ownership; consistent with existing shell pattern      |

## Documentation Updates Required

| Document                                             | Update                                              |
| ---------------------------------------------------- | --------------------------------------------------- |
| `AGENTS.md`                                          | Add `recharts` dependency, new frontend page routes |
| `apps/frontend/project.json`                         | Add `test:discovery-pages` Nx target                |
| `specs/018-frontend-dataset-discovery/quickstart.md` | Add execution evidence after implementation         |
| `docs/runbooks/provider-onboarding.md`               | Note frontend pages display provider data           |
