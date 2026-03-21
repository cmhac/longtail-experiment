# Implementation Plan: Local Development Database Readiness

**Branch**: `004-local-dev-db` | **Date**: 2026-03-21 | **Spec**: `/Users/hackerc/Projects/longtail-experiment/specs/004-local-dev-db/spec.md`
**Input**: Feature specification from `/Users/hackerc/Projects/longtail-experiment/specs/004-local-dev-db/spec.md`

**Note**: This template is filled in by the `/speckit.plan` command. See `.specify/templates/plan-template.md` for the execution workflow.

## Summary

Establish a reproducible local development database workflow that includes startup
configuration, migration execution and verification, and remediation of all discovered
local setup defects. The plan introduces a concrete local DB bootstrap and migration
contract so developers can reliably transition from repository bootstrap to app-logic
implementation readiness.

## Technical Context

**Language/Version**: Python 3.12 (backend and pipeline tooling), shell scripts for local verification
**Primary Dependencies**: Docker Compose, PostgreSQL 16 image for local DB service, SQLAlchemy 2.x, Alembic, psycopg 3.x, uv, pytest, Nx quality scripts
**Storage**: PostgreSQL 16 local development database with persistent volume by default
**Testing**: pytest (backend, pipeline, shared DB), local stack verification script, affected lint/format/typecheck/test/coverage/duplication commands
**Target Platform**: macOS/Linux developer machines running Docker Desktop or Docker Engine
**Project Type**: Nx monorepo with Python backend plus pipeline and shared DB library (`libs/db`)
**Performance Goals**: First-time local DB setup completed within 15 minutes; migration status verification completes in under 1 minute per run
**Constraints**: Persistent DB by default with explicit reset flow only; fail-fast migration behavior; documentation-only non-development warning guard; no quality-gate bypasses
**Scale/Scope**: One local DB service and migration chain supporting current shared contract schema baseline and iterative future revisions

## Constitution Check

_GATE: Must pass before Phase 0 research. Re-check after Phase 1 design._

- Pre-Design Gate Review (PASS)
- Monorepo cohesion: PASS. Work remains in `docker-compose.yml`, `docker/compose`, `libs/db`, `tools/quality`, docs, and feature spec artifacts without introducing new project boundaries.
- Quality gate enforcement: PASS. Plan preserves existing quality scripts and includes no suppression strategy.
- Test and coverage discipline: PASS. Plan includes migration and setup verification tests and requires affected coverage commands to pass.
- Local-first parity: PASS. Local DB setup and migration readiness are explicitly tied to compose workflow and stack-health checks.
- Data integrity and reliability: PASS. Migration baseline verification, fail-fast behavior, and repeatable rerun semantics are specified.
- Documentation fidelity: PASS. Plan includes updates to onboarding, runbooks, architecture notes, and AGENTS.md when workflows change.

- Post-Design Gate Review (PASS)
- Monorepo cohesion: PASS. Data model and contracts map to existing backend/pipeline/shared-db boundaries only.
- Quality gate enforcement: PASS. Quickstart defines full verification command path.
- Test and coverage discipline: PASS. Verification artifacts include tests for migration state and setup defect regressions.
- Local-first parity: PASS. End-to-end local stack plus migration workflow is runnable with documented commands.
- Data integrity and reliability: PASS. Migration contract includes baseline checkpoint and deterministic recovery semantics.
- Documentation fidelity: PASS. Required docs are enumerated with same-change update expectation.

## Project Structure

### Documentation (this feature)

```text
specs/004-local-dev-db/
├── plan.md
├── research.md
├── data-model.md
├── defect-log.md
├── quickstart.md
├── contracts/
│   ├── local-db-bootstrap-contract.md
│   └── migration-readiness-contract.md
└── tasks.md
```

### Source Code (repository root)

```text
docker-compose.yml
docker/
└── compose/
    └── stack.env

libs/
└── db/
    ├── alembic/
    │   ├── env.py
    │   └── versions/
    ├── src/db/
    │   ├── engine.py
    │   └── session.py
    └── tests/

tools/
└── quality/
    └── local-stack/
        └── test-compose-stack.sh

docs/
├── architecture/
├── onboarding/
└── runbooks/

apps/
├── backend/
│   └── tests/
│       ├── test_local_db_bootstrap.py
│       ├── test_local_db_migration_commands.py
│       └── test_local_db_defect_regressions.py
└── pipeline/
    └── tests/
        ├── test_local_db_profile_defaults.py
        └── test_local_db_defect_regressions.py
```

**Structure Decision**: Keep all implementation inside existing compose, shared DB, and quality-tooling surfaces. No new application package is introduced; the feature hardens local runtime/migration readiness across current infrastructure boundaries while story verification is implemented across shared DB tests and app-level tests under `apps/backend/tests` and `apps/pipeline/tests`.

## Complexity Tracking

> **Fill ONLY if Constitution Check has violations that must be justified**

| Violation | Why Needed | Simpler Alternative Rejected Because |
| --------- | ---------- | ------------------------------------ |
| None      | N/A        | N/A                                  |

## Implementation Consistency Notes

- Local development DB persistence is default-on; reset is explicit and documented.
- Migration execution is fail-fast with recovery guidance and explicit rerun trigger.
- All reproducible local setup defects found during implementation are in scope for fixes.
- Non-development usage protection is warning-based via documentation, aligned with clarified spec decisions.
- Defect tracking evidence is maintained in `specs/004-local-dev-db/defect-log.md` and summarized in readiness research evidence.
