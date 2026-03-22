# Implementation Plan: Schedule State Persistence

**Branch**: `[007-schedule-state-persistence]` | **Date**: 2026-03-22 | **Spec**: `specs/007-schedule-state-persistence/spec.md`
**Input**: Feature specification from `specs/007-schedule-state-persistence/spec.md`

## Summary

Wire the existing `source_schedule_policies` database table to the orchestration
runtime so that per-source cadence enforcement is backed by durable run history.
Before evaluating which sources are due, the coordinator reads `last_successful_at`
from the DB and merges it into each source's in-memory policy. After a source
succeeds, the coordinator writes the run's completion timestamp back to that table.
No new migration is required — the schema already exists since migration 0003.

## Technical Context

**Language/Version**: Python 3.12 (pipeline), TypeScript 5.x unchanged
**Primary Dependencies**: Dagster 1.x, Pydantic 2.x, SQLAlchemy 2.x, psycopg 3.x, uv
**Storage**: PostgreSQL 16 via `source_schedule_policies` table (created in migration
`0003_sched_eligibility`); fields: `source_key` (unique), `cadence_type`,
`last_successful_at`, `next_eligible_at`, `is_active`, `priority_class`, `updated_at`
**Testing**: pytest + pytest-cov; unit tests with in-memory mock repo, integration
tests against local Docker Compose DB
**Target Platform**: macOS/Linux local dev via Docker Compose
**Project Type**: Nx monorepo data platform — pipeline orchestration feature
**Performance Goals**: Read/write latency must not materially increase job startup
time; single SELECT and one INSERT/UPDATE per source per run is acceptable
**Constraints**: No quality-gate bypasses; ≥90% coverage in affected projects;
getattr duck-typed repo access pattern must be preserved; no new Protocol/ABC needed

## Constitution Check

- Monorepo cohesion: PASS. Changes are confined to `apps/pipeline` orchestration and
  shared DB runtime table; no cross-project contracts are altered.
- Quality gate enforcement: PASS. Existing ruff, ty, pytest, and coverage gates
  remain mandatory; no inline suppression introduced beyond one `noqa: PLW2901` for
  loop-variable reassignment that is idiomatically required by the frozen dataclass
  pattern.
- Test and coverage discipline: PASS. Plan includes unit tests for both new repo
  methods and coordinator hydration logic, plus integration tests against the live DB,
  maintaining ≥90% pipeline coverage.
- Local-first parity: PASS. Full behavior is exercisable through local Docker Compose
  DB and existing `execute_in_process` Dagster harness.
- Data integrity and reliability: PASS. Upsert uses `ON CONFLICT (source_key) DO
UPDATE` for atomic idempotent writes; read is non-destructive SELECT.
- Documentation fidelity: PASS. Quickstart and runbook include schedule state
  inspection, manual reset procedures, and real-world verification steps.

## Project Structure

### Documentation (this feature)

```text
specs/007-schedule-state-persistence/
├── spec.md
├── plan.md
├── research.md
├── data-model.md
├── quickstart.md
├── contracts/
│   └── schedule-state-persistence-contract.md
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
    │       ├── jobs/
    │       │   └── run_coordinator.py          ← read path + write path wiring
    │       └── resources/
    │           └── postgres_run_repository.py  ← new read/upsert methods
    └── tests/
        └── orchestration/
            ├── test_run_coordinator.py                ← hydration unit tests
            └── test_schedule_policy_persistence.py    ← repo integration tests
```

**Structure Decision**: All changes extend existing orchestration files; no new
modules or packages are created. The `source_schedule_policies` table in shared DB
is accessed exclusively by `PostgresRunRepository`.

## Complexity Tracking

| Violation                                     | Why Needed                                                                                             | Simpler Alternative Rejected Because                                                       |
| --------------------------------------------- | ------------------------------------------------------------------------------------------------------ | ------------------------------------------------------------------------------------------ |
| `noqa: PLW2901` on loop variable reassignment | `SourceWorkflowRegistration` is a frozen dataclass; `replace()` must produce a new binding in the loop | Using `enumerate` + list indexing produces less readable code for a one-liner policy patch |

## Implementation Consistency Notes

- The read path runs once per run, not per source, via a single SELECT returning all
  rows keyed by source_key.
- Hydration merges only `last_successful_at` from the DB row onto the in-memory
  policy; all other policy fields (cadence_type, is_active) are sourced from code at
  registration time.
- The write path runs once per successful source result after execution completes;
  `completed_at` (the run's finish timestamp) is used as `last_successful_at`.
- Sources with `schedule_policy = None` in registration are silently skipped by the
  write path; the hourly in-memory fallback in DueSourceSelector remains unchanged.
- `clear_all()` is extended to include `source_schedule_policies` to maintain test
  isolation correctness.

## Phase 0: Research

All technical decisions were resolved without open unknowns. See `research.md` for
rationale on key choices.

## Phase 1: Design & Contracts

### Data Model

See `data-model.md` for entity definitions and DB column mapping.

### Interface Contracts

See `contracts/schedule-state-persistence-contract.md` for the read and upsert
method signatures and behavior contracts.

### Quickstart

See `quickstart.md` for step-by-step verification of real-world scheduling behavior
using the local DB and Dagster job harness.
