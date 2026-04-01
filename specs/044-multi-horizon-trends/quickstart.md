# Quickstart: Current-State Multi-Lookback Trends

## Prerequisites

- Dependencies installed (`pnpm install`, `uv sync --project apps/backend --frozen`, `uv sync --project apps/pipeline --frozen`)
- Local Docker runtime available
- Local secrets configured (`docker/compose/local.secrets.env`)

## 1. Start from a clean local runtime

1. `docker compose down`
2. `docker compose up -d`
3. `docker compose ps`

## 2. Library-first iteration (multi-lookback classification)

1. Red: add failing tests in `libs/trend_analysis/tests/` for lookback applicability and weighted canonical descriptor determinism.
2. Green: implement minimal classifier/model changes in `libs/trend_analysis/src/trend_analysis/`.
3. Refactor while preserving deterministic behavior.
4. Repeat checks:
   - `uv run --project apps/backend ruff check libs/trend_analysis`
   - `PYTHONPATH=libs/trend_analysis/src uv run --project apps/backend ty check libs/trend_analysis`
   - `PYTHONPATH=libs/trend_analysis/src uv run --project apps/backend pytest libs/trend_analysis/tests`

## 3. Database and pipeline integration

1. Add and apply migration for lookback snapshots + canonical descriptor persistence.
2. Update pipeline runtime/repository writes and idempotency behavior.
3. Repeat checks:
   - `uv run --project apps/pipeline ruff check apps/pipeline`
   - `uv run --project apps/pipeline ty check apps/pipeline`
   - `uv run --project apps/pipeline pytest apps/pipeline/tests/orchestration`
4. Manual validation:
   - trigger one ingest path that creates a fresh observation
   - verify per-lookback outcomes and canonical descriptor rows are persisted
   - rerun same observation path and confirm no duplicates

## 4. Backend contract/query integration

1. Update discovery dataset detail contracts for canonical descriptor payload.
2. Replace span-read logic with lookback snapshot + canonical descriptor reads.
3. Repeat checks:
   - `uv run --project apps/backend ruff check apps/backend`
   - `uv run --project apps/backend ty check apps/backend`
   - `uv run --project apps/backend pytest apps/backend/tests`
4. Manual validation:
   - `curl -sS http://127.0.0.1:8090/api/datasets/<DATASET_ID>`
   - confirm payload contains canonical descriptor fields for chip rendering and no required client ranking inputs

## 5. Frontend simplification and chip rendering

1. Remove overlay components from dataset detail render path.
2. Add canonical trend chip under dataset title, driven by API payload only.
3. Repeat checks:
   - `pnpm --dir apps/frontend exec biome check .`
   - `pnpm --dir apps/frontend typecheck`
   - `pnpm --dir apps/frontend test`
4. Manual validation:
   - open dataset detail page
   - confirm no overlay appears
   - confirm chip renders canonical descriptor when available and unavailable state when absent

## 6. Full quality gates (mandatory before commit/handoff)

1. `pre-commit run --all-files`
2. `pnpm exec nx run-many -t test --all`
3. `pnpm exec nx run-many -t coverage --all`

All commands above must pass with no exceptions.
