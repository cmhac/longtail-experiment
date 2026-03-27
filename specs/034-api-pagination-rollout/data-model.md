# Data Model: Discovery Pagination Rollout

## Entity: PaginatedListRequest

- Description: Request envelope for any user-facing list route.
- Fields:
  - `page` (integer, required default by route): must be >= 1
  - `page_size` (integer, required default by route): must be within configured bounds
  - `query` (string, optional): free-text search term when supported
  - `filters` (object, optional): route-specific filter values
  - `sort` (string, optional): stable sort key in route-supported set
- Validation Rules:
  - Reject invalid `page` and `page_size` with clear invalid-request response.
  - Normalize empty string inputs for optional query/filter fields according to existing route behavior.

## Entity: PaginatedListResponse

- Description: Generic paginated response contract for list-type routes.
- Fields:
  - `items` (array): records for requested page only
  - `page` (integer): current page returned
  - `page_size` (integer): page size applied
  - `total_items` (integer): count of all records in current filtered scope
  - `total_pages` (integer): derived from `total_items` and `page_size`
  - `sort` (string, optional): applied sort descriptor where already present
  - `aggregations` (object, optional): route-specific aggregate metadata
- Validation Rules:
  - `items.length` must be <= `page_size`
  - `total_pages` is 0 when `total_items` is 0
  - `page` in response reflects resolved request page

## Entity: ListRoutePaginationPolicy

- Description: Route-level pagination policy governing defaults and bounds.
- Fields:
  - `route_id` (string): unique route identifier
  - `default_page` (integer)
  - `default_page_size` (integer)
  - `max_page_size` (integer)
  - `supports_filters` (boolean)
  - `supports_sort` (boolean)
- Validation Rules:
  - Policy values must produce deterministic and bounded responses.
  - Policy must be reflected in route contract tests.

## Entity: FrontendPaginationState

- Description: UI state for list navigation synchronized with URL/query parameters.
- Fields:
  - `selected_page` (integer)
  - `selected_page_size` (integer)
  - `total_pages` (integer)
  - `total_items` (integer)
  - `active_query` (string, optional)
  - `active_filters` (map, optional)
  - `active_sort` (string, optional)
- State Transitions:
  - On `page_change`: request selected page and update state from response metadata.
  - On `filter_or_query_change`: reset/reconcile page state to valid range and request refreshed results.
  - On `out_of_range_response`: move to safe fallback state and preserve explicit user feedback.
