# Tasks: Gap-Tolerant Cadence Inference

**Input**: Design documents from `/specs/047-handle-cadence-gaps/`
**Prerequisites**: plan.md (required), spec.md (required for user stories), research.md, data-model.md, contracts/

**Tests**: Test tasks are REQUIRED. Every user story and foundational component MUST include automated test coverage sufficient to maintain >= 90% coverage in affected projects. Before any commit and before any AI agent stops work, the full repository suite MUST pass via `pnpm exec nx run-many -t test --all`. Before any commit, monorepo coverage MUST pass via `pnpm exec nx run-many -t coverage --all`.

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Align feature artifacts and ensure baseline reference data for threshold validation.

- [X] T001 Verify feature docs are present and aligned in `/root/snap/longtail-experiment/specs/047-handle-cadence-gaps/plan.md`
- [X] T002 Record reference EIA gap-ratio baseline query and expected values in `/root/snap/longtail-experiment/specs/047-handle-cadence-gaps/quickstart.md`
- [X] T003 [P] Validate local runtime prerequisites and secrets usage guidance in `/root/snap/longtail-experiment/specs/047-handle-cadence-gaps/quickstart.md`

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Introduce shared cadence decision model and policy constants used by all stories.

**CRITICAL**: No user story implementation starts until this phase is complete.

- [X] T004 Add cadence decision dataclasses/enums and reason codes in `/root/snap/longtail-experiment/libs/trend_analysis/src/trend_analysis/models.py`
- [X] T005 Add centralized gap-tolerance policy constants (including `MAX_IRREGULAR_GAP_RATIO = 0.002`) in `/root/snap/longtail-experiment/libs/trend_analysis/src/trend_analysis/cadence.py`
- [X] T006 [P] Add model-level unit tests for cadence decision outcome typing in `/root/snap/longtail-experiment/libs/trend_analysis/tests/test_multi_lookback_classifier.py`
- [X] T007 [P] Add cadence policy contract-consistency test coverage in `/root/snap/longtail-experiment/libs/trend_analysis/tests/test_cadence_and_failures.py`

**Checkpoint**: Shared cadence policy surface is defined and testable.

---

## Phase 3: User Story 1 - Continue Processing Through Isolated Gaps (Priority: P1) 🎯 MVP

**Goal**: Allow trend processing to continue for mostly regular series that contain isolated historical gaps.

**Independent Test**: Run ingest for known affected series and verify no `trend_processing_failed` due to irregular spacing for isolated-gap cases.

### Tests for User Story 1 (REQUIRED)

- [X] T008 [P] [US1] Add cadence-library test for isolated-gap acceptance under threshold in `/root/snap/longtail-experiment/libs/trend_analysis/tests/test_cadence_and_failures.py`
- [X] T009 [P] [US1] Add cadence-library test for dominant-cadence requirement with tolerated gaps in `/root/snap/longtail-experiment/libs/trend_analysis/tests/test_cadence_and_failures.py`
- [X] T010 [P] [US1] Add runtime processor test for gap-tolerant continuation in `/root/snap/longtail-experiment/apps/pipeline/tests/orchestration/test_trend_runtime_processor.py`

### Implementation for User Story 1

- [X] T011 [US1] Implement ratio-based irregular-gap handling in `infer_cadence` in `/root/snap/longtail-experiment/libs/trend_analysis/src/trend_analysis/cadence.py`
- [X] T012 [US1] Update lookback evaluation cadence integration to use new cadence outcome shape in `/root/snap/longtail-experiment/libs/trend_analysis/src/trend_analysis/classifier.py`
- [X] T013 [US1] Update runtime processor to continue processing when cadence state is gap-tolerant in `/root/snap/longtail-experiment/apps/pipeline/src/orchestration/jobs/trend_runtime_processor.py`
- [X] T014 [US1] Ensure ingest runner propagates only true irregular cadence failures as trend-processing errors in `/root/snap/longtail-experiment/apps/pipeline/src/orchestration/jobs/source_ingest_runner.py`
- [X] T015 [US1] Validate US1 local ingest behavior with reference series steps in `/root/snap/longtail-experiment/specs/047-handle-cadence-gaps/quickstart.md`

**Checkpoint**: US1 works independently and resolves the known isolated-gap failure mode.

---

## Phase 4: User Story 2 - Preserve True Irregular Detection (Priority: P2)

**Goal**: Keep strict rejection for truly irregular mixed-spacing histories.

**Independent Test**: Execute cadence tests with persistent mixed-spacing fixtures and confirm explicit irregular rejection persists.

### Tests for User Story 2 (REQUIRED)

- [X] T016 [P] [US2] Add cadence-library test for persistent mixed-spacing rejection above threshold in `/root/snap/longtail-experiment/libs/trend_analysis/tests/test_cadence_and_failures.py`
- [X] T017 [P] [US2] Add cadence-library test preserving non-increasing-period failure in `/root/snap/longtail-experiment/libs/trend_analysis/tests/test_cadence_and_failures.py`
- [X] T018 [P] [US2] Add pipeline branch-scoped failure mapping test for true irregular rejection in `/root/snap/longtail-experiment/apps/pipeline/tests/orchestration/test_trend_asset_failure_scope.py`

### Implementation for User Story 2

- [X] T019 [US2] Enforce dominant-cadence uniqueness and threshold breach rejection in `/root/snap/longtail-experiment/libs/trend_analysis/src/trend_analysis/cadence.py`
- [X] T020 [US2] Ensure classifier raises explicit irregular rejection path for cadence-invalid series in `/root/snap/longtail-experiment/libs/trend_analysis/src/trend_analysis/classifier.py`
- [X] T021 [US2] Keep source-level failure reason mapping unchanged for true irregular cadence failures in `/root/snap/longtail-experiment/apps/pipeline/src/orchestration/jobs/parallel_source_executor.py`

**Checkpoint**: US2 independently confirms no guardrail regression.

---

## Phase 5: User Story 3 - Explain Gap-Tolerant Decisions (Priority: P3)

**Goal**: Emit deterministic cadence decision metadata that explains acceptance or rejection.

**Independent Test**: Re-run identical inputs and verify cadence decision metadata and reason codes are identical.

### Tests for User Story 3 (REQUIRED)

- [X] T022 [P] [US3] Add deterministic cadence decision metadata test in `/root/snap/longtail-experiment/libs/trend_analysis/tests/test_cadence_and_failures.py`
- [X] T023 [P] [US3] Add runtime processor test asserting cadence decision metadata on series outcomes in `/root/snap/longtail-experiment/apps/pipeline/tests/orchestration/test_trend_runtime_processor.py`
- [X] T024 [P] [US3] Add ingest runtime integration assertion for cadence decision context visibility in `/root/snap/longtail-experiment/apps/pipeline/tests/orchestration/test_ingest_job_runtime.py`

### Implementation for User Story 3

- [X] T025 [US3] Extend cadence decision payload fields and reason detail handling in `/root/snap/longtail-experiment/libs/trend_analysis/src/trend_analysis/models.py`
- [X] T026 [US3] Propagate cadence decision metadata through runtime processor outputs in `/root/snap/longtail-experiment/apps/pipeline/src/orchestration/jobs/trend_runtime_processor.py`
- [X] T027 [US3] Extend source workflow result schema for cadence decision metadata in `/root/snap/longtail-experiment/apps/pipeline/src/orchestration/jobs/workflow_result.py`
- [X] T028 [US3] Include cadence decision context in source execution summaries in `/root/snap/longtail-experiment/apps/pipeline/src/orchestration/jobs/source_ingest_runner.py`

**Checkpoint**: US3 independently provides operational explainability.

---

## Phase 6: Polish & Cross-Cutting Concerns

**Purpose**: Final hardening, documentation sync, and full-gate verification.

- [X] T029 [P] Update threshold rationale and decision notes in `/root/snap/longtail-experiment/specs/047-handle-cadence-gaps/research.md`
- [X] T030 [P] Update operational validation steps and expected outcomes in `/root/snap/longtail-experiment/specs/047-handle-cadence-gaps/quickstart.md`
- [X] T031 [P] Update pipeline/trend-analysis command references in `/root/snap/longtail-experiment/AGENTS.md`
- [X] T032 Run feature-targeted test suites in `/root/snap/longtail-experiment/libs/trend_analysis/tests/test_cadence_and_failures.py` and `/root/snap/longtail-experiment/apps/pipeline/tests/orchestration/test_trend_runtime_processor.py`
- [X] T033 Run mandatory full-suite tests with `pnpm exec nx run-many -t test --all` from `/root/snap/longtail-experiment`
- [X] T034 Run mandatory full-suite coverage with `pnpm exec nx run-many -t coverage --all` from `/root/snap/longtail-experiment`
- [X] T035 Run mandatory pre-commit gate with `pre-commit run --all-files` from `/root/snap/longtail-experiment`

---

## Dependencies & Execution Order

### Phase Dependencies

- Setup (Phase 1): no dependencies.
- Foundational (Phase 2): depends on Setup.
- User Stories (Phases 3-5): depend on Foundational completion.
- Polish (Phase 6): depends on all selected user stories being complete.

### User Story Dependencies

- **US1 (P1)**: starts after Phase 2; no dependency on US2/US3.
- **US2 (P2)**: starts after Phase 2; can run in parallel with US1 but validates guardrails.
- **US3 (P3)**: starts after Phase 2; can run after/alongside US1 once cadence decision shape is stable.

### Within Each User Story

- Write tests first and confirm they fail.
- Implement library/runtime logic.
- Re-run story-specific tests.
- Confirm independent acceptance criteria before moving on.

### Parallel Opportunities

- Phase 1 task T003 parallel with T001-T002.
- Phase 2 tasks T006-T007 parallel after T004-T005.
- US1 tests T008-T010 parallel.
- US2 tests T016-T018 parallel.
- US3 tests T022-T024 parallel.
- Polish docs tasks T029-T031 parallel.

---

## Parallel Example: User Story 1

```bash
# Launch US1 tests in parallel:
Task: "Add cadence-library test for isolated-gap acceptance under threshold in libs/trend_analysis/tests/test_cadence_and_failures.py"
Task: "Add cadence-library test for dominant-cadence requirement with tolerated gaps in libs/trend_analysis/tests/test_cadence_and_failures.py"
Task: "Add runtime processor test for gap-tolerant continuation in apps/pipeline/tests/orchestration/test_trend_runtime_processor.py"

# After tests fail, implementation tasks can proceed:
Task: "Implement ratio-based irregular-gap handling in libs/trend_analysis/src/trend_analysis/cadence.py"
Task: "Update runtime processor continuation behavior in apps/pipeline/src/orchestration/jobs/trend_runtime_processor.py"
```

---

## Parallel Example: User Story 2

```bash
# Launch US2 tests in parallel:
Task: "Add persistent mixed-spacing rejection test in libs/trend_analysis/tests/test_cadence_and_failures.py"
Task: "Add non-increasing-period failure preservation test in libs/trend_analysis/tests/test_cadence_and_failures.py"
Task: "Add branch-scoped failure mapping test in apps/pipeline/tests/orchestration/test_trend_asset_failure_scope.py"
```

---

## Parallel Example: User Story 3

```bash
# Launch US3 tests in parallel:
Task: "Add deterministic cadence decision metadata test in libs/trend_analysis/tests/test_cadence_and_failures.py"
Task: "Add runtime metadata propagation test in apps/pipeline/tests/orchestration/test_trend_runtime_processor.py"
Task: "Add ingest runtime metadata visibility test in apps/pipeline/tests/orchestration/test_ingest_job_runtime.py"
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1 and Phase 2.
2. Complete Phase 3 (US1).
3. Validate isolated-gap reference case end-to-end.
4. Stop and verify that known failures are resolved.

### Incremental Delivery

1. Deliver US1 to restore ingestion continuity for isolated-gap series.
2. Deliver US2 to confirm true-irregular guardrails are still strict.
3. Deliver US3 to provide operational decision transparency.
4. Execute Polish phase and mandatory stop-gate commands.

### Parallel Team Strategy

1. One developer handles cadence library core changes.
2. One developer handles pipeline runtime propagation and tests.
3. One developer handles documentation and quickstart verification artifacts.

---

## Notes

- All tasks use strict checklist format: checkbox, ID, optional [P], story label for story phases, and explicit file path.
- Story labels map directly to spec priorities: US1 (P1), US2 (P2), US3 (P3).
- Preserve deterministic behavior and existing hard-failure semantics where required.
- Treat the selected threshold/rules as a current-data baseline; if future datasets show meaningfully more irregular spacing, add a follow-up task batch to revise cadence-gap policy.
- Before commit/handoff, all mandatory repository gates must pass.
