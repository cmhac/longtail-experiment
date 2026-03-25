# Contract: Homepage Editorial Recent Updates Feed

## Interface Summary

- Interface type: Homepage read contract for editorial recent-updates presentation
- Consumer: Frontend home page editorial feed section
- Provider: Backend discovery recent-updates endpoint and frontend mapping layer

## Endpoint: Recent Updates Feed

### Route

GET /api/datasets/recent?limit={n}

### Purpose

Provide up to five most recent dataset updates for editorial rendering on the homepage.

### Query Parameters

- limit: integer (optional, bounded to 1..5, default 5)

### Response Contract (200)

- items: array of EditorialRecentItem
- limit: integer
- sort: string

### EditorialRecentItem

- dataset_id: string
- source:
  - id: string
  - name: string
- title: string
- latest_update_at: ISO timestamp string
- description: string or null (optional for editorial body copy)
- geographic_scope: string or null (optional for geography line)
- action_links:
  - view_table_href: string
  - download_csv_href: string

### Response Example (200)

```json
{
  "items": [
    {
      "dataset_id": "ENERGY.US.GASREGW_CO",
      "source": {
        "id": "eia",
        "name": "EIA"
      },
      "title": "Regular All Formulations Retail Gasoline Prices - Colorado",
      "latest_update_at": "2026-03-24T00:00:00+00:00",
      "description": "Weekly EIA retail regular all formulations gasoline prices in dollars per gallon.",
      "geographic_scope": "Colorado",
      "action_links": {
        "view_table_href": "/datasets/ENERGY.US.GASREGW_CO",
        "download_csv_href": "/api/datasets/ENERGY.US.GASREGW_CO.csv"
      }
    }
  ],
  "limit": 5,
  "sort": "latest_update_at_desc,title_asc,dataset_id_asc"
}
```

## Behavioral Guarantees

1. Items are ordered by descending recency.
2. Returned item count never exceeds limit.
3. Required row fields and action links are present for each returned item.
4. Optional descriptive fields may be null and must be treated as non-fatal by consumers.

## Error Contract

- Invalid limit values return standard invalid-request envelope.
- Service or persistence failures return standard error envelope and do not alter other homepage sections.

## Frontend Rendering Contract

1. Feed section heading and recency label are always visible when section renders.
2. Each row renders source/date context, title, and action links.
3. Optional description and geography render only when present.
4. Empty payload renders explicit no recent updates state.
5. Feed failure falls back gracefully without disabling search interactions.

## Versioning

- Contract version: 1.0
- Breaking response-shape changes require synchronized updates to backend contracts, frontend discovery types/client mapping, and feed tests.
