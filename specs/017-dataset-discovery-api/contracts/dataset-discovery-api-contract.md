# Contract: Dataset Discovery Backend API

## Purpose

Define backend read contracts for dataset discovery and detail workflows used by homepage and catalog UI surfaces.

## Scope

- Landing-page search across title, description, geographic scope, and tags.
- Recent-updates feed with top five datasets by recency.
- Full catalog listing with source organization, search, and pagination.
- Dataset detail retrieval with metadata and chronological observations.

## Common Rules

- All dataset identifiers use canonical series keys.
- Responses are deterministic for identical inputs.
- Unknown dataset identifiers return explicit not-found behavior.
- Optional metadata fields may be null/empty without failing requests.

## Endpoints

### 1) Search Datasets

- Method: GET
- Path: /api/datasets/search

Query parameters:

- q: string (optional)
- page: integer (optional, default 1)
- page_size: integer (optional, bounded)

Success response (200):

```json
{
  "items": [
    {
      "dataset_id": "UNRATE",
      "source": { "id": "fred", "name": "FRED" },
      "title": "Unemployment Rate",
      "description": "Percent of labor force unemployed",
      "geographic_scope": "US",
      "topic_tags": ["labor", "employment"],
      "latest_update_at": "2026-02-01T00:00:00Z"
    }
  ],
  "page": 1,
  "page_size": 20,
  "total_items": 1,
  "total_pages": 1,
  "sort": "latest_update_at_desc,title_asc,dataset_id_asc"
}
```

Behavior:

- Match must include any of: title, description, geographic_scope, topic_tags.
- Empty q is treated as a valid default search context.

### 2) Recent Dataset Updates

- Method: GET
- Path: /api/datasets/recent

Query parameters:

- limit: integer (optional, default 5, max 5)

Success response (200):

```json
{
  "items": [
    {
      "dataset_id": "UNRATE",
      "source": { "id": "fred", "name": "FRED" },
      "title": "Unemployment Rate",
      "latest_update_at": "2026-02-01T00:00:00Z"
    }
  ],
  "limit": 5,
  "sort": "latest_update_at_desc,title_asc,dataset_id_asc"
}
```

Behavior:

- Always returns at most five datasets.
- Recency is based on canonical dataset observation/report timestamps.

### 3) List Catalog Datasets

- Method: GET
- Path: /api/datasets

Query parameters:

- q: string (optional)
- source_id: string (optional)
- page: integer (optional, default 1)
- page_size: integer (optional, bounded)
- group_by_source: boolean (optional)

Success response (200):

```json
{
  "items": [
    {
      "dataset_id": "UNRATE",
      "source": { "id": "fred", "name": "FRED" },
      "title": "Unemployment Rate",
      "description": "Percent of labor force unemployed",
      "geographic_scope": "US",
      "topic_tags": ["labor", "employment"],
      "latest_update_at": "2026-02-01T00:00:00Z"
    }
  ],
  "groups": [
    {
      "source": { "id": "fred", "name": "FRED" },
      "dataset_count": 1,
      "dataset_ids": ["UNRATE"]
    }
  ],
  "page": 1,
  "page_size": 20,
  "total_items": 1,
  "total_pages": 1,
  "sort": "source_name_asc,title_asc,dataset_id_asc"
}
```

Behavior:

- Applies the same search matching fields as /api/datasets/search.
- source_id filter and q filter are composable.
- Paging metadata is always included.

### 4) Get Dataset Detail

- Method: GET
- Path: /api/datasets/{dataset_id}

Query parameters:

- from_date: date (optional)
- to_date: date (optional)

Success response (200):

```json
{
  "dataset_id": "UNRATE",
  "source": { "id": "fred", "name": "FRED" },
  "title": "Unemployment Rate",
  "description": "Percent of labor force unemployed",
  "geographic_scope": "US",
  "topic_tags": ["labor", "employment"],
  "metadata": {
    "units": "Percent",
    "seasonal_adjustment": "Seasonally Adjusted"
  },
  "observations": [
    {
      "observed_on": "2025-12-01",
      "value": 4.1,
      "reported_at": "2026-01-10T00:00:00Z",
      "attributes": {
        "revision": 0
      }
    }
  ],
  "observation_sort": "observed_on_asc,reported_at_asc"
}
```

Not-found response (404):

```json
{
  "error": {
    "code": "dataset_not_found",
    "message": "Dataset with id 'UNKNOWN' was not found"
  }
}
```

Behavior:

- Valid dataset with no observations returns `observations: []` and status 200.
- Observations are chronological and stable for repeated identical inputs.

## Error Contract

Bad request (400) is returned for invalid pagination or malformed date ranges.

```json
{
  "error": {
    "code": "invalid_request",
    "message": "page_size must be between 1 and 100"
  }
}
```

## Edge-Case Semantics

- Empty search query values are valid and use default search behavior.
- Metadata fields (`description`, `geographic_scope`) may be null and must not fail responses.
- Topic tags are always serialized as an array; missing tags become `[]`.
- Known datasets with no observations return `200` with `observations: []`.
- Unknown dataset identifiers return `404` with `dataset_not_found` error code.
- Search and recent responses use deterministic tie-break ordering:
  `latest_update_at DESC`, then `title ASC`, then `dataset_id ASC`.
- Catalog responses use deterministic ordering:
  `source_name ASC`, then `title ASC`, then `dataset_id ASC`.

## Non-Goals

- Data ingestion or mutation endpoints.
- Authentication and authorization policy changes.
- Frontend rendering behavior beyond API payload needs.
