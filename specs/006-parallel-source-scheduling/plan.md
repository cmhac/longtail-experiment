# Implementation Plan: Parallel Source Scheduling and Bounded Concurrency

**Branch**: `[006-parallel-source-scheduling]` | **Date**: 2026-03-21 | **Spec**: `/Users/hackerc/Projects/longtail-experiment/specs/006-parallel-source-scheduling/spec.md`
**Input**: Feature specification from `/Users/hackerc/Projects/longtail-experiment/specs/006-parallel-source-scheduling/spec.md`

**Note**: This template is filled in by the `/speckit.plan` command. See `.specify/templates/plan-template.md` for the execution workflow.

## Summary

Add explicit per-source scheduling policy and bounded parallel source execution to the
ingestion orchestrator so run throughput scales while respecting source cadence
requirements. The approach keeps orchestration logic in `apps/pipeline`, persists
run/eligibility outcomes through shared DB runtime tables, and preserves operator
visibility by extending run-level audit records with due/executed/deferred semantics.

## Technical Context

<!--
  ACTION REQUIRED: Replace the content in this section with the technical details
  for the project. The structure here is presented in advisory capacity to guide
  the iteration process.
-->

**Language/Version**: Python 3.12 (pipeline/backend/shared DB), TypeScript 5.x unchanged  
**Primary Dependencies**: Dagster 1.x, Pydantic 2.x, SQLAlchemy 2.x, Alembic, psycopg 3.x, Nx tooling  
**Storage**: PostgreSQL 16 local runtime DB persisted via `ingestion_runs` and `source_run_outcomes` tables  
**Testing**: pytest + pytest-cov, orchestration integration tests, contract tests, affected quality scripts  
**Target Platform**: macOS/Linux local dev via Docker Compose; Python pipeline service runtime
**Project Type**: Nx monorepo data platform feature (pipeline orchestration + shared runtime persistence)  
**Performance Goals**: Keep active source executions within configured limit in 100% of runs; avoid two consecutive missed due windows for hourly/daily sources over two weeks  
**Constraints**: No quality-gate bypasses; >=90% coverage in affected projects; deterministic source launch order; source-level duplicate execution protection in overlapping runs  
**Scale/Scope**: Dozens to low hundreds of registered sources with mixed cadences (hourly through monthly+)

## Constitution Check

_GATE: Must pass before Phase 0 research. Re-check after Phase 1 design._

- Monorepo cohesion: Does the plan preserve clear Nx project boundaries and include
  cross-layer contract updates for vertical-slice changes?
- Quality gate enforcement: Are lint, format, type-check, and test gates defined with no
  suppression, bypass, or workaround strategy?
- Test and coverage discipline: Does the plan include automated tests needed to maintain
  > = 90% coverage across affected backend/frontend projects?
- Local-first parity: Can the complete impacted flow run locally via unified Docker
  Compose, and are compose/healthcheck updates identified?
- Data integrity and reliability: Are data provenance, schema/contract versioning, and
  trend/alert regression protections explicitly designed?
- Documentation fidelity: Does the plan identify all documentation that MUST be added or
  updated for the proposed code and behavior changes?

- Pre-Design Gate Review (PASS)
- Monorepo cohesion: PASS. Work is scoped to pipeline orchestration and shared DB runtime persistence without breaking app boundaries.
- Quality gate enforcement: PASS. Existing lint, format, type-check, test, and coverage gates remain mandatory.
- Test and coverage discipline: PASS. Plan includes bounded-concurrency, cadence-selection, and visibility test coverage with >=90% preservation.
- Local-first parity: PASS. Feature remains runnable through local Docker Compose DB + pipeline execution paths.
- Data integrity and reliability: PASS. Source-level overlap protection and persisted eligibility/outcome audit semantics are explicit.
- Documentation fidelity: PASS. Plan includes updates to quickstart/runbooks/onboarding plus AGENTS.md when commands or workflows change.

- Post-Design Gate Review (PASS)
- Monorepo cohesion: PASS. Data model and contracts keep source policy metadata in orchestration registration boundaries and persistence in shared DB boundaries.
- Quality gate enforcement: PASS. No suppression strategy introduced.
- Test and coverage discipline: PASS. Planned tests map directly to FR-001..FR-015 and SC-001..SC-004.
- Local-first parity: PASS. Design includes local scheduling verification and on-demand subset execution checks.
- Data integrity and reliability: PASS. Due-state snapshots, deterministic launch ordering, and overlap safety are modeled.
- Documentation fidelity: PASS. Feature artifacts and run instructions are included for same-change delivery.

## Project Structure

### Documentation (this feature)

```text
specs/006-parallel-source-scheduling/
├── plan.md
├── research.md
├── data-model.md
├── quickstart.md
├── contracts/
│   ├── source-schedule-policy-contract.md
│   ├── bounded-parallel-execution-contract.md
│   └── run-eligibility-audit-contract.md
└── tasks.md
```

### Source Code (repository root)

<!--
  ACTION REQUIRED: Replace the placeholder tree below with the concrete layout
  for this feature. Delete unused options and expand the chosen structure with
  real paths (e.g., apps/admin, packages/something). The delivered plan must
  not include Option labels.
-->

```text
apps/
├── pipeline/
│   ├── src/
│   │   └── orchestration/
│   │       ├── definitions.py
│   │       ├── runtime.py
│   │       ├── jobs/
│   │       │   ├── run_coordinator.py
│   │       │   ├── workflow_registry.py
│   │       │   └── sources/
│   │       ├── schedules/
│   │       ├── sensors/
│   │       └── resources/
│   └── tests/
│       └── orchestration/
├── backend/
│   └── tests/contract/
└── frontend/
  └── (no feature-scope changes)

libs/
└── db/
  ├── src/db/
  │   ├── models/
  │   └── repositories/
  ├── alembic/
  │   └── versions/
  └── tests/

docs/
├── onboarding/
├── runbooks/
└── architecture/
```

**Structure Decision**: Extend the existing orchestration and shared DB persistence
boundaries; no new top-level project is introduced. Source schedule metadata lives with
source workflow registration, and run eligibility/outcome persistence remains in shared
runtime DB tables consumed by pipeline and backend operational checks.

## Complexity Tracking

> **Fill ONLY if Constitution Check has violations that must be justified**

| Violation | Why Needed | Simpler Alternative Rejected Because |
| --------- | ---------- | ------------------------------------ |
| None      | N/A        | N/A                                  |

## Implementation Consistency Notes

- Bounded parallelism applies per orchestration run and must be operator configurable.
- Scheduled runs evaluate due-state per source and include only due sources by default.
- On-demand runs may explicitly select source subsets and bypass cadence exclusion for
  selected sources only.
- Source launch order remains strict FIFO by earliest due timestamp.
- Overlapping run safety remains source-scoped to prevent duplicate concurrent execution.
- When scheduled runs exceed a tick boundary, active work completes and remaining due
  sources are carried forward as deferred with warning-level signals.
- Missing or malformed cadence policy metadata is treated as `skipped_invalid_policy`
  with warning-level operational signals.
