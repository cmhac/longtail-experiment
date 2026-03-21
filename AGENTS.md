# longtail-experiment Development Guidelines

Auto-generated from all feature plans. Last updated: 2026-03-21

## Active Technologies

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

Frontend quality commands:

- pnpm --dir apps/frontend lint
- pnpm --dir apps/frontend exec biome check .
- pnpm --dir apps/frontend typecheck
- pnpm --dir apps/frontend test
- pnpm --dir apps/frontend coverage

Local stack and duplication:

- bash tools/quality/cpd/run-cpd.sh
- bash tools/quality/local-stack/test-compose-stack.sh
- docker compose up -d
- docker compose ps
- docker compose down

## Code Style

- Python: ruff rules configured in apps/backend/pyproject.toml and
  apps/pipeline/pyproject.toml; no inline suppression bypasses are allowed.
- TypeScript: strict compiler settings in apps/frontend/tsconfig.json; Biome check is the
  lint/format authority.
- Quality gates: lint, format, typecheck, test, coverage, and duplication must pass via
  affected targets and pre-commit hooks.

## Recent Changes

- 002-pipeline-app-baseline: Added Python 3.12 (pipeline/backend), TypeScript 5.x (frontend), Node.js 22 LTS + Nx workspace tooling, uv, ruff, ty, pytest, dagster (baseline package only), pnpm, Biome, Vitest, PMD CPD

- 001-setup-monorepo-baseline: Established Nx monorepo baseline with backend/frontend
  placeholder projects, strict quality gates, affected-only checks, PMD duplication
  scripts, and Docker Compose local stack verification.

<!-- MANUAL ADDITIONS START -->

- AGENTS.md is mandatory maintained documentation. Update this file whenever repository
structure, toolchain, or canonical developer commands change.
<!-- MANUAL ADDITIONS END -->
