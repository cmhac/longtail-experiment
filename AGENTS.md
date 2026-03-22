# longtail-experiment Development Guidelines

Auto-generated from all feature plans. Last updated: 2026-03-21

## Active Technologies
- Python 3.12 (pipeline/backend/shared DB), TypeScript 5.x unchanged + Dagster 1.x, Pydantic 2.x, SQLAlchemy 2.x, Alembic, psycopg 3.x, Nx tooling (006-parallel-source-scheduling)
- PostgreSQL 16 local runtime DB persisted via `ingestion_runs` and `source_run_outcomes` tables (006-parallel-source-scheduling)

- Python 3.12 (pipeline and shared DB), TypeScript 5.x unchanged + Dagster 1.x, Pydantic 2.x, SQLAlchemy 2.x, Alembic, psycopg 3.x, structlog, OpenTelemetry API/SDK, Nx workspace tooling (005-dagster-ingest-pipeline)
- PostgreSQL 16 local dev database with relational time-series persistence and migration authority under `libs/db/alembic` (005-dagster-ingest-pipeline)

- Python 3.12 (backend and pipeline tooling), shell scripts for local verification + Docker Compose, PostgreSQL 16 image for local DB service, SQLAlchemy 2.x, Alembic, psycopg 3.x, uv, pytest, Nx quality scripts (004-local-dev-db)
- PostgreSQL 16 local development database with persistent volume by default (004-local-dev-db)

- Python 3.12 (pipeline and backend), TypeScript 5.x (frontend unchanged) + Nx workspace tooling, uv, ruff, ty, pytest, dagster baseline package, SQLAlchemy 2.x, Alembic, Pydantic 2.x, psycopg 3.x, structlog, OpenTelemetry SDK/API (003-define-data-contract)
- PostgreSQL 16 with TimescaleDB 2.14 extension for hypertable time-series partitioning and relational integrity (003-define-data-contract)

- Python 3.12 (backend and pipeline contract implementation), TypeScript 5.x (no feature scope changes) + Nx workspace tooling, uv, ruff, ty, pytest, baseline dagster package, contract documentation set under specs (003-define-data-contract)
- Contract-target storage is relational time-series persistence with immutable provenance and revision linkage (exact engine selected in implementation phase) (003-define-data-contract)

- Python 3.12 (pipeline/backend), TypeScript 5.x (frontend), Node.js 22 LTS + Nx workspace tooling, uv, ruff, ty, pytest, dagster (baseline package only), pnpm, Biome, Vitest, PMD CPD (002-pipeline-app-baseline)
- N/A (scaffolding-only feature; no production persistence design) (002-pipeline-app-baseline)

- Python 3.12 (backend), TypeScript 5.x (frontend), Node.js 22 LTS
- Nx workspace orchestration
- pnpm 9 workspace management
- Backend tooling: uv, ruff, ty, pytest, pytest-cov
- Frontend tooling: Biome, TypeScript compiler, Vitest, @vitest/coverage-v8
- Cross-repo duplication tooling: PMD CPD 7.22.0 scripts

## Project Structure

```text
apps/
	backend/
		src/
		tests/
		pyproject.toml
		uv.lock
		project.json
	pipeline/
		src/
		tests/
		pyproject.toml
		uv.lock
		project.json
	frontend/
		src/
		tests/
		package.json
		tsconfig.json
		vitest.config.ts
		biome.json
		project.json
tools/
	quality/
		cpd/
		local-stack/
		pmd/
		verification/
docs/
	architecture/
	onboarding/
	runbooks/
specs/
	001-setup-monorepo-baseline/
docker/
	compose/
docker-compose.yml
nx.json
package.json
pnpm-workspace.yaml
.pre-commit-config.yaml
```

## Commands

Workspace bootstrap and validation:

- pnpm install
- uv sync --project apps/backend --frozen
- uv sync --project apps/pipeline --frozen
- pnpm run quality:all

Affected-only quality checks:

- pnpm run affected:lint
- pnpm run affected:format
- pnpm run affected:typecheck
- pnpm run affected:test
- pnpm run affected:coverage
- pnpm run affected:duplication

Backend quality commands:

- uv run --project apps/backend ruff check apps/backend
- uv run --project apps/backend ruff format --check apps/backend
- uv run --project apps/backend ty check apps/backend
- uv run --project apps/backend pytest apps/backend/tests

Pipeline quality commands:

- uv run --project apps/pipeline ruff check apps/pipeline
- uv run --project apps/pipeline ruff format --check apps/pipeline
- uv run --project apps/pipeline ty check apps/pipeline
- uv run --project apps/pipeline pytest apps/pipeline/tests
- uv run --project apps/pipeline pytest apps/pipeline/tests/orchestration
- pnpm exec nx run pipeline:test:orchestration:cadence
- pnpm exec nx run pipeline:test:orchestration:parallel

Frontend quality commands:

- pnpm --dir apps/frontend lint
- pnpm --dir apps/frontend exec biome check .
- pnpm --dir apps/frontend typecheck
- pnpm --dir apps/frontend test
- pnpm --dir apps/frontend coverage

Local stack and duplication:

- bash tools/quality/cpd/run-cpd.sh
- bash tools/quality/local-stack/test-local-db-bootstrap.sh
- bash tools/quality/local-stack/run-db-migrations.sh
- bash tools/quality/local-stack/check-db-revision.sh
- uv run --project apps/pipeline pytest --no-cov apps/pipeline/tests/orchestration/test_ingest_job_runtime.py::test_ingest_job_persists_deferred_counts_when_sources_are_carried_forward
- bash tools/quality/local-stack/test-db-readiness.sh
- uv run --project apps/backend pytest apps/backend/tests/contract/test_ingest_audit_query_contract.py apps/backend/tests/contract/test_revision_lineage_traceability.py
- bash tools/quality/local-stack/test-compose-stack.sh
- docker compose up -d
- docker compose ps
- docker compose down

Current migration head expected by local revision checks: `0003_sched_eligibility`.

## Code Style

- Python: ruff rules configured in apps/backend/pyproject.toml and
  apps/pipeline/pyproject.toml; no inline suppression bypasses are allowed.
- TypeScript: strict compiler settings in apps/frontend/tsconfig.json; Biome check is the
  lint/format authority.
- Quality gates: lint, format, typecheck, test, coverage, and duplication must pass via
  affected targets and pre-commit hooks.

## Recent Changes
- 006-parallel-source-scheduling: Added Python 3.12 (pipeline/backend/shared DB), TypeScript 5.x unchanged + Dagster 1.x, Pydantic 2.x, SQLAlchemy 2.x, Alembic, psycopg 3.x, Nx tooling

- 005-dagster-ingest-pipeline: Added Python 3.12 (pipeline and shared DB), TypeScript 5.x unchanged + Dagster 1.x, Pydantic 2.x, SQLAlchemy 2.x, Alembic, psycopg 3.x, structlog, OpenTelemetry API/SDK, Nx workspace tooling

- 004-local-dev-db: Added Python 3.12 (backend and pipeline tooling), shell scripts for local verification + Docker Compose, PostgreSQL 16 image for local DB service, SQLAlchemy 2.x, Alembic, psycopg 3.x, uv, pytest, Nx quality scripts


  placeholder projects, strict quality gates, affected-only checks, PMD duplication
  scripts, and Docker Compose local stack verification.

<!-- MANUAL ADDITIONS START -->

structure, toolchain, or canonical developer commands change.

<!-- MANUAL ADDITIONS END -->
