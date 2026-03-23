# Data Model: Frontend Dataset Discovery UI (018)

**Branch**: `018-frontend-dataset-discovery`  
**Date**: 2026-03-23  
**Source**: Derived from 017 API contract response shapes

---

## Overview

This feature introduces no new database schema or backend data structures. All data
is read-only from the 017 Dataset Discovery API. The data model documented here
describes the TypeScript type contracts that the frontend uses to represent, validate,
and render API responses.

---

## Core Types

### `SourceRef`

Represents the data provider/source of a dataset.

```typescript
interface SourceRef {
  id: string; // e.g. "fred"
  name: string; // e.g. "FRED"
}
```

### `DatasetSummary`

Used in search results, recent updates feed, and catalog list rows.

```typescript
interface DatasetSummary {
  dataset_id: string; // canonical series key, e.g. "UNRATE"
  source: SourceRef;
  title: string;
  description: string | null;
  geographic_scope: string | null;
  topic_tags: string[];
  latest_update_at: string; // ISO 8601 datetime string
}
```

### `DatasetRecentItem`

Lightweight variant used in the recent-updates feed (no description/tags/geo).

```typescript
interface DatasetRecentItem {
  dataset_id: string;
  source: SourceRef;
  title: string;
  latest_update_at: string; // ISO 8601 datetime string
}
```

### `DatasetSourceGroup`

Used when the catalog is viewed grouped by source.

```typescript
interface DatasetSourceGroup {
  source: SourceRef;
  dataset_count: number;
  dataset_ids: string[];
}
```

### `ObservationPoint`

A single data point in a dataset's time series.

```typescript
interface ObservationPoint {
  observed_on: string; // ISO 8601 date string (YYYY-MM-DD)
  value: number;
  reported_at: string; // ISO 8601 datetime string
  attributes: Record<string, unknown>;
}
```

### `DatasetDetail`

Full dataset response including metadata and all observations.

```typescript
interface DatasetDetail {
  dataset_id: string;
  source: SourceRef;
  title: string;
  description: string | null;
  geographic_scope: string | null;
  topic_tags: string[];
  metadata: Record<string, string | null>;
  observations: ObservationPoint[];
  observation_sort: string;
}
```

---

## API Response Envelopes

### `DatasetSearchResponse`

Response from `GET /api/datasets/search`.

```typescript
interface DatasetSearchResponse {
  items: DatasetSummary[];
  page: number;
  page_size: number;
  total_items: number;
  total_pages: number;
  sort: string;
}
```

### `DatasetRecentUpdatesResponse`

Response from `GET /api/datasets/recent`.

```typescript
interface DatasetRecentUpdatesResponse {
  items: DatasetRecentItem[];
  limit: number;
  sort: string;
}
```

### `DatasetCatalogResponse`

Response from `GET /api/datasets`.

```typescript
interface DatasetCatalogResponse {
  items: DatasetSummary[];
  groups: DatasetSourceGroup[] | null;
  page: number;
  page_size: number;
  total_items: number;
  total_pages: number;
  sort: string;
}
```

### `ApiErrorEnvelope`

Returned on 400/404 responses from the API.

```typescript
interface ApiErrorEnvelope {
  error: {
    code: string; // e.g. "dataset_not_found", "invalid_request"
    message: string;
  };
}
```

---

## UI-Layer Derived Types

These types are computed or derived in the frontend and are not part of API contracts.

### `CatalogViewMode`

Controls whether the catalog renders as a flat list or grouped by source.

```typescript
type CatalogViewMode = "flat" | "grouped";
```

### `ChartDataPoint`

Projected from `ObservationPoint` for the Recharts `LineChart`.

```typescript
interface ChartDataPoint {
  date: string; // formatted from observed_on for display axis
  value: number;
}
```

---

## Invariants and Constraints

- `dataset_id` values are stable canonical keys (uppercase, alphanumeric + underscores).
  They are safe to use as URL path segments.
- `topic_tags` is always an array (never null); it may be empty.
- `description` and `geographic_scope` may be null; UI must handle both.
- `observations` on a detail response is always an array (never null); it may be empty.
- `latest_update_at` is always a valid ISO 8601 string in all list response shapes.
- All numeric observation `value` fields are finite numbers.

---

## No Schema Migrations

This feature introduces no Alembic migrations. The frontend data model is a TypeScript-
only concern. Migration head remains at `0008_dataset_discovery_indexes`.
