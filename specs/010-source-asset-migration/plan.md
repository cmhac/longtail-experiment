# Implementation Plan: Source-Per-Asset Migration

**Branch**: `[010-source-asset-migration]` | **Date**: 2026-03-22 | **Spec**: `specs/010-source-asset-migration/spec.md`
**Input**: Feature specification from `specs/010-source-asset-migration/spec.md`

## Summary

Migrate ingestion orchestration from coordinator-centric fan-out to source-per-asset execution, with a one-time greenfield cutover where Dagster becomes the sole scheduling authority. The plan prioritizes source-level operability in Dagit, deterministic source registration, and post-cutover recovery paths without re-enabling legacy scheduling.

## Technical Context

**Language/Version**: Python 3.12 (pipeline/backend), TypeScript 5.x unchanged  
**Primary Dependencies**: Dagster 1.x, Pydantic 2.x, SQLAlchemy 2.x, psycopg 3.x, structlog, OpenTelemetry API/SDK, uv, pytest, Nx tooling  
**Storage**: PostgreSQL 16 local runtime DB (`ingestion_runs`, `source_run_outcomes`, related orchestration tables)  
**Testing**: pytest + pytest-cov for pipeline/backend, orchestration smoke tests, Nx affected quality targets, local-stack verification scripts  
**Target Platform**: Local-first macOS/Linux developer environments and CI runners  
**Project Type**: Nx monorepo data platform feature centered on pipeline orchestration runtime and operational runbooks  
**Performance Goals**: Source-level manual trigger success >=95%; no duplicate non-Dagster schedule-triggered runs after cutover; deterministic source registration on every startup  
**Constraints**: Big-bang cutover, no rollback to legacy scheduler as normal recovery path, no quality-gate bypasses, preserve >=90% affected-project coverage, maintain forward outcome visibility in Dagit and persistence  
**Scale/Scope**: All currently supported sources plus any source onboarded during implementation; migration impacts orchestration runtime assembly, source wiring, schedules/sensors, tests, and documentation

## Constitution Check

_GATE: Must pass before Phase 0 research. Re-check after Phase 1 design._

- Monorepo cohesion: PASS. Changes remain within existing pipeline/backend/docs/tooling boundaries and preserve shared contract alignment.
- Quality gate enforcement: PASS. Plan uses existing ruff/ty/pytest/Nx checks with no suppression strategy.
- Test and coverage discipline: PASS. Includes source-level orchestration and cutover regression tests to preserve >=90% coverage in affected projects.
- Local-first parity: PASS. Plan includes Docker Compose local-stack validation for post-cutover scheduling and operability.
- Data integrity and reliability: PASS. Forward outcome visibility and persistence integrity are explicit acceptance targets despite greenfield parity relaxation.
- Documentation fidelity: PASS. Plan includes runbook, onboarding, and command-path updates for source-as-asset operations.

## Project Structure

### Documentation (this feature)

```text
specs/010-source-asset-migration/
├── spec.md
├── plan.md
├── research.md
├── data-model.md
├── quickstart.md
├── contracts/
│   └── source-asset-orchestration-contract.md
├── checklists/
│   └── requirements.md
└── tasks.md
```

### Source Code (repository root)

```text
apps/
└── pipeline/
    ├── src/
    │   └── orchestration/
    │       ├── definitions.py
    │       ├── runtime.py
    │       ├── jobs/
    │       │   ├── ingest_job.py
    │       │   ├── workflow_registry.py
    │       │   └── sources/
    │       ├── schedules/
    │       └── sensors/
    └── tests/
        └── orchestration/
            ├── test_definitions_smoke.py
            ├── test_ingest_job_runtime.py
            ├── test_scheduler_runtime.py
            └── test_parallel_dispatch.py

docs/
├── runbooks/
│   └── local-stack-baseline.md
└── onboarding/
    └── monorepo-baseline.md

tools/
└── quality/
    └── local-stack/
        ├── test-compose-stack.sh
        ├── start-dagit-local.sh
        └── test-dagit-endpoint.sh
```

**Structure Decision**: Extend existing pipeline orchestration modules and docs in place. No new project boundary is required; this is a runtime orchestration migration within current monorepo architecture.

## Complexity Tracking

| Violation | Why Needed | Simpler Alternative Rejected Because |
| --------- | ---------- | ------------------------------------ |
| None      | N/A        | N/A                                  |

## Phase 0: Research

Resolve unknowns around big-bang cutover safety, deterministic source discovery contracts, and post-cutover failure handling without legacy scheduler fallback. Output captured in `research.md`.

## Phase 1: Design & Contracts

### Data Model

See `data-model.md` for source-asset registration, cutover state, and run outcome visibility models.

### Interface Contracts

See `contracts/source-asset-orchestration-contract.md` for operator trigger, scheduling authority, failure behavior, and validation contracts.

### Quickstart

See `quickstart.md` for local validation flow, cutover verification sequence, and quality commands.

## Post-Design Constitution Re-Check

- Monorepo cohesion: PASS
- Quality gate enforcement: PASS
- Test and coverage discipline: PASS
- Local-first parity: PASS
- Data integrity and reliability: PASS
- Documentation fidelity: PASS

## Phase 2: Task Planning Approach

`/speckit.tasks` should produce dependency-ordered tasks across:

1. Source-as-asset registration and deterministic startup loading.
2. Dagster-only scheduling cutover and legacy scheduling retirement.
3. Source-level trigger, visibility, and partial-failure operational handling.
4. Regression tests for scheduled/manual/deferred/locked scenarios.
5. Runbook/onboarding/verification command updates and acceptance validation.

## Implementation Finalization Notes

- Big-bang cutover is explicit and owner-approved for this early greenfield phase.
- Legacy scheduler/coordinator fallback is not part of normal recovery strategy after cutover.
- Forward run visibility and operator triage remain mandatory despite relaxed historical parity requirements.
