# Research: Frontend Dataset Discovery UI (018)

**Branch**: `018-frontend-dataset-discovery`  
**Date**: 2026-03-23  
**Phase 0 status**: Complete — all questions resolved

---

## Question 1: Charting Library for Time Series Visualization

**Decision**: Recharts

**Rationale**:
Recharts is a React-native composable charting library built on D3 primitives. It is
the most widely adopted charting choice for React 18/19 projects, has no D3 peer-
dependency conflicts, and provides a `LineChart` + `Tooltip` combination that maps
directly to the observation dataset (date → numeric value). It integrates cleanly with
the existing TypeScript strict project, supports SSR-safe rendering patterns, and adds
minimal bundle weight (~130 KB gzip) relative to alternatives.

**Alternatives considered**:

- **Chart.js + react-chartjs-2**: Heavier bundle, imperative API, canvas-only (no
  SVG DOM for testing), requires ref-based lifecycle management.
- **Tremor / @tremor/react**: Opinionated design system that conflicts with the
  existing HeroUI monochrome theme contract.
- **Nivo**: Strong but depends on older D3 internals and has known React 19
  compatibility caveats.
- **Lightweight Charts (TradingView)**: Financial-grade, heavily over-engineered for
  simple time series line charts.

**Resolved**: Use `recharts` as a `dependencies` entry.

---

## Question 2: Data Fetching Pattern in Next.js App Router

**Decision**: Server Components for initial page loads, with a thin typed API client
module in `src/lib/api/discovery-client.ts`. Search and group-by-source interactions
on the catalog page and home page use Client Components with URL search params to
maintain shareable, bookmarkable state.

**Rationale**:
App Router Server Components are the canonical data-fetching layer: they run on the
server, avoid waterfalls, and require no client bundle weight for fetch logic. The API
base URL is injected via the `DISCOVERY_API_BASE_URL` environment variable (read
server-side only). Client Components are used only at the dynamic interaction boundary
(search input, group toggle).

The discovery client wraps native `fetch()` with typed request/response shapes derived
from the 017 contract. Data is never fetched client-side except when re-filtering an
already-loaded catalog (URL-param-driven navigation causes a server re-render, not a
client fetch).

**Alternatives considered**:

- **SWR / React Query**: Over-engineered for read-mostly static pages with no mutation,
  adds bundle weight, and requires client components everywhere.
- **getServerSideProps / getStaticProps**: Page Router patterns, incompatible with App
  Router's Server Component model.

**Resolved**: `src/lib/api/discovery-client.ts` wraps `fetch()` with typed interfaces.
Pages are Server Components by default; only search input and group toggle are Client
Components.

---

## Question 3: URL State vs Local Component State

**Decision**: URL search parameters for all user-driven filter state (search query,
group-by-source toggle). Local `useState` is only for UI interaction pre-commit (typing
before submitting).

**Rationale**:
URL-driven state makes search results and catalog grouping views bookmarkable,
shareable, and navigable via browser back/forward. Next.js App Router re-renders Server
Components when URL params change, so no client-side fetch or state sync is needed.

**Pattern**:

- `?q=<search term>` on `/` and `/datasets`
- `?group=source` on `/datasets`
- Detail page: `/datasets/[id]` (no query params needed)

**Resolved**: Use `useRouter` + `useSearchParams` from `next/navigation` in Client
Components that own the search input and group toggle.

---

## Question 4: Component Organization

**Decision**: Discovery UI components live in `src/components/discovery/`. Shared
structural components (already existing) remain in `src/shell/`. API client lives in
`src/lib/api/`. No new shared library is introduced.

**Structure**:

```text
src/
  app/
    page.tsx                    # Home page (Server Component)
    datasets/
      page.tsx                  # Catalog page (Server Component shell)
      [id]/
        page.tsx                # Detail page (Server Component)
        not-found.tsx           # Next.js not-found boundary
  lib/
    api/
      discovery-client.ts       # Typed fetch wrappers for all 4 endpoints
      discovery-types.ts        # TypeScript types mirroring 017 response shapes
  components/
    discovery/
      DatasetSearchBox.tsx      # Client Component — search input + submit
      DatasetSearchResults.tsx  # Server Component — list of search result cards
      RecentUpdatesFeed.tsx     # Server Component — recent 5 datasets feed
      DatasetCatalogList.tsx    # Server Component — full catalog flat/grouped list
      GroupBySourceToggle.tsx   # Client Component — toggle control
      DatasetCard.tsx           # Shared card for list-view entries
      DatasetDetailHeader.tsx   # Metadata display section
      ObservationsChart.tsx     # Recharts LineChart wrapper
      ObservationsTable.tsx     # Fallback tabular view / accessibility companion
      EmptyState.tsx            # Reusable empty/no-results message
      ErrorState.tsx            # Reusable API error message
```

**Resolved**: Components follow a flat-module convention under `src/components/discovery/`.

---

## Question 5: Not-Found and Error Handling

**Decision**:

- Dataset detail page not-found: use Next.js `notFound()` helper from `next/navigation`
  to render the App Router `not-found.tsx` boundary at the `[id]` segment.
- API error states: wrap each server component's fetch in try/catch; render `<ErrorState />`
  component on failure rather than crashing.
- Client-side rendering gaps (Suspense): use `<Suspense fallback={...}>` boundaries
  where needed for streaming.

**Resolved**: `not-found.tsx` at the `app/datasets/[id]/` level; `ErrorState` component
for generic fetch failures.

---

## Question 6: XSS Safety

**Decision**: All data from the API is rendered via React JSX text content (not
`dangerouslySetInnerHTML`). This is React's default — JSX text nodes are always escaped.
No additional sanitization library is required because the application does not render
HTML from API responses.

Search input values passed to the API are URL-encoded via `URLSearchParams` before
inclusion in fetch URLs.

**Resolved**: No additional sanitization library; rely on React JSX escaping and
URL encoding.

---

## Summary of Resolved Decisions

| Question            | Decision                                                |
| ------------------- | ------------------------------------------------------- |
| Charting library    | `recharts` as a runtime dependency                      |
| Data fetching       | Server Components + typed `discovery-client.ts` wrapper |
| URL state           | `useSearchParams` / `useRouter` for all filter params   |
| Component structure | `src/components/discovery/` flat module                 |
| Not-found handling  | Next.js `notFound()` + `not-found.tsx` boundary         |
| XSS safety          | React JSX escaping + URL encoding (no extra library)    |
