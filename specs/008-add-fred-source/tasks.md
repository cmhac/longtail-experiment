# Tasks: FRED Interest Rate Source

**Input**: Design documents from `/specs/008-add-fred-source/`
**Prerequisites**: plan.md (required), spec.md (required for user stories), research.md, data-model.md, contracts/

**Tests**: Test tasks are REQUIRED. Every user story and foundational component MUST include automated test coverage sufficient to maintain >= 90% coverage in affected projects.

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3)
- Include exact file paths in descriptions

## Path Conventions

- Pipeline source: `apps/pipeline/src/`
- Pipeline tests: `apps/pipeline/tests/`
- Shared DB migrations/tests: `libs/db/alembic/versions/`, `libs/db/tests/`
- Feature docs: `specs/008-add-fred-source/`

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Prepare local secret handling and feature verification scaffolding.

- [x] T001 Verify local secret ignore behavior in docker/compose/.gitignore
- [x] T002 Add or update provider key template in docker/compose/local.secrets.env.example
- [x] T003 [P] Add FRED source verification guidance stub to docs/runbooks/local-stack-baseline.md
- [x] T004 [P] Validate and refine feature quickstart run commands and expected outputs in specs/008-add-fred-source/quickstart.md

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Implement persistence and runtime wiring prerequisites required by all user stories.

**⚠️ CRITICAL**: No user story work can begin until this phase is complete.

- [x] T005 Create observation-store migration 0004 in libs/db/alembic/versions/0004_observation_store.py
- [x] T006 [P] Add migration metadata/table assertions for 0004 in libs/db/tests/test_ingestion_runtime_migrations.py
- [x] T007 Implement durable Postgres observation repository in apps/pipeline/src/orchestration/resources/postgres_observation_repository.py
- [x] T008 [P] Add unit tests for Postgres observation upsert/query behavior in apps/pipeline/tests/orchestration/test_postgres_observation_repository.py
- [x] T009 Wire runtime to use Postgres observation repository in apps/pipeline/src/orchestration/runtime.py
- [x] T010 [P] Extend runtime smoke coverage for registered sources and durable repository wiring in apps/pipeline/tests/orchestration/test_definitions_smoke.py
- [x] T011 Add migration revision expectation for local stack checks in tools/quality/local-stack/check-db-revision.sh
- [x] T012 Run foundational quality gates (ruff, ty, pytest, coverage) for affected modules and record results in specs/008-add-fred-source/quickstart.md

**Checkpoint**: Foundation ready - user story implementation can now begin in parallel.

---

## Phase 3: User Story 1 - Ingest Baseline Interest Rate Series (Priority: P1) 🎯 MVP

**Goal**: Deliver first real-world FRED source ingest path with credential handling and canonical persistence.

**Independent Test**: Configure valid `FRED_API_KEY`, run ingest on-demand, and confirm at least one persisted `INT.US.FEDFUNDS` observation.

### Tests for User Story 1 (REQUIRED) ⚠️

- [x] T013 [P] [US1] Add source adapter contract tests for payload mapping and status accounting in apps/pipeline/tests/orchestration/test_fred_source_workflow.py
- [x] T014 [US1] Add credential failure-path test in apps/pipeline/tests/orchestration/test_fred_source_workflow.py
- [x] T015 [P] [US1] Add ingest job integration test asserting FRED source outcome visibility in apps/pipeline/tests/orchestration/test_ingest_job_runtime.py
- [x] T016 [P] [US1] Add canonical ingest compatibility test for upsert_observation repository path in apps/pipeline/tests/contract/test_ingest_frequency_handling.py

### Implementation for User Story 1

- [x] T017 [US1] Implement FRED source workflow adapter in apps/pipeline/src/orchestration/jobs/sources/fred_fedfunds_source.py
- [x] T018 [US1] Implement provider response normalization and canonical payload mapping in apps/pipeline/src/orchestration/jobs/sources/fred_fedfunds_source.py
- [x] T019 [US1] Implement explicit credential-read and missing-key failure signaling in apps/pipeline/src/orchestration/jobs/sources/fred_fedfunds_source.py
- [x] T020 [US1] Register FRED source workflow in apps/pipeline/src/orchestration/runtime.py
- [x] T021 [US1] Ensure run outcome reason/message mapping for provider and credential failures in apps/pipeline/src/orchestration/jobs/sources/fred_fedfunds_source.py
- [x] T022 [US1] Verify US1 coverage contribution maintains >= 90% in apps/pipeline/tests/orchestration/test_fred_source_workflow.py

**Checkpoint**: User Story 1 is independently functional and demo-ready.

---

## Phase 4: User Story 2 - Perform Incremental Refreshes Safely (Priority: P2)

**Goal**: Add checkpoint-driven incremental fetch behavior and duplicate-safe persistence.

**Independent Test**: Execute two consecutive runs with unchanged upstream data and verify no new duplicate observations are persisted.

### Tests for User Story 2 (REQUIRED) ⚠️

- [x] T023 [P] [US2] Add integration test for second-run no-duplicate behavior in apps/pipeline/tests/orchestration/test_ingest_job_runtime.py
- [x] T024 [P] [US2] Add repository test for latest-observed-on checkpoint lookup in apps/pipeline/tests/orchestration/test_postgres_observation_repository.py
- [x] T025 [P] [US2] Add source adapter test for incremental start-date request construction in apps/pipeline/tests/orchestration/test_fred_source_workflow.py
- [x] T026 [US2] Add scheduled trigger cadence test for FRED due/not_due behavior in apps/pipeline/tests/orchestration/test_trigger_modes.py

### Implementation for User Story 2

- [x] T027 [US2] Add latest persisted observation checkpoint API in apps/pipeline/src/orchestration/resources/postgres_observation_repository.py
- [x] T028 [US2] Implement incremental request window logic in apps/pipeline/src/orchestration/jobs/sources/fred_fedfunds_source.py
- [x] T029 [US2] Enforce idempotent upsert semantics for repeated periods in apps/pipeline/src/orchestration/resources/postgres_observation_repository.py
- [x] T030 [US2] Integrate incremental behavior into on-demand and scheduled flows in apps/pipeline/src/orchestration/jobs/sources/fred_fedfunds_source.py
- [x] T031 [US2] Verify US2 coverage contribution maintains >= 90% in apps/pipeline/tests/orchestration/test_ingest_job_runtime.py

**Checkpoint**: User Stories 1 and 2 both operate independently without duplicate writes.

---

## Phase 5: User Story 3 - Detect and Capture Implementation Gaps (Priority: P3)

**Goal**: Institutionalize in-feature gap capture and keep spec/plan/tasks aligned with discovered blockers.

**Independent Test**: Introduce a confirmed blocker scenario and verify it is reflected across spec, plan, and task artifacts without unresolved undocumented gaps.

### Tests for User Story 3 (REQUIRED) ⚠️

- [x] T032 [P] [US3] Add automated artifact consistency test for spec-plan-tasks alignment in apps/pipeline/tests/orchestration/test_feature_artifact_alignment.py
- [x] T033 [P] [US3] Add automated gap-log completeness test for required blocker fields in apps/pipeline/tests/orchestration/test_feature_artifact_alignment.py

### Implementation for User Story 3

- [x] T034 [US3] Add explicit gap-log section with update protocol to specs/008-add-fred-source/spec.md
- [x] T035 [US3] Add plan update protocol for newly discovered blockers in specs/008-add-fred-source/plan.md
- [x] T036 [US3] Add gap-driven task amendment rules in specs/008-add-fred-source/tasks.md
- [x] T037 [US3] Add operator-facing gap triage and escalation guidance in docs/runbooks/local-stack-baseline.md
- [x] T038 [US3] Verify US3 coverage contribution maintains >= 90% using apps/pipeline/tests/orchestration/test_feature_artifact_alignment.py

**Checkpoint**: All user stories are independently functional and scope-change resilient.

---

## Phase 6: Polish & Cross-Cutting Concerns

**Purpose**: Final hardening, documentation fidelity, and full quality verification.

- [x] T039 [P] Update feature research and design artifacts with implementation-final decisions in specs/008-add-fred-source/research.md
- [x] T040 [P] Update quickstart with exact verified commands and observed outputs in specs/008-add-fred-source/quickstart.md
- [x] T041 [P] Ensure AGENTS command/toolchain references stay current in AGENTS.md
- [x] T042 Run full pipeline quality suite and confirm >= 90% coverage in apps/pipeline/tests
- [x] T043 Run migration and local stack verification commands in tools/quality/local-stack/check-db-revision.sh
- [x] T044 Execute end-to-end local workflow validation and capture troubleshooting deltas in docs/runbooks/local-stack-baseline.md

---

## Dependencies & Execution Order

### Phase Dependencies

- **Phase 1 (Setup)**: No dependencies.
- **Phase 2 (Foundational)**: Depends on Phase 1 and blocks all user stories.
- **Phase 3 (US1)**: Starts after Phase 2.
- **Phase 4 (US2)**: Starts after Phase 2; integrates US1 source implementation.
- **Phase 5 (US3)**: Starts after Phase 2; can proceed alongside US2.
- **Phase 6 (Polish)**: Starts after selected user stories are complete.

### User Story Dependencies

- **US1 (P1)**: Independent after foundational work.
- **US2 (P2)**: Depends on US1 adapter/repository baseline.
- **US3 (P3)**: Depends only on foundational artifacts and can run parallel with US2.

### Within Each User Story

- Tests first (failing) before implementation.
- Source/repository model updates before runtime integration.
- Integration checks before documentation updates.

## Parallel Opportunities

- Setup: T003 and T004 can run in parallel.
- Foundational: T006, T008, and T010 can run in parallel after T005/T007 start.
- US1: T013, T014, T015, and T016 can run in parallel.
- US2: T023, T024, and T025 can run in parallel.
- US3: T032 and T033 can run in parallel.
- Polish: T039, T040, and T041 can run in parallel.

## Parallel Example: User Story 1

```bash
# Parallel test authoring for US1
Task: "T013 [US1] Add source adapter contract tests in apps/pipeline/tests/orchestration/test_fred_source_workflow.py"
Task: "T014 [US1] Add credential failure-path test in apps/pipeline/tests/orchestration/test_fred_source_workflow.py"
Task: "T015 [US1] Add ingest integration test in apps/pipeline/tests/orchestration/test_ingest_job_runtime.py"
Task: "T016 [US1] Add canonical ingest compatibility test in apps/pipeline/tests/contract/test_ingest_frequency_handling.py"

# Parallel implementation slices for US1
Task: "T018 [US1] Implement payload mapping in apps/pipeline/src/orchestration/jobs/sources/fred_fedfunds_source.py"
Task: "T020 [US1] Register workflow in apps/pipeline/src/orchestration/runtime.py"
```

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phases 1-2.
2. Complete Phase 3 (US1).
3. Validate on-demand real-data ingest and persistence.
4. Demo and decide go/no-go for incremental enhancement.

### Incremental Delivery

1. Build persistence/runtime foundation.
2. Ship US1 as first real-world source MVP.
3. Add US2 incremental optimization.
4. Add US3 process hardening for blocker capture.
5. Run full polish and quality gates.

### Parallel Team Strategy

1. Team A: Foundational migration/repository path.
2. Team B: US1 source adapter + tests.
3. Team C: US3 artifact consistency process.
4. Team B/C converge with Team A for US2 incremental behavior.

## Notes

- [P] tasks indicate no same-file dependency on incomplete tasks.
- Each user story phase includes explicit independent test criteria.
- All tasks include concrete file paths and strict checklist format.
- Keep `FRED_API_KEY` out of tracked files and logs.
- Update docs and AGENTS in the same change as behavior/workflow changes.

## Gap-Driven Amendment Rules

1. For each confirmed blocker in `spec.md` Gap Log, add at least one test task and one
   implementation task in this file before ending the implementation session.
2. Added blocker tasks must include explicit file paths, story labels, and dependency
   ordering relative to affected foundational or user-story tasks.
3. If blocker work is deferred, keep an open task in this file with owner, deferral
   rationale, and the trigger condition for resuming work.
