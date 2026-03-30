# longtail-experiment Development Guidelines

Auto-generated from all feature plans. Last updated: 2026-03-30

## Active Technologies
- TypeScript 5.x + React 19 (Next.js 15 App Router), Python 3.12 backend query layer, existing pipeline contracts/persistence semantics + Existing discovery API client/types, Next.js routing primitives, existing shell/layout tokens, backend dataset discovery service/repository surfaces (032-source-pages)
- Existing PostgreSQL 16 discovery metadata in `source_profiles`, `data_series`, `topic_tags`, and `observations`; no new datastore expected (032-source-pages)
- TypeScript 5.x + React 19 (Next.js 15 App Router), Python 3.12 backend query layer, existing pipeline contracts/persistence semantics + Existing discovery API client/types, Next.js routing primitives, existing dataset list/detail components, backend dataset discovery service/repository surfaces (033-tag-geography-pages)
- Existing PostgreSQL 16 discovery metadata in `data_series`, `topic_tags`, `data_series_topic_tags`, `source_profiles`, and `observations`; no new datastore expected (033-tag-geography-pages)
- Python 3.12 (backend), TypeScript 5.x + React 19 (frontend) + SQLAlchemy query repository and service orchestration in backend; Next.js App Router discovery client/pages/components in frontend (034-api-pagination-rollout)
- PostgreSQL 16 discovery metadata tables and observations (034-api-pagination-rollout)
- TypeScript 5.x + React 19 in Next.js 15 App Router + Existing discovery UI components, HeroUI component primitives, shell theme tokens and global CSS (035-filter-ui-improvements)
- N/A (presentation and client interaction behavior only) (035-filter-ui-improvements)
- TypeScript 5.x + React 19 in Next.js 15 App Router + `@heroui/react`, HeroUI v3 styling system, Tailwind CSS v4/PostCSS integration, existing Next.js routing primitives, existing discovery client/types, existing Recharts detail visualizations (036-heroui-ui-migration)
- N/A for new persistence; existing PostgreSQL-backed discovery APIs remain the data source (036-heroui-ui-migration)
- TypeScript 5.x + React 19 in Next.js 15 App Router + Existing discovery API client/types, Recharts time-series primitives, HeroUI components, Tailwind utility classes, existing dataset-detail view-model helpers (037-detail-chart-overhaul)
- Python 3.12 for pipeline/backend layers; TypeScript 5.x + React 19 + Next.js 15 App Router for frontend + SQLAlchemy 2.x, Alembic, Pydantic 2.x, Dagster 1.x, existing pipeline source discovery/registration utilities, existing backend discovery service/repository contracts, HeroUI 3, Tailwind, existing frontend discovery client/types (038-source-metadata-relocation)
- PostgreSQL 16 discovery metadata in `source_profiles`, `data_series`, `topic_tags`, and `observations`, with Alembic-managed schema changes required for source-level metadata (038-source-metadata-relocation)

- TypeScript 5.x + React 19 in Next.js 15 App Router + Existing discovery client/types, existing dataset catalog components, shell/nav primitives, HeroUI-aligned theme tokens (027-dataset-list-page)
- N/A (frontend listing and interaction state over existing discovery catalog payload) (027-dataset-list-page)
- TypeScript 5.x + React 19 in Next.js 15 App Router + Existing discovery UI components, Next.js routing/link primitives, shell theme tokens, existing discovery API client/types (028-unify-dataset-list-item)
- N/A (presentation-level unification over existing fetched payloads) (028-unify-dataset-list-item)
- TypeScript 5.x + React 19 in Next.js 15 App Router + Existing shell layout classes, discovery page components, theme tokens, Next.js page composition (029-global-content-width)
- N/A (presentation/layout behavior only) (029-global-content-width)
- TypeScript 5.x + React 19 (Next.js 15 App Router), Python 3.12 backend contracts unchanged + Next.js routing primitives, existing discovery API client/types, HeroUI-aligned shell/theme tokens (030-unified-search-page)
- N/A for new persistence; existing PostgreSQL-backed discovery search source remains unchanged (030-unified-search-page)
- TypeScript 5.x + React 19 (Next.js 15 App Router), Python 3.12 backend contracts reused unchanged + Existing discovery API client/types, Recharts time-series primitives, shell/theme tokens and layout classes (031-dataset-detail-overhaul)
- N/A for new persistence; existing PostgreSQL-backed dataset detail payload remains source-of-truth (031-dataset-detail-overhaul)

- TypeScript 5.x with React 19 in Next.js 15 App Router + HeroUI 3 components, Next.js navigation primitives, existing frontend theme tokens (023-initial-ui-design)
- N/A (presentation and client interaction state only) (023-initial-ui-design)
- Python 3.12 (backend query/runtime), TypeScript 5.x + React 19 + Next.js 15 (frontend) + existing backend discovery service/repository surfaces, PostgreSQL 16 dataset metadata store, frontend discovery client, HeroUI-aligned shell styling (024-home-search-bar)
- PostgreSQL 16 canonical/discovery tables with trigram-enabled text matching support for likely suggestions (024-home-search-bar)
- TypeScript 5.x + React 19 + Next.js 15 (frontend), Python 3.12 (backend discovery contract/repository surfaces) + Existing homepage shell components, discovery API client/types, persisted discovery repository/service, HeroUI-aligned theme tokens (025-homepage-editorial-feed)
- PostgreSQL 16 discovery metadata tables (existing recent-updates source) (025-homepage-editorial-feed)
- TypeScript 5.x + React 19 in Next.js 15 App Router + Existing shell components, HeroUI-aligned theme tokens, Next.js routing primitives (026-global-footer)
- N/A (presentation-only shell/footer content) (026-global-footer)

- Python 3.12 (pipeline runtime), YAML/shell compose configuration, SQL for database provisioning checks + Dagster orchestration runtime, SQLAlchemy-backed Dagster storage configuration, Docker Compose local stack, PostgreSQL 16 containers (022-dagster-postgres-backend)
- Two local PostgreSQL database roles: orchestration metadata store and canonical output-data store (022-dagster-postgres-backend)

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
- Local runtime: unified Docker Compose stack is the canonical local-dev
  orchestration surface; use `docker compose` directly for startup, shutdown,
  logs, readiness, migrations, and Dagit access
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
- pnpm run provider:bootstrap -- --provider-group-key acme --source-key acme_cpi --module-name acme_cpi_source --cadence-label monthly --cron-schedule "0 0 1 \* \*" --series-item-key acme_cpi --canonical-series-key PRICE.US.CPI --provider-series-id CPIAUCSL
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
- pnpm exec nx run pipeline:test:orchestration:metadata-store

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
- uv run --project apps/pipeline pytest --no-cov apps/pipeline/tests/orchestration/test_ingest_job_runtime.py::test_ingest_job_persists_deferred_counts_when_sources_are_carried_forward
- uv run --project apps/backend pytest apps/backend/tests/contract/test_ingest_audit_query_contract.py apps/backend/tests/contract/test_revision_lineage_traceability.py
- uv run --project apps/pipeline pytest --no-cov apps/pipeline/tests/orchestration/test_dagster_metadata_storage_config.py apps/pipeline/tests/orchestration/test_dagit_runtime_fail_fast.py apps/pipeline/tests/orchestration/test_dagster_metadata_concurrency.py
- bash tools/quality/local-stack/test-discovery-persisted-parity.sh
- docker compose up -d
- docker compose ps
- docker compose logs <service>
- docker compose up -d db dagster_db
- docker compose up -d backend
- docker compose up -d dagit
- docker compose exec db psql -U "${LOCAL_DB_USER:-longtail}" -d "${LOCAL_DB_NAME:-longtail_local}" -c "SELECT version_num FROM alembic_version;"
- docker compose down

Current migration head expected by local revision checks: `0010_source_profile_metadata`.

Docker Compose policy:

- `docker compose` is the only canonical local-dev control surface for stack lifecycle and service verification.
- Do not add or use wrapper scripts under `tools/quality/local-stack` for startup, shutdown, readiness polling, migration application, or Dagit management when the same behavior can be expressed with `docker compose`.
- For migration application, start `backend`; its container command owns `alembic upgrade head` before the API server starts.
- For Dagit verification, use `docker compose ps dagit` and `docker compose logs dagit`; the compose healthcheck now verifies both HTTP reachability and workspace load.
- Before manual testing, restart from a clean compose state with `docker compose down` followed by `docker compose up -d`.

## Code Style

- Python: ruff rules configured in apps/backend/pyproject.toml and
  apps/pipeline/pyproject.toml; no inline suppression bypasses are allowed.
- TypeScript: strict compiler settings in apps/frontend/tsconfig.json; Biome check is the
  lint/format authority.
- Frontend UI: HeroUI is the default component system in `apps/frontend`; Tailwind is
  the default styling mechanism. New local or feature-specific CSS is not permitted
  unless the need is a shared global token, framework integration point, or a documented
  gap that HeroUI + Tailwind cannot cover cleanly.
- Frontend reuse: when a component pattern will be used more than once, extract or
  extend a shared component in `apps/frontend/src/components` instead of duplicating
  markup/class lists in routes or feature-local files.
- Frontend composition: related reusable UI primitives may be exported as grouped,
  composable components from a single module, following the pattern used in
  `apps/frontend/src/components/discovery/PageHeader.tsx`.
- Quality gates: lint, format, typecheck, test, coverage, and duplication must pass via
  affected targets and pre-commit hooks.
- Mandatory stop rule: before any commit and before AI agent handoff/stop, the full
  monorepo test suite MUST pass via `pnpm exec nx run-many -t test --all`.
- Mandatory commit rule: before any commit, monorepo coverage MUST pass via
  `pnpm exec nx run-many -t coverage --all` with minimum thresholds satisfied.

## Testing Guidelines

CRITICAL: each time you finish working on a given task, before you stop work, you MUST go through two steps: manual testing, and monorepo-wide quality gates.

### Manual Testing

Once you finish implementing a change, verify it by executing the code in a real-world scenario using the local development environment rather than assuming it works: first run any existing automated tests, then perform manual testing using the most appropriate mechanism for the stack.

For example, if you updated an API route, start the local development server and use a CURL command, python script, or other means to send a request to that route and confirm the expected response. If you updated a database migration, run the migration against a local database instance and check the schema changes. If you updated a data processing function, execute it with real input data and verify the output. If you updated a frontend component, start the development server and interact with the UI to confirm the change is reflected as expected. If you updated an orchestration job, run it in the local Dagster environment and check the logs and outputs.

If you encounter any issues during manual testing, fix them immediately and then re-test until the change works as expected in the local environment. Do not skip or rush through this step, as it is critical for catching issues that may not be covered by automated tests and for ensuring that your change works in a realistic scenario.

CRITICAL: each time you do this, first take down the local development environment to ensure a clean state, then bring it back up to test the change in a realistic scenario. This is especially important for changes that affect startup behavior, database configuration, or orchestration runtimes, where the change may not be fully exercised until the environment is restarted.

### Monorepo-wide Quality Gates

After manual testing, you MUST run the full monorepo test suite and coverage checks to ensure that your change does not introduce regressions or reduce test coverage. This is a mandatory stop gate before committing any changes, and it applies to both human and AI agent contributions.

Use this exact command to run the full suite: `pre-commit run --all-files`.

If you discover any test failures or coverage reductions, you MUST fix them before committing. This may involve writing new tests to cover uncovered code paths, or updating existing tests to reflect the new behavior. The goal is to maintain a high standard of quality and ensure that all changes are thoroughly tested and documented.

<!-- —use python -c or a temporary script for library code and edge cases, curl to explore JSON endpoints, and Playwright or a browser automation CLI for interactive web UI flows, including screenshots to confirm visual details. Actively probe normal paths, edge cases, startup behavior, and obvious failure modes; if you find a bug, fix it using red/green test-driven development (TDD) so the issue is captured in permanent automated tests. Keep a concise record of what you tested, the exact commands you ran, outputs observed, and any screenshots or notes that demonstrate the feature working end to end.” This closely follows Simon Willison’s guidance that coding agents should execute what they write, use manual testing in addition to automated tests, use browser automation for web interfaces, and document the testing process with command/output artifacts. -->

## Recent Changes
- 038-source-metadata-relocation: Added Python 3.12 for pipeline/backend layers; TypeScript 5.x + React 19 + Next.js 15 App Router for frontend + SQLAlchemy 2.x, Alembic, Pydantic 2.x, Dagster 1.x, existing pipeline source discovery/registration utilities, existing backend discovery service/repository contracts, HeroUI 3, Tailwind, existing frontend discovery client/types
- 037-detail-chart-overhaul: Added TypeScript 5.x + React 19 in Next.js 15 App Router + Existing discovery API client/types, Recharts time-series primitives, HeroUI components, Tailwind utility classes, existing dataset-detail view-model helpers
- 036-heroui-ui-migration: Added TypeScript 5.x + React 19 in Next.js 15 App Router + `@heroui/react`, HeroUI v3 styling system, Tailwind CSS v4/PostCSS integration, existing Next.js routing primitives, existing discovery client/types, existing Recharts detail visualizations


  PostgreSQL datasets, using SQLAlchemy repositories in `libs/db` and Pydantic contracts
  in `apps/backend/src/contract`.
  with HeroUI/Recharts and strict TypeScript + Biome + Vitest quality tooling.
  query layer integration with PostgreSQL 16 canonical tables.
  provider ownership model and source-owned schedule authority in orchestration runtime.
  manifests discovered from `src/sources/*_source.py`, with schedules/assets/catalog/runtime
  derived dynamically and anti-hardcoding bootstrap guards.
  coverage stop gates (`nx run-many -t test --all` and `nx run-many -t coverage --all`),
  plus all-project lint/format/typecheck/test/coverage enforcement.

<!-- MANUAL ADDITIONS START -->

structure, toolchain, or canonical developer commands change.

<!-- MANUAL ADDITIONS END -->
