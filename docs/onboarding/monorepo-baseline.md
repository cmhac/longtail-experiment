# Monorepo Baseline Onboarding

## Required Tools

- Node.js 22 LTS
- pnpm
- Python 3.12
- uv
- Docker

## Initial Setup

1. pnpm install
2. uv sync --project apps/backend --frozen
3. uv sync --project apps/pipeline --frozen
4. Start local stack: docker compose up -d
5. Verify local DB bootstrap: bash tools/quality/local-stack/test-local-db-bootstrap.sh
6. Run backend, pipeline, and frontend quality checks
7. Install PMD and run duplication check

## Development-only Warning

- Local DB commands and scripts in this repository are for development environments only.
- Do not run local-stack reset/bootstrap workflows against shared, staging, or production databases.

## Quality Command Matrix

- Backend lint: uv run --project apps/backend ruff check apps/backend
- Backend format: uv run --project apps/backend ruff format --check apps/backend
- Backend typecheck: uv run --project apps/backend ty check apps/backend
- Backend test: uv run --project apps/backend pytest apps/backend/tests
- Pipeline lint: uv run --project apps/pipeline ruff check apps/pipeline
- Pipeline format: uv run --project apps/pipeline ruff format --check apps/pipeline
- Pipeline typecheck: uv run --project apps/pipeline ty check apps/pipeline
- Pipeline test: uv run --project apps/pipeline pytest apps/pipeline/tests
- Frontend lint: pnpm --dir apps/frontend lint
- Frontend format: pnpm --dir apps/frontend exec biome check .
- Frontend typecheck: pnpm --dir apps/frontend typecheck
- Frontend test: pnpm --dir apps/frontend test
- Duplication: bash tools/quality/cpd/run-cpd.sh

## Local DB Migration Commands (Development-only)

- Bootstrap DB service: bash tools/quality/local-stack/test-local-db-bootstrap.sh
- Apply migrations: bash tools/quality/local-stack/run-db-migrations.sh
- Verify current revision: bash tools/quality/local-stack/check-db-revision.sh
- Full readiness verification: bash tools/quality/local-stack/test-db-readiness.sh

## Local Dagit Commands (Feature 009)

- Start Dagit compose service: docker compose up -d dagit
- View Dagit logs: docker compose logs dagit
- Stop Dagit compose service: docker compose stop dagit
- Start local Dagit UI: bash tools/quality/local-stack/start-dagit-local.sh
- Verify Dagit endpoint/workspace: bash tools/quality/local-stack/test-dagit-endpoint.sh
- Stop local Dagit UI: bash tools/quality/local-stack/stop-dagit-local.sh
- Run compose stack with Dagit endpoint verification: VERIFY_DAGIT_ENDPOINT=1 bash tools/quality/local-stack/test-compose-stack.sh

## Affected-only Checks

- pnpm run affected:lint
- pnpm run affected:format
- pnpm run affected:typecheck
- pnpm run affected:test
- pnpm run affected:coverage
- pnpm run affected:duplication

## Contract Verification Commands

- Pipeline contract tests: uv run --project apps/pipeline pytest apps/pipeline/tests/contract
- Backend contract tests: uv run --project apps/backend pytest apps/backend/tests/contract
- Shared DB model tests: PYTHONPATH=libs/db/src uv run --project apps/backend pytest libs/db/tests
- US1-US3 targeted pipeline checks: PYTHONPATH=libs/db/src uv run --project apps/pipeline pytest apps/pipeline/tests/contract/test_canonical_schema_validation.py apps/pipeline/tests/contract/test_ingest_frequency_handling.py apps/pipeline/tests/contract/test_provenance_immutability.py apps/pipeline/tests/contract/test_revision_lineage.py apps/pipeline/tests/contract/test_taxonomy_hierarchy_validation.py apps/pipeline/tests/contract/test_geography_hierarchy_validation.py
- US1-US3 targeted backend checks: PYTHONPATH=libs/db/src uv run --project apps/backend pytest apps/backend/tests/contract/test_canonical_observation_reads.py apps/backend/tests/contract/test_provenance_audit_queries.py apps/backend/tests/contract/test_hierarchy_filter_queries.py

## Ingestion Operations Guide

- Run orchestration test bundle: uv run --project apps/pipeline pytest apps/pipeline/tests/orchestration
- Validate scheduled trigger mode: uv run --project apps/pipeline pytest apps/pipeline/tests/orchestration/test_trigger_modes.py -k scheduled
- Validate on-demand trigger mode: uv run --project apps/pipeline pytest apps/pipeline/tests/orchestration/test_trigger_modes.py -k ondemand
- Validate queue and partial-success behavior: uv run --project apps/pipeline pytest apps/pipeline/tests/orchestration/test_partial_success_status.py apps/pipeline/tests/orchestration/test_source_queue_policy.py

## Per-Source Schedule Ownership (Feature 011)

- After cutover, each source asset owns its own Dagster schedule definition.
- No shared all-source schedule remains active in runtime.
- Validate per-source schedule registration: `uv run --project apps/pipeline pytest apps/pipeline/tests/orchestration/test_definitions_smoke.py`
- Validate source cadence selection: `uv run --project apps/pipeline pytest apps/pipeline/tests/orchestration/test_source_cadence_selection.py`
- Validate trigger attribution: `uv run --project apps/pipeline pytest apps/pipeline/tests/orchestration/test_trigger_modes.py`

## Multi-Series Adapter Onboarding (Feature 012)

- Use stable keys:
  - `provider_group_key`: provider grouping identity.
  - `series_item_key`: operator-facing series trigger identity.
  - `canonical_series_key`: persistence identity used by observation storage.
- Default ownership mode is grouped when cadence requirements are shared.
- Split ownership is allowed when cadence or operational isolation needs diverge.
- Manual trigger expectations:
  - Series-level trigger should execute only the selected series item.
  - Grouped scheduled runs may execute multiple series items under one provider group.
- Escalation workflow:
  - If grouped/split coexistence causes duplicate scheduling, escalate to pipeline owner and attach trigger-attribution evidence from orchestration tests.
  - If ownership transitions lose traceability, escalate with run_id, series_item_key, and persistence evidence.

## Source Schedule Metadata Maintenance (Feature 006)

- Keep source cadence metadata with each `SourceWorkflowRegistration` entry in orchestration runtime wiring.
- Validate cadence policy updates with `nx run pipeline:test:orchestration:cadence` before merging.
- Validate bounded parallel ingestion behavior with `nx run pipeline:test:orchestration:parallel` when changing concurrency settings.

## Source-Asset Migration Validation (Feature 010)

- Validate source discovery determinism and contract guards:
  `uv run --project apps/pipeline pytest apps/pipeline/tests/orchestration/test_source_asset_discovery.py apps/pipeline/tests/orchestration/test_source_asset_contract_validation.py`
- Validate single-source trigger and invalid-key rejection:
  `uv run --project apps/pipeline pytest apps/pipeline/tests/orchestration/test_single_source_trigger_runtime.py`
- Validate source-level outcome visibility and persistence:
  `uv run --project apps/pipeline pytest apps/pipeline/tests/orchestration/test_source_outcome_visibility.py apps/pipeline/tests/orchestration/test_source_outcome_persistence_post_cutover.py`
- Validate Dagster-only authority and partial-failure recovery path:
  `uv run --project apps/pipeline pytest apps/pipeline/tests/orchestration/test_scheduler_runtime.py apps/pipeline/tests/orchestration/test_cutover_partial_failure_behavior.py`
