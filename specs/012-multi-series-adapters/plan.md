# Implementation Plan: Multi-Series Source Adapter Model

**Branch**: `012-multi-series-adapters` | **Date**: 2026-03-22 | **Spec**: `specs/012-multi-series-adapters/spec.md`
**Input**: Feature specification from `/specs/012-multi-series-adapters/spec.md`

**Note**: This template is filled in by the `/speckit.plan` command. See `.specify/templates/plan-template.md` for the execution workflow.

## Summary

Extend the source-asset ingestion model so one provider adapter can ingest multiple series while preserving operator-visible, independently triggerable series items and allowing optional split-adapter ownership for divergent cadence needs. Delivery prioritizes a grouped-adapter default (single cadence) with clear migration and coexistence rules for later split models.

## Technical Context

**Language/Version**: Python 3.12 (pipeline/backend), TypeScript 5.x unchanged  
**Primary Dependencies**: Dagster 1.x, Pydantic 2.x, SQLAlchemy 2.x, psycopg 3.x, structlog, OpenTelemetry API/SDK, uv, pytest, Nx tooling  
**Storage**: PostgreSQL 16 runtime store plus canonical observation store (`source_profiles`, `data_series`, `observations`)  
**Testing**: pytest and pytest-cov in pipeline/backend, orchestration integration tests, Nx affected quality targets, local-stack scripts  
**Target Platform**: Local-first macOS/Linux developer environments and CI runners  
**Project Type**: Nx monorepo data-platform orchestration/runtime feature  
**Performance Goals**: >=95% successful series-targeted manual runs without unrelated executions; zero duplicate scheduled triggers in grouped/split coexistence validation; 100% traceability of grouped-run series outcomes  
**Constraints**: Preserve source-asset scheduling authority and operator visibility from features 010/011; no quality-gate suppressions; maintain >=90% coverage in affected projects; maintain forward-only data integrity during ownership transitions  
**Scale/Scope**: Initial rollout validates one provider group with at least two series (for example FEDFUNDS and GASREGW) and defines reusable patterns for future multi-series providers

## Constitution Check

_GATE: Must pass before Phase 0 research. Re-check after Phase 1 design._

- Monorepo cohesion: PASS. Changes remain in existing pipeline, db, docs, and quality-script boundaries with no new project boundaries.
- Quality gate enforcement: PASS. Plan uses existing lint/format/typecheck/test gates with no bypass path.
- Test and coverage discipline: PASS. Plan includes grouped and split execution tests to preserve >=90% coverage in affected pipeline/db modules.
- Local-first parity: PASS. Plan includes compose + Dagit verification updates for grouped and series-targeted execution paths.
- Data integrity and reliability: PASS. Plan defines series identity persistence, outcome attribution, and duplicate-trigger safeguards during ownership changes.
- Documentation fidelity: PASS. Plan includes runbook/onboarding updates and AGENTS updates for canonical adapter ownership guidance.

## Project Structure

### Documentation (this feature)

```text
specs/012-multi-series-adapters/
├── spec.md
├── plan.md
├── research.md
├── data-model.md
├── quickstart.md
├── contracts/
│   └── series-ownership-and-triggering-contract.md
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
    │       ├── source_asset_definitions.py
    │       ├── schedules/
    │       │   └── source_asset_schedules.py
    │       └── jobs/
    │           ├── ingest_job.py
    │           ├── run_coordinator.py
    │           ├── workflow_result.py
    │           ├── source_assets/
    │           │   ├── discovery.py
    │           │   ├── ownership_mode.py
    │           │   ├── ownership_transition.py
    │           │   ├── series_catalog.py
    │           │   └── series_selection.py
    │           └── sources/
    │               └── fred_fedfunds_source.py
    └── tests/
        └── orchestration/
            ├── test_fred_source_workflow.py
            ├── test_series_catalog.py
            ├── test_series_ownership_mode.py
            ├── test_series_ownership_transition.py
            ├── test_source_outcome_visibility.py
            ├── test_definitions_smoke.py
            ├── test_ingest_job_runtime.py
            └── test_trigger_modes.py

libs/
└── db/
    ├── alembic/versions/
    ├── src/db/models/
    └── tests/

docs/
├── runbooks/
│   └── local-stack-baseline.md
├── onboarding/
│   └── monorepo-baseline.md
└── architecture/
    └── monorepo-boundaries.md
```

**Structure Decision**: Extend current orchestration runtime and adapter modules in place. Introduce no new application boundaries; evolve source-level modeling to accommodate series-level items and ownership modes.

## Complexity Tracking

| Violation | Why Needed | Simpler Alternative Rejected Because |
| --------- | ---------- | ------------------------------------ |
| None      | N/A        | N/A                                  |

## Phase 0: Research

Resolve policy and behavioral decisions for grouped vs split adapter ownership so implementation can proceed without ambiguities.

- Confirm grouped adapter default semantics and allowed split strategy for divergent cadence.
- Define conflict-prevention strategy when series ownership transitions between grouped and split.
- Define operator visibility expectations for series items under shared provider grouping.
- Confirm minimal viable scope for initial provider validation set.

Output captured in `research.md`.

## Phase 1: Design & Contracts

### Data Model

Define provider group, series item, ownership mode, and series-level outcome entities including validation and lifecycle transitions. Output in `data-model.md`.

### Interface Contracts

Define runtime and operator-facing contracts for grouped execution, series-targeted execution, ownership attribution, and migration guardrails. Output in `contracts/series-ownership-and-triggering-contract.md`.

### Quickstart

Define local validation flow for grouped ingestion and series-specific triggering, including quality-gate and compose verification commands. Output in `quickstart.md`.

### Agent Context Update

Run `.specify/scripts/bash/update-agent-context.sh codex` after design artifacts are generated.

## Post-Design Constitution Re-Check

- Monorepo cohesion: PASS
- Quality gate enforcement: PASS
- Test and coverage discipline: PASS
- Local-first parity: PASS
- Data integrity and reliability: PASS
- Documentation fidelity: PASS

## Phase 2: Task Planning Approach

`/speckit.tasks` should generate dependency-ordered tasks across:

1. Adapter model refactor for multi-series grouped ingestion within one provider adapter.
2. Series-item catalog and trigger semantics that support independent runs.
3. Ownership-mode support (grouped and split) with duplicate-trigger prevention.
4. Series-level outcome attribution and persistence mapping adjustments.
5. Regression and integration tests for grouped, split, migration, and mixed-mode operations.
6. Documentation updates in runbooks, onboarding, architecture docs, and AGENTS command references.

## Implementation Finalization Notes

- Initial delivery prioritizes grouped adapters with shared cadence.
- Split adapters remain an explicitly supported operational strategy, not a mandatory default.
- Ownership migration guardrails must protect traceability and prevent duplicate ingestion.
