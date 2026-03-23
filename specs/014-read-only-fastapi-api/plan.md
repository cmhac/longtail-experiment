# Implementation Plan: Initial Read-Only FastAPI API For Ingested Data

**Branch**: `014-read-only-fastapi-api` | **Date**: 2026-03-23 | **Spec**: `specs/014-read-only-fastapi-api/spec.md`
**Input**: Feature specification from `/specs/014-read-only-fastapi-api/spec.md`

## Summary

Add the first HTTP API layer to the backend so frontend clients can read data already persisted in the PostgreSQL runtime store. The implementation wires a FastAPI application with six read-only Phase 1 endpoints (`/health`, `/api/runs`, `/api/runs/{run_id}`, `/api/runs/{run_id}/outcomes`, `/api/runs/{run_id}/eligibility`, `/api/conflicts`) backed by SQLAlchemy read repositories over the existing `libs/db` ORM models. A checked-in OpenAPI contract snapshot under `specs/contracts/` provides the shared frontend/backend interface boundary identified in the alignment review.

## Technical Context

**Language/Version**: Python 3.12 (backend); TypeScript 5.x frontend unchanged
**Primary Dependencies**: FastAPI 0.115.x, uvicorn[standard], SQLAlchemy 2.x (already in backend), psycopg 3.x (already in backend), Pydantic 2.x (already in backend), structlog (already in backend), pytest + httpx (test client), Nx tooling
**Storage**: PostgreSQL 16 — existing runtime tables: `ingestion_runs`, `source_run_outcomes`, `source_eligibility_snapshots`, `conflict_records` (all managed by `libs/db` ORM models)
**Testing**: pytest + pytest-cov + httpx `TestClient` in `apps/backend/tests`; Nx affected quality targets
**Target Platform**: Local-first macOS/Linux developer environments and CI runners; Docker Compose local stack
**Project Type**: Nx monorepo read-only web-service layer within `apps/backend`
**Performance Goals**: All Phase 1 endpoints respond within 500 ms for typical local development data volumes
**Constraints**: Read-only only (no write paths); no quality-gate bypasses; ≥90% coverage on affected backend scope; no regression in pipeline or db projects; backend remains startable in Docker Compose local stack
**Scale/Scope**: Phase 1 only — 6 endpoints over 4 existing runtime tables; Phase 2 (observations/audit/hierarchy) explicitly deferred

## Constitution Check

_GATE: Must pass before Phase 0 research. Re-check after Phase 1 design._

- **Monorepo cohesion**: PASS. Work stays within `apps/backend` and reuses `libs/db` ORM models and session utilities. No new Nx project boundaries created. OpenAPI snapshot checked into `specs/contracts/` so frontend can consume the contract without coupling to backend code.
- **Quality gate enforcement**: PASS. Plan relies on existing ruff/ty/pytest gates in `apps/backend` with no suppressions. FastAPI and httpx added via `uv add` — no manual pyproject edits bypassing lockfile.
- **Test and coverage discipline**: PASS. All new route modules and repository adapters include unit and contract tests. Integration tests exercise real SQLAlchemy sessions where appropriate. Coverage floor remains ≥90%.
- **Local-first parity**: PASS. `docker-compose.yml` backend service updated from placeholder to real FastAPI uvicorn command; healthcheck updated to hit `/health`. Local run documented in `quickstart.md`.
- **Data integrity and reliability**: PASS. All endpoints are read-only. No schema changes introduced. ORM models read from existing runtime tables without modification. Response envelopes define stable field names and value sets documented in `contracts/`.
- **Documentation fidelity**: PASS. `quickstart.md` documents local API run/test flow. Runbook updated with backend API start commands. `AGENTS.md` updated when backend structure/commands change.

## Project Structure

### Documentation (this feature)

```text
specs/014-read-only-fastapi-api/
├── spec.md
├── plan.md
├── research.md
├── data-model.md
├── quickstart.md
├── contracts/
│   └── phase1-api-contract.md
├── checklists/
│   └── requirements.md
└── tasks.md
```

### Source Code (repository root)

```text
apps/
└── backend/
    ├── src/
    │   ├── __init__.py
    │   ├── api/
    │   │   ├── __init__.py
    │   │   ├── app.py                    # FastAPI application factory
    │   │   ├── dependencies.py           # DB session dependency injection
    │   │   ├── schemas/
    │   │   │   ├── __init__.py
    │   │   │   ├── common.py             # Pagination envelope, error envelope
    │   │   │   ├── runs.py               # IngestionRun response schemas
    │   │   │   ├── outcomes.py           # SourceRunOutcome response schemas
    │   │   │   ├── eligibility.py        # SourceEligibilitySnapshot response schemas
    │   │   │   └── conflicts.py          # ConflictRecord response schemas
    │   │   └── routers/
    │   │       ├── __init__.py
    │   │       ├── health.py             # GET /health
    │   │       ├── runs.py               # GET /api/runs, GET /api/runs/{run_id}
    │   │       ├── outcomes.py           # GET /api/runs/{run_id}/outcomes
    │   │       ├── eligibility.py        # GET /api/runs/{run_id}/eligibility
    │   │       └── conflicts.py          # GET /api/conflicts
    │   ├── repositories/
    │   │   ├── __init__.py
    │   │   ├── run_repository.py         # SQLAlchemy read repo for ingestion_runs
    │   │   ├── outcome_repository.py     # SQLAlchemy read repo for source_run_outcomes
    │   │   ├── eligibility_repository.py # SQLAlchemy read repo for source_eligibility_snapshots
    │   │   └── conflict_repository.py    # SQLAlchemy read repo for conflict_records
    │   └── contract/                     # existing — unchanged
    │       └── query/
    │           └── ...
    └── tests/
        ├── api/
        │   ├── __init__.py
        │   ├── test_health.py
        │   ├── test_runs.py
        │   ├── test_outcomes.py
        │   ├── test_eligibility.py
        │   └── test_conflicts.py
        └── repositories/
            ├── __init__.py
            ├── test_run_repository.py
            ├── test_outcome_repository.py
            ├── test_eligibility_repository.py
            └── test_conflict_repository.py

specs/
└── contracts/
    └── openapi-phase1-snapshot.json      # Checked-in OpenAPI schema snapshot

docs/
└── runbooks/
    └── backend-api-local-run.md          # Local start/test commands

docker-compose.yml                        # Update backend service to run FastAPI
```

**Structure Decision**: Extend `apps/backend` in place by adding `api/` (FastAPI app, schemas, routers) and `repositories/` (SQLAlchemy read adapters) modules alongside the existing `contract/` module. No new Nx projects created. The `libs/db` ORM models and session/engine utilities are reused as-is.

## Complexity Tracking

| Violation | Why Needed | Simpler Alternative Rejected Because |
| --------- | ---------- | ------------------------------------ |
| None      | N/A        | N/A                                  |

## Phase 0: Research

Resolve key architectural and dependency decisions before implementation:

- FastAPI version selection and uvicorn dependency mode.
- DB session lifecycle strategy in FastAPI dependency injection (per-request vs. global).
- OpenAPI snapshot generation and consistency validation approach.
- Pagination strategy (page-number vs. cursor) for Phase 1.
- Error handler registration pattern (FastAPI exception handlers vs. middleware).
- Test client approach (httpx `TestClient` vs. pytest-asyncio).
- Docker Compose backend service upgrade path from placeholder to FastAPI uvicorn.

Output captured in `research.md`.

## Phase 1: Design & Contracts

### Data Model

Define API-layer response entities (IngestionRunResponse, SourceRunOutcomeResponse, SourceEligibilityResponse, ConflictRecordResponse), pagination envelope, and error envelope in `data-model.md`.

### Interface Contracts

Define the Phase 1 HTTP API contract — endpoint paths, query parameters, response envelopes, error shapes, enum value sets, and timestamp format — in `contracts/phase1-api-contract.md`.

### Quickstart

Document local API start/test flow, Docker Compose backend service usage, OpenAPI UI access, and quality gate commands in `quickstart.md`.

### Agent Context Update

Run `.specify/scripts/bash/update-agent-context.sh codex` after design artifacts are generated.

## Post-Design Constitution Re-Check

- Monorepo cohesion: PASS — structure stays within `apps/backend` and `specs/contracts/`; no new projects.
- Quality gate enforcement: PASS — dependencies added via uv; ruff/ty/pytest gates unchanged.
- Test and coverage discipline: PASS — all new modules have tests; httpx TestClient used for router tests.
- Local-first parity: PASS — docker-compose.yml backend service updated; quickstart documents local run.
- Data integrity and reliability: PASS — read-only; no schema changes; envelopes are stable and documented.
- Documentation fidelity: PASS — runbook, quickstart, AGENTS.md, and OpenAPI snapshot all updated in same change.
