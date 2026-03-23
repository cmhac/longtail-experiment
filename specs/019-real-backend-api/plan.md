# Implementation Plan: Real Backend Discovery API Runtime

**Branch**: `019-real-backend-api` | **Date**: 2026-03-23 | **Spec**: `specs/019-real-backend-api/spec.md`
**Input**: Feature specification from `/specs/019-real-backend-api/spec.md`

**Note**: This template is filled in by the `/speckit.plan` command. See `.specify/templates/plan-template.md` for the execution workflow.

## Summary

Replace fixture-backed discovery runtime behavior with persisted-data-backed behavior for all backend discovery surfaces (search, recent, catalog, detail), while allowing fixtures only in automated tests. The plan removes runtime seed wiring, introduces a persisted repository-backed service composition for HTTP startup, and adds end-to-end ingest-to-API parity checks plus documentation updates so local and CI verification reflect production-intent data behavior.

## Technical Context

**Language/Version**: Python 3.12 for backend runtime and query composition  
**Primary Dependencies**: Existing backend query/service modules in `apps/backend/src/query`, SQLAlchemy-based repository access in `libs/db/src/db/repositories`, Pydantic contract models in `apps/backend/src/contract`, psycopg/PostgreSQL runtime stack via existing local infrastructure  
**Storage**: PostgreSQL 16 canonical dataset store (`source_profiles`, `data_series`, `observations`, topic tag tables)  
**Testing**: pytest (backend unit/contract/integration), existing local-stack scripts, Nx affected quality checks  
**Target Platform**: Unified Docker Compose local stack and CI validation runs  
**Project Type**: Nx monorepo backend runtime and contract integration feature  
**Performance Goals**: Maintain deterministic response behavior and practical local-stack responsiveness for discovery surfaces on current dataset volume  
**Constraints**: No runtime fixture fallback, no contract regressions for not-found semantics, no quality gate bypasses, preserve provenance/timestamp semantics and deterministic ordering  
**Scale/Scope**: Backend HTTP runtime composition, query/repository wiring, contract/integration tests, and runbook/spec documentation updates

## Constitution Check

_GATE: Must pass before Phase 0 research. Re-check after Phase 1 design._

- Monorepo cohesion: PASS. Work remains within existing backend and shared DB boundaries, with spec artifacts updated in the same feature scope.
- Quality gate enforcement: PASS. Plan relies on existing lint/format/typecheck/test/coverage commands with no suppression strategy.
- Test and coverage discipline: PASS. Plan requires integration coverage for ingest-to-API parity and runtime non-fixture behavior to preserve >=90% standards.
- Local-first parity: PASS. Plan explicitly verifies compose-backed startup, migrations, ingest, and API responses from persisted data.
- Data integrity and reliability: PASS. Read behavior continues to derive from canonical persisted tables and deterministic ordering rules.
- Documentation fidelity: PASS. Plan includes quickstart/spec updates and downstream runbook alignment for operational accuracy.

## Project Structure

### Documentation (this feature)

```text
specs/019-real-backend-api/
├── spec.md
├── plan.md
├── research.md
├── data-model.md
├── quickstart.md
├── contracts/
│   └── runtime-discovery-contract.md
├── checklists/
│   └── requirements.md
└── tasks.md
```

### Source Code (repository root)

```text
apps/
└── backend/
    ├── src/
    │   ├── http_api_server.py
    │   ├── contract/
    │   │   └── query/
    │   └── query/
    │       ├── dataset_discovery_service.py
    │       ├── dataset_discovery_runtime_repository.py
    │       ├── dataset_discovery_persisted_repository.py
    │       └── dataset_discovery_seed.py
    └── tests/
        ├── contract/
        ├── fixtures/
        └── ...

libs/
└── db/
    └── src/db/repositories/
        └── dataset_discovery_repository.py

tools/
└── quality/local-stack/

docs/
└── runbooks/
```

**Structure Decision**: Keep discovery query contracts stable while changing runtime composition to persisted-data-backed repository wiring in backend startup. Preserve fixture usage only for test modules and test-only fixtures, not runtime startup.

## Complexity Tracking

| Violation | Why Needed | Simpler Alternative Rejected Because |
| --------- | ---------- | ------------------------------------ |
| None      | N/A        | N/A                                  |

## Phase 0: Research

Research outcomes are captured in `research.md` and resolve runtime architecture choices:

- Runtime composition strategy that guarantees persisted-data sourcing and eliminates runtime fixture fallback.
- Test-scope-only fixture policy with clear boundaries between runtime and test wiring.
- Ingest-to-API parity verification strategy for local and CI loops.
- Deterministic ordering and no-regression handling for detail/search/recent/catalog responses.

## Phase 1: Design & Contracts

### Data Model

Define persisted-runtime read projections and verification evidence entities in `data-model.md`, including fixture-boundary constraints and parity assertions.

### Interface Contracts

Define runtime discovery behavior and verification contracts in `contracts/runtime-discovery-contract.md`, including fixture prohibition in runtime execution paths and unchanged not-found behavior.

### Quickstart

Document local runtime validation in `quickstart.md`, including compose startup, migration checks, ingest execution, and API parity verification proving persisted-data behavior.

### Agent Context Update

Run `.specify/scripts/bash/update-agent-context.sh codex` after plan artifacts are generated.

## Post-Design Constitution Re-Check

- Monorepo cohesion: PASS
- Quality gate enforcement: PASS
- Test and coverage discipline: PASS
- Local-first parity: PASS
- Data integrity and reliability: PASS
- Documentation fidelity: PASS

## Phase 2: Task Planning Approach

`/speckit.tasks` should generate dependency-ordered tasks across:

1. Backend runtime composition changes to remove fixture-backed startup paths and wire persisted repository-backed discovery service.
2. Query/service integration updates to ensure all discovery surfaces read canonical persisted records with deterministic ordering.
3. Test updates that allow fixtures only in automated tests and add explicit runtime non-fixture assertions.
4. End-to-end ingest-to-API parity tests and local verification scripts/steps.
5. Documentation updates for runbooks, quickstart verification, and migration/runtime expectations.

## Implementation Finalization Notes

- Fixtures remain valid only for automated tests and test helpers.
- Runtime startup and fallback paths must not include seed-backed discovery data wiring.
- Existing endpoint shapes and explicit not-found contracts remain stable unless explicitly versioned.
