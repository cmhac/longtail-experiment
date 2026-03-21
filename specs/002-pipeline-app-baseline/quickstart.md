# Quickstart: Pipeline App Baseline

## Goal

Extend the monorepo baseline with a third app (`pipeline`) that mirrors backend Python
quality setup and participates in three-app local stack verification.

## Prerequisites

- Git
- Docker (or Docker Desktop)
- Node.js 22 LTS
- pnpm
- Python 3.12
- uv

## 1. Bootstrap Workspace

```bash
pnpm install
uv sync --project apps/backend --frozen
uv sync --project apps/pipeline --frozen
```

## 2. Verify Project Registration

```bash
pnpm nx show projects
pnpm nx graph --file tmp/nx-graph.html
```

Expected outcome:

- Project list includes backend, frontend, and pipeline.
- Project graph contains a dedicated `pipeline` node under `apps/pipeline`.

## 3. Run Pipeline Quality Gates

```bash
uv run --project apps/pipeline ruff check apps/pipeline
uv run --project apps/pipeline ruff format --check apps/pipeline
uv run --project apps/pipeline ty check apps/pipeline
uv run --project apps/pipeline pytest apps/pipeline/tests
```

## 4. Run Affected-Only Workspace Gates

```bash
pnpm run affected:lint
pnpm run affected:format
pnpm run affected:typecheck
pnpm run affected:test
pnpm run affected:coverage
pnpm run affected:duplication
```

## 5. Verify Three-App Local Stack

```bash
docker compose up -d
docker compose ps
bash tools/quality/local-stack/test-compose-stack.sh
docker compose down
```

Expected outcome:

- Pipeline, backend, and frontend placeholders all report healthy status.
- Compose output contains `pipeline`, `backend`, and `frontend` service entries.

## 6. Definition of Done for This Baseline

- `apps/pipeline` is registered and discoverable as an Nx project.
- Pipeline quality gates execute without suppression paths.
- Affected-only workspace checks include pipeline behavior.
- Three-app local stack starts, verifies health, and shuts down cleanly.
- No business data processing logic exists in pipeline app scope.

## 8. Verification Evidence Template

- Workspace registration status: PASS/FAIL
- Pipeline quality gates status: PASS/FAIL
- Affected-only pipeline lint runtime (seconds):
- Affected-only pipeline test runtime (seconds):
- Three-app local stack startup status: PASS/FAIL
- Three-app local stack shutdown status: PASS/FAIL

## 7. Documentation Impact Checklist

Update these docs in the same implementation change if feature code is added:

- `AGENTS.md`
- `docs/architecture/monorepo-boundaries.md`
- `docs/onboarding/monorepo-baseline.md`
- `docs/runbooks/local-stack-baseline.md`
