# Quickstart: End-to-End Trend Detection

## Prerequisites

- Repository dependencies installed (`pnpm install`, backend/pipeline `uv sync`)
- Local Docker runtime available
- Local stack configuration present (`docker/compose/local.secrets.env`)

## Feature Quality Commands

- `pre-commit run --all-files`
- `pnpm exec nx run trend-analysis:lint`
- `pnpm exec nx run trend-analysis:typecheck`
- `pnpm exec nx run trend-analysis:test`
- `pnpm exec nx run trend-analysis:coverage`

## 1. Start from clean local runtime

1. `docker compose down`
2. `docker compose up -d`
3. `docker compose ps`

## 2. Stage 1 workflow (library first)

1. Red: add/adjust failing trend library tests.
2. Green: implement minimal library behavior to pass.
3. Refactor: clean types/contracts while tests remain green.
4. Run repeated checks while iterating:
   - `pre-commit run --all-files`
   - project-specific pytest/ruff/ty commands.
5. Manual validation:
   - Run one-off trend analysis commands/scripts against local data.
   - Use prototype files as scenario guidance:
     - `specs/043-implement-trend-detection/prototype/spike_real_series_seasonality.py`
     - `specs/043-implement-trend-detection/prototype/spike_multi_horizon.py`

## 3. Stage 2 workflow (pipeline)

1. Red/Green/Refactor for downstream trend asset orchestration, failure scope, and idempotency.
2. Run repeated checks:
   - `pre-commit run --all-files`
   - `uv run --project apps/pipeline pytest apps/pipeline/tests`
3. Manual validation:
   - Execute one-off ingest/trend run in local stack.
   - Verify branch-scoped failures and retry idempotency.

## 4. Stage 3 workflow (backend)

1. Red/Green/Refactor for discovery contract/query changes.
2. Run repeated checks:
   - `pre-commit run --all-files`
   - `uv run --project apps/backend pytest apps/backend/tests`
3. Manual validation:
   - Query recent updates and dataset detail endpoints via curl/httpie.
   - Validate trend ordering and payload semantics.

## 5. Stage 4 workflow (frontend)

1. Red/Green/Refactor for feed + chart overlays + interaction/accessibility behavior.
2. Run repeated checks:
   - `pre-commit run --all-files`
   - `pnpm --dir apps/frontend test`
   - `pnpm --dir apps/frontend exec biome check .`
   - `pnpm --dir apps/frontend typecheck`
3. Manual validation:
   - Open UI in desktop and touch-size viewport.
   - Verify single-tooltip rule, non-overlap rendering, dual encoding, and error-state behavior.

## 6. Mandatory final gates before commit or handoff

1. `pre-commit run --all-files`
2. `pnpm exec nx run-many -t test --all`
3. `pnpm exec nx run-many -t coverage --all`

All three must pass with no exceptions.
