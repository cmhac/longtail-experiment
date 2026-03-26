# Quickstart: Source Discovery Pages

## Prerequisites

- Workspace dependencies are installed.
- Frontend application can run locally.
- Backend discovery runtime is available through the existing local environment.
- Existing persisted discovery metadata includes at least two sources and multiple datasets for manual validation.

## Implementation Validation Flow

1. Run focused backend tests for source repository, service, and HTTP contracts.
2. Run focused frontend tests for source list/detail pages and discovery client methods.
3. Run frontend and backend static quality checks for affected projects.
4. Manually validate the new source browsing routes against the local stack after a clean restart.
5. Run required monorepo stop gates before commit or handoff.

## Suggested Verification Commands

- Focused backend tests:
  - `uv run --project apps/backend pytest --no-cov apps/backend/tests/contract/test_source_list_query_contract.py apps/backend/tests/contract/test_source_detail_query_contract.py apps/backend/tests/contract/test_http_runtime_source_endpoints.py`
  - `uv run --project apps/backend pytest apps/backend/tests/contract/test_dataset_discovery_persisted_repository_contract.py`
- Focused frontend tests:
  - `pnpm --dir apps/frontend test -- tests/source-list-page.test.tsx tests/source-detail-page.test.tsx tests/source-discovery-client.test.ts tests/discovery-types.test.ts tests/shell-structure-contract.test.tsx`
- Frontend static quality checks:
  - `pnpm --dir apps/frontend typecheck`
  - `pnpm --dir apps/frontend exec biome check .`
- Backend static quality checks:
  - `uv run --project apps/backend ruff check apps/backend`
  - `uv run --project apps/backend ty check apps/backend`
- Repo-wide final check:
  - `pre-commit run --all-files`
- Mandatory monorepo stop gates:
  - `pnpm exec nx run-many -t test --all`
  - `pnpm exec nx run-many -t coverage --all`

## Manual Validation Checklist

- Restart the local environment in a clean state before validation.
- Open `/sources` and confirm all discoverable sources appear exactly once with readable names and dataset counts.
- Open at least two source detail pages and confirm each page shows only datasets from the selected source.
- Confirm dataset entries on source detail pages navigate to the existing `/datasets/{id}` route.
- Confirm a source with no datasets shows a clear no-datasets state.
- Confirm an unknown `/sources/{sourceId}` route shows the source not-found experience.
- Confirm backend or fetch failure scenarios show a generic error state while preserving shell navigation.
- Validate desktop and narrow/mobile viewport readability for both source pages.

## Validation Evidence

- Focused backend validation passed:
  - `uv run --project apps/backend ruff check apps/backend`
  - `uv run --project apps/backend ty check apps/backend`
  - `uv run --project apps/backend pytest --no-cov apps/backend/tests/contract/test_source_list_query_contract.py apps/backend/tests/contract/test_source_detail_query_contract.py apps/backend/tests/contract/test_http_runtime_source_endpoints.py`
  - Result: `5 passed in 0.87s`
- Focused frontend validation passed:
  - `pnpm --dir apps/frontend typecheck`
  - `pnpm --dir apps/frontend exec biome check .`
  - `pnpm --dir apps/frontend test -- tests/source-list-page.test.tsx tests/source-detail-page.test.tsx tests/source-discovery-client.test.ts tests/discovery-types.test.ts tests/shell-structure-contract.test.tsx`
  - Result: `5 files passed, 27 tests passed`
- Additional backend persisted-repository validation passed:
  - `uv run --project apps/backend pytest apps/backend/tests/contract/test_dataset_discovery_persisted_repository_contract.py`
  - Result: source list/detail persisted projection coverage added and passing
- Manual clean-restart validation passed after:
  - `docker compose down`
  - `docker compose up -d --build`
  - `docker compose ps`
- Manual backend checks against the restarted stack passed:
  - `curl -sf http://localhost:8080/api/sources`
  - Result: `EIA` and `FRED` returned with dataset counts and `sort: source_name_asc,source_id_asc`
  - `curl -sf http://localhost:8080/api/sources/fred`
  - Result: returned source context for `FRED` plus only `INT.US.FEDFUNDS` and `ENERGY.US.GASREGW`
  - `curl -s -o /tmp/source-404.json -w '%{http_code}' http://localhost:8080/api/sources/unknown`
  - Result: `404` with `{"error":{"code":"source_not_found",...}}`
- Manual frontend checks against the restarted stack passed:
  - `http://localhost:3000/sources`
  - Result: rendered shell navigation, `Sources` heading, total source count, and links for `EIA` and `FRED`
  - `http://localhost:3000/sources/fred`
  - Result: rendered source header plus only FRED datasets, each linked to existing `/datasets/{id}` routes
  - `http://localhost:3000/sources/unknown`
  - Result: rendered `Source not found` inside the shared shell with a `Back to all sources` link
- Mandatory stop gates passed:
  - `pnpm exec nx run-many -t test --all`
  - Result: passed for `frontend`, `pipeline`, `backend`, and `db`
  - `pnpm exec nx run-many -t coverage --all`
  - Result: passed with `backend` at `91.50%`, `frontend` at `96.40%`, `pipeline` at `90.03%`, and `db` at `99.59%`
- Repo-wide final check passed:
  - `pre-commit run --all-files`
  - Result: all hooks passed, including lint, format, typecheck, test, coverage, duplication, and inline-suppression guard

## Completion Criteria

- Source list and source detail routes are both present and usable.
- Source identity remains stable from source list into source detail and nested dataset entries.
- Empty, not-found, and generic error states are explicit and correct.
- Existing dataset detail navigation continues working from source-owned dataset listings.
- All required automated checks and monorepo stop gates pass.
