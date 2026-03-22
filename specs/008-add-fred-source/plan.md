# Implementation Plan: FRED Interest Rate Source

**Branch**: `[008-add-fred-source]` | **Date**: 2026-03-22 | **Spec**: `specs/008-add-fred-source/spec.md`
**Input**: Feature specification from `specs/008-add-fred-source/spec.md`

## Summary

Add the first production-style external source workflow for FRED interest-rate data,
including local secret-based credential loading, robust provider-response validation,
incremental fetch behavior, and durable observation persistence. The plan explicitly
includes enabling work discovered during analysis: the current pipeline runtime still
uses a discard-only observation repository, so this feature must also wire canonical
observations into Postgres-backed storage and ship the required migration(s)/adapters.

## Technical Context

**Language/Version**: Python 3.12 (pipeline/backend), TypeScript 5.x unchanged  
**Primary Dependencies**: Dagster 1.x, Pydantic 2.x, SQLAlchemy 2.x, psycopg 3.x, requests/httpx adapter for external provider calls, uv, pytest  
**Storage**: PostgreSQL 16 local runtime DB; existing runtime tables plus new canonical observation persistence path (currently missing in runtime wiring)  
**Testing**: pytest + pytest-cov; unit tests for source adapter/validation; orchestration integration tests; migration/repository tests under libs/db  
**Target Platform**: macOS/Linux local dev via Docker Compose  
**Project Type**: Nx monorepo data platform; pipeline orchestration feature with shared DB contract impact  
**Performance Goals**: In local verification on standard developer hardware, a scheduled run for `fred_fedfunds` completes within 120 seconds at p95 across 10 runs; a second run with unchanged upstream data adds zero new observations and completes within 30 seconds at p95  
**Constraints**: No quality-gate bypasses; maintain ≥90% coverage in affected projects; secrets must come from local secret env files and never be committed; feature scope must absorb discovered blockers  
**Scale/Scope**: Initial single source (`fred_fedfunds`) with extensible pattern for future external sources; expected low-frequency scheduled polling

## Constitution Check

_GATE: Must pass before Phase 0 research. Re-check after Phase 1 design._

- Monorepo cohesion: PASS. Changes stay within `apps/pipeline`, `libs/db`, docs/runbooks, and specs; no ad hoc sidecar components.
- Quality gate enforcement: PASS. Plan uses existing ruff/ty/pytest/coverage gates with no suppression strategy.
- Test and coverage discipline: PASS. Plan includes unit, integration, contract, and migration tests to preserve ≥90% affected coverage.
- Local-first parity: PASS. Feature is runnable in local Docker Compose stack with secret file setup and migration scripts.
- Data integrity and reliability: PASS with explicit design requirement for idempotent upsert semantics and revision-safe schema changes.
- Documentation fidelity: PASS. Plan includes updates for quickstart, runbook, onboarding docs, and AGENTS command references if canonical commands change.

## Project Structure

### Documentation (this feature)

```text
specs/008-add-fred-source/
├── spec.md
├── plan.md
├── research.md
├── data-model.md
├── quickstart.md
├── contracts/
│   └── fred-interest-rate-contract.md
├── checklists/
│   └── requirements.md
└── tasks.md
```

### Source Code (repository root)

```text
apps/
└── pipeline/
    ├── src/
    │   ├── contract/
    │   │   └── services/
    │   │       └── canonical_ingest_service.py               ← keep canonical validation contract
    │   └── orchestration/
    │       ├── jobs/
    │       │   ├── sources/
    │       │   │   └── fred_fedfunds_source.py               ← new source workflow adapter
    │       │   └── source_ingest_runner.py                   ← no semantic change expected
    │       ├── resources/
    │       │   └── postgres_observation_repository.py        ← new durable observation adapter
    │       └── runtime.py                                    ← register source + wire durable repo
    └── tests/
        ├── contract/
        │   └── test_ingest_frequency_handling.py             ← compatibility coverage
        └── orchestration/
            ├── test_definitions_smoke.py                     ← runtime registration assertions
            ├── test_fred_source_workflow.py                  ← adapter behavior and failure modes
            └── test_ingest_job_runtime.py                    ← end-to-end persistence assertions

libs/
└── db/
    ├── alembic/
    │   └── versions/
    │       └── 0004_observation_store.py                     ← new migration for canonical tables
    └── tests/
        └── test_ingestion_runtime_migrations.py              ← migration metadata/table assertions

docker/
└── compose/
    ├── .gitignore                                             ← ensure local secrets remain ignored
    ├── local.secrets.env.example                              ← operator template for FRED_API_KEY
    └── stack.env                                               ← base stack vars only (no secrets)
```

**Structure Decision**: Extend existing pipeline orchestration and shared DB modules.
No new app or service is introduced; this is a vertical slice across source adapter,
runtime wiring, DB migration/repository, and operator docs.

## Complexity Tracking

| Violation | Why Needed | Simpler Alternative Rejected Because |
| --------- | ---------- | ------------------------------------ |
| None      | N/A        | N/A                                  |

## Implementation Consistency Notes

- Discovered blocker captured in scope: runtime currently instantiates a discard-only
  observation repository, so real source data cannot persist without enabling work.
- Plan therefore includes migration + Postgres observation repository wiring as part of
  this feature, not deferred follow-up.
- Credentials are sourced from local secret env file path under `docker/compose` and
  surfaced to the source workflow through runtime environment configuration.
- Source integration follows existing `SourceWorkflowRegistration` pattern and existing
  run outcome aggregation/scheduling behavior.

## Phase 0: Research

All planning unknowns were resolved in `research.md`, including provider integration
choices, canonical persistence enabling strategy, and incremental fetch semantics.

## Phase 1: Design & Contracts

### Data Model

See `data-model.md` for source credential context, external observation mapping, and
new canonical persistence entities/constraints.

### Interface Contracts

See `contracts/fred-interest-rate-contract.md` for source adapter input/output,
credential requirements, error mapping, and persistence interface expectations.

### Quickstart

See `quickstart.md` for local secret setup, migration application, first ingest run,
incremental re-run verification, and troubleshooting.

## Phase 2: Task Planning Approach

`/speckit.tasks` will produce a dependency-ordered task list that separates:

1. Enabling data-store and migration work.
2. FRED source adapter implementation and runtime wiring.
3. Test suites (unit/integration/migration/contract).
4. Documentation and operator workflow finalization.

## Blocker Update Protocol

When a delivery blocker is confirmed during implementation, update artifacts in this
order within the same working session:

1. Add or update the blocker entry in `spec.md` Gap Log with impact, owner,
   resolution target, and status.
2. Reflect architecture or dependency implications in this plan, including whether
   migration, contract, or runtime wiring scope expands.
3. Ensure corresponding implementation tasks exist in `tasks.md`; add explicit
   dependencies and test coverage tasks for any new scope.
4. If a blocker is deferred, include owner-approved deferral rationale and expected
   re-entry trigger in both spec and tasks.
