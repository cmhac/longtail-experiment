# Tasks: Schedule State Persistence

**Input**: Design documents from `specs/007-schedule-state-persistence/`
**Prerequisites**: plan.md (required), spec.md (required), data-model.md, contracts/, research.md, quickstart.md

**Tests**: Test tasks are REQUIRED. Every user story and repository method MUST include automated coverage sufficient to keep affected projects at or above 90%.

**Organization**: Tasks are grouped by user story so each story can be implemented and tested independently.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependency on incomplete tasks)
- **[Story]**: User story label (US1, US2, US3)
- Every task includes an exact file path

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Prepare repository structure and spec artifacts for feature implementation.

- [x] T001 Create spec directory structure for feature 007 in specs/007-schedule-state-persistence/
- [x] T002 [P] Create data-model.md documenting the source_schedule_policies entity in specs/007-schedule-state-persistence/data-model.md
- [x] T003 [P] Create research.md documenting technical decisions and rationale in specs/007-schedule-state-persistence/research.md
- [x] T004 [P] Create quickstart.md with real-world verification steps for local DB schedule state checks in specs/007-schedule-state-persistence/quickstart.md
- [x] T005 [P] Create schedule-state-persistence-contract.md in specs/007-schedule-state-persistence/contracts/schedule-state-persistence-contract.md
- [x] T006 [P] Create checklists/requirements.md with specification quality validation in specs/007-schedule-state-persistence/checklists/requirements.md

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Add repository persistence methods that both US1 and US2 depend on.

**⚠️ CRITICAL**: No user story phase should start until this phase is complete.

- [x] T007 Add `read_all_schedule_policies() -> dict[str, dict[str, Any]]` method to PostgresRunRepository that SELECT all rows from source_schedule_policies keyed by source_key in apps/pipeline/src/orchestration/resources/postgres_run_repository.py
- [x] T008 Add `upsert_schedule_policy(source_key, cadence_type, last_successful_at, updated_at)` method to PostgresRunRepository using INSERT ON CONFLICT (source_key) DO UPDATE in apps/pipeline/src/orchestration/resources/postgres_run_repository.py
- [x] T009 Extend `clear_all()` in PostgresRunRepository to also DELETE FROM source_schedule_policies for test isolation in apps/pipeline/src/orchestration/resources/postgres_run_repository.py

**Checkpoint**: Repository methods exist and are callable; user stories can begin.

---

## Phase 3: User Story 1 - Enforce Per-Source Cadence Across Runs (Priority: P1) 🎯 MVP

**Goal**: Sources are evaluated against their DB-persisted last_successful_at before each run, so sources only execute when their cadence has elapsed.

**Independent Test**: Run the pipeline once with all sources succeeding. Immediately trigger a second run. Verify all sources are not_due and no executions occur.

### Tests for User Story 1 (REQUIRED)

- [x] T010 [P] [US1] Add unit test asserting coordinator marks source not_due when DB reports a recent last_successful_at within cadence window in apps/pipeline/tests/orchestration/test_run_coordinator.py
- [x] T011 [P] [US1] Add unit test asserting coordinator marks source due when DB reports a stale last_successful_at outside cadence window in apps/pipeline/tests/orchestration/test_run_coordinator.py
- [x] T012 [P] [US1] Add integration test for read_all_schedule_policies returning empty dict when table has no rows in apps/pipeline/tests/orchestration/test_schedule_policy_persistence.py
- [x] T013 [P] [US1] Add integration test for read_all_schedule_policies returning all inserted source keys in apps/pipeline/tests/orchestration/test_schedule_policy_persistence.py

### Implementation for User Story 1

- [x] T014 [US1] Add `dataclasses.replace` import to run_coordinator.py in apps/pipeline/src/orchestration/jobs/run_coordinator.py
- [x] T015 [US1] Add `_hydrate_schedule_policies(registrations, db_policies)` static method to RunCoordinator that patches last_successful_at from DB rows onto each registration's schedule policy using model_copy and dataclasses.replace in apps/pipeline/src/orchestration/jobs/run_coordinator.py
- [x] T016 [US1] Wire DB policy read path into RunCoordinator.run() before \_build_eligibility_decisions(): call read_all_schedule_policies via getattr, then call \_hydrate_schedule_policies with the result in apps/pipeline/src/orchestration/jobs/run_coordinator.py

**Checkpoint**: US1 is independently functional — second immediate run produces all not_due outcomes.

---

## Phase 4: User Story 2 - Preserve Schedule State Across Restarts (Priority: P2)

**Goal**: After a successful run, last_successful_at is durably written to the DB so that a pipeline restart does not reset cadence enforcement.

**Independent Test**: Run the pipeline so all sources succeed. Confirm source_schedule_policies rows exist. Simulate restart (re-initialize runtime). Re-run and verify sources remain not_due.

### Tests for User Story 2 (REQUIRED)

- [x] T017 [P] [US2] Add unit test asserting coordinator calls upsert_schedule_policy once per successful source result after execution in apps/pipeline/tests/orchestration/test_run_coordinator.py
- [x] T018 [P] [US2] Add integration test asserting upsert_schedule_policy inserts a new row for a new source_key in apps/pipeline/tests/orchestration/test_schedule_policy_persistence.py
- [x] T019 [P] [US2] Add integration test asserting upsert_schedule_policy overwrites last_successful_at on a second call for the same source_key in apps/pipeline/tests/orchestration/test_schedule_policy_persistence.py

### Implementation for User Story 2

- [x] T020 [US2] Wire DB policy write path into RunCoordinator.run() after execution: for each source_result with status "success" and a non-None schedule_policy, call upsert_schedule_policy via getattr with completed_at as last_successful_at in apps/pipeline/src/orchestration/jobs/run_coordinator.py

**Checkpoint**: US1 and US2 are independently functional — schedule state survives process restart.

---

## Phase 5: User Story 3 - Inspect and Reset Source Schedule State (Priority: P3)

**Goal**: Operators can read and manipulate source_schedule_policies via SQL to force specific sources to re-run or inspect scheduling anomalies.

**Independent Test**: Backdate a source's last_successful_at beyond its cadence. Trigger the orchestrator. Verify the backdated source is due while others remain not_due.

### Tests for User Story 3 (REQUIRED)

- [x] T021 [P] [US3] Add integration test asserting clear_all() removes source_schedule_policies rows alongside other runtime tables in apps/pipeline/tests/orchestration/test_schedule_policy_persistence.py
- [x] T022 [P] [US3] Add integration test: run full Dagster ingest_job, confirm source_schedule_policies rows are created for all registered sources in apps/pipeline/tests/orchestration/test_ingest_job_runtime.py

### Implementation for User Story 3

- [x] T023 [US3] Update test_ingest_job_runtime.py carry-forward test to call clear_all() before acquiring locks so prior schedule state does not cause sources to appear not_due instead of deferred in apps/pipeline/tests/orchestration/test_ingest_job_runtime.py
- [x] T024 [US3] Document SQL commands for inspecting, backdating, and clearing source schedule state in specs/007-schedule-state-persistence/quickstart.md

**Checkpoint**: All user stories functional; operator reset workflow documented and verified.

---

## Phase 6: Polish & Cross-Cutting Concerns

**Purpose**: Final validation, documentation sync, and quality gate confirmation.

- [x] T025 [P] Update quickstart.md with real verification output from live DB runs (run 1 all-due, run 2 all not_due, backdate + run 3 selective due) in specs/007-schedule-state-persistence/quickstart.md
- [x] T026 [P] Update docs/runbooks/local-stack-baseline.md with schedule state inspection and reset procedures in docs/runbooks/local-stack-baseline.md
- [x] T027 Run full pipeline quality gate suite and confirm ≥90% coverage in apps/pipeline
- [x] T028 Update AGENTS.md if any new canonical commands or workflows are introduced in AGENTS.md

---

## Dependencies & Execution Order

### Phase Dependencies

- **Phase 1 (Setup)**: Can start immediately.
- **Phase 2 (Foundational)**: Depends on Phase 1; blocks all user stories.
- **Phase 3 (US1)**: Depends on Phase 2 (read_all_schedule_policies).
- **Phase 4 (US2)**: Depends on Phase 2 (upsert_schedule_policy) and can run in parallel with US1.
- **Phase 5 (US3)**: Depends on Phases 3 and 4 for full scheduling behavior.
- **Phase 6 (Polish)**: Depends on all user-story phases.

### User Story Dependencies

- **US1 (P1)**: Requires T007 (read method).
- **US2 (P2)**: Requires T008 (upsert method).
- **US3 (P3)**: Requires US1 + US2 to be testable end-to-end.

### Within Each User Story

- Tests are written before or alongside implementation and should fail before code changes.
- Repository methods precede coordinator wiring.
- Coordinator wiring precedes integration tests.

### Dependency Graph

```
Setup -> Foundational (T007-T009)
  -> US1 (T010-T016) -> US3 (T021-T024)
  -> US2 (T017-T020) -> US3
US1 + US2 + US3 -> Polish
```

---

## Parallel Opportunities

- **Phase 1**: T002, T003, T004, T005, T006 can all run in parallel after T001.
- **Phase 3**: T010, T011, T012, T013 can run in parallel; T014, T015 can run in parallel before T016.
- **Phase 4**: T017, T018, T019 can run in parallel; T020 follows T017.
- **Phase 5**: T021, T022 can run in parallel.
- **Phase 6**: T025, T026 can run in parallel.

### Parallel Example: User Story 1 Tests

```bash
Task: "T010 [US1] Unit test: not_due when DB has recent ts in apps/pipeline/tests/orchestration/test_run_coordinator.py"
Task: "T011 [US1] Unit test: due when DB has stale ts in apps/pipeline/tests/orchestration/test_run_coordinator.py"
Task: "T012 [US1] Integration test: read returns empty in apps/pipeline/tests/orchestration/test_schedule_policy_persistence.py"
Task: "T013 [US1] Integration test: read returns all keys in apps/pipeline/tests/orchestration/test_schedule_policy_persistence.py"
```

### Parallel Example: User Story 2 Tests

```bash
Task: "T018 [US2] Integration test: upsert inserts new row in apps/pipeline/tests/orchestration/test_schedule_policy_persistence.py"
Task: "T019 [US2] Integration test: upsert overwrites on conflict in apps/pipeline/tests/orchestration/test_schedule_policy_persistence.py"
```

---

## Implementation Strategy

**MVP scope**: Phase 2 + Phase 3 (US1 read path). After T016, the second-run not-due behavior is demonstrable against the live DB. US2 write path (T020) completes the durable state contract. US3 adds operator tooling and test isolation.

**Incremental delivery**:

1. Foundational (T007-T009): DB access layer
2. US1 (T010-T016): Read path + hydration
3. US2 (T017-T020): Write path + durability
4. US3 (T021-T024): Test isolation + operator docs
5. Polish (T025-T028): Quality gate + runbook
