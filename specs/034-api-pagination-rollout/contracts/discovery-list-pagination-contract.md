# Discovery List Pagination Contract

## Scope

This contract applies to all discovery user-facing list routes. Any route returning a list collection is in scope unless explicitly documented as excluded.

## Request Contract

### Query Parameters

- `page` (optional): integer page number; defaults to route default when omitted.
- `page_size` (optional): integer page size; defaults to route default when omitted.
- Additional route-specific query/filter/sort parameters remain supported.

### Validation

- `page` must be >= 1.
- `page_size` must be >= 1 and <= route max page size.
- Invalid values return invalid-request response with field-specific message.

## Response Contract

### Required Fields

- `items`: array of records for the selected page.
- `page`: resolved current page.
- `page_size`: resolved current page size.
- `total_items`: total records within current query/filter scope.
- `total_pages`: total pages within current query/filter scope.

### Optional Existing Fields

- `sort`, `aggregations`, group metadata, and route-specific envelope properties may remain when already supported.

### Invariants

- `items.length <= page_size`
- If `total_items = 0`, then `total_pages = 0` and `items` is empty.
- Ordering is stable and deterministic within the same query/filter/sort scope.

## Route Coverage Matrix

- Search list routes: paginated
- Catalog list routes: paginated
- Source detail dataset list routes: paginated
- Topic detail dataset list routes: paginated
- Geography detail dataset list routes: paginated
- Other list-type discovery routes: paginated or explicitly documented as excluded

### Rollout Status

- Search list route: implemented
- Catalog list route: implemented
- Source detail dataset list route: implemented
- Topic detail dataset list route: implemented
- Geography detail dataset list route: implemented

### In-Scope Inventory

| Route                                                   | Type                 | Pagination Requirement | Exclusion |
| ------------------------------------------------------- | -------------------- | ---------------------- | --------- |
| `/api/datasets/search`                                  | Search list          | Required               | No        |
| `/api/datasets`                                         | Catalog list         | Required               | No        |
| `/api/sources/{source_id}` (datasets collection)        | Detail-attached list | Required               | No        |
| `/api/topics/{topic_id}` (datasets collection)          | Detail-attached list | Required               | No        |
| `/api/geographies/{geography_id}` (datasets collection) | Detail-attached list | Required               | No        |

### Explicit Exclusions

| Route                              | Reason Excluded                                                                      | Revisit Trigger                                                    |
| ---------------------------------- | ------------------------------------------------------------------------------------ | ------------------------------------------------------------------ |
| `/api/datasets/{dataset_id}`       | Detail endpoint, not a list route                                                    | If endpoint adds list windowing parameters for nested collections  |
| `/api/datasets/recent`             | Bounded editorial feed governed by `limit` contract                                  | If feed requirements change to full catalog navigation             |
| `/api/datasets/search/suggestions` | Bounded suggestions contract governed by `limit`                                     | If suggestions become browsable full result lists                  |
| `/api/sources`                     | Source summary inventory currently bounded by source count and not paged in UI scope | If source counts become large enough to require route-level paging |

## Error Contract

- Invalid pagination parameters return a structured invalid-request envelope.
- Out-of-range page requests reconcile to the last valid page for all in-scope list routes.

## Frontend Consumption Requirements

- Frontend list views must drive navigation from `page`, `page_size`, `total_items`, and `total_pages`.
- Frontend must not rely on oversized one-page fetch behavior to simulate pagination.
- Filter/query changes must reconcile selected page into valid range.
