# Contract: Frontend Dataset Discovery UI

## Purpose

Define the interface contracts the frontend UI presents to users, specifically:
the required data shapes consumed from the backend API, the URL routing contract,
the environment configuration contract, and the component rendering contracts
(what each component must receive and render to satisfy acceptance scenarios).

This contract layer ensures the frontend can be developed and tested independently
from the backend by mocking these contracts, and ensures the backend 017 API and
the frontend remain in sync.

---

## 1. Backend API Consumption Contract

The frontend **MUST** consume the following endpoints as defined in
`specs/017-dataset-discovery-api/contracts/dataset-discovery-api-contract.md`.
No endpoint behavior may be added or assumed beyond what is defined there.

| Endpoint | Path | Used By |
|---|---|---|
| Search | `GET /api/datasets/search?q=<term>&page=<n>&page_size=<n>` | Home page search |
| Recent Updates | `GET /api/datasets/recent?limit=5` | Home page feed |
| Catalog | `GET /api/datasets?q=<term>&group_by_source=<bool>&page=<n>` | Catalog page |
| Detail | `GET /api/datasets/<dataset_id>` | Detail page |

The frontend MUST treat all optional metadata fields (`description`,
`geographic_scope`) as possibly null and render gracefully in that case.

---

## 2. URL Routing Contract

The frontend exposes the following stable URL routes:

| Route | Page | URL State |
|---|---|---|
| `/` | Home page | `?q=<search term>` (optional) |
| `/datasets` | Catalog page | `?q=<term>` (optional), `?group=source` (optional) |
| `/datasets/<dataset_id>` | Detail page | None |

Rules:
- `dataset_id` in the URL path MUST match the canonical `dataset_id` from API responses.
- Navigating to `/datasets/<unknown_id>` MUST render a "not found" page rather than crashing.
- URL search params MUST be preserved on browser back/forward navigation.

---

## 3. Environment Configuration Contract

The frontend requires one environment variable at build/runtime:

| Variable | Required | Description |
|---|---|---|
| `DISCOVERY_API_BASE_URL` | Yes (server-side) | Base URL of the 017 backend API, e.g. `http://backend:8080` |

This variable is consumed only in Server Components and API client code.
It MUST NOT be exposed to the client bundle (`NEXT_PUBLIC_` prefix is forbidden for
this variable).

---

## 4. Discovery API Client Contract

The `src/lib/api/discovery-client.ts` module MUST expose these four functions:

```typescript
fetchDatasetSearch(params: {
  q?: string;
  page?: number;
  pageSize?: number;
}): Promise<DatasetSearchResponse>

fetchRecentDatasets(params?: {
  limit?: number;
}): Promise<DatasetRecentUpdatesResponse>

fetchDatasetCatalog(params: {
  q?: string;
  groupBySource?: boolean;
  page?: number;
  pageSize?: number;
}): Promise<DatasetCatalogResponse>

fetchDatasetDetail(datasetId: string): Promise<DatasetDetail>
```

Each function MUST:
- Throw a typed error (or re-throw with `ApiError` wrapper) on non-200 responses.
- Return typed response matching the types in `discovery-types.ts`.
- Never include credentials in outbound requests.
- URL-encode all user-supplied query parameter values before including them in URLs.

---

## 5. Component Rendering Contracts

### `DatasetSearchBox`
- Renders a `<form>` with a text `<input>` and submit action.
- On submit, pushes `?q=<value>` to the current page URL via `useRouter`.
- Input value is pre-populated from current `?q` URL param on mount.

### `DatasetSearchResults`
- Receives `items: DatasetSummary[]` and `query: string`.
- If `items` is empty, renders `<EmptyState />`.
- Each item renders as a `<DatasetCard />` linking to `/datasets/<dataset_id>`.

### `RecentUpdatesFeed`
- Receives `items: DatasetRecentItem[]`.
- Renders at most 5 items in order.
- Each item links to `/datasets/<dataset_id>`.
- Shows title, source name, and `latest_update_at` formatted as a locale date string.

### `DatasetCatalogList`
- Receives `items: DatasetSummary[]`, `groups: DatasetSourceGroup[] | null`,
  `viewMode: CatalogViewMode`.
- Flat mode: renders items as `<DatasetCard />` list.
- Grouped mode: renders one section per group with source heading and member items.

### `GroupBySourceToggle`
- Renders a toggle button/checkbox.
- On change, pushes or removes `?group=source` from the current URL.

### `DatasetDetailHeader`
- Receives a `DatasetDetail` object.
- Renders title, description (or "No description available"), geographic scope
  (or omitted if null), topic tags as tag chips, source name.

### `ObservationsChart`
- Receives `observations: ObservationPoint[]`.
- If empty, renders `<EmptyState message="No observation data available" />`.
- Otherwise renders a Recharts `LineChart` with `observed_on` on X axis and
  `value` on Y axis.
- Must render meaningfully with 1 data point (no crash or blank).

### `EmptyState`
- Receives `message?: string`.
- Default message: "No results found."
- Renders accessible, non-broken layout.

### `ErrorState`
- Receives `message?: string`.
- Default message: "Unable to load data. Please try again."
- Renders accessible, non-broken layout.

---

## 6. Accessibility Baseline

- All interactive elements (search input, submit button, toggle) MUST have accessible
  labels (either visible text or `aria-label`).
- Navigation links MUST use `<a>` elements (via Next.js `<Link>`).
- The chart MUST include an `aria-label` describing its content.
- Empty and error states MUST use ARIA `role="status"` or equivalent to communicate
  state changes to screen readers.

---

## Non-Goals

- This contract does not define visual design, color scheme, or responsive breakpoints.
- This contract does not define data ingestion, mutation, or write paths.
- Authentication, session management, or user identity contracts are out of scope.
