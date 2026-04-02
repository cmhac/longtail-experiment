# Quickstart: Historical As-Of Trend Tooltips

## Prerequisites

- Workspace dependencies installed (`pnpm install`, `uv sync --project apps/backend --frozen`, `uv sync --project apps/pipeline --frozen`)
- Local secrets configured (`docker/compose/local.secrets.env`)
- Docker daemon running

## 1. Start from a clean runtime

1. `docker compose down`
2. `docker compose up -d`
3. `docker compose ps`

## 2. Backend: observation-level as-of trend contract

1. Red: add failing backend tests for observation-level `as_of_trend_descriptor` in detail payloads.
2. Green: extend detail contract models and service assembly to include one descriptor per observation.
3. Add deterministic tie-break tests and mixed-availability tests.
4. Run backend quality checks:
   - `uv run --project apps/backend ruff check apps/backend`
   - `uv run --project apps/backend ty check apps/backend`
   - `uv run --project apps/backend pytest apps/backend/tests`

## 3. Manual API validation

1. Query dataset detail payload:
   - `curl -sS http://127.0.0.1:8090/api/datasets/<DATASET_ID>`
2. Validate:
   - each item in `observations` includes `as_of_trend_descriptor`
   - observations with no match show `descriptor_state: unavailable`
   - top-level `canonical_trend_descriptor` and `lookback_trend_snapshots` still exist

## 4. Frontend: tooltip trend indicator chip

1. Red: add failing Vitest coverage for tooltip chip rendering from observation as-of descriptor.
2. Green: extend API types and tooltip chart point model; render shared `DatasetTrendIndicator` chip at tooltip bottom.
3. Validate no regressions to existing value/movement tooltip text.
4. Run frontend quality checks:
   - `pnpm --dir apps/frontend exec biome check .`
   - `pnpm --dir apps/frontend typecheck`
   - `pnpm --dir apps/frontend test`

## 5. Manual browser validation

1. Open a dataset detail page with trend history.
2. Hover multiple points in the observations chart.
3. Confirm each tooltip shows:
   - value/movement content as before
   - one trend chip at the bottom
   - per-observation chip updates (not fixed to latest dataset trend)
4. Confirm unavailable observations render explicit unavailable chip state.

## 6. Mandatory full-suite stop gates

1. `pre-commit run --all-files`
2. `pnpm exec nx run-many -t test --all`
3. `pnpm exec nx run-many -t coverage --all`

All commands must pass before commit or handoff.
