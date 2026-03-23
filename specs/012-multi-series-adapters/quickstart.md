# Quickstart: Multi-Series Source Adapter Model

## Objective

Validate grouped multi-series ingestion, independent series triggering, and grouped/split ownership coexistence in the local stack.

## Prerequisites

- Repository dependencies installed.
- Local Postgres and orchestration services available via Docker Compose.
- Feature branch checked out.

## Feature Command Aliases

- `pnpm exec nx run pipeline:test:orchestration:multi-series`
- `pnpm exec nx run pipeline:verify:multi-series`

## 1) Run targeted orchestration tests

```bash
uv run --project apps/pipeline pytest apps/pipeline/tests/orchestration/test_fred_source_workflow.py
uv run --project apps/pipeline pytest apps/pipeline/tests/orchestration/test_trigger_modes.py
uv run --project apps/pipeline pytest apps/pipeline/tests/orchestration/test_definitions_smoke.py
uv run --project apps/pipeline pytest apps/pipeline/tests/orchestration/test_ingest_job_runtime.py
```

Expected:

- Grouped adapter scenarios pass for multiple series.
- Series-targeted trigger scenarios pass with isolated execution behavior.

## 2) Run affected quality gates

```bash
pnpm run affected:lint
pnpm run affected:format
pnpm run affected:typecheck
pnpm run affected:test
pnpm run affected:coverage
```

Expected:

- All affected targets pass without suppressions.
- Coverage remains at or above repository thresholds.

## 3) Validate local-stack orchestration behavior

```bash
bash tools/quality/local-stack/test-compose-stack.sh
bash tools/quality/local-stack/test-dagit-endpoint.sh
```

Expected:

- Dagit workspace loads and exposes series-level items.
- Scheduled and on-demand trigger attribution is visible.

## 4) Verify grouped and split coexistence workflow

Validation checklist:

- One provider group runs with multiple series under grouped ownership.
- One selected series triggers independently.
- A split-owned series path remains isolated.
- No duplicate scheduled execution is observed in the same cadence window.

## 5) Documentation updates

Ensure these documents reflect final behavior:

- docs/runbooks/local-stack-baseline.md
- docs/onboarding/monorepo-baseline.md
- docs/architecture/monorepo-boundaries.md
- AGENTS.md

## 6) Release-readiness evidence

Capture evidence for:

- Grouped multi-series success.
- Independent series triggering.
- Ownership attribution clarity.
- Grouped/split coexistence with zero duplicate scheduled triggers.

## 7) Execution Evidence (2026-03-22)

Feature verification and affected gates were executed after implementation and migration fixes.

Command evidence:

- `pnpm exec nx run pipeline:verify:multi-series`
  - Result: `38 passed, 1 skipped in 1.76s`
- `pnpm run affected:lint`
  - Result: passed
- `pnpm run affected:format`
  - Result: passed
- `pnpm run affected:typecheck`
  - Result: passed
- `pnpm run affected:test`
  - Result: passed
- `pnpm run affected:coverage`
  - Result: passed
- `pnpm run affected:duplication`
  - Result: passed

Local-stack and Dagit evidence:

- `bash tools/quality/local-stack/test-db-readiness.sh`
  - Result: local DB healthy
- `bash tools/quality/local-stack/run-db-migrations.sh`
  - Result: migrated to `0006_series_ownership_transition`
- `bash tools/quality/local-stack/check-db-revision.sh`
  - Result: `Revision OK: 0006_series_ownership_transition`
- `bash tools/quality/local-stack/start-dagit-local.sh`
  - Result: `DAGIT_START_STATUS=ready`, `DAGIT_ENDPOINT=http://127.0.0.1:3001`
- `bash tools/quality/local-stack/test-dagit-endpoint.sh`
  - Result: `DAGIT_HEALTH_STATUS=ready`, `DAGIT_LOCATION_ENTRIES=1`, `DAGIT_SCHEDULE_MODEL=per_source`

SC-002 metric:

- Target: operators trigger an individual series without unrelated execution in >=95% targeted runs.
- Measured: 100% pass rate across series-targeted orchestration validation suite (`pipeline:verify:multi-series` passed).

SC-003 metric:

- Target: 100% unambiguous ownership attribution with zero duplicate schedule triggers under grouped/split coexistence.
- Measured: 100% pass rate in grouped/split coexistence and ownership-transition validation tests, with Dagit workspace and schedule model checks passing.
