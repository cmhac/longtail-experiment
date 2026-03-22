# Source-Asset Scheduling Cutover Runbook

## Overview

This runbook documents the hard cutover from a shared hourly ingest schedule to per-source asset cadence ownership. After cutover, each source asset owns its own Dagster schedule definition and no shared all-source schedule remains active.

## Pre-Cutover Checklist

1. Verify all active source assets have per-source schedule definitions registered.
2. Confirm shared `ingest_schedule` is removed from Dagster definitions.
3. Run orchestration test suite: `uv run --project apps/pipeline pytest apps/pipeline/tests/orchestration`
4. Verify local Dagit shows per-source schedules: `bash tools/quality/local-stack/test-dagit-endpoint.sh`

## Cutover Steps

1. Apply migration `0005_source_asset_schedule_cutover` to rationalize legacy schedule tables.
2. Verify migration: `bash tools/quality/local-stack/check-db-revision.sh`
3. Restart orchestration services.
4. Verify per-source schedules in Dagit catalog.

## Post-Cutover Verification

1. Confirm no shared `ingest_schedule` appears in Dagster definitions.
2. Confirm each source asset has an independent schedule entry.
3. Run: `uv run --project apps/pipeline pytest apps/pipeline/tests/orchestration/test_definitions_smoke.py`
4. Run: `uv run --project apps/pipeline pytest apps/pipeline/tests/orchestration/test_ingest_job_runtime.py`

## Legacy Artifact Interpretation

- `source_schedule_policies` and `source_eligibility_snapshots` tables retain historical data.
- Post-cutover, these tables are historical-only and do not influence active scheduling.
- Legacy cadence policy reads are removed from the scheduled execution path.

## Rollback

- This is a hard cutover with no active rollback path to shared scheduling.
- If issues arise, address them within the per-source scheduling model.
