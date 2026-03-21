# Tasks: Dagster-Orchestrated Time-Series Ingestion

**Input**: Design documents from `/specs/005-dagster-ingest-pipeline/`
**Prerequisites**: plan.md (required), spec.md (required for user stories), research.md, data-model.md, contracts/

**Tests**: Test tasks are REQUIRED. Every user story and foundational component MUST include automated test coverage sufficient to maintain >= 90% coverage in affected projects.

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3)
- Include exact file paths in descriptions

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Establish orchestration module skeleton, test directories, and command wiring.

- [ ] T001 Create orchestration package skeleton in apps/pipeline/src/orchestration/**init**.py
- [ ] T002 [P] Create Dagster definitions entrypoint in apps/pipeline/src/orchestration/definitions.py
- [ ] T003 [P] Add orchestration test package bootstrap in apps/pipeline/tests/orchestration/**init**.py
- [ ] T004 [P] Add orchestration smoke test scaffold in apps/pipeline/tests/orchestration/test_definitions_smoke.py
- [ ] T005 [P] Register orchestration test target and run command wiring in apps/pipeline/project.json

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Implement shared persistence and run-state infrastructure required by all user stories.

**⚠️ CRITICAL**: No user story work can begin until this phase is complete.

- [ ] T006 Create run-state schema models in libs/db/src/db/models/ingestion_runtime.py
- [ ] T007 [P] Export new runtime models in libs/db/src/db/models/**init**.py
- [ ] T008 Create conflict persistence repository adapter in libs/db/src/db/repositories/conflict_repository.py
- [ ] T009 [P] Create run outcome repository adapter in libs/db/src/db/repositories/run_repository.py
- [ ] T010 [P] Export new repository adapters in libs/db/src/db/repositories/**init**.py
- [ ] T011 Add Alembic migration for run-state and conflict tables in libs/db/alembic/versions/0002_ingestion_runtime_and_conflicts.py
- [ ] T012 Add migration repeatability tests for new runtime tables in libs/db/tests/test_ingestion_runtime_migrations.py
- [ ] T013 [P] Add foundational repository unit tests in libs/db/tests/test_ingestion_runtime_repositories.py
- [ ] T014 Add source lock service for one-active-one-queued policy in apps/pipeline/src/orchestration/resources/source_lock_service.py
- [ ] T015 [P] Add concurrency policy tests in apps/pipeline/tests/orchestration/test_source_lock_service.py

**Checkpoint**: Foundation ready; user story implementation can begin.

---

## Phase 3: User Story 1 - Onboard a New Source Quickly (Priority: P1) 🎯 MVP

**Goal**: Add bounded source workflow registration and execution path so a new source can be onboarded without changing core orchestration behavior.

**Independent Test**: Register a new source workflow and run one ingestion cycle where valid records are accepted and invalid records are quarantined with explicit reasons.

### Tests for User Story 1 (REQUIRED) ⚠️

- [ ] T016 [P] [US1] Add source workflow contract tests in apps/pipeline/tests/orchestration/test_source_workflow_contract.py
- [ ] T017 [P] [US1] Add source onboarding integration test in apps/pipeline/tests/orchestration/test_source_onboarding_flow.py
- [ ] T018 [P] [US1] Add unit tests for workflow registry behavior in apps/pipeline/tests/orchestration/test_workflow_registry.py

### Implementation for User Story 1

- [ ] T019 [US1] Implement source workflow registry in apps/pipeline/src/orchestration/jobs/workflow_registry.py
- [ ] T020 [P] [US1] Implement source execution request schema in apps/pipeline/src/orchestration/jobs/workflow_request.py
- [ ] T021 [US1] Implement source execution result schema in apps/pipeline/src/orchestration/jobs/workflow_result.py
- [ ] T022 [US1] Implement reusable source ingest runner in apps/pipeline/src/orchestration/jobs/source_ingest_runner.py
- [ ] T023 [US1] Add reference source adapter example in apps/pipeline/src/orchestration/jobs/sources/example_source.py
- [ ] T024 [US1] Wire canonical validation and quarantine mapping in apps/pipeline/src/orchestration/jobs/source_ingest_runner.py
- [ ] T025 [US1] Add onboarding runbook section for adding a new source workflow in docs/runbooks/local-stack-baseline.md

**Checkpoint**: User Story 1 is independently functional and testable.

---

## Phase 4: User Story 2 - Run Standardized Ingestion Operations (Priority: P2)

**Goal**: Provide one orchestration entry point supporting both scheduled and on-demand runs with partial-success semantics and deterministic rerun behavior.

**Independent Test**: Trigger both scheduled and on-demand executions and verify source failures do not block healthy sources while run status is reported as partial success.

### Tests for User Story 2 (REQUIRED) ⚠️

- [ ] T026 [P] [US2] Add trigger mode tests for scheduled and on-demand runs in apps/pipeline/tests/orchestration/test_trigger_modes.py
- [ ] T027 [P] [US2] Add partial-success run aggregation test in apps/pipeline/tests/orchestration/test_partial_success_status.py
- [ ] T028 [P] [US2] Add deduplicated queued trigger and deterministic three-rerun test in apps/pipeline/tests/orchestration/test_source_queue_policy.py

### Implementation for User Story 2

- [ ] T029 [US2] Implement orchestration run coordinator in apps/pipeline/src/orchestration/jobs/run_coordinator.py
- [ ] T030 [P] [US2] Implement scheduled job definition in apps/pipeline/src/orchestration/schedules/ingest_schedule.py
- [ ] T031 [P] [US2] Implement on-demand trigger sensor in apps/pipeline/src/orchestration/sensors/ondemand_sensor.py
- [ ] T032 [US2] Implement run outcome aggregation service in apps/pipeline/src/orchestration/jobs/run_outcome_service.py
- [ ] T033 [US2] Wire source failure continuation and partial-success status in apps/pipeline/src/orchestration/jobs/run_coordinator.py
- [ ] T034 [US2] Register jobs, schedules, sensors, and resources in apps/pipeline/src/orchestration/definitions.py
- [ ] T035 [US2] Add operations guide for scheduled and on-demand trigger usage in docs/onboarding/monorepo-baseline.md

**Checkpoint**: User Stories 1 and 2 work independently with standardized operations.

---

## Phase 5: User Story 3 - Preserve Auditability During Ingestion (Priority: P3)

**Goal**: Persist provenance-compatible run context and conflict lifecycle records so audit and governance workflows can trace accepted and conflicting observations.

**Independent Test**: Execute an ingest run with revised and conflicting records and verify run context, lineage linkage, and conflict records are queryable.

### Tests for User Story 3 (REQUIRED) ⚠️

- [ ] T036 [P] [US3] Add conflict lifecycle contract tests in apps/pipeline/tests/orchestration/test_conflict_lifecycle_contract.py
- [ ] T037 [P] [US3] Add duplicate drift classification tests in apps/pipeline/tests/orchestration/test_duplicate_drift_policy.py
- [ ] T038 [P] [US3] Add provenance persistence and backend audit query compatibility integration test in apps/backend/tests/contract/test_ingest_audit_query_contract.py
- [ ] T051 [P] [US3] Add sampled revision-lineage traceability integration test in apps/backend/tests/contract/test_revision_lineage_traceability.py

### Implementation for User Story 3

- [ ] T039 [US3] Implement duplicate drift classifier in apps/pipeline/src/orchestration/jobs/duplicate_drift_classifier.py
- [ ] T040 [US3] Implement conflict record persistence service in apps/pipeline/src/orchestration/jobs/conflict_persistence_service.py
- [ ] T041 [US3] Implement record outcome and provenance/run-context persistence service in apps/pipeline/src/orchestration/jobs/record_outcome_service.py
- [ ] T042 [US3] Add conflict and duplicate outcome counters to run summaries in apps/pipeline/src/orchestration/jobs/run_outcome_service.py
- [ ] T043 [US3] Extend backend audit projection for conflict identifiers in apps/backend/src/contract/query/provenance_audit_query.py
- [ ] T044 [US3] Add architecture documentation for conflict queryability in docs/architecture/monorepo-boundaries.md

**Checkpoint**: All user stories are independently functional and auditable.

---

## Phase 6: Polish & Cross-Cutting Concerns

**Purpose**: Final verification, documentation consistency, and quality gate completion.

- [ ] T045 [P] Run pipeline quality suite for changed scope using package scripts in package.json
- [ ] T046 [P] Run backend contract tests for changed audit paths in apps/backend/tests/contract
- [ ] T047 Run local DB readiness and migration verification scripts in tools/quality/local-stack/test-db-readiness.sh
- [ ] T048 [P] Update feature-specific quickstart validation steps in specs/005-dagster-ingest-pipeline/quickstart.md
- [ ] T049 [P] Sync canonical command/toolchain updates in AGENTS.md
- [ ] T050 Confirm affected coverage remains >=90% and validate operator visibility <=5 minutes in apps/pipeline/tests/orchestration/test_operator_visibility_slo.py

---

## Dependencies & Execution Order

### Phase Dependencies

- **Phase 1 (Setup)**: No dependencies; starts immediately.
- **Phase 2 (Foundational)**: Depends on Phase 1; blocks all user stories.
- **Phase 3 (US1)**: Depends on Phase 2; establishes MVP onboarding path.
- **Phase 4 (US2)**: Depends on Phase 2 and integrates with US1 registry/runner.
- **Phase 5 (US3)**: Depends on Phase 2 and uses US1/US2 run outputs for auditability.
- **Phase 6 (Polish)**: Depends on completion of all targeted user story phases.

### User Story Dependencies

- **US1 (P1)**: Independent after foundational completion.
- **US2 (P2)**: Independent after foundational completion, but reuses US1 registration/execution abstractions.
- **US3 (P3)**: Independent after foundational completion, but consumes US2 run outcomes and US1 record processing flow.

### Parallel Opportunities

- Phase 1: T002, T003, T004, T005 can run in parallel after T001.
- Phase 2: T007, T009, T010, T013 can run in parallel once T006/T008 baselines exist.
- US1: T016-T018 can run in parallel before implementation tasks.
- US2: T026-T028 and T030-T031 can run in parallel.
- US3: T036-T038 and T039-T041 can run in parallel by file boundary.
- Polish: T045, T046, T048, T049 can run in parallel.

---

## Parallel Example: User Story 2

```bash
# Run US2 test tasks in parallel:
Task: "T026 [US2] Add trigger mode tests in apps/pipeline/tests/orchestration/test_trigger_modes.py"
Task: "T027 [US2] Add partial-success run aggregation test in apps/pipeline/tests/orchestration/test_partial_success_status.py"
Task: "T028 [US2] Add deduplicated queued trigger and deterministic three-rerun test in apps/pipeline/tests/orchestration/test_source_queue_policy.py"

# Run US2 implementation tasks in parallel where file-independent:
Task: "T030 [US2] Implement scheduled job definition in apps/pipeline/src/orchestration/schedules/ingest_schedule.py"
Task: "T031 [US2] Implement on-demand trigger sensor in apps/pipeline/src/orchestration/sensors/ondemand_sensor.py"
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1 and Phase 2.
2. Complete Phase 3 (US1).
3. Validate onboarding independent test for US1.
4. Demo source onboarding flow before expanding scope.

### Incremental Delivery

1. Deliver US1 onboarding path.
2. Add US2 operations and trigger orchestration.
3. Add US3 auditability and conflict lifecycle persistence.
4. Finish with Phase 6 quality/documentation verification.

### Parallel Team Strategy

1. Team completes Phase 1 and Phase 2 together.
2. Then split:
   - Engineer A: US1 tasks.
   - Engineer B: US2 tasks.
   - Engineer C: US3 tasks.
3. Rejoin for Phase 6 cross-cutting verification.

---

## Notes

- All tasks use strict checklist format with ID and explicit file path.
- User story tasks include required [US#] labels.
- Tasks marked [P] are file-independent and parallelizable.
- Test tasks are included per story and foundational components.
- Coverage floor (>=90%) and documentation updates are treated as release blockers.
