# Quickstart: Core Pipeline Data Contract

## Goal

Prepare contributors to implement and verify the backend and pipeline canonical data contract for multi-source time-series ingestion, provenance, revision lineage, and hierarchical filtering.

## Locked Implementation Stack

- Persistence: PostgreSQL 16 + TimescaleDB 2.14
- Validation: Pydantic 2.x
- Persistence modeling: SQLAlchemy 2.x
- Migration engine: Alembic
- DB driver: psycopg 3.x
- Observability: structlog + OpenTelemetry SDK/API

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

## 2. Review Planning Artifacts

Read these artifacts before writing implementation code:

- specs/003-define-data-contract/spec.md
- specs/003-define-data-contract/plan.md
- specs/003-define-data-contract/research.md
- specs/003-define-data-contract/data-model.md
- specs/003-define-data-contract/contracts/canonical-observation-contract.md
- specs/003-define-data-contract/contracts/provenance-and-revision-contract.md
- specs/003-define-data-contract/contracts/taxonomy-and-query-contract.md

## 3. Implement Contract Validation and Persistence Boundaries

Implementation scope for the next coding phase:

- Add canonical contract validation paths in pipeline ingest flow.
- Add provenance immutability and revision linkage handling.
- Add category/geography hierarchy mapping and query filter semantics.
- Add contract and regression tests for edge cases defined in spec.

## 4. Verify Concrete Persistence Stack

```bash
docker compose up -d
docker compose ps
```

Expected outcome:

- Local stack includes database service with PostgreSQL 16 compatibility.
- TimescaleDB extension is available in the database image used for contract persistence.
- Pipeline and backend services can establish connections through configured DSN values.

## 5. Run Backend and Pipeline Quality Gates

```bash
uv run --project apps/backend ruff check apps/backend
uv run --project apps/backend ruff format --check apps/backend
uv run --project apps/backend ty check apps/backend
uv run --project apps/backend pytest apps/backend/tests

uv run --project apps/pipeline ruff check apps/pipeline
uv run --project apps/pipeline ruff format --check apps/pipeline
uv run --project apps/pipeline ty check apps/pipeline
uv run --project apps/pipeline pytest apps/pipeline/tests
```

## 6. Run Affected-Only Workspace Gates

```bash
pnpm run affected:lint
pnpm run affected:format
pnpm run affected:typecheck
pnpm run affected:test
pnpm run affected:coverage
pnpm run affected:duplication
```

## 7. Validate Local Stack Baseline

```bash
docker compose up -d
docker compose ps
bash tools/quality/local-stack/test-compose-stack.sh
docker compose down
```

Expected outcome:

- backend, frontend, and pipeline services report healthy.
- quality gates pass with no suppressions.

## 8. Verification Evidence Template

- Canonical contract validation tests: PASS/FAIL
- Provenance immutability tests: PASS/FAIL
- Revision lineage tests: PASS/FAIL
- Taxonomy/geography filter tests: PASS/FAIL
- Observability assertions (logs/traces): PASS/FAIL
- Affected lint runtime (seconds):
- Affected test runtime (seconds):
- Local stack startup status: PASS/FAIL
- Local stack shutdown status: PASS/FAIL

## 9. Documentation Impact Checklist

Update these docs in the same implementation change if behavior or commands change:

- AGENTS.md
- docs/architecture/monorepo-boundaries.md
- docs/onboarding/monorepo-baseline.md
- docs/runbooks/local-stack-baseline.md
