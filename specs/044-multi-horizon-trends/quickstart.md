# Quickstart: Current-State Multi-Lookback Trends

## Prerequisites

- Dependencies installed (`pnpm install`, `uv sync --project apps/backend --frozen`, `uv sync --project apps/pipeline --frozen`)
- Local Docker runtime available
- Local secrets configured (`docker/compose/local.secrets.env`)

## 1. Start from a clean local runtime

1. `docker compose down`
2. `docker compose up -d`
3. `docker compose ps`

## 2. Backend contract and query refinement

1. Red: add failing backend tests for dataset-summary responses carrying `canonical_trend_descriptor`.
2. Green: update shared summary contracts and persisted-query/service projections so catalog/search/metadata/recent dataset updates all return the latest canonical descriptor.
3. Refactor while preserving deterministic unavailable-state behavior.
4. Repeat checks:
   - `uv run --project apps/backend ruff check apps/backend`
   - `uv run --project apps/backend ty check apps/backend`
   - `uv run --project apps/backend pytest apps/backend/tests`
5. Manual validation:
   - `curl -sS http://127.0.0.1:8090/api/datasets?page=1&page_size=5`
   - `curl -sS "http://127.0.0.1:8090/api/datasets/search?q=gasoline"`
   - `curl -sS http://127.0.0.1:8090/api/datasets/recent`
   - confirm each dataset-summary item includes `canonical_trend_descriptor`, including explicit unavailable states where applicable

## 3. Dataset detail payload verification

1. Red: add or update backend tests that lock the detail payload shape for the shared canonical descriptor and lookback snapshots.
2. Green: keep dataset-detail assembly aligned with the shared canonical descriptor contract.
3. Repeat checks:
   - `uv run --project apps/backend pytest apps/backend/tests/contract`
4. Manual validation:
   - `curl -sS http://127.0.0.1:8090/api/datasets/<DATASET_ID>`
   - confirm the response still includes `canonical_trend_descriptor` plus `lookback_trend_snapshots`

## 4. Frontend shared indicator integration

1. Red: add failing frontend tests for:
   - strong up
   - mild up
   - mild down
   - strong down
   - unavailable state
   - row placement
   - detail-heading placement
2. Green: implement one shared trend-indicator component and wire it into shared dataset rows plus the dataset-detail `Historical Trend` heading.
3. Refactor duplicated mapper/view-model logic into shared component helpers only if tests remain green.
4. Repeat checks:
   - `pnpm --dir apps/frontend exec biome check .`
   - `pnpm --dir apps/frontend typecheck`
   - `pnpm --dir apps/frontend test`
5. Manual validation:
   - open homepage recent updates
   - open dataset catalog/search-style list surfaces
   - open one dataset detail page
   - confirm the arrow indicator appears at the far right of dataset rows and adjacent to `Historical Trend`
   - confirm the detail page still shows no overlay

## 5. Responsive and unavailable-state checks

1. Resize to narrow/mobile widths and verify the list-row indicator remains visible and aligned without breaking row content.
2. Verify datasets with unavailable canonical descriptors render a consistent unavailable indicator state on list and detail surfaces.
3. Verify no list or detail rendering path computes trend strength/direction from lookback snapshots on the client.

## 6. Full quality gates (mandatory before commit/handoff)

1. `pre-commit run --all-files`
2. `pnpm exec nx run-many -t test --all`
3. `pnpm exec nx run-many -t coverage --all`

All commands above must pass with no exceptions.
