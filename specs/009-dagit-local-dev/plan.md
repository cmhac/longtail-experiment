# Implementation Plan: Local Dagit Access

**Branch**: `[009-dagit-local-dev]` | **Date**: 2026-03-22 | **Spec**: `specs/009-dagit-local-dev/spec.md`
**Input**: Feature specification from `specs/009-dagit-local-dev/spec.md`

## Summary

Enable a reliable local developer workflow to start the Dagit UI, load existing orchestration definitions, and validate UI visibility with repeatable commands and troubleshooting guidance. Scope is explicitly local development only, with no infrastructure deployment work included.

## Technical Context

**Language/Version**: Python 3.12 (pipeline/backend), TypeScript 5.x unchanged  
**Primary Dependencies**: Dagster 1.x with Dagit UI (`dagster-webserver`), existing pipeline orchestration modules, uv, pytest, Docker Compose local stack tooling  
**Storage**: PostgreSQL 16 local runtime DB (existing local stack) for orchestration-backed views where required; no new production storage introduced  
**Testing**: pytest + pytest-cov for pipeline tests; existing quality commands under Nx/pnpm and local-stack verification scripts  
**Target Platform**: macOS/Linux local development environments  
**Project Type**: Nx monorepo data-platform feature spanning pipeline runtime wiring, local operator workflow docs, and verification tests  
**Performance Goals**: On a correctly prepared machine, developers can start UI and reach definitions view within 10 minutes; repeated restart cycles succeed consistently across 5 consecutive runs  
**Constraints**: Local-only scope; no infrastructure/deployment automation; no quality gate bypasses; maintain >=90% coverage in affected projects; preserve existing orchestration definitions behavior  
**Scale/Scope**: Single-repository local Dagit visibility for existing jobs/assets/schedules and one-click developer troubleshooting path for common local failures

## Constitution Check

_GATE: Must pass before Phase 0 research. Re-check after Phase 1 design._

- Monorepo cohesion: PASS. Scope stays within existing monorepo projects and documentation with no new sidecar service.
- Quality gate enforcement: PASS. Plan uses established ruff/ty/pytest/Nx quality commands with no suppression strategy.
- Test and coverage discipline: PASS. Plan includes targeted orchestration and startup verification tests to preserve >=90% coverage in affected code.
- Local-first parity: PASS. Feature objective is local runtime usability, aligned with Docker Compose-first workflow and health verification.
- Data integrity and reliability: PASS. No schema contract expansion in this feature; existing definitions and runtime integrity are validated through smoke/definition visibility checks.
- Documentation fidelity: PASS. Plan includes runbook/quickstart updates and keeps AGENTS-aligned command references where needed.

## Project Structure

### Documentation (this feature)

```text
specs/009-dagit-local-dev/
├── spec.md
├── plan.md
├── research.md
├── data-model.md
├── quickstart.md
├── contracts/
│   └── local-dagit-operator-contract.md
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
    │       │   └── workflow_registry.py
    │       └── schedules/
    │           └── ingest_schedule.py
    └── tests/
        └── orchestration/
            ├── test_definitions_smoke.py
            ├── test_orchestration_package_exports.py
            └── test_ingest_job_runtime.py

docs/
└── runbooks/
    └── local-stack-baseline.md

tools/
└── quality/
    └── local-stack/
    ├── start-dagit-local.sh
    ├── stop-dagit-local.sh
    ├── test-dagit-endpoint.sh
        ├── test-compose-stack.sh
        └── test-db-readiness.sh
```

**Structure Decision**: Extend the existing pipeline orchestration package and local-stack operational documentation. No new app/project boundary is introduced; this is a local workflow and verification slice.

## Complexity Tracking

| Violation | Why Needed | Simpler Alternative Rejected Because |
| --------- | ---------- | ------------------------------------ |
| None      | N/A        | N/A                                  |

## Phase 0: Research

All identified unknowns are resolved in `research.md`, including startup entrypoint strategy, local endpoint behavior expectations, and troubleshooting coverage boundaries.

## Phase 1: Design & Contracts

### Data Model

See `data-model.md` for local session lifecycle entities, definition visibility expectations, and verification outcome records.

### Interface Contracts

See `contracts/local-dagit-operator-contract.md` for local startup inputs, expected UI availability behavior, and failure reporting contract.

### Quickstart

See `quickstart.md` for prerequisites, startup commands, verification flow, and troubleshooting steps.

## Post-Design Constitution Re-Check

- Monorepo cohesion: PASS
- Quality gate enforcement: PASS
- Test and coverage discipline: PASS
- Local-first parity: PASS
- Data integrity and reliability: PASS
- Documentation fidelity: PASS

## Phase 2: Task Planning Approach

`/speckit.tasks` should produce dependency-ordered tasks across:

1. Local Dagit startup entrypoint and runtime wiring validation.
2. Definition visibility and smoke/integration test coverage.
3. Troubleshooting diagnostics and operator-facing documentation updates.
4. End-to-end local quality and acceptance verification commands.

## Implementation Finalization Notes

- Local Dagit startup required adding `dagster-webserver` to the pipeline project dependencies.
- Runtime now exposes explicit Dagit verification helpers for resource and source registration checks.
- Local stack verification accepts `VERIFY_DAGIT_ENDPOINT=1` to include Dagit endpoint/workspace checks.
