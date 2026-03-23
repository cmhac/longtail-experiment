# Quickstart: Multi-Series Source Adapter Model

## Objective

Validate grouped multi-series ingestion, independent series triggering, and grouped/split ownership coexistence in the local stack.

## Prerequisites

- Repository dependencies installed.
- Local Postgres and orchestration services available via Docker Compose.
- Feature branch checked out.

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
