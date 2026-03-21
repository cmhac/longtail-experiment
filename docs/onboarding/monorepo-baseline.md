# Monorepo Baseline Onboarding

## Required Tools

- Node.js 22 LTS
- pnpm
- Python 3.12
- uv
- Docker

## Initial Setup

1. pnpm install
2. uv sync --frozen
3. Run backend and frontend quality checks
4. Install PMD and run duplication check

## Quality Command Matrix

- Backend lint: uv run --project apps/backend ruff check apps/backend
- Backend format: uv run --project apps/backend ruff format --check apps/backend
- Backend typecheck: uv run --project apps/backend ty check apps/backend
- Backend test: uv run --project apps/backend pytest apps/backend/tests
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
