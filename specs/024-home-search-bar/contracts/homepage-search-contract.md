# Contract: Homepage Search Scope and Suggestions

## Interface Summary

- Interface type: Backend HTTP read contract consumed by homepage discovery UI
- Consumer: Frontend homepage search surface and suggestion dropdown
- Provider: Backend dataset discovery API and query service layer

## Endpoint A: Homepage Search Summary

### Route

GET /api/datasets/search/summary

### Purpose

Provides aggregate values for the homepage sentence:
Searching [dataset count] active datasets from [source count] sources.

### Response Contract (200)

- active_dataset_count: integer >= 0
- active_source_count: integer >= 0
- generated_at: ISO timestamp (optional)

### Response Example (200)

```json
{
  "active_dataset_count": 48,
  "active_source_count": 3,
  "generated_at": "2026-03-24T00:00:00+00:00"
}
```

### Error Contract

- Standard error envelope with code and message.
- Frontend fallback behavior must keep search input usable.

## Endpoint B: Dataset Likely Suggestions

### Route

GET /api/datasets/search/suggestions?q={query}&limit={n}

### Purpose

Returns likely dataset matches for partial query text.

### Query Parameters

- q: string (required, trimmed)
- limit: integer (optional, bounded to 1..10, default 5)

### Response Contract (200)

- query: string
- limit: integer
- items: array of
  - dataset_id: string
  - title: string
  - source:
    - id: string
    - name: string
  - rank_score: number

### Response Example (200)

```json
{
  "query": "fund",
  "limit": 5,
  "items": [
    {
      "dataset_id": "FEDFUNDS",
      "source": {
        "id": "fred",
        "name": "FRED"
      },
      "title": "Federal Funds Effective Rate",
      "rank_score": 0.91
    }
  ]
}
```

### Behavioral Guarantees

1. Result ordering is deterministic by relevance then stable tiebreakers.
2. Returned items correspond to supplied query text.
3. Result count never exceeds limit.

### Error Contract

- Invalid query parameters return bad-request envelope.
- Service failures return non-success envelope without exposing internal details.
- Invalid `limit` values outside 1..10 return `invalid_request`.

## Frontend Rendering Contract

1. Summary sentence renders with real values when summary response is available.
2. Suggestions render only for current query value.
3. Stale suggestions from previous query values are not displayed.
4. Missing summary/suggestions do not disable primary input interaction.
5. Summary fallback sentence remains readable as: `Searching active datasets from sources.`

## Versioning

- Contract version: 1.0
- Any breaking shape change requires synchronized updates to backend contracts, frontend discovery types/client parsing, and tests.
