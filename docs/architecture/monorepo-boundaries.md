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
- `apps/pipeline/src/orchestration/**` owns workflow registration, trigger execution, per-source concurrency policy, duplicate drift classification, and conflict/run summary persistence orchestration.
- `apps/backend/src/contract/query/**` owns read-side projections, audit retrieval, and hierarchy-aware filter expansion.
- `libs/db/src/db/models/**` and `libs/db/src/db/repositories/**` own shared persistence entities and repository interfaces/adapters consumed by both apps.
- `libs/db/alembic/**` is the sole migration authority for shared contract persistence.
- `tools/quality/local-stack/test-local-db-bootstrap.sh`, `tools/quality/local-stack/run-db-migrations.sh`, and `tools/quality/local-stack/check-db-revision.sh` are canonical local DB bootstrap/migration verification entry points.
- `tools/quality/local-stack/test-db-readiness.sh` is the canonical end-to-end local readiness verification command.

## Conflict Queryability Boundary

- Conflict lifecycle writes are produced in pipeline orchestration modules and persisted via shared DB repositories.
- Backend audit projection may enrich provenance/revision rows with conflict identifiers, but does not own conflict lifecycle state transitions.
- Shared DB migration and model updates are required whenever conflict record schema changes.

## Per-Source Scheduling Boundary (Feature 006)

- `apps/pipeline/src/orchestration/jobs/source_schedule_policy.py` owns cadence policy parsing and validation.
- `apps/pipeline/src/orchestration/jobs/due_source_selector.py` owns due/not-due eligibility decisions and deterministic source ordering for scheduled runs.
- `apps/pipeline/src/orchestration/jobs/parallel_source_executor.py` owns bounded active-source launch policy.
- `apps/pipeline/src/orchestration/resources/postgres_run_repository.py` owns persistence of run-level due/executed/deferred/not-due counters and per-source eligibility snapshots.

## Per-Source Schedule Ownership Boundary (Feature 011)

- `apps/pipeline/src/orchestration/schedules/source_asset_schedules.py` owns per-source Dagster schedule definitions.
- Each source asset schedule directly targets `ingest_job` with source-specific tags.
- The shared `ingest_schedule` (hourly all-source trigger) is retired and not active post-cutover.
- `apps/pipeline/src/orchestration/definitions.py` registers per-source schedules and no shared schedule.
- Legacy `source_schedule_policies` and `source_eligibility_snapshots` tables are historical-only after migration `0005_source_asset_schedule_cutover`.
