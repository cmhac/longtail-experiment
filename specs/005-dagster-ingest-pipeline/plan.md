# Implementation Plan: Dagster-Orchestrated Time-Series Ingestion

**Branch**: `005-dagster-ingest-pipeline` | **Date**: 2026-03-21 | **Spec**: `/Users/hackerc/Projects/longtail-experiment/specs/005-dagster-ingest-pipeline/spec.md`
**Input**: Feature specification from `/Users/hackerc/Projects/longtail-experiment/specs/005-dagster-ingest-pipeline/spec.md`

**Note**: This template is filled in by the `/speckit.plan` command. See `.specify/templates/plan-template.md` for the execution workflow.

## Summary

Introduce a Dagster-based orchestration layer for source-specific time-series ingest workflows that enforces canonical contract validation, supports scheduled and on-demand runs, and persists deterministic run outcomes including partial-success behavior and explicit duplicate/conflict handling. The plan preserves existing monorepo boundaries by keeping orchestration and source adapters in `apps/pipeline`, shared persistence contracts in `libs/db`, and read/audit consumption in `apps/backend`.

## Technical Context

**Language/Version**: Python 3.12 (pipeline and shared DB), TypeScript 5.x unchanged  
**Primary Dependencies**: Dagster 1.x, Pydantic 2.x, SQLAlchemy 2.x, Alembic, psycopg 3.x, structlog, OpenTelemetry API/SDK, Nx workspace tooling  
**Storage**: PostgreSQL 16 local dev database with relational time-series persistence and migration authority under `libs/db/alembic`  
**Testing**: pytest + pytest-cov (pipeline/backend/libs), contract tests, integration tests for run outcomes, Nx affected quality targets  
**Target Platform**: macOS/Linux local development via Docker Compose, Python runtime services for pipeline/backend  
**Project Type**: Nx monorepo data-platform feature (pipeline orchestration + shared persistence + backend read compatibility)  
**Performance Goals**: New source onboarding to first successful run within one business day; run outcome visibility under 5 minutes post-run; deterministic outcomes across 3 consecutive reruns for identical input  
**Constraints**: No quality gate bypasses; >=90% coverage in affected projects; one active plus one queued run per source; partial-success run status for mixed source outcomes; idempotent no-op on exact duplicates; non-matching duplicates persisted as queryable conflicts  
**Scale/Scope**: Initial phase targets dozens of sources and daily operation cadence, with source-level isolation and run-level outcome aggregation

## Constitution Check

_GATE: Must pass before Phase 0 research. Re-check after Phase 1 design._

- Pre-Design Gate Review (PASS)
- Monorepo cohesion: PASS. Changes are bounded to pipeline orchestration modules, shared DB repositories/migrations, and backend query compatibility updates.
- Quality gate enforcement: PASS. Existing lint/format/typecheck/test gates remain mandatory through Nx and uv commands.
- Test and coverage discipline: PASS. Plan includes contract and integration tests for scheduling, partial outcomes, concurrency policy, and conflict persistence while preserving coverage thresholds.
- Local-first parity: PASS. Feature is designed for local Docker Compose execution with documented trigger/run workflows and migration verification.
- Data integrity and reliability: PASS. Provenance, revision lineage, idempotency, and conflict persistence are explicit design constraints.
- Documentation fidelity: PASS. Plan includes updates to runbooks/onboarding/architecture and AGENTS.md if command workflows or structure change.

- Post-Design Gate Review (PASS)
- Monorepo cohesion: PASS. Source adapters, orchestration, and repositories remain in designated bounded contexts.
- Quality gate enforcement: PASS. No workaround strategy required; all affected checks are included in quickstart.
- Test and coverage discipline: PASS. Scenario coverage maps directly to clarified functional requirements and success criteria.
- Local-first parity: PASS. Design artifacts include local scheduling/on-demand execution verification.
- Data integrity and reliability: PASS. Conflict records and deterministic deduplicated queue policy are formally modeled.
- Documentation fidelity: PASS. Artifact set includes contracts and operational quickstart for same-change updates.

## Project Structure

### Documentation (this feature)

```text
specs/005-dagster-ingest-pipeline/
├── plan.md
├── research.md
├── data-model.md
├── quickstart.md
├── contracts/
│   ├── ingest-orchestration-contract.md
│   ├── source-workflow-contract.md
│   └── conflict-lifecycle-contract.md
└── tasks.md
```

### Source Code (repository root)

```text
apps/
├── pipeline/
│   ├── src/
│   │   ├── contract/
│   │   │   ├── normalizers/
│   │   │   ├── observability/
│   │   │   ├── schemas/
│   │   │   └── services/
│   │   └── orchestration/
│   │       ├── definitions.py
│   │       ├── jobs/
│   │       ├── schedules/
│   │       ├── sensors/
│   │       └── resources/
│   └── tests/
│       ├── contract/
│       └── orchestration/
├── backend/
│   ├── src/contract/query/
│   └── tests/contract/
└── frontend/
    └── (no feature-scope changes)

libs/
└── db/
    ├── src/db/
    │   ├── models/
    │   ├── repositories/
    │   ├── engine.py
    │   ├── session.py
    │   └── settings.py
    ├── alembic/
    │   └── versions/
    └── tests/

tools/
└── quality/local-stack/
```

**Structure Decision**: Preserve current app/library boundaries and add a dedicated orchestration subpackage in `apps/pipeline/src` while keeping persistence and migration authorities in `libs/db`.

## Complexity Tracking

> **Fill ONLY if Constitution Check has violations that must be justified**

| Violation | Why Needed | Simpler Alternative Rejected Because |
| --------- | ---------- | ------------------------------------ |
| None      | N/A        | N/A                                  |

## Implementation Consistency Notes

- Scheduled and on-demand runs are both required in this phase.
- Mixed source outcomes produce partial-success run status when at least one source fails and at least one succeeds.
- Per-source concurrency policy is fixed to one active run plus one deduplicated queued run.
- Duplicate drift policy is fixed: exact duplicate is no-op; conflicting duplicate becomes a persisted conflict record.
