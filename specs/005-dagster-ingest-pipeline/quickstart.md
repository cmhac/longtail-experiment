# Quickstart: Dagster-Orchestrated Time-Series Ingestion

## Goal

Guide contributors through local verification for scheduled and on-demand ingestion orchestration, source-level outcomes, and duplicate conflict handling.

## Prerequisites

- Git
- Docker or Docker Desktop
- Node.js 22 LTS
- pnpm
- Python 3.12
- uv

## 1. Bootstrap Workspace

```bash
pnpm install
uv sync --project apps/pipeline --frozen
uv sync --project apps/backend --frozen
```

## 2. Prepare Local Database and Migrations

```bash
docker compose up -d db
bash tools/quality/local-stack/run-db-migrations.sh
bash tools/quality/local-stack/check-db-revision.sh
```

Expected outcome:

- Local DB is healthy.
- Latest migration revision is applied.

## 3. Run Pipeline Contract Baseline Tests

```bash
PYTHONPATH=libs/db/src uv run --project apps/pipeline pytest apps/pipeline/tests/contract
```

Expected outcome:

- Canonical validation, provenance, and lineage tests pass before orchestration additions.

## 4. Verify Orchestration Trigger Paths (Post-Implementation)

Scheduled trigger validation:

```bash
uv run --project apps/pipeline pytest apps/pipeline/tests/orchestration -k scheduled
```

On-demand trigger validation:

```bash
uv run --project apps/pipeline pytest apps/pipeline/tests/orchestration -k ondemand
```

Expected outcome:

- Both trigger modes are supported by one orchestration entry point.

## 5. Verify Mixed Outcome and Concurrency Policies

```bash
uv run --project apps/pipeline pytest apps/pipeline/tests/orchestration -k "partial_success or concurrency"
```

Expected outcome:

- Source failures produce partial-success run state while unaffected sources continue.
- Per-source concurrency enforces one active + one deduplicated queued run.

## 6. Verify Duplicate Drift and Conflict Persistence

```bash
uv run --project apps/pipeline pytest apps/pipeline/tests/orchestration -k "duplicate or conflict"
```

Expected outcome:

- Exact duplicates are no-op and do not produce additional observation writes.
- Non-matching duplicates produce conflict outcomes and queryable conflict records.

## 7. Run Affected Quality Gates

```bash
pnpm run affected:lint
pnpm run affected:format
pnpm run affected:typecheck
pnpm run affected:test
pnpm run affected:coverage
pnpm run affected:duplication
```

## 8. Documentation Impact Checklist

Update in same change when behavior or commands change:

- AGENTS.md
- docs/architecture/monorepo-boundaries.md
- docs/onboarding/monorepo-baseline.md
- docs/runbooks/local-stack-baseline.md
