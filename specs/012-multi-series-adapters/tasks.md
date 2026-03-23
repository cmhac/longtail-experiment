# Tasks: Multi-Series Source Adapter Model

**Input**: Design documents from `/specs/012-multi-series-adapters/`
**Prerequisites**: plan.md (required), spec.md (required for user stories), research.md, data-model.md, contracts/

**Tests**: Test tasks are REQUIRED. Every user story and foundational component MUST include automated test coverage sufficient to maintain >= 90% coverage in affected projects.

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: [ID] [P?] [Story] Description

- [P]: Can run in parallel (different files, no dependencies)
- [Story]: Which user story this task belongs to (e.g., US1, US2, US3)
- Include exact file paths in descriptions

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Prepare feature scaffolding, canonical naming conventions, and verification entrypoints.

- [x] T001 Create feature task and verification command aliases in apps/pipeline/project.json
- [x] T002 [P] Create multi-series design notes anchor in docs/architecture/monorepo-boundaries.md
- [x] T003 [P] Add runbook section defining grouped-vs-split decision criteria and ownership transition guardrails in docs/runbooks/local-stack-baseline.md
- [x] T004 [P] Add onboarding section defining series-item naming, trigger expectations, and escalation workflow in docs/onboarding/monorepo-baseline.md
- [x] T005 Add feature quick validation command references in specs/012-multi-series-adapters/quickstart.md

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Introduce shared runtime primitives required by all user stories.

**CRITICAL**: No user story implementation can begin before this phase is complete.

- [x] T006 Implement provider-group and series-item catalog types in apps/pipeline/src/orchestration/jobs/source_assets/series_catalog.py
- [x] T007 [P] Implement ownership-mode validation and overlap guards in apps/pipeline/src/orchestration/jobs/source_assets/ownership_mode.py
- [x] T008 [P] Extend source discovery to emit grouped and split ownership metadata in apps/pipeline/src/orchestration/jobs/source_assets/discovery.py
- [x] T009 Wire catalog and ownership-mode resources into runtime assembly in apps/pipeline/src/orchestration/runtime.py
- [x] T010 [P] Add foundational tests for series catalog validation in apps/pipeline/tests/orchestration/test_series_catalog.py
- [x] T011 [P] Add foundational tests for ownership overlap rejection in apps/pipeline/tests/orchestration/test_series_ownership_mode.py
- [x] T012 Add foundational telemetry fields for provider_group_key and series_item_key in apps/pipeline/src/orchestration/runtime.py

**Checkpoint**: Foundational model is ready; user stories can proceed.

---

## Phase 3: User Story 1 - Ingest Multiple Series from One Source Adapter (Priority: P1) MVP

**Goal**: One adapter ingests multiple provider series in a single run while preserving per-series identity.

**Independent Test**: Configure one adapter with at least two series and verify both are ingested with distinct series identities and incremental behavior.

### Tests for User Story 1 (REQUIRED)

- [x] T013 [P] [US1] Add grouped multi-series ingest contract test in apps/pipeline/tests/orchestration/test_fred_source_workflow.py
- [x] T014 [P] [US1] Add per-series incremental checkpoint test in apps/pipeline/tests/orchestration/test_fred_source_workflow.py
- [x] T015 [P] [US1] Add partial-success mixed-series outcome test in apps/pipeline/tests/orchestration/test_fred_source_workflow.py

### Implementation for User Story 1

- [x] T016 [US1] Refactor FRED source adapter to load multiple series configurations in apps/pipeline/src/orchestration/jobs/sources/fred_fedfunds_source.py
- [x] T017 [US1] Implement per-series checkpoint reads for grouped runs in apps/pipeline/src/orchestration/jobs/sources/fred_fedfunds_source.py
- [x] T018 [US1] Implement per-series record mapping preserving canonical identities in apps/pipeline/src/orchestration/jobs/sources/fred_fedfunds_source.py
- [x] T019 [US1] Extend source ingest workflow result payload to include series-level outcome slices in apps/pipeline/src/orchestration/jobs/workflow_result.py
- [x] T020 [US1] Update run outcome aggregation to account for series-level grouped outcomes in apps/pipeline/src/orchestration/jobs/run_coordinator.py
- [x] T021 [US1] Verify US1 coverage contribution and threshold in apps/pipeline/tests/orchestration/test_fred_source_workflow.py

**Checkpoint**: US1 is independently functional and testable.

---

## Phase 4: User Story 2 - Operate Series as Separate Dagit Items (Priority: P2)

**Goal**: Operators can run and inspect each series item independently from orchestration.

**Independent Test**: Trigger one series item and verify only that series runs while related series remain idle.

### Tests for User Story 2 (REQUIRED)

- [x] T022 [P] [US2] Add series-targeted selection test for ingest job runtime in apps/pipeline/tests/orchestration/test_ingest_job_runtime.py
- [x] T023 [P] [US2] Add Dagit catalog visibility and grouped-default-cadence test for series items in apps/pipeline/tests/orchestration/test_definitions_smoke.py
- [x] T024 [P] [US2] Add run-attribution test for series-level trigger origin in apps/pipeline/tests/orchestration/test_trigger_modes.py

### Implementation for User Story 2

- [x] T025 [US2] Implement series-targeted request normalization helper in apps/pipeline/src/orchestration/jobs/source_assets/series_selection.py
- [x] T026 [US2] Wire series selection semantics into ingest job execution in apps/pipeline/src/orchestration/jobs/ingest_job.py
- [x] T027 [US2] Add series-level Dagit assets grouped by provider metadata in apps/pipeline/src/orchestration/source_asset_definitions.py
- [x] T028 [US2] Enforce grouped-series shared-cadence default policy and per-series schedule attribution tags in apps/pipeline/src/orchestration/schedules/source_asset_schedules.py
- [x] T029 [US2] Update workspace definition catalog for series-item visibility in apps/pipeline/src/orchestration/definitions.py
- [x] T030 [US2] Ensure series-level outcome records are persisted for operator views in apps/pipeline/src/orchestration/runtime.py
- [x] T031 [US2] Verify US2 coverage contribution and threshold in apps/pipeline/tests/orchestration/test_ingest_job_runtime.py

**Checkpoint**: US2 is independently functional and testable.

---

## Phase 5: User Story 3 - Choose Grouped or Split Adapter Strategy (Priority: P3)

**Goal**: Support coexistence of grouped and split ownership with safe migration and no duplicate schedule execution.

**Independent Test**: Run grouped and split ownership models together, then migrate one series ownership and verify zero duplicate scheduled runs.

### Tests for User Story 3 (REQUIRED)

- [x] T032 [P] [US3] Add grouped/split coexistence schedule test in apps/pipeline/tests/orchestration/test_trigger_modes.py
- [x] T033 [P] [US3] Add ownership transition duplicate-prevention test in apps/pipeline/tests/orchestration/test_series_ownership_transition.py
- [x] T034 [P] [US3] Add persistence traceability test across ownership transition in apps/pipeline/tests/orchestration/test_source_outcome_visibility.py
- [x] T035 [P] [US3] Add migration-model contract test for ownership effective window validation in libs/db/tests/test_ingestion_runtime_models.py

### Implementation for User Story 3

- [x] T036 [US3] Implement grouped/split schedule authority resolver in apps/pipeline/src/orchestration/jobs/source_assets/ownership_mode.py
- [x] T037 [US3] Add duplicate schedule guardrails for ownership transitions in apps/pipeline/src/orchestration/jobs/run_coordinator.py
- [x] T038 [US3] Implement ownership transition helper and validation in apps/pipeline/src/orchestration/jobs/source_assets/ownership_transition.py
- [x] T039 [US3] Extend run repository mappings for series ownership attribution in apps/pipeline/src/orchestration/resources/postgres_run_repository.py
- [x] T040 [US3] Update runtime exposure for ownership mode visibility in apps/pipeline/src/orchestration/runtime.py
- [x] T041 [US3] Define ownership transition model fields and constraints in libs/db/src/db/models/ingestion_runtime.py
- [x] T042 [US3] Add migration for ownership transition metadata persistence in libs/db/alembic/versions/0006_series_ownership_transition.py
- [x] T043 [US3] Verify US3 coverage contribution and threshold in apps/pipeline/tests/orchestration/test_series_ownership_transition.py

**Checkpoint**: US3 is independently functional and testable.

---

## Phase 6: Polish & Cross-Cutting Concerns

**Purpose**: Finalize docs, quality, and end-to-end verification across all stories.

- [x] T044 [P] Update grouped-vs-split operational runbook details in docs/runbooks/local-stack-baseline.md
- [x] T045 [P] Update onboarding guidance for multi-series adapter ownership decisions in docs/onboarding/monorepo-baseline.md
- [x] T046 [P] Update architecture constraints and naming conventions in docs/architecture/monorepo-boundaries.md
- [x] T047 [P] Update command and feature history entries in AGENTS.md
- [x] T048 Run quickstart validation command sequence, compute SC-002 and SC-003 metrics, and capture evidence in specs/012-multi-series-adapters/quickstart.md
- [x] T049 Run affected quality gates and record outcomes in specs/012-multi-series-adapters/quickstart.md

---

## Dependencies & Execution Order

### Phase Dependencies

- Phase 1 (Setup): no dependencies.
- Phase 2 (Foundational): depends on Phase 1 and blocks all user story work.
- Phase 3 (US1): depends on Phase 2.
- Phase 4 (US2): depends on Phase 2 and can proceed independently; optional integration checkpoint can follow US1 stabilization.
- Phase 5 (US3): depends on Phase 2 and should follow US1/US2 to minimize ownership model churn.
- Phase 6 (Polish): depends on completion of selected user stories.

### User Story Dependencies

- US1 (P1): can begin immediately after Foundational and is the MVP.
- US2 (P2): depends on foundational catalog/selection primitives and remains independently testable from US1.
- US3 (P3): depends on foundational ownership primitives and benefits from US1/US2 runtime contracts being stable.

### Within Each User Story

- Tests first and failing before implementation.
- Runtime/model updates before orchestration exposure wiring.
- Coverage verification after implementation is complete.

### Dependency Graph

- Phase 1 -> Phase 2 -> US1 -> US2 -> US3 -> Phase 6
- Optional parallel lane: author US3 tests in advance while US2 implementation is underway.

---

## Parallel Opportunities

- Setup: T002, T003, T004 can run in parallel after T001.
- Foundational: T007, T008, T010, T011 can run in parallel after T006 starts.
- US1: T013, T014, T015 can run in parallel.
- US2: T022, T023, T024 can run in parallel.
- US3: T032, T033, T034, T035 can run in parallel.
- Polish: T044, T045, T046, T047 can run in parallel.

---

## Parallel Example: User Story 1

```bash
Task: "Add grouped multi-series ingest contract test in apps/pipeline/tests/orchestration/test_fred_source_workflow.py"
Task: "Add per-series incremental checkpoint test in apps/pipeline/tests/orchestration/test_fred_source_workflow.py"
Task: "Add partial-success mixed-series outcome test in apps/pipeline/tests/orchestration/test_fred_source_workflow.py"
```

## Parallel Example: User Story 2

```bash
Task: "Add series-targeted selection test for ingest job runtime in apps/pipeline/tests/orchestration/test_ingest_job_runtime.py"
Task: "Add Dagit catalog visibility test for series items in apps/pipeline/tests/orchestration/test_definitions_smoke.py"
Task: "Add run-attribution test for series-level trigger origin in apps/pipeline/tests/orchestration/test_trigger_modes.py"
```

## Parallel Example: User Story 3

```bash
Task: "Add grouped/split coexistence schedule test in apps/pipeline/tests/orchestration/test_trigger_modes.py"
Task: "Add ownership transition duplicate-prevention test in apps/pipeline/tests/orchestration/test_series_ownership_transition.py"
Task: "Add persistence traceability test across ownership transition in apps/pipeline/tests/orchestration/test_source_outcome_visibility.py"
Task: "Add migration-model contract test for ownership effective window validation in libs/db/tests/test_ingestion_runtime_models.py"
```

---

## Implementation Strategy

### MVP First (User Story 1)

1. Complete Phase 1 and Phase 2.
2. Complete Phase 3 (US1).
3. Validate grouped multi-series ingestion behavior independently.
4. Demo and checkpoint before series-item operability enhancements.

### Incremental Delivery

1. Deliver US1 for grouped multi-series ingestion.
2. Deliver US2 for independent series-item operations in Dagit.
3. Deliver US3 for grouped/split coexistence and transition safety.
4. Complete Phase 6 quality/documentation verification.

### Parallel Team Strategy

1. Team completes Setup and Foundational phases together.
2. After Phase 2:
   - Engineer A: US1
   - Engineer B: US2
   - Engineer C: US3 tests and migration groundwork
3. Rejoin for Phase 6 final quality and local-stack validation.

---

## Notes

- Every task follows checklist format with task ID, optional [P], optional [USx], and exact file path.
- Tests are required by feature specification and are included for foundational and each user story.
- User stories remain independently testable increments.
- Coverage must remain >=90% in affected projects.
- Documentation updates are required in the same change as behavior updates.
