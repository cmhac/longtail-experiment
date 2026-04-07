# Quickstart: Trend Analysis Upgrade (Spec 050)

## Prerequisites

- Workspace dependencies installed:
  - `pnpm install`
  - `uv sync --project apps/backend --frozen`
  - `uv sync --project apps/pipeline --frozen`
- Local secrets available in `docker/compose/local.secrets.env`
- Docker daemon running

## 1. Clean local runtime restart

1. `docker compose down`
2. `docker compose up -d`
3. `docker compose ps`

## 2. Red/green for trend-analysis library upgrades

1. Add failing tests for:
   - Theil-Sen slope-based lookback scoring
   - Kendall tau confidence modifier behavior
   - EWMA default preprocessing metadata
   - cadence-aware STL/MSTL routing and fallback behavior
   - irregular cadence rejection precedence
2. Implement selected tools and scoring/arbitration logic.
3. Run library-focused checks (project-specific command variants as applicable):
   - `uv run --project apps/pipeline pytest apps/pipeline/tests/orchestration`
   - `PYTHONPATH=libs/trend_analysis/src uv run --project libs/trend_analysis pytest libs/trend_analysis/tests`

## 3. Persistence and pipeline propagation

1. Add failing repository/runtime tests for versioned descriptor/snapshot fields and event eligibility semantics.
2. Implement DB model/repository/pipeline runtime updates.
3. Ensure transition processing remains directional-only (`up <-> down`) with `flat` non-event behavior.
4. Run checks:
   - `uv run --project apps/pipeline ruff check apps/pipeline`
   - `uv run --project apps/pipeline ty check apps/pipeline`
   - `uv run --project apps/pipeline pytest apps/pipeline/tests/orchestration`

## 4. Backend contract and endpoint propagation

1. Add failing contract/service/http tests for versioned descriptor payload semantics.
2. Implement detail/as-of evidence payload exposure and summary canonical-only behavior.
3. Validate unavailable descriptor shape for cadence rejection.
4. Run checks:
   - `uv run --project apps/backend ruff check apps/backend`
   - `uv run --project apps/backend ty check apps/backend`
   - `uv run --project apps/backend pytest apps/backend/tests`

## 5. Frontend contract-consumption updates

1. Add failing tests for:
   - canonical chip state handling with `flat` and unavailable states
   - detail/as-of evidence rendering in secondary expandable sections
   - numeric confidence formatting behavior
2. Implement API type/normalizer and UI updates while preserving primary indicator UX.
3. Run checks:
   - `pnpm --dir apps/frontend exec biome check .`
   - `pnpm --dir apps/frontend typecheck`
   - `pnpm --dir apps/frontend test`

## 6. Manual runtime verification

1. Keep local stack running from clean restart.
2. Execute pipeline processing on representative datasets (noisy, smooth, irregular cadence, sub-daily).
3. Verify backend detail/as-of payloads include evidence and OLS diagnostics; summary remains canonical-only.
4. Verify canonical behavior:
   - explicit `flat` outcomes when no meaningful movement
   - unavailable descriptor with `reason_code=cadence_irregular_rejected` for rejected cadence
5. Verify event behavior:
   - emit exactly once for `up <-> down`
   - do not emit for transitions involving `flat`.
6. Verify frontend consistency across list/detail/notification surfaces for same as-of point.

## 7. Mandatory quality stop gates

1. `pre-commit run --all-files`
2. `pnpm exec nx run-many -t test --all`
3. `pnpm exec nx run-many -t coverage --all`

All commands must pass before commit or handoff.

## 8. Tooling policy guardrail

- Statistical implementation must use selected and recent tools only:
  - `scipy.stats.theilslopes`
  - `scipy.stats.kendalltau`
  - `pandas.Series.ewm`
  - `statsmodels` STL/MSTL and OLS diagnostics
  - `ruptures`
- Do not introduce excluded stale packages:
  - `pymannkendall`, `mannkendall`, `kats`

## 9. Hard cutover reset validation

Use the local reset validator to enforce the v2-only baseline and verify that
post-reset trend/notification rows are generated after reset time only.

```bash
bash tools/verification/spec050_trend_v2_reset_validation.sh
```

Optional custom ingest command:

```bash
SPEC050_RESET_INGEST_COMMAND="<your ingest command>" bash tools/verification/spec050_trend_v2_reset_validation.sh
```

Reference runbook: `docs/runbooks/trend-descriptor-v2-cutover.md`.

## 10. Phase 6 output artifacts

- Replay outcomes: `specs/050-trend-analysis-update/research/replay_comparison_results.md`
- Manual verification log: `specs/050-trend-analysis-update/research/manual_verification_log.md`
- Quality gate log: `specs/050-trend-analysis-update/research/quality_gate_results.md`
- Daily seasonal-adjustment phase gate: `specs/050-trend-analysis-update/research/daily-seasonal-adjustment-phase-gate.md`
