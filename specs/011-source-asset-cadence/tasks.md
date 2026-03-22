# Tasks: Per-Source Asset Cadence

**Input**: Design documents from /specs/011-source-asset-cadence/
**Prerequisites**: plan.md (required), spec.md (required for user stories), research.md, data-model.md, contracts/

**Tests**: Test tasks are REQUIRED. Every user story and foundational component MUST include automated test coverage sufficient to maintain >= 90% coverage in affected projects.

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: [ID] [P?] [Story] Description

- [P]: Can run in parallel (different files, no dependencies)
- [Story]: Which user story this task belongs to (for example, US1, US2, US3)
- Include exact file paths in descriptions

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Prepare baseline scaffolding for schedule ownership migration.

- [x] T001 Capture feature baseline and impacted modules in specs/011-source-asset-cadence/plan.md
- [x] T002 Create migration notes skeleton in docs/runbooks/source-asset-scheduling-cutover.md
- [x] T003 [P] Add schedule-ownership verification section placeholder in docs/onboarding/monorepo-baseline.md
- [x] T004 [P] Add architecture delta placeholder for scheduling model in docs/architecture/monorepo-boundaries.md

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Remove shared cadence foundations and establish runtime primitives required by all stories.

**CRITICAL**: No user story work begins until this phase is complete.

- [x] T005 Remove shared ingest schedule definition from apps/pipeline/src/orchestration/schedules/ingest_schedule.py
- [x] T006 Remove shared schedule wiring from apps/pipeline/src/orchestration/definitions.py
- [x] T007 Refactor scheduled-path cadence ownership logic in apps/pipeline/src/orchestration/jobs/run_coordinator.py
- [x] T008 Remove due-selector dependency from runtime assembly in apps/pipeline/src/orchestration/runtime.py
- [x] T009 [P] Deprecate due-evaluation helper for scheduled flow in apps/pipeline/src/orchestration/jobs/due_source_selector.py
- [x] T010 [P] Deprecate source cadence policy helper for active scheduling decisions in apps/pipeline/src/orchestration/jobs/source_schedule_policy.py
- [x] T011 Add foundational regression test for absence of shared all-source schedule in apps/pipeline/tests/orchestration/test_definitions_smoke.py
- [x] T012 Add foundational regression test for runtime without shared due-filter scheduled path in apps/pipeline/tests/orchestration/test_run_coordinator.py

**Checkpoint**: Shared-schedule architecture is retired and source-schedule foundations are ready.

---

## Phase 3: User Story 1 - Schedule Each Source Independently (Priority: P1) MVP

**Goal**: Each active source asset owns and executes from its own schedule.

**Independent Test**: Configure distinct cadences for at least three source assets and verify each triggers on its own schedule without a shared run-all cadence.

### Tests for User Story 1 (REQUIRED)

- [x] T013 [P] [US1] Add schedule registration test for per-source cadence definitions in apps/pipeline/tests/orchestration/test_definitions_smoke.py
- [x] T014 [P] [US1] Add integration test for independent source cadence triggering in apps/pipeline/tests/orchestration/test_ingest_schedule_due_sources.py
- [x] T015 [P] [US1] Add source asset schedule ownership test in apps/pipeline/tests/orchestration/test_source_cadence_selection.py

### Implementation for User Story 1

- [x] T016 [US1] Implement source-specific schedule definitions for dummy, example, and fred assets in apps/pipeline/src/orchestration/schedules/source_asset_schedules.py
- [x] T017 [US1] Wire per-source schedules into Dagster definitions in apps/pipeline/src/orchestration/definitions.py
- [x] T018 [US1] Update source asset definitions to align scheduled execution entrypoint with source ownership in apps/pipeline/src/orchestration/source_asset_definitions.py
- [x] T019 [US1] Update runtime schedule catalog metadata to enumerate per-source schedules in apps/pipeline/src/orchestration/definitions.py
- [x] T020 [US1] Add schedule-state visibility metadata for source assets in apps/pipeline/src/orchestration/source_asset_definitions.py
- [x] T021 [US1] Update quick local verification helper for per-source schedule visibility in tools/quality/local-stack/test-dagit-endpoint.sh
- [x] T022 [US1] Verify US1 coverage impact and threshold in apps/pipeline/tests/orchestration/test_definitions_smoke.py

**Checkpoint**: US1 delivers independently scheduled source assets and is testable on its own.

---

## Phase 4: User Story 2 - Simplify Scheduling Operations (Priority: P2)

**Goal**: Make schedule behavior understandable entirely through source-level Dagster schedules and attribution.

**Independent Test**: Remove legacy shared cadence routing and validate run timing and attribution via source schedules only.

### Tests for User Story 2 (REQUIRED)

- [x] T023 [P] [US2] Add run attribution integration test for source schedule trigger origin in apps/pipeline/tests/orchestration/test_trigger_modes.py
- [x] T024 [P] [US2] Add repository persistence test for source trigger attribution in apps/pipeline/tests/orchestration/test_source_outcome_visibility.py
- [x] T025 [P] [US2] Add local-stack smoke test for per-source schedule introspection in tools/quality/local-stack/test-compose-stack.sh

### Implementation for User Story 2

- [x] T026 [US2] Simplify ingest execution flow to rely on schedule-owned source selection in apps/pipeline/src/orchestration/jobs/ingest_job.py
- [x] T027 [US2] Update run summary schema to emphasize trigger attribution and remove obsolete due/not-due semantics in apps/pipeline/src/orchestration/jobs/run_coordinator.py
- [x] T028 [US2] Update outcome aggregation fields for source-owned schedule model in apps/pipeline/src/orchestration/jobs/run_outcome_service.py
- [x] T029 [US2] Update run repository insert/select mappings for revised run summary fields in apps/pipeline/src/orchestration/resources/postgres_run_repository.py
- [x] T030 [US2] Add operator-visible trigger attribution mapping in runtime view helpers in apps/pipeline/src/orchestration/runtime.py
- [x] T031 [US2] Align on-demand sensor tags with source-owned trigger attribution in apps/pipeline/src/orchestration/sensors/ondemand_sensor.py
- [x] T032 [US2] Verify US2 coverage impact and threshold in apps/pipeline/tests/orchestration/test_trigger_modes.py

**Checkpoint**: US2 delivers simplified schedule operations with clear trigger attribution.

---

## Phase 5: User Story 3 - Perform a Safe Hard Cutover (Priority: P3)

**Goal**: Complete hard cutover by removing active legacy cadence artifacts while preserving historical interpretability.

**Independent Test**: Validate no active shared all-source schedule path exists and legacy cadence artifacts do not drive current scheduling.

### Tests for User Story 3 (REQUIRED)

- [x] T033 [P] [US3] Add migration test for legacy cadence artifact historical-only behavior in libs/db/tests/test_ingestion_runtime_migrations.py
- [x] T034 [P] [US3] Add orchestration regression test proving no shared schedule trigger path in apps/pipeline/tests/orchestration/test_ingest_job_runtime.py
- [x] T035 [P] [US3] Add integration test for historical artifact non-authority in apps/pipeline/tests/orchestration/test_run_visibility_audit.py

### Implementation for User Story 3

- [x] T036 [US3] Create migration to rationalize legacy schedule-policy and eligibility schema in libs/db/alembic/versions/0005_source_asset_schedule_cutover.py
- [x] T037 [US3] Update ingestion runtime ORM models for post-cutover schema contract in libs/db/src/db/models/ingestion_runtime.py
- [x] T038 [US3] Remove legacy schedule-policy persistence methods from repository runtime path in apps/pipeline/src/orchestration/resources/postgres_run_repository.py
- [x] T039 [US3] Update runtime clear/fetch behaviors for historical artifact interpretation in apps/pipeline/src/orchestration/resources/postgres_run_repository.py
- [x] T040 [US3] Implement explicit cutover guardrails in scheduling authority checks in apps/pipeline/src/orchestration/runtime.py
- [x] T041 [US3] Update source discovery defaults to cadence metadata used only for operator visibility in apps/pipeline/src/orchestration/jobs/source_assets/discovery.py
- [x] T042 [US3] Verify US3 coverage impact and threshold in libs/db/tests/test_ingestion_runtime_models.py

**Checkpoint**: US3 completes hard cutover and preserves historical context without active legacy authority.

---

## Phase 6: Polish & Cross-Cutting Concerns

**Purpose**: Final consistency, documentation, and end-to-end validation across stories.

- [x] T043 [P] Update cutover runbook with verification commands in docs/runbooks/local-stack-baseline.md
- [x] T044 [P] Update onboarding guidance for per-source schedule operations in docs/onboarding/monorepo-baseline.md
- [x] T045 [P] Update architecture documentation for schedule ownership model in docs/architecture/monorepo-boundaries.md
- [x] T046 [P] Update spec quickstart alignment notes in specs/011-source-asset-cadence/quickstart.md
- [x] T047 Run feature quality gate command set and document results in specs/011-source-asset-cadence/quickstart.md
- [x] T048 Run local compose end-to-end schedule verification and document results in specs/011-source-asset-cadence/quickstart.md
- [x] T049 Update AGENTS feature history and canonical commands for schedule model changes in AGENTS.md

---

## Dependencies & Execution Order

### Phase Dependencies

- Setup (Phase 1): no dependencies.
- Foundational (Phase 2): depends on Setup and blocks all user stories.
- User stories (Phases 3-5): depend on Foundational completion; execute in priority order for MVP delivery.
- Polish (Phase 6): depends on selected user stories being complete.

### User Story Dependencies

- US1 (P1): starts immediately after Foundational and is the MVP.
- US2 (P2): starts after Foundational; depends on US1 schedule definitions for attribution integration.
- US3 (P3): starts after Foundational; should follow US2 to reduce migration/repository churn risk.

### Within Each User Story

- Write tests first and ensure they fail.
- Implement scheduling/runtime changes.
- Update persistence and operator visibility behavior.
- Validate coverage threshold for affected projects.

### Dependency Graph

- Phase 1 -> Phase 2 -> US1 -> US2 -> US3 -> Phase 6
- Optional parallel lane after Phase 2: start US3 test authoring (T033-T035) while US2 implementation is in progress.

---

## Parallel Opportunities

- Phase 1 parallel tasks: T003, T004
- Phase 2 parallel tasks: T009, T010
- US1 parallel tests: T013, T014, T015
- US2 parallel tests: T023, T024, T025
- US3 parallel tests: T033, T034, T035
- Polish parallel docs: T043, T044, T045, T046

---

## Parallel Example: User Story 1

```bash
Task: "Add schedule registration test for per-source cadence definitions in apps/pipeline/tests/orchestration/test_definitions_smoke.py"
Task: "Add integration test for independent source cadence triggering in apps/pipeline/tests/orchestration/test_ingest_schedule_due_sources.py"
Task: "Add source asset schedule ownership test in apps/pipeline/tests/orchestration/test_source_cadence_selection.py"
```

## Parallel Example: User Story 2

```bash
Task: "Add run attribution integration test for source schedule trigger origin in apps/pipeline/tests/orchestration/test_trigger_modes.py"
Task: "Add repository persistence test for source trigger attribution in apps/pipeline/tests/orchestration/test_source_outcome_visibility.py"
Task: "Add local-stack smoke test for per-source schedule introspection in tools/quality/local-stack/test-compose-stack.sh"
```

## Parallel Example: User Story 3

```bash
Task: "Add migration test for legacy cadence artifact historical-only behavior in libs/db/tests/test_ingestion_runtime_migrations.py"
Task: "Add orchestration regression test proving no shared schedule trigger path in apps/pipeline/tests/orchestration/test_ingest_job_runtime.py"
Task: "Add integration test for historical artifact non-authority in apps/pipeline/tests/orchestration/test_run_visibility_audit.py"
```

---

## Implementation Strategy

### MVP First (US1 Only)

1. Complete Phase 1 and Phase 2.
2. Complete US1 (Phase 3).
3. Validate independent source schedules in Dagit and orchestration tests.
4. Demo and checkpoint before US2/US3.

### Incremental Delivery

1. Deliver US1 for independent source scheduling.
2. Deliver US2 for attribution and operational simplification.
3. Deliver US3 for hard cutover and legacy artifact migration.
4. Finish with Phase 6 documentation and full verification.

### Parallel Team Strategy

1. Team completes Setup and Foundational phases together.
2. Engineer A drives US1 schedule definitions.
3. Engineer B drives US2 attribution and repository mappings.
4. Engineer C prepares US3 migration tests and schema changes.
5. Rejoin for Phase 6 quality and local-stack verification.

---

## Notes

- All tasks follow strict checklist format: checkbox, task ID, optional [P], required [USx] in story phases, and explicit file path.
- Tests are included for foundational and each user story to maintain >= 90% coverage in affected projects.
- User stories are independently testable and mapped to spec priorities P1 -> P2 -> P3.
- No task uses a quality-gate bypass, suppression-only strategy, or undocumented behavior change.
