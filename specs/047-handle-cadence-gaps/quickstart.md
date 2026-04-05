# Quickstart: Gap-Tolerant Cadence Inference

## Prerequisites

- Workspace dependencies installed (`pnpm install`, `uv sync --project apps/backend --frozen`, `uv sync --project apps/pipeline --frozen`)
- Local secrets configured in `docker/compose/local.secrets.env`
- Docker daemon running

## 1. Start from a clean local runtime

1. `docker compose down`
2. `docker compose up -d`
3. `docker compose ps`

## 2. Baseline cadence-gap measurement (reference)

1. Run the interval-ratio query for `ENERGY.US.RETAIL_GASOLINE.NUS`.
2. Record baseline values:
   - total intervals
   - irregular intervals
   - irregular ratio
3. Confirm baseline ratio is below the new threshold and use this as the acceptance reference.

Reference SQL (PostgreSQL):

```sql
WITH ordered AS (
  SELECT
    observed_on,
    LAG(observed_on) OVER (ORDER BY observed_on) AS prev_observed_on
  FROM observations
  WHERE series_key = 'ENERGY.US.RETAIL_GASOLINE.NUS'
), gaps AS (
  SELECT
    (observed_on - prev_observed_on) AS gap_days
  FROM ordered
  WHERE prev_observed_on IS NOT NULL
)
SELECT
  COUNT(*)::int AS total_intervals,
  COUNT(*) FILTER (WHERE gap_days NOT BETWEEN 6 AND 8)::int AS irregular_intervals,
  ROUND(
    (COUNT(*) FILTER (WHERE gap_days NOT BETWEEN 6 AND 8)::numeric / NULLIF(COUNT(*), 0)) * 100,
    4
  ) AS irregular_ratio_percent
FROM gaps;
```

Expected reference output (current baseline):

- `total_intervals = 1852`
- `irregular_intervals = 1`
- `irregular_ratio_percent = 0.0540`
- acceptance threshold: `MAX_IRREGULAR_GAP_RATIO = 0.20%`

## 3. Red/green cadence-policy tests

1. Red: add failing tests in `libs/trend_analysis/tests` for:
   - isolated-gap acceptance under threshold
   - true mixed-spacing rejection over threshold
   - deterministic result consistency on repeated runs
2. Green: update cadence inference policy implementation.
3. Add runtime processor tests in `apps/pipeline/tests/orchestration` validating source outcomes for both accepted-gap and rejected-irregular scenarios.

## 4. Local ingest verification

1. Trigger on-demand ingest run.
2. Validate outcomes:
   - gap-tolerant reference series no longer fails with irregular-spacing cadence error
   - truly irregular fixtures still fail with cadence irregularity
3. Verify series/source outcome metadata includes cadence decision reason context.

## 5. Quality gates (mandatory)

1. `pre-commit run --all-files`
2. `pnpm exec nx run-many -t test --all`
3. `pnpm exec nx run-many -t coverage --all`

All commands must pass before commit or handoff.

## 6. Runtime prerequisites and secrets guidance

- Required secrets (fail-fast if missing):
  - `FRED_API_KEY`
  - `EIA_API_KEY`
- Local secret source for compose services: `docker/compose/local.secrets.env`
- Do not expose provider secrets in logs or checked-in files.
- Before manual runtime validation, always restart from clean compose state:
  1. `docker compose down`
  2. `docker compose up -d`
