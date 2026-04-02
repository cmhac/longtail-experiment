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

## 7. US1 Validation Log (2026-03-31)

### T036 Red/Green checkpoints

- Red (expected failing import/module stage):
  - `PYTHONPATH=libs/trend_analysis/src uv run --project apps/backend pytest libs/trend_analysis/tests/test_deterministic_outputs.py libs/trend_analysis/tests/test_terminal_outcomes.py libs/trend_analysis/tests/test_cadence_and_failures.py`
  - `uv run --project apps/pipeline pytest apps/pipeline/tests/orchestration/test_trend_transition_logic.py`
- Green (after implementation):
  - `PYTHONPATH=libs/trend_analysis/src uv run --project apps/backend pytest -q libs/trend_analysis/tests/test_deterministic_outputs.py libs/trend_analysis/tests/test_terminal_outcomes.py libs/trend_analysis/tests/test_cadence_and_failures.py libs/trend_analysis/tests/test_real_series_behavior.py libs/trend_analysis/tests/test_multi_horizon_behavior.py`
  - `uv run --project apps/pipeline pytest --no-cov apps/pipeline/tests/orchestration/test_trend_transition_logic.py apps/pipeline/tests/orchestration/test_trend_asset_noop_outcomes.py apps/pipeline/tests/orchestration/test_trend_asset_retry_idempotency.py apps/pipeline/tests/orchestration/test_trend_asset_failure_scope.py apps/pipeline/tests/orchestration/test_trend_signature.py apps/pipeline/tests/orchestration/test_trend_backfill_service.py apps/pipeline/tests/orchestration/test_trend_processing_asset.py`

### T037 Repeated quality checks

- Focused iterations:
  - `uv run --project apps/backend ruff check ...`
  - `uv run --project apps/pipeline ruff check ...`
  - `PYTHONPATH=libs/trend_analysis/src uv run --project apps/backend ty check libs/trend_analysis`
  - `uv run --project apps/pipeline ty check ...`
- Mandatory full gate:
  - `pre-commit run --all-files`
  - Result: pass for lint, format, typecheck, test, coverage, duplication, suppression checks.

### T038 Manual local-stack validation

- Clean restart:
  - `docker compose down`
  - `docker compose up -d`
  - `docker compose ps`
- One-off runtime validation:
  - `PYTHONPATH=apps/pipeline uv run --project apps/pipeline python -c "...TrendProcessingError..."`
  - Observed output: `failure trend_processing_failed` (confirms branch-scoped trend failure mapping).

## 8. US2 Validation Log (2026-04-01)

### T051 Red/Green checkpoints

- Red (new trend-aware tests fail before implementation):
  - `uv run --project apps/backend pytest --no-cov apps/backend/tests/contract/test_recent_updates_trend_contract.py apps/backend/tests/contract/test_dataset_detail_trend_spans_contract.py apps/backend/tests/contract/test_dataset_detail_trend_payload_error_contract.py apps/backend/tests/integration/test_recent_updates_trend_ordering.py apps/backend/tests/integration/test_dataset_detail_trend_normalization.py`
- Green (after implementation in service/mapper/repository):
  - `uv run --project apps/backend pytest --no-cov apps/backend/tests/contract/test_dataset_discovery_persisted_repository_contract.py apps/backend/tests/contract/test_discovery_trend_contract_schema.py apps/backend/tests/contract/test_recent_updates_trend_contract.py apps/backend/tests/contract/test_dataset_detail_trend_spans_contract.py apps/backend/tests/contract/test_dataset_detail_trend_payload_error_contract.py apps/backend/tests/integration/test_recent_updates_trend_ordering.py apps/backend/tests/integration/test_dataset_detail_trend_normalization.py`
  - Result: `17 passed`.

### T052 Repeated backend quality checks

- Focused checks during iteration:
  - `uv run --project apps/backend ruff check ...`
  - `uv run --project apps/backend ty check ...`
  - `uv run --project apps/backend pytest --no-cov ...`
- Mandatory full gate:
  - `pre-commit run --all-files`
  - Result: pass for lint, format, typecheck, test, coverage, duplication, suppression checks.

### T053 Manual API verification

- Clean runtime restart:
  - `docker compose down`
  - `docker compose up -d db dagster_db backend`
  - `docker compose ps`
- Manual API session (trend migration head override for local script run):
  - `PYTHONPATH=apps/backend DISCOVERY_EXPECTED_DB_REVISION=0011_trend_lifecycle_tables uv run --project apps/backend python apps/backend/src/http_api_server.py --host 127.0.0.1 --port 8090`
- Endpoint checks:
  - `curl -sS http://127.0.0.1:8090/api/health`
  - `curl -sS 'http://127.0.0.1:8090/api/datasets/recent?limit=5'`
  - Seeded one trend row in Postgres for validation, then re-queried recent feed.
  - `curl -sS 'http://127.0.0.1:8090/api/datasets/ENERGY.US.RETAIL_GASOLINE.SWA'`
- Observed outputs:
  - Recent feed includes interleaved `trend_event` item with `start_period`, `latest_update_at`, and action links.
  - Dataset detail payload includes `trend_spans` with normalized `start_period`/`end_period`, `direction`, `trend_label`, and tooltip `{headline, detail}`.

## 9. US3 Validation Log (2026-04-01)

### T069 Red/Green checkpoints

- Red (new frontend trend tests before implementation):
  - `pnpm --dir apps/frontend test -- --run tests/components/TrendFeedItem.test.tsx tests/components/TrendOverlayLayer.test.tsx tests/components/TrendTooltipController.test.tsx tests/components/TrendOverlayInteractions.test.tsx tests/components/TrendDirectionAccessibility.test.tsx tests/app/dataset-detail-trend-error-state.test.tsx`
- Green (after implementation):
  - `pnpm --dir apps/frontend test -- --run tests/components/TrendFeedItem.test.tsx tests/components/TrendOverlayLayer.test.tsx tests/components/TrendTooltipController.test.tsx tests/components/TrendOverlayInteractions.test.tsx tests/components/TrendDirectionAccessibility.test.tsx tests/app/dataset-detail-trend-error-state.test.tsx tests/navbar-interactions.test.tsx tests/RecentUpdatesFeed.test.tsx tests/detail-page.test.tsx tests/discovery-client.test.ts`
  - Result: `10 passed`, `39 passed` tests.

### T070 Repeated frontend quality checks

- Focused checks during implementation:
  - `pnpm --dir apps/frontend exec biome check ...`
  - `pnpm --dir apps/frontend typecheck`
  - `pnpm --dir apps/frontend test -- --run ...`
- Monorepo quality gate:
  - `pre-commit run --all-files`

### T071 Manual desktop + touch validation

- Runtime setup:
  - `docker compose up -d backend frontend`
  - `docker compose ps backend frontend`
- Desktop verification (`http://127.0.0.1:3000`):
  - Home feed shows interleaved `trend_event` item at top with trend metadata and dataset-detail link.
  - Top nav includes `Home`, `Sources`, `Datasets` and no `Trends` tab.
  - Dataset detail page renders trend overlay span and tooltip.
- Touch-viewport verification (390x844):
  - Set mobile viewport and tap trend span.
  - Tooltip pins on tap and closes on outside tap.

## 10. Phase 6 Final Validation Log (2026-04-01)

### T076 Full pre-commit gate

- `pre-commit run --all-files`
- Result: all hooks passed (`lint`, `format`, `typecheck`, `test`, `coverage`, duplication, suppression).

### T077 Monorepo full test stop gate

- `pnpm exec nx run-many -t test --all`
- Result: success across 5 projects (`frontend`, `backend`, `pipeline`, `trend-analysis`, `db`).

### T078 Monorepo full coverage stop gate

- `pnpm exec nx run-many -t coverage --all`
- Result: success across 5 projects (`frontend`, `backend`, `pipeline`, `trend-analysis`, `db`).

### T079 End-to-end manual stack validation (ingestion -> API -> UI)

- Ingestion/pipeline validation (US1 log):
  - One-off trend processing runtime check confirmed branch-scoped trend failure mapping (`trend_processing_failed`) without collapsing unrelated flow.
- API validation (US2 log):
  - Seeded trend lifecycle row in local Postgres.
  - Verified `/api/datasets/recent?limit=5` includes interleaved `trend_event` item.
  - Verified `/api/datasets/{datasetId}` includes normalized `trend_spans` with tooltip payload.
- UI validation (US3 log):
  - Home page feed rendered trend event and linked to default dataset detail route.
  - Dataset detail chart rendered trend overlay region with hover tooltip (desktop).
  - Touch viewport tap-to-pin and outside-tap dismiss behavior confirmed.
