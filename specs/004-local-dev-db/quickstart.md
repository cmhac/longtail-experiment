# Quickstart: Local Development Database Readiness

## Goal

Enable contributors to start a local development database, apply migrations, verify schema baseline, and confirm environment readiness for app logic implementation.

## Prerequisites

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

## 2. Start Local Stack

```bash
docker compose up -d
docker compose ps
```

Expected outcome:

- Local stack reports healthy app services and a reachable local database service.
- Startup output includes clear development-only warning context.

## 3. Apply Shared DB Migrations

```bash
# Canonical migration command path for this feature
PYTHONPATH=libs/db/src uv run --project apps/backend alembic -c libs/db/alembic.ini upgrade head
```

Expected outcome:

- Migration chain applies successfully from current local baseline.
- On first error, command exits immediately with actionable recovery output.

## 4. Verify Migration Baseline

```bash
PYTHONPATH=libs/db/src uv run --project apps/backend alembic -c libs/db/alembic.ini current
```

Expected outcome:

- Current revision matches expected latest shared-db revision.

## 5. Run Local Readiness Verification

```bash
bash tools/quality/local-stack/test-compose-stack.sh
pnpm run affected:lint
pnpm run affected:format
pnpm run affected:typecheck
pnpm run affected:test
pnpm run affected:coverage
pnpm run affected:duplication
```

Expected outcome:

- Stack verification passes.
- Affected quality gates pass with no suppressions.

## 6. Explicit Reset Flow (Only When Requested)

```bash
# Example explicit local reset sequence
# Use only when a clean-state rerun is required

docker compose down -v
docker compose up -d
```

Expected outcome:

- Local database state is reset only because developer explicitly requested reset.

## 7. Shutdown

```bash
docker compose down
```

## Documentation Impact Checklist

Update these docs in the same implementation change if setup behavior or commands change:

- AGENTS.md
- docs/architecture/monorepo-boundaries.md
- docs/onboarding/monorepo-baseline.md
- docs/runbooks/local-stack-baseline.md
