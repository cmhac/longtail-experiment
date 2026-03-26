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
# Canonical migration apply path for this feature
docker compose up -d backend
```

Expected outcome:

- Migration chain applies successfully from current local baseline before the backend API serves traffic.
- On first error, the backend container exits and the failure is visible through `docker compose logs backend`.

## 4. Verify Migration Baseline

```bash
docker compose exec db psql -U "${LOCAL_DB_USER:-longtail}" -d "${LOCAL_DB_NAME:-longtail_local}" -c "SELECT version_num FROM alembic_version;"
```

Expected outcome:

- Current revision matches expected latest shared-db revision.
- Command output includes the latest `version_num` row when baseline matches.

## 5. Run Local Readiness Verification

```bash
docker compose ps
pnpm run affected:lint
pnpm run affected:format
pnpm run affected:typecheck
pnpm run affected:test
pnpm run affected:coverage
pnpm run affected:duplication
```

Expected outcome:

- Compose health verification passes.
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

## Development-only Warning

- Local DB compose workflows are development-only commands.
- Do not execute these commands against staging or production databases.

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
