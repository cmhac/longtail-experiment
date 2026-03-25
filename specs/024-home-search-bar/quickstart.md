# Quickstart: Homepage Search Bar Experience

## Purpose

Validate centered homepage search UX, runtime summary counts, and likely-match suggestions end-to-end.

## Prerequisites

- Monorepo dependencies installed.
- Backend and frontend apps available in local environment.
- Discovery API base URL configured for frontend runtime.

## 1. Start local services

1. Start backend API runtime exposing discovery endpoints.
2. Start frontend app runtime.
3. Confirm home page loads without server errors.

## 2. Verify centered search surface

1. Open homepage.
2. Confirm main search bar is visually centered and prominent.
3. Confirm minimal scope line appears under search bar.

## 3. Verify runtime aggregate scope values

1. Confirm summary sentence uses real numbers:
   Searching X active datasets from Y sources.
2. Confirm values are not static TK placeholders.
3. Refresh and verify values remain coherent with backend state.
4. If summary is unavailable, confirm fallback text remains readable:
   Searching active datasets from sources.

## 4. Verify likely-match dropdown behavior

1. Enter partial query text (example: gas, infl, unem).
2. Confirm likely-match dropdown appears.
3. Continue typing and confirm suggestions refresh for latest query.
4. Confirm old suggestions are not retained after query changes.
5. Enter a query with no likely matches and confirm no misleading stale suggestions are shown.

## 5. Verify graceful fallback behavior

1. Simulate temporary summary or suggestion failure.
2. Confirm search input remains usable.
3. Confirm fallback state is readable and non-blocking.

## 6. Focused quality checks

1. Run backend tests for summary/suggestion query contracts.
2. Run frontend tests for centered search rendering and dropdown interaction behavior.

Suggested commands:

- `uv run --project apps/backend pytest --no-cov apps/backend/tests/contract/test_homepage_search_summary_contract.py apps/backend/tests/contract/test_dataset_search_suggestions_contract.py apps/backend/tests/contract/test_http_runtime_persisted_discovery_endpoints.py`
- `pnpm --dir apps/frontend test -- tests/home-page.test.tsx tests/shell-structure-contract.test.tsx tests/discovery-client.test.ts tests/DatasetSearchBox.suggestions.test.tsx`

## 7. Required stop-gate commands

1. pnpm exec nx run-many -t test --all
2. pnpm exec nx run-many -t coverage --all

## Completion Criteria

- Homepage search bar is centered and prominent.
- Summary sentence renders real aggregate values.
- Likely-match dropdown updates correctly from current query.
- Fallback states preserve core search usability.
- Monorepo test and coverage gates pass.
