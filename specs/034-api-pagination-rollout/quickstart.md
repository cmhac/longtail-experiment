# Quickstart: Discovery Pagination Rollout

## Prerequisites

- Dependencies installed for monorepo workspace.
- Local stack available via Docker Compose when running runtime verification.

## 1. Run Targeted Development Checks

1. Backend contract/runtime tests covering discovery list routes.
2. Frontend tests covering discovery list page navigation and client query behavior.

## 2. Manual Verification Flow

1. Start from clean local compose state.
2. Bring up required services and open discovery frontend.
3. Verify each in-scope list route supports page navigation with consistent metadata:
   - Search list route
   - Catalog list route
   - Source detail dataset list route
   - Topic detail dataset list route
   - Geography detail dataset list route
4. Verify invalid pagination parameters show explicit invalid-request behavior.
5. Verify filter/search changes reconcile page state and do not show duplicate/skip behavior.

## Story-Level Verification Checklist

### US1 - Navigate Large Result Sets

- Verify each in-scope list route returns `items`, `page`, `page_size`, `total_items`, and `total_pages`.
- Verify requests for different valid pages return different bounded record windows.
- Verify invalid `page` and `page_size` values return invalid-request responses.

### US2 - Frontend and Service State Alignment

- Verify frontend pagination controls reflect response metadata values.
- Verify page changes update both request query params and rendered list state.
- Verify deep links with explicit page query values hydrate correct list views.

### US3 - Preserve Existing Discovery Behaviors

- Verify filter and sort behavior remains unchanged except for explicit paging.
- Verify empty states still render when filtered result sets are empty.
- Verify error states still render when upstream requests fail.

## 3. Required Quality Gates Before Commit

1. `pnpm exec nx run-many -t test --all`
2. `pnpm exec nx run-many -t coverage --all`

## 4. Documentation Verification

1. Confirm contract docs for list-route pagination are updated.
2. Confirm feature docs capture any explicitly excluded routes.
3. Confirm AGENTS-aligned command/workflow references remain accurate if changed.

## Execution Evidence

### Automated Verification

1. Full monorepo tests:
   - Command: `pnpm exec nx run-many -t test --all`
   - Result: Passed for frontend, backend, pipeline, and db projects.
2. Full monorepo coverage:
   - Command: `pnpm exec nx run-many -t coverage --all --outputStyle=static`
   - Result: Passed; frontend branch coverage >= 90% (91.18%), backend total coverage 90.13%, pipeline total coverage 90.03%, db total coverage 99.59%.
3. Mandatory all-files stop gate:
   - Command: `pre-commit run --all-files`
   - Result: Passed (`monorepo-lint-all`, `monorepo-format-all`, `monorepo-typecheck-all`, `monorepo-test-all`, `monorepo-coverage-all`, duplication, and inline-suppression checks).

### Manual Runtime Verification

Environment reset and startup:

1. `docker compose down`
2. `docker compose up -d`
3. `docker compose ps`

HTTP contract checks executed:

1. Search page 1:
   - `curl -sS "http://localhost:8080/api/datasets/search?q=gas&page=1&page_size=2"`
   - Verified: `items` bounded to page size and metadata fields (`page`, `page_size`, `total_items`, `total_pages`) present.
2. Search out-of-range reconciliation:
   - `curl -sS "http://localhost:8080/api/datasets/search?q=gas&page=99&page_size=2"`
   - Verified: response reconciles to last page (`page=8`, `total_pages=8`).
3. Catalog pagination:
   - `curl -sS "http://localhost:8080/api/datasets?page=2&page_size=2&sort=title&order=asc"`
   - Verified: bounded `items`, pagination metadata, aggregations, and groups envelope.
4. Source detail pagination:
   - `curl -sS "http://localhost:8080/api/sources/fred?page=1&page_size=1"`
   - Verified: `source` plus paginated `items` envelope.
5. Topic detail pagination:
   - `curl -sS "http://localhost:8080/api/topics/interest-rates?page=1&page_size=1"`
   - Verified: `topic` plus paginated `items` envelope.
6. Geography detail pagination:
   - `curl -sS "http://localhost:8080/api/geographies/united-states?page=1&page_size=1"`
   - Verified: `geography` plus paginated `items` envelope.
7. Invalid page handling:
   - `curl -sS -o /tmp/pagination_invalid.json -w "%{http_code}" "http://localhost:8080/api/datasets/search?q=gas&page=0&page_size=2"`
   - Verified: HTTP 400 with `invalid_request` error message for invalid page value.

Browser verification:

1. `http://localhost:3000/datasets?page=2`
   - Verified pagination controls render and metadata-driven navigation appears as expected.
2. `http://localhost:3000/search?q=gas&page=99`
   - Verified UI reconciles to valid page state (`Page 1 of 1`).
3. `http://localhost:3000/sources/fred?page=2`
   - Verified source detail list renders paginated metadata and reconciled page state.
