# longtail-experiment Development Guidelines

Auto-generated from all feature plans. Last updated: 2026-03-24

## Active Technologies

- Python 3.12 for backend and pipeline applications (`apps/backend`, `apps/pipeline`)
- TypeScript 5.x for frontend application (`apps/frontend`) with Node.js 22 LTS runtime
- Nx monorepo orchestration with pnpm 9 workspace management

- Backend/pipeline stack: SQLAlchemy 2.x, Alembic, psycopg 3.x, Pydantic 2.x,
  Dagster 1.x, structlog, OpenTelemetry API/SDK
- Python quality tooling: uv, ruff, ty, pytest, pytest-cov
- Frontend stack: Next.js 15 (App Router), React 19, HeroUI 3, Recharts
- Frontend quality tooling: Biome, TypeScript compiler, Vitest, @vitest/coverage-v8

- Data stores: PostgreSQL 16 canonical dataset store (`source_profiles`, `data_series`,
  `observations`, topic-tag relation tables) and ingestion runtime tables
  (`ingestion_runs`, `source_run_outcomes`, cadence/eligibility persistence)
- Local runtime: unified Docker Compose stack plus Dagit local tooling under
  `tools/quality/local-stack`
- Shared DB library: `libs/db` with migration authority under `libs/db/alembic`
- Cross-repo duplication tooling: PMD CPD 7.22.0 scripts

Feature references for current stack shape:

- 019-real-backend-api (backend runtime/query composition and canonical dataset APIs)
- 018-frontend-dataset-discovery (frontend discovery UX stack and charting)
- 017-dataset-discovery-api (dataset discovery/search backend contract)
- 012-multi-series-adapters (provider grouping/series ownership runtime model)
- 011-source-asset-cadence (source-owned schedule authority)

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
			app/
				datasets/
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
- pnpm run provider:bootstrap -- --provider-group-key acme --source-key acme_cpi --module-name acme_cpi_source --cadence-label monthly --cron-schedule "0 0 1 * *" --series-item-key acme_cpi --canonical-series-key PRICE.US.CPI --provider-series-id CPIAUCSL
- pnpm run quality:all

Affected-only quality checks:

- pnpm run affected:lint
- pnpm run affected:format
- pnpm run affected:typecheck
- pnpm run affected:test
- pnpm run affected:coverage
- pnpm run affected:duplication

Mandatory full-suite stop gate (non-bypass):

- Before any commit, and before any AI agent stops work or hands off, run:
  `pnpm exec nx run-many -t test --all`
- This command MUST pass with no exceptions. Targeted or affected-only tests are
  insufficient for this stop gate.
- Before any commit, run:
  `pnpm exec nx run-many -t coverage --all`
- Coverage MUST meet configured minimums (90% or higher) for every project; exceptions
  and bypasses are not allowed.

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
- pnpm exec nx run pipeline:test:orchestration:source-assets

Frontend quality commands:

- pnpm --dir apps/frontend dev
- pnpm --dir apps/frontend build
- pnpm --dir apps/frontend start
- pnpm --dir apps/frontend lint
- pnpm --dir apps/frontend exec biome check .
- pnpm --dir apps/frontend typecheck
- pnpm --dir apps/frontend test
- pnpm --dir apps/frontend coverage
- pnpm exec nx run frontend:test:discovery-pages

Frontend discovery runtime environment:

- DISCOVERY*API_BASE_URL (server-side only; do not expose via NEXT_PUBLIC* prefix)

Local stack and duplication:

- bash tools/quality/cpd/run-cpd.sh
- bash tools/quality/local-stack/test-local-db-bootstrap.sh
- bash tools/quality/local-stack/run-db-migrations.sh
- bash tools/quality/local-stack/check-db-revision.sh
- bash tools/quality/local-stack/start-dagit-local.sh
- bash tools/quality/local-stack/test-dagit-endpoint.sh
- bash tools/quality/local-stack/stop-dagit-local.sh
- VERIFY_DAGIT_ENDPOINT=1 bash tools/quality/local-stack/test-compose-stack.sh
- uv run --project apps/pipeline pytest --no-cov apps/pipeline/tests/orchestration/test_ingest_job_runtime.py::test_ingest_job_persists_deferred_counts_when_sources_are_carried_forward
- bash tools/quality/local-stack/test-db-readiness.sh
- uv run --project apps/backend pytest apps/backend/tests/contract/test_ingest_audit_query_contract.py apps/backend/tests/contract/test_revision_lineage_traceability.py
- bash tools/quality/local-stack/test-compose-stack.sh
- bash tools/quality/local-stack/test-discovery-persisted-parity.sh
- docker compose up -d
- docker compose ps
- docker compose down

Current migration head expected by local revision checks: `0008_dataset_discovery_indexes`.

## Code Style

- Python: ruff rules configured in apps/backend/pyproject.toml and
  apps/pipeline/pyproject.toml; no inline suppression bypasses are allowed.
- TypeScript: strict compiler settings in apps/frontend/tsconfig.json; Biome check is the
  lint/format authority.
- Quality gates: lint, format, typecheck, test, coverage, and duplication must pass via
  affected targets and pre-commit hooks.
- Mandatory stop rule: before any commit and before AI agent handoff/stop, the full
  monorepo test suite MUST pass via `pnpm exec nx run-many -t test --all`.
- Mandatory commit rule: before any commit, monorepo coverage MUST pass via
  `pnpm exec nx run-many -t coverage --all` with minimum thresholds satisfied.

## Recent Changes
- 021-bootstrap-provider-script: Added provider adapter bootstrap tooling (`tools/provider_bootstrap`) and root script `pnpm run provider:bootstrap` to standardize new source adapter scaffolding.

- 019-real-backend-api: Delivered backend runtime/query composition against canonical
  PostgreSQL datasets, using SQLAlchemy repositories in `libs/db` and Pydantic contracts
  in `apps/backend/src/contract`.
- 018-frontend-dataset-discovery: Delivered dataset discovery UI on Next.js 15/React 19
  with HeroUI/Recharts and strict TypeScript + Biome + Vitest quality tooling.
  query layer integration with PostgreSQL 16 canonical tables.
  provider ownership model and source-owned schedule authority in orchestration runtime.
  manifests discovered from `jobs/sources/*_source.py`, with schedules/assets/catalog/runtime
  derived dynamically and anti-hardcoding bootstrap guards.
  coverage stop gates (`nx run-many -t test --all` and `nx run-many -t coverage --all`),
  plus all-project lint/format/typecheck/test/coverage enforcement.

<!-- MANUAL ADDITIONS START -->

structure, toolchain, or canonical developer commands change.

<!-- MANUAL ADDITIONS END -->
