# Quickstart: FRED Interest Rate Source

**Feature**: 008-add-fred-source  
**Goal**: Run first real-world source ingestion using local credentials, verify persistence, and validate incremental behavior.

## Prerequisites

1. Local stack is running:
   - docker compose up -d
2. Pipeline dependencies are synced:
   - uv sync --project apps/pipeline --frozen
3. Shared DB migrations are current:
   - bash tools/quality/local-stack/run-db-migrations.sh
4. Local secret file exists with provider key:
   - docker/compose/local.secrets.env

## Step 1: Configure local credential

1. Create local secret file if missing by copying the example template.
2. Set `FRED_API_KEY` in `docker/compose/local.secrets.env`.
3. Confirm the key is not printed in logs or committed to git history.

## Step 2: Verify migration/revision state

1. Run:
   - bash tools/quality/local-stack/check-db-revision.sh
2. Confirm the expected migration revision includes observation-store support for this feature.

## Step 3: Run first on-demand ingest

1. Execute ingest job with on-demand trigger and request metadata.
2. Confirm run summary reports successful execution for `fred_fedfunds`.
3. Confirm accepted observation count is greater than zero.

## Step 4: Verify persisted observations

Run SQL query in local DB:

```sql
SELECT ds.series_key, o.observed_on, o.value, o.reported_at
FROM observations o
JOIN data_series ds ON ds.id = o.series_id
WHERE ds.series_key = 'INT.US.FEDFUNDS'
ORDER BY o.observed_on DESC
LIMIT 20;
```

Expected:

1. At least one row exists.
2. `observed_on` values are valid dates.
3. `value` is numeric.

## Step 5: Verify incremental no-duplicate behavior

1. Run the same ingest workflow again immediately.
2. Compare observation row counts for the same date window before and after second run.
3. Confirm no duplicate `(series_key, observed_on)` rows are created.

## Step 6: Failure-path verification

1. Temporarily clear `FRED_API_KEY` in local secret file.
2. Run ingest job again.
3. Confirm source outcome is failure with explicit credential error reason.
4. Restore key and rerun to confirm recovery.

## Troubleshooting

1. If source fails with credential error:
   - verify `FRED_API_KEY` exists and is non-empty in local secret env file.
2. If source fails with provider/network error:
   - verify internet connectivity and provider endpoint availability.
3. If run succeeds but rows are missing:
   - confirm observation-store migration is applied and runtime is wired to durable repository.
4. If duplicate rows appear:
   - verify unique key/upsert behavior for `(series_key, observed_on)` in observation persistence path.

## Quality Gate Commands

1. Pipeline lint/type/tests:
   - uv run --project apps/pipeline ruff check apps/pipeline
   - uv run --project apps/pipeline ty check apps/pipeline
   - uv run --project apps/pipeline pytest apps/pipeline/tests
2. DB migration tests:
   - uv run --project apps/pipeline pytest libs/db/tests/test_ingestion_runtime_migrations.py
3. Affected quality suite:
   - pnpm run affected:test
   - pnpm run affected:coverage

## Verified Execution Snapshot (2026-03-22)

Commands run and verified during implementation:

1. Migration and revision checks:
   - `bash tools/quality/local-stack/run-db-migrations.sh`
   - `bash tools/quality/local-stack/check-db-revision.sh`
   - Observed: `Revision OK: 0004_observation_store`
2. Full pipeline quality gate:
   - `uv run --project apps/pipeline ruff check apps/pipeline`
   - `uv run --project apps/pipeline ty check apps/pipeline`
   - `uv run --project apps/pipeline pytest apps/pipeline/tests`
   - Observed: `All checks passed!` (ruff), `All checks passed!` (ty), `97 passed, 1 skipped`, `Total coverage: 93.44%`
3. Real two-run on-demand ingest with local `FRED_API_KEY`:
   - Executed ingest job twice via `defs.get_job_def("ingest_job").execute_in_process(...)`
   - Observed outputs:
     - `FIRST_RUN_SUCCESS True`
     - `SECOND_RUN_SUCCESS True`
     - `FIRST_FRED_STATE success`
     - `SECOND_FRED_STATE success`
     - `FIRST_FRED_ACCEPTED 860`
     - `SECOND_FRED_ACCEPTED 1`
     - `FIRST_TOTAL_ROWS 860`
     - `SECOND_TOTAL_ROWS 860`
     - `ROW_COUNT_DELTA 0`
     - `LATEST_OBSERVED_ON 2026-02-01`
     - `LATEST_VALUE 3.64000000`
