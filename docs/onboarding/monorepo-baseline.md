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
4. Run backend, pipeline, and frontend quality checks
5. Install PMD and run duplication check

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
