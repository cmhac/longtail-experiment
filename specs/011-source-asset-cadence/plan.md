# Implementation Plan: Per-Source Asset Cadence

**Branch**: `[011-source-asset-cadence]` | **Date**: 2026-03-22 | **Spec**: `specs/011-source-asset-cadence/spec.md`
**Input**: Feature specification from `specs/011-source-asset-cadence/spec.md`

**Note**: This template is filled in by the `/speckit.plan` command. See `.specify/templates/plan-template.md` for the execution workflow.

## Summary

Replace the shared hourly ingestion schedule and internal due-selection subsystem with source-owned Dagster cadence definitions so each source asset runs on its own schedule. This plan delivers a hard cutover that retires shared schedule authority, preserves source-level run visibility, and updates persistence and operator docs to reflect the new schedule ownership model.

## Technical Context

**Language/Version**: Python 3.12 (pipeline/backend), TypeScript 5.x unchanged  
**Primary Dependencies**: Dagster 1.x, Pydantic 2.x, SQLAlchemy 2.x, psycopg 3.x, structlog, OpenTelemetry API/SDK, uv, pytest, Nx tooling  
**Storage**: PostgreSQL 16 runtime store for ingestion run and source outcome visibility; schema currently includes legacy cadence/eligibility structures that will be rationalized  
**Testing**: pytest and pytest-cov for pipeline/backend, orchestration smoke tests, Nx affected targets, local-stack verification scripts  
**Target Platform**: Local-first macOS/Linux developer environments and CI runners
**Project Type**: Nx monorepo data platform feature in pipeline orchestration runtime and runbooks  
**Performance Goals**: Independent source schedules produce expected run timing with zero duplicate schedule triggers; operator verification of source cadence in Dagit for all active sources  
**Constraints**: Hard cutover to source-owned schedule model; no shared all-sources schedule in active runtime; no quality-gate bypasses; maintain >=90% coverage for affected projects  
**Scale/Scope**: All active source assets currently represented in runtime discovery and Dagit catalog, plus future source additions following the same scheduling model

## Constitution Check

_GATE: Must pass before Phase 0 research. Re-check after Phase 1 design._

- Monorepo cohesion: PASS. Changes stay inside existing pipeline, db, docs, and quality-script boundaries with no new project boundary.
- Quality gate enforcement: PASS. Plan uses existing lint, format, typecheck, and test gates with no suppression strategy.
- Test and coverage discipline: PASS. Plan includes replacement tests for schedule ownership and retention of source outcome visibility to maintain >=90% coverage expectations.
- Local-first parity: PASS. Plan includes compose and Dagit verification steps for source-specific schedule registration and behavior.
- Data integrity and reliability: PASS. Plan explicitly addresses hard-cutover persistence semantics and migration guidance for legacy schedule artifacts.
- Documentation fidelity: PASS. Plan includes runbook/onboarding updates and AGENTS alignment when canonical scheduling commands or structure change.

## Project Structure

### Documentation (this feature)

```text
specs/011-source-asset-cadence/
├── spec.md
├── plan.md
├── research.md
├── data-model.md
├── quickstart.md
├── checklists/
│   └── requirements.md
├── contracts/
│   └── source-asset-cadence-contract.md
└── tasks.md
```

### Source Code (repository root)

```text
apps/
└── pipeline/
  ├── src/
  │   └── orchestration/
  │       ├── definitions.py
  │       ├── source_asset_definitions.py
  │       ├── runtime.py
  │       ├── jobs/
  │       │   ├── ingest_job.py
  │       │   ├── run_coordinator.py
  │       │   ├── due_source_selector.py
  │       │   ├── source_schedule_policy.py
  │       │   └── source_assets/
  │       ├── schedules/
  │       └── sensors/
  └── tests/
    └── orchestration/

libs/
└── db/
  ├── alembic/
  │   └── versions/
  ├── src/db/models/
  └── tests/

docs/
├── onboarding/
├── runbooks/
└── architecture/

tools/
└── quality/
  └── local-stack/
```

**Structure Decision**: Keep changes in existing orchestration and db modules while replacing schedule ownership semantics. No new project is created; this is a targeted runtime and contract migration within current boundaries.

## Complexity Tracking

> **Fill ONLY if Constitution Check has violations that must be justified**

| Violation | Why Needed | Simpler Alternative Rejected Because |
| --------- | ---------- | ------------------------------------ |
| None      | N/A        | N/A                                  |

## Phase 0: Research

Resolve architecture decisions required for hard cutover from shared cadence to source-owned schedules, including handling of legacy schedule-policy persistence, trigger attribution, and local operator verification.

Research output is captured in `research.md` and resolves all planning unknowns.

## Phase 1: Design & Contracts

### Data Model

See `data-model.md` for entities and lifecycle expectations covering source assets, source schedules, schedule trigger records, and legacy artifact interpretation post-cutover.

### Interface Contracts

See `contracts/source-asset-cadence-contract.md` for externally visible operator and runtime contracts including schedule ownership, trigger attribution, coexistence boundaries, and migration guarantees.

### Quickstart

See `quickstart.md` for local development validation flow, quality checks, and schedule-behavior verification using Dagit and local compose stack.

## Post-Design Constitution Re-Check

- Monorepo cohesion: PASS
- Quality gate enforcement: PASS
- Test and coverage discipline: PASS
- Local-first parity: PASS
- Data integrity and reliability: PASS
- Documentation fidelity: PASS

## Phase 2: Task Planning Approach

`/speckit.tasks` should generate dependency-ordered tasks across:

1. Replace shared ingest schedule with source-specific schedule definitions.
2. Refactor orchestration runtime to remove due-selection and legacy cadence policy ownership from scheduled path.
3. Preserve source-level on-demand capability and source outcome visibility after schedule migration.
4. Rationalize persistence models and migration behavior for legacy schedule-policy and eligibility artifacts.
5. Replace and expand orchestration, persistence, and local-stack tests for per-source schedule behavior.
6. Update runbooks, onboarding, architecture docs, and AGENTS command references impacted by scheduling cutover.

## Implementation Finalization Notes

- This feature is an explicit hard break and should not preserve active shared-schedule execution paths.
- Historical data can remain queryable while current schedule authority is exclusively source-asset cadence.
- Source registration and source visibility in Dagit remain non-negotiable operational requirements.
