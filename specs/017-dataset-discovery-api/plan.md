# Implementation Plan: Dataset Discovery Backend API

**Branch**: `017-dataset-discovery-api` | **Date**: 2026-03-23 | **Spec**: `specs/017-dataset-discovery-api/spec.md`
**Input**: Feature specification from `/specs/017-dataset-discovery-api/spec.md`

**Note**: This template is filled in by the `/speckit.plan` command. See `.specify/templates/plan-template.md` for the execution workflow.

## Summary

Deliver backend read APIs and query contracts that power dataset discovery and detail experiences: landing-page search, recent updates, full catalog browsing by source, and per-dataset detail with full chronological observations. The implementation uses additive schema/index updates where needed, deterministic query ordering, and backend contract/integration tests to preserve performance, correctness, and constitution quality gates.

## Technical Context

**Language/Version**: Python 3.12 for backend query layer; SQL targeting PostgreSQL 16  
**Primary Dependencies**: SQLAlchemy 2.x models/repositories in `libs/db`, psycopg 3.x runtime access, Pydantic 2.x contract models, existing backend contract/query modules in `apps/backend/src`  
**Storage**: PostgreSQL 16 canonical dataset store (`source_profiles`, `data_series`, `observations`, topic tag relation tables)  
**Testing**: pytest (backend contract and integration tests), existing Nx quality targets for affected projects  
**Target Platform**: Local Docker Compose stack and CI runners for backend quality/test verification  
**Project Type**: Nx monorepo backend API/query feature with shared DB migration updates  
**Performance Goals**: Discovery endpoints return deterministic, paginated result sets with responsive query plans on current local dataset baseline; detail retrieval supports full-series chart rendering without unstable ordering  
**Constraints**: Preserve strict lint/format/typecheck/test/coverage gates; no suppression bypasses; additive schema evolution only; explicit not-found behavior; maintain source/timestamp provenance  
**Scale/Scope**: Four read surfaces (search, recent, catalog, detail), optional observation range controls, migration/index additions, backend docs and tests in scope

## Constitution Check

_GATE: Must pass before Phase 0 research. Re-check after Phase 1 design._

- Monorepo cohesion: PASS. Changes are contained to backend query/contract modules, shared DB migrations, and spec/docs artifacts within established Nx boundaries.
- Quality gate enforcement: PASS. Plan requires backend and affected workspace quality commands with no bypass strategy.
- Test and coverage discipline: PASS. Plan includes dedicated contract/integration tests for each read surface and expects >=90% coverage in affected backend scope.
- Local-first parity: PASS. Plan includes local Compose-backed verification and migration execution using existing local-stack scripts.
- Data integrity and reliability: PASS. Read models preserve canonical identifiers, source attribution, and observation timestamp ordering with explicit schema/index versioning.
- Documentation fidelity: PASS. Plan includes updates to spec artifacts, quickstart validation steps, API contract doc, and downstream runbook/documentation touchpoints as implementation proceeds.

## Project Structure

### Documentation (this feature)

```text
specs/017-dataset-discovery-api/
├── spec.md
├── plan.md
├── research.md
├── data-model.md
├── quickstart.md
├── contracts/
│   └── dataset-discovery-api-contract.md
├── checklists/
│   └── requirements.md
└── tasks.md
```

### Source Code (repository root)

```text
apps/
└── backend/
    ├── src/
    │   ├── contract/
    │   │   └── query/
    │   └── query/
    └── tests/
        ├── contract/
        └── fixtures/

libs/
└── db/
    ├── alembic/
    │   └── versions/
    └── src/db/
        ├── models/
        └── repositories/

docs/
└── runbooks/
```

**Structure Decision**: Extend existing backend query contract and query modules in place, add supporting database migrations/indexes in `libs/db/alembic/versions`, and validate behavior with backend tests under `apps/backend/tests` while documenting operations in feature docs.

## Complexity Tracking

| Violation | Why Needed | Simpler Alternative Rejected Because |
| --------- | ---------- | ------------------------------------ |
| None      | N/A        | N/A                                  |

## Phase 0: Research

Research outcomes are captured in `research.md` and resolve discovery/detail design choices:

- Search matching strategy across metadata and tags, including index implications.
- Recent-updates derivation from canonical observation timestamps.
- Catalog pagination and deterministic ordering semantics.
- Detail payload boundary for metadata plus chronological observations.
- Additive schema/index strategy to satisfy discovery/read performance goals.

## Phase 1: Design & Contracts

### Data Model

Define backend read models and validation constraints in `data-model.md` for search, catalog, recent updates, dataset detail, and observation payloads.

### Interface Contracts

Define request/response and error contracts for discovery and detail endpoints in `contracts/dataset-discovery-api-contract.md`.

### Quickstart

Document local migration, validation, and verification workflow in `quickstart.md`, including backend tests and local-stack commands.

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

1. Backend contract model and query service scaffolding for search, recent, catalog, and detail surfaces.
2. Database migration work for any required search/recency indexes or additive columns/views.
3. Query implementation for metadata/tag search, source grouping/filtering, deterministic pagination, and chronological detail retrieval.
4. Contract/integration tests covering happy paths, edge cases, and explicit not-found behavior.
5. Documentation and runbook updates for local verification and operational expectations.

## Implementation Finalization Notes

- Keep this feature read-only; no ingest or mutation behavior is introduced.
- Reuse canonical dataset identifiers and existing provenance/timestamp semantics.
- Ensure tie-breaking rules are explicit and test-verified to avoid non-deterministic UI behavior.
