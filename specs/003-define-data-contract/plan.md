# Implementation Plan: Core Pipeline Data Contract

**Branch**: `003-define-data-contract` | **Date**: 2026-03-21 | **Spec**: `/Users/hackerc/Projects/longtail-experiment/specs/003-define-data-contract/spec.md`
**Input**: Feature specification from `/Users/hackerc/Projects/longtail-experiment/specs/003-define-data-contract/spec.md`

**Note**: This template is filled in by the `/speckit.plan` command. See `.specify/templates/plan-template.md` for the execution workflow.

## Summary

Define and implement a single source-of-truth contract system for backend and pipeline
time-series ingestion, including canonical observation shape, provenance immutability,
revision lineage, and hierarchical taxonomy/geography filtering. This plan locks the
persistence engine and Python module ownership before coding to remove architecture
ambiguity and centralizes shared database logic in one reusable library.

## Technical Context

**Language/Version**: Python 3.12 (pipeline and backend)
**Primary Dependencies**: Nx workspace tooling, uv, ruff, ty, pytest, dagster baseline package, SQLAlchemy 2.x, Alembic, Pydantic 2.x, psycopg 3.x, structlog, OpenTelemetry SDK/API
**Storage**: PostgreSQL 16 with TimescaleDB 2.14 extension for hypertable time-series partitioning and relational integrity
**Testing**: pytest, pytest-cov, contract/integration/unit suites for backend and pipeline, plus schema and observability assertions
**Target Platform**: Local macOS/Linux developer environments and Docker Compose stack parity
**Project Type**: Nx monorepo data-platform contract implementation (backend plus pipeline plus shared DB library)
**Performance Goals**: 95% source onboarding without exception handling; ingestion validation sustained for daily mixed-frequency loads; analyst filter workflows complete in under 2 minutes as defined in spec
**Constraints**: No quality-gate bypasses; immutable provenance post-persist; explicit revision lineage; structured observability for ingest paths; frontend excluded from feature scope
**Scale/Scope**: Initial catalog of dozens to low hundreds of series with extensible support for internal and external feeds across category/geography hierarchies

### Concrete Module Stack (Locked)

- **Normative Contract Authority**: `specs/003-define-data-contract/contracts/canonical-observation-contract.md`
- **Runtime Canonical Schema Authority**: `apps/pipeline/src/contract/schemas/canonical_observation.py`
- **Shared Python DB Logic Authority**: `libs/db/src/db/`
- **Validation Layer**: Pydantic 2.x models and validators for source payload normalization and canonical observation enforcement
- **Persistence Layer**: SQLAlchemy 2.x declarative models and repositories under `libs/db/src/db/`, with Alembic migrations under `libs/db/alembic/versions/`, targeting PostgreSQL 16 + TimescaleDB hypertables
- **Database Driver**: psycopg 3.x for synchronous/transactional writes in pipeline ingest and backend query paths via the shared DB library
- **Query Projection Layer**: backend contract services that consume shared DB repositories for filterable reads
- **Observability Layer**: structlog for structured logs and OpenTelemetry spans/metrics for ingest, validation, and persistence pipelines

No unresolved technical clarifications remain for implementation kickoff.

## Constitution Check

_GATE: Must pass before Phase 0 research. Re-check after Phase 1 design._

- Pre-Design Gate Review (PASS)
- Monorepo cohesion: PASS. Changes remain scoped to `apps/pipeline`, `apps/backend`, and `libs/db` with explicit contract artifacts in `specs/003-define-data-contract`.
- Quality gate enforcement: PASS. Plan keeps existing lint/format/type/test gates and forbids suppression paths.
- Test and coverage discipline: PASS. Contract, integration, and unit tests are required for every story and maintain >= 90% coverage in affected projects.
- Local-first parity: PASS. Docker Compose verification remains mandatory in quickstart.
- Data integrity and reliability: PASS. Provenance immutability, revision lineage, versioned contracts, and raw plus normalized value semantics are explicit.
- Documentation fidelity: PASS. Plan includes same-change updates for docs and AGENTS.md.

- Post-Design Gate Review (PASS)
- Monorepo cohesion: PASS. Canonical schema authority and shared DB library boundaries are clear.
- Quality gate enforcement: PASS. Full affected quality commands are part of execution.
- Test and coverage discipline: PASS. Story-level tests include validation, lineage, hierarchy filters, and observability assertions.
- Local-first parity: PASS. Contract stack can be run and verified with existing compose.
- Data integrity and reliability: PASS. Locked storage stack and centralized migration path support required constraints.
- Documentation fidelity: PASS. All impacted documents are enumerated in quickstart.

## Project Structure

### Documentation (this feature)

```text
specs/003-define-data-contract/
├── plan.md
├── research.md
├── data-model.md
├── quickstart.md
├── contracts/
│   ├── canonical-observation-contract.md
│   ├── provenance-and-revision-contract.md
│   └── taxonomy-and-query-contract.md
└── tasks.md
```

### Source Code (repository root)

```text
apps/
├── backend/
│   ├── src/
│   │   └── contract/
│   │       ├── services/
│   │       └── query/
│   └── tests/
│       └── contract/
├── pipeline/
│   ├── src/
│   │   └── contract/
│   │       ├── normalizers/
│   │       ├── schemas/
│   │       ├── services/
│   │       └── observability/
│   └── tests/
│       └── contract/
└── frontend/
    └── (no changes in this feature)

libs/
└── db/
    ├── src/
    │   └── db/
    │       ├── engine.py
    │       ├── models/
    │       ├── repositories/
    │       └── session.py
    ├── alembic/
    │   ├── env.py
    │   └── versions/
    └── tests/

docs/
├── architecture/
├── onboarding/
└── runbooks/

tools/
└── quality/
    └── verification/

specs/
└── 003-define-data-contract/
    ├── plan.md
    ├── research.md
    ├── data-model.md
    ├── quickstart.md
    ├── tasks.md
    └── contracts/
```

**Structure Decision**: Preserve Nx app boundaries for ingest and query services while centralizing all Python database engine/session/model/repository/migration logic in `libs/db`. Backend and pipeline modules consume the shared DB library and do not define competing app-local persistence authorities.

## Complexity Tracking

> **Fill ONLY if Constitution Check has violations that must be justified**

| Violation | Why Needed | Simpler Alternative Rejected Because |
| --------- | ---------- | ------------------------------------ |
| None      | N/A        | N/A                                  |

## Implementation Consistency Notes

- PostgreSQL plus TimescaleDB is fixed for this feature and is no longer deferred.
- Pydantic schema modules remain the runtime authority for canonical contract validity.
- All shared Python DB logic (engine, session, ORM models, repositories, Alembic migrations) lives under `libs/db`.
- `apps/pipeline` and `apps/backend` import and use `libs/db` instead of implementing separate DB stacks.
- Observability is required in ingest services through structured logs and OpenTelemetry.
