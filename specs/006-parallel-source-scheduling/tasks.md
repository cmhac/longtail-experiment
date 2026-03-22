# Tasks: Parallel Source Scheduling and Bounded Concurrency

**Input**: Design documents from `/specs/006-parallel-source-scheduling/`  
**Prerequisites**: plan.md (required), spec.md (required), research.md, data-model.md, contracts/, quickstart.md

**Tests**: Test tasks are REQUIRED. Every user story and foundational component MUST include automated coverage sufficient to keep affected projects at or above 90%.

**Organization**: Tasks are grouped by user story so each story can be implemented and tested independently.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependency on incomplete tasks)
- **[Story]**: User story label (US1, US2, US3)
- Every task includes an exact file path

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Prepare repository wiring for feature implementation and validation.

- [X] T001 Add orchestration test target filters for cadence and parallel execution in apps/pipeline/project.json
- [X] T002 Add local verification command notes for feature 006 in specs/006-parallel-source-scheduling/quickstart.md
- [X] T003 [P] Add placeholder architecture note for per-source scheduling in docs/architecture/monorepo-boundaries.md
- [X] T004 [P] Add onboarding note for source schedule metadata maintenance in docs/onboarding/monorepo-baseline.md
- [X] T005 [P] Add local runbook notes for bounded parallel ingestion validation in docs/runbooks/local-stack-baseline.md

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Build shared runtime primitives required by all user stories.

**⚠️ CRITICAL**: No user story phase should start until this phase is complete.

- [X] T006 Add source schedule policy and eligibility snapshot ORM models in libs/db/src/db/models/ingestion_runtime.py
- [X] T007 Export new runtime models in libs/db/src/db/models/**init**.py
- [X] T008 Create migration for schedule policy and eligibility persistence in libs/db/alembic/versions/0003_source_schedule_and_eligibility.py
- [X] T009 [P] Extend run repository persistence contract for due/executed/deferred/not-due counts in apps/pipeline/src/orchestration/resources/postgres_run_repository.py
- [X] T010 [P] Add runtime repository helper methods for eligibility snapshot writes/reads in apps/pipeline/src/orchestration/resources/postgres_run_repository.py
- [X] T011 Add schedule policy schema and validation helpers in apps/pipeline/src/orchestration/jobs/source_schedule_policy.py
- [X] T012 Add due-source selection service with strict FIFO ordering by earliest due timestamp in apps/pipeline/src/orchestration/jobs/due_source_selector.py
- [X] T013 Add bounded parallel execution service interface in apps/pipeline/src/orchestration/jobs/parallel_source_executor.py
- [X] T014 Wire foundational services into runtime container in apps/pipeline/src/orchestration/runtime.py
- [X] T015 Update orchestration package exports for new foundational modules in apps/pipeline/src/orchestration/jobs/**init**.py
- [X] T016 Add foundational unit tests for schedule policy validation and due selection in apps/pipeline/tests/orchestration/test_source_schedule_policy.py
- [X] T017 Add migration/model tests for new runtime entities in libs/db/tests/test_ingestion_runtime_models.py

**Checkpoint**: Foundational primitives complete; user stories can begin.

---

## Phase 3: User Story 1 - Control Run Throughput (Priority: P1) 🎯 MVP

**Goal**: Execute due sources with bounded parallelism while keeping runs progressing under partial failure.

**Independent Test**: Configure source count greater than parallelism cap and verify active executions never exceed the cap while due sources complete or fail with explicit outcomes.

### Tests for User Story 1 (REQUIRED)

- [X] T018 [P] [US1] Add bounded parallelism integration test for max-active-source ceiling in apps/pipeline/tests/orchestration/test_bounded_parallel_execution.py
- [X] T019 [P] [US1] Add failure-isolation integration test for mixed source outcomes under bounded parallel execution in apps/pipeline/tests/orchestration/test_bounded_parallel_execution.py
- [X] T020 [P] [US1] Add strict FIFO earliest-due ordering unit test for equal-capacity contention in apps/pipeline/tests/orchestration/test_bounded_parallel_execution.py

### Implementation for User Story 1

- [X] T021 [US1] Implement bounded parallel source launch loop with strict FIFO earliest-due queue policy in apps/pipeline/src/orchestration/jobs/parallel_source_executor.py
- [X] T022 [US1] Integrate bounded parallel executor into run coordinator flow in apps/pipeline/src/orchestration/jobs/run_coordinator.py
- [X] T023 [US1] Extend run summary counters for due/executed/deferred/failed source counts in apps/pipeline/src/orchestration/jobs/run_coordinator.py
- [X] T024 [US1] Persist per-source terminal states for deferred and failure cases in apps/pipeline/src/orchestration/resources/postgres_run_repository.py
- [X] T025 [US1] Ensure source-level overlap guard is enforced during parallel launches in apps/pipeline/src/orchestration/jobs/run_coordinator.py
- [X] T026 [US1] Update ingest job output payload to include bounded-execution aggregate counters in apps/pipeline/src/orchestration/jobs/ingest_job.py
- [X] T027 [US1] Add runtime integration test validating persisted bounded-execution counters and tick-boundary carry-forward behavior in apps/pipeline/tests/orchestration/test_ingest_job_runtime.py

**Checkpoint**: US1 is independently functional and testable (MVP).

---

## Phase 4: User Story 2 - Schedule Sources by Cadence (Priority: P2)

**Goal**: Run only due sources based on explicit per-source cadence metadata.

**Independent Test**: Register mixed-cadence sources with different last-success timestamps and verify scheduled runs include only due sources.

### Tests for User Story 2 (REQUIRED)

- [X] T028 [P] [US2] Add due/not-due selection tests across hourly/daily/weekly/monthly cadence policies in apps/pipeline/tests/orchestration/test_source_cadence_selection.py
- [X] T029 [P] [US2] Add invalid policy handling test for malformed cadence metadata, including skipped_invalid_policy warning assertions, in apps/pipeline/tests/orchestration/test_source_cadence_selection.py
- [X] T030 [P] [US2] Add trigger-mode integration test asserting scheduled runs include only due sources and on-demand selected sources bypass due-state in apps/pipeline/tests/orchestration/test_ingest_schedule_due_sources.py

### Implementation for User Story 2

- [X] T031 [US2] Extend workflow registration metadata to include source schedule policy in apps/pipeline/src/orchestration/jobs/workflow_registry.py
- [X] T032 [US2] Implement due-source filtering for scheduled runs in apps/pipeline/src/orchestration/jobs/due_source_selector.py
- [X] T033 [US2] Update scheduled trigger wiring to pass due-source subset context in apps/pipeline/src/orchestration/schedules/ingest_schedule.py
- [X] T034 [US2] Apply due-source subset execution path in run coordinator for scheduled triggers and due-state bypass for on-demand selected subsets in apps/pipeline/src/orchestration/jobs/run_coordinator.py
- [X] T035 [US2] Persist eligibility snapshots and not-due reasons per source per run in apps/pipeline/src/orchestration/resources/postgres_run_repository.py
- [X] T036 [US2] Register cadence metadata for existing example and dummy sources in apps/pipeline/src/orchestration/runtime.py
- [X] T037 [US2] Add DB persistence test for eligibility snapshot records in apps/pipeline/tests/orchestration/test_run_eligibility_persistence.py

**Checkpoint**: US1 and US2 operate independently with due-state scheduling.

---

## Phase 5: User Story 3 - Operate with Predictable Visibility (Priority: P3)

**Goal**: Provide persisted run visibility for due/executed/deferred/not-due source states and operator triage.

**Independent Test**: Run mixed-cadence and constrained-capacity scenarios and verify persisted run records explain why each source did or did not execute.

### Tests for User Story 3 (REQUIRED)

- [X] T038 [P] [US3] Add source eligibility and outcome audit contract test in apps/pipeline/tests/orchestration/test_run_visibility_audit.py
- [X] T039 [P] [US3] Add operator triage query test for deferred/not-due reason codes in apps/backend/tests/contract/test_ingest_audit_query_contract.py
- [X] T040 [P] [US3] Add run-level aggregate consistency test (sum of source states equals run counters) in apps/pipeline/tests/orchestration/test_run_visibility_audit.py

### Implementation for User Story 3

- [X] T041 [US3] Extend run repository read API to return eligibility and outcome reason details in apps/pipeline/src/orchestration/resources/postgres_run_repository.py
- [X] T042 [US3] Include due/executed/deferred/not-due counters in run summary aggregation service in apps/pipeline/src/orchestration/jobs/run_outcome_service.py
- [X] T043 [US3] Update ingest job logging fields for operator triage visibility, including warning-level carry-forward and invalid-policy signals, in apps/pipeline/src/orchestration/jobs/ingest_job.py
- [X] T044 [US3] Update backend audit projection for new run visibility fields in apps/backend/src/contract/query/provenance_audit_query.py
- [X] T045 [US3] Add orchestration definitions smoke assertion for visibility resources in apps/pipeline/tests/orchestration/test_definitions_smoke.py

**Checkpoint**: All user stories are independently functional and auditable.

---

## Phase 6: Polish & Cross-Cutting Concerns

**Purpose**: Final hardening, documentation sync, and full-quality verification.

- [X] T046 [P] Update feature-specific commands and outcomes in specs/006-parallel-source-scheduling/quickstart.md
- [X] T047 [P] Update repository operation docs for per-source scheduling behavior in docs/runbooks/local-stack-baseline.md
- [X] T048 [P] Update architecture and onboarding docs for source schedule policy ownership in docs/architecture/monorepo-boundaries.md
- [X] T049 Run full pipeline quality gate suite and capture results in specs/006-parallel-source-scheduling/quickstart.md
- [X] T050 Run local DB migration, scheduled-run verification, and two-week backlog replay checks for missed due-window risk and document outputs in specs/006-parallel-source-scheduling/quickstart.md
- [X] T051 Update AGENTS.md with canonical commands/workflow changes introduced by feature 006 in AGENTS.md

---

## Dependencies & Execution Order

### Phase Dependencies

- **Phase 1 (Setup)**: Can start immediately.
- **Phase 2 (Foundational)**: Depends on Phase 1 completion; blocks all user stories.
- **Phase 3 (US1)**: Depends on Phase 2 completion; defines MVP.
- **Phase 4 (US2)**: Depends on Phase 2 completion and integrates with US1 coordinator flow.
- **Phase 5 (US3)**: Depends on Phases 3 and 4 for complete visibility semantics.
- **Phase 6 (Polish)**: Depends on all user-story phases.

### User Story Dependencies

- **US1 (P1)**: No dependency on other user stories once foundational phase is complete.
- **US2 (P2)**: Depends on foundational phase; can start after US1 baseline coordinator integration is in place.
- **US3 (P3)**: Depends on US1 bounded execution states and US2 eligibility persistence outputs.

### Within Each User Story

- Tests are authored before implementation and should fail before code changes.
- Models/persistence changes precede service orchestration behavior.
- Service behavior precedes run wiring and integration assertions.

### Dependency Graph

- Setup -> Foundational -> US1 -> US3
- Setup -> Foundational -> US2 -> US3
- US1 + US2 + US3 -> Polish

---

## Parallel Opportunities

- **Setup**: T003, T004, T005 can run in parallel.
- **Foundational**: T009 and T010 can run in parallel after T006-T008; T016 and T017 can run in parallel after foundational implementation.
- **US1**: T018, T019, T020 can run in parallel; T027 can run after T022-T026.
- **US2**: T028, T029, T030 can run in parallel; T035 and T036 can run in parallel after T031-T034.
- **US3**: T038, T039, T040 can run in parallel; T043 and T044 can run in parallel after T041-T042.
- **Polish**: T046, T047, T048 can run in parallel.

### Parallel Example: User Story 1

```bash
Task: "T018 [US1] Add bounded parallelism integration test in apps/pipeline/tests/orchestration/test_bounded_parallel_execution.py"
Task: "T019 [US1] Add failure-isolation integration test in apps/pipeline/tests/orchestration/test_bounded_parallel_execution.py"
Task: "T020 [US1] Add deterministic launch-order unit test in apps/pipeline/tests/orchestration/test_bounded_parallel_execution.py"
```

### Parallel Example: User Story 2

```bash
Task: "T028 [US2] Add due/not-due selection tests in apps/pipeline/tests/orchestration/test_source_cadence_selection.py"
Task: "T029 [US2] Add invalid policy handling test in apps/pipeline/tests/orchestration/test_source_cadence_selection.py"
Task: "T030 [US2] Add scheduler tick integration test in apps/pipeline/tests/orchestration/test_ingest_schedule_due_sources.py"
```

### Parallel Example: User Story 3

```bash
Task: "T038 [US3] Add source eligibility and outcome audit contract test in apps/pipeline/tests/orchestration/test_run_visibility_audit.py"
Task: "T039 [US3] Add operator triage query test in apps/backend/tests/contract/test_ingest_audit_query_contract.py"
Task: "T040 [US3] Add aggregate consistency test in apps/pipeline/tests/orchestration/test_run_visibility_audit.py"
```

---

## Implementation Strategy

### MVP First (US1 Only)

1. Complete Phase 1 and Phase 2.
2. Complete Phase 3 (US1).
3. Validate bounded parallel throughput independently.
4. Demo/deploy MVP if stable.

### Incremental Delivery

1. Setup + foundational baseline.
2. Deliver US1 bounded concurrency.
3. Deliver US2 per-source cadence selection.
4. Deliver US3 run visibility and audit completeness.
5. Execute polish and full quality gates.

### Suggested MVP Scope

- **MVP**: User Story 1 (Phase 3) after setup and foundational phases.

---

## Notes

- All tasks follow strict checklist format with ID, optional [P], optional [USx], and file path.
- Coverage in affected projects must remain >=90% throughout implementation.
- Documentation updates and AGENTS.md updates are required in the same change as behavior changes.
