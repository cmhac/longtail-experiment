# Monorepo Boundaries

## Purpose

Define ownership and separation boundaries for baseline monorepo projects.

## Project Boundaries

- apps/pipeline: Python Dagster-oriented pipeline placeholder and pipeline quality targets.
- apps/backend: Python backend placeholder and backend quality targets.
- apps/frontend: TypeScript frontend placeholder and frontend quality targets.
- tools/quality: Shared duplication and verification tooling.
- docker-compose.yml: Local stack orchestration for pipeline, backend, frontend, and development-only PostgreSQL db service.
- docker/compose/stack.env: Canonical local DB defaults (host/port/db/user/password) for development workflows.

## Rules

- No product business logic is allowed in baseline placeholders.
- Pipeline is upstream of backend placeholders, and frontend only consumes backend boundaries.
- Cross-project dependencies must be explicit and minimal.
- Quality targets must remain project-scoped and affected-aware.

## Contract Workflow Boundaries

- `apps/pipeline/src/contract/**` owns canonical validation, source normalization, provenance guards, lineage creation, and taxonomy/geography mapping.
- `apps/backend/src/contract/query/**` owns read-side projections, audit retrieval, and hierarchy-aware filter expansion.
- `libs/db/src/db/models/**` and `libs/db/src/db/repositories/**` own shared persistence entities and repository interfaces/adapters consumed by both apps.
- `libs/db/alembic/**` is the sole migration authority for shared contract persistence.
- `tools/quality/local-stack/test-local-db-bootstrap.sh`, `tools/quality/local-stack/run-db-migrations.sh`, and `tools/quality/local-stack/check-db-revision.sh` are canonical local DB bootstrap/migration verification entry points.
- `tools/quality/local-stack/test-db-readiness.sh` is the canonical end-to-end local readiness verification command.
