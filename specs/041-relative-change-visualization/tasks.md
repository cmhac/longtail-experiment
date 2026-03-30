# Tasks: Relative Change Visualizations

**Input**: Design documents from /specs/041-relative-change-visualization/
**Prerequisites**: plan.md (required), spec.md (required for user stories), research.md, data-model.md, contracts/

**Tests**: Test tasks are REQUIRED. Every user story and foundational component MUST include automated test coverage sufficient to maintain >= 90% coverage in affected projects. Before any commit and before any AI agent stops work, the full repository suite MUST pass via pnpm exec nx run-many -t test --all; targeted tests alone are never sufficient for this stop gate. Before any commit, monorepo coverage MUST pass via pnpm exec nx run-many -t coverage --all with >= 90% thresholds in every project.

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: [ID] [P?] [Story] Description

- [P]: Can run in parallel (different files, no dependencies)
- [Story]: Which user story this task belongs to (for example US1, US2, US3)
- Include exact file paths in descriptions

## Path Conventions

- Frontend app: apps/frontend/src/, apps/frontend/tests/
- Backend app: apps/backend/src/, apps/backend/tests/
- Feature docs: specs/041-relative-change-visualization/

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Prepare implementation scaffolding and verification surfaces.

- [X] T001 Confirm feature artifacts are present in specs/041-relative-change-visualization/plan.md, specs/041-relative-change-visualization/spec.md, and specs/041-relative-change-visualization/contracts/relative-change-visualization-contract.md
- [X] T002 [P] Add relative-change test fixture scenarios to apps/frontend/tests/fixtures/dataset-detail-fixtures.ts
- [X] T003 [P] Add task-level verification checklist section to specs/041-relative-change-visualization/quickstart.md for slice-by-slice red/green TDD and manual browser checks
- [X] T004 [P] Create placeholder test blocks for new relative-change suites in apps/frontend/tests/ObservationsChart.test.tsx and apps/frontend/tests/dataset-detail-view-model.test.ts

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core transformed-series primitives required before story-specific behavior.

**CRITICAL**: No user story work can begin until this phase is complete.

- [X] T005 Extend relative-change domain types in apps/frontend/src/lib/api/discovery-types.ts
- [X] T006 Implement baseline and computability enums/helpers in apps/frontend/src/components/discovery/dataset-detail-view-model.ts
- [X] T007 [P] Add formula utility for signed baseline-relative change in apps/frontend/src/components/discovery/dataset-detail-view-model.ts
- [X] T008 [P] Add chronology and non-computable gap projection helpers in apps/frontend/src/components/discovery/dataset-detail-view-model.ts
- [X] T009 Add foundational unit tests for formula, chronology, and gap semantics in apps/frontend/tests/dataset-detail-view-model.test.ts
- [X] T010 Verify backend dataset detail contract assumptions remain valid in apps/backend/tests/contract/test_dataset_detail_query_contract.py and apps/backend/tests/contract/test_dataset_detail_observation_order.py

**Checkpoint**: Foundation ready - user story implementation can now begin.

---

## Phase 3: User Story 1 - Switch To Relative Change View (Priority: P1) 🎯 MVP

**Goal**: Enable mode switching between observed values and relative-change chart rendering with signed percentage semantics.

**Independent Test**: Open a dataset detail page and verify mode switch changes chart output/formatting between raw values and signed percentage values while preserving existing page behavior.

### Tests for User Story 1 (REQUIRED)

- [X] T011 [P] [US1] Add chart mode-switch rendering tests in apps/frontend/tests/ObservationsChart.test.tsx
- [X] T012 [P] [US1] Add value-formatting and sign-display tests in apps/frontend/tests/dataset-detail-view-model.test.ts
- [X] T013 [US1] Add dataset detail page integration assertions for mode toggle presence in apps/frontend/tests/detail-page.test.tsx

### Implementation for User Story 1

- [X] T014 [US1] Add chart mode state and controls in apps/frontend/src/components/discovery/DatasetDetailAnalysis.tsx
- [X] T015 [US1] Implement relative-change projection wiring in apps/frontend/src/components/discovery/ObservationsChart.tsx
- [X] T016 [US1] Implement percentage axis/tooltip formatting paths in apps/frontend/src/components/discovery/ObservationsChart.tsx
- [X] T017 [US1] Update insights-mode compatibility with selected chart mode in apps/frontend/src/components/discovery/DatasetDetailInsights.tsx
- [X] T018 [US1] Run targeted frontend tests for US1 in apps/frontend/tests/ObservationsChart.test.tsx, apps/frontend/tests/dataset-detail-view-model.test.ts, and apps/frontend/tests/detail-page.test.tsx
- [X] T019 [US1] Manually verify mode switching and signed percentage display using browser tools following specs/041-relative-change-visualization/quickstart.md
- [ ] T020 [US1] Run full gates before US1 commit: pre-commit run --all-files, pnpm exec nx run-many -t test --all, pnpm exec nx run-many -t coverage --all
- [ ] T021 [US1] Commit stable US1 slice with touched files in apps/frontend/src/components/discovery/ and apps/frontend/tests/

**Checkpoint**: User Story 1 is independently functional and testable (MVP).

---

## Phase 4: User Story 2 - Rolling Baseline Relative Change (Priority: P2)

**Goal**: Support rolling offset baselines (1, 2, 3, n) and render non-computable points as timeline gaps.

**Independent Test**: In relative-change mode, changing rolling offsets updates computed values; insufficient-history points remain timeline gaps with unavailable behavior.

### Tests for User Story 2 (REQUIRED)

- [X] T022 [P] [US2] Add rolling-offset computation tests (1, 2, 3, n) in apps/frontend/tests/dataset-detail-view-model.test.ts
- [X] T023 [P] [US2] Add non-computable gap rendering tests in apps/frontend/tests/ObservationsChart.test.tsx
- [X] T024 [US2] Add interaction tests for rolling offset controls in apps/frontend/tests/ObservationsChart.test.tsx

### Implementation for User Story 2

- [X] T025 [US2] Implement rolling offset selector logic in apps/frontend/src/components/discovery/ObservationsChart.tsx
- [X] T026 [US2] Implement rolling baseline computation path in apps/frontend/src/components/discovery/dataset-detail-view-model.ts
- [X] T027 [US2] Implement unavailable/gap state rendering for rolling mode in apps/frontend/src/components/discovery/ObservationsChart.tsx
- [X] T028 [US2] Ensure insights and chart controls stay synchronized for rolling mode in apps/frontend/src/components/discovery/DatasetDetailAnalysis.tsx and apps/frontend/src/components/discovery/DatasetDetailInsights.tsx
- [X] T029 [US2] Run targeted frontend tests for US2 in apps/frontend/tests/ObservationsChart.test.tsx and apps/frontend/tests/dataset-detail-view-model.test.ts
- [X] T030 [US2] Manually verify rolling offsets and gap behavior using browser tools per specs/041-relative-change-visualization/quickstart.md
- [ ] T031 [US2] Run full gates before US2 commit: pre-commit run --all-files, pnpm exec nx run-many -t test --all, pnpm exec nx run-many -t coverage --all
- [ ] T032 [US2] Commit stable US2 slice with touched files in apps/frontend/src/components/discovery/ and apps/frontend/tests/

**Checkpoint**: User Stories 1 and 2 both work independently.

---

## Phase 5: User Story 3 - Fixed Baseline Selection and Persistence (Priority: P3)

**Goal**: Support fixed baseline by exact available date and index/offset, and preserve settings across scope changes with explicit unavailable fallback behavior.

**Independent Test**: In fixed mode, user can choose baseline by date/index; date selector offers only available dates; scope changes preserve valid settings and show explicit unavailable state for invalid preserved settings.

### Tests for User Story 3 (REQUIRED)

- [X] T033 [P] [US3] Add fixed-baseline-by-date and fixed-baseline-by-index tests in apps/frontend/tests/dataset-detail-view-model.test.ts
- [X] T034 [P] [US3] Add exact-available-date selector tests in apps/frontend/tests/ObservationsChart.test.tsx
- [X] T035 [P] [US3] Add persistence/invalid-preserved-setting tests across range changes in apps/frontend/tests/ObservationsChart.test.tsx
- [ ] T036 [US3] Add page-level regression checks for preserved settings visibility in apps/frontend/tests/detail-page.test.tsx

### Implementation for User Story 3

- [X] T037 [US3] Implement fixed baseline date selector populated from available observation dates in apps/frontend/src/components/discovery/ObservationsChart.tsx
- [X] T038 [US3] Implement fixed baseline index/offset selector and wiring in apps/frontend/src/components/discovery/ObservationsChart.tsx
- [X] T039 [US3] Implement exact-match-only date baseline resolution in apps/frontend/src/components/discovery/dataset-detail-view-model.ts
- [X] T040 [US3] Implement baseline setting persistence and invalid-preserved unavailable behavior in apps/frontend/src/components/discovery/ObservationsChart.tsx and apps/frontend/src/components/discovery/dataset-detail-view-model.ts
- [ ] T041 [US3] Validate contract alignment and update notes if needed in specs/041-relative-change-visualization/contracts/relative-change-visualization-contract.md
- [X] T042 [US3] Run targeted frontend tests for US3 in apps/frontend/tests/ObservationsChart.test.tsx, apps/frontend/tests/dataset-detail-view-model.test.ts, and apps/frontend/tests/detail-page.test.tsx
- [X] T043 [US3] Manually verify fixed baseline date/index flows and persistence using browser tools per specs/041-relative-change-visualization/quickstart.md
- [ ] T044 [US3] Run full gates before US3 commit: pre-commit run --all-files, pnpm exec nx run-many -t test --all, pnpm exec nx run-many -t coverage --all
- [ ] T045 [US3] Commit stable US3 slice with touched files in apps/frontend/src/components/discovery/, apps/frontend/tests/, and specs/041-relative-change-visualization/contracts/

**Checkpoint**: All user stories are independently functional.

---

## Phase 6: Polish & Cross-Cutting Concerns

**Purpose**: Final hardening, docs parity, and end-to-end validation.

- [ ] T046 [P] Update implementation notes and verification outcomes in specs/041-relative-change-visualization/quickstart.md and specs/041-relative-change-visualization/research.md
- [ ] T047 [P] Add/adjust backend runtime regression coverage if frontend behavior requires contract guarantees in apps/backend/tests/contract/test_http_runtime_persisted_discovery_endpoints.py
- [ ] T048 Run full local stack verification (docker compose down && docker compose up -d) and manual dataset-detail walkthrough per specs/041-relative-change-visualization/quickstart.md
- [ ] T049 Run final mandatory gates: pre-commit run --all-files, pnpm exec nx run-many -t test --all, pnpm exec nx run-many -t coverage --all
- [ ] T050 Final documentation sync for feature behavior in specs/041-relative-change-visualization/spec.md, specs/041-relative-change-visualization/plan.md, and AGENTS.md if commands/workflow references changed
- [ ] T051 Create final feature integration commit covering polish, docs, and any remaining test adjustments

---

## Dependencies & Execution Order

### Phase Dependencies

- Setup (Phase 1): No dependencies.
- Foundational (Phase 2): Depends on Setup completion and blocks all user stories.
- User Story phases (Phases 3-5): Depend on Foundational completion.
- Polish (Phase 6): Depends on completion of all desired user story phases.

### User Story Dependencies

- US1 (P1): Starts after Foundational; independent MVP.
- US2 (P2): Starts after Foundational; depends on US1 mode infrastructure for UI surface but remains independently testable once integrated.
- US3 (P3): Starts after Foundational; depends on relative-change infrastructure from US1 and transformed-series behavior from US2.

### Within Each User Story

- Tests first and failing (red) before implementation.
- Computation helpers before chart wiring.
- UI controls before persistence/polish behaviors.
- Targeted tests and manual browser verification before running full gates and committing.

### Commit Strategy Dependencies

- Commit after each stable story slice (US1, US2, US3) and after final polish.
- No large single-commit implementation allowed.

---

## Parallel Opportunities

- Setup phase: T002, T003, T004 can run in parallel.
- Foundational phase: T007 and T008 can run in parallel after T005/T006.
- US1: T011 and T012 parallel test creation; T018 manual and gate tasks remain sequential.
- US2: T022 and T023 can run in parallel; T025 and T026 can be split across contributors.
- US3: T033, T034, and T035 can run in parallel; T037 and T038 can be split by selector mode.
- Polish: T046 and T047 can run in parallel before final verification.

### Parallel Example: User Story 1

- [X] T011 [P] [US1] Add chart mode-switch rendering tests in apps/frontend/tests/ObservationsChart.test.tsx
- [X] T012 [P] [US1] Add value-formatting and sign-display tests in apps/frontend/tests/dataset-detail-view-model.test.ts

### Parallel Example: User Story 2

- [X] T022 [P] [US2] Add rolling-offset computation tests (1, 2, 3, n) in apps/frontend/tests/dataset-detail-view-model.test.ts
- [X] T023 [P] [US2] Add non-computable gap rendering tests in apps/frontend/tests/ObservationsChart.test.tsx

### Parallel Example: User Story 3

- [X] T033 [P] [US3] Add fixed-baseline-by-date and fixed-baseline-by-index tests in apps/frontend/tests/dataset-detail-view-model.test.ts
- [X] T034 [P] [US3] Add exact-available-date selector tests in apps/frontend/tests/ObservationsChart.test.tsx

---

## Implementation Strategy

### MVP First (US1)

1. Complete Phase 1 and Phase 2.
2. Deliver US1 mode switching and signed percentage rendering.
3. Validate independently with tests and manual browser checks.
4. Run full gates and commit US1 slice.

### Incremental Delivery

1. US1 establishes mode and formula baseline.
2. US2 adds rolling offsets and gap semantics.
3. US3 adds fixed baseline selectors and persistence behavior.
4. Phase 6 hardens regressions and documentation.

### Red/Green TDD and Verification Enforcement

1. For every slice: write failing tests first, implement minimal fix, refactor safely.
2. Manually verify each slice in local environment.
3. For frontend slices: use browser tools to confirm interactive behavior and visual states.
4. Before each commit and before agent stop: run pre-commit run --all-files, pnpm exec nx run-many -t test --all, pnpm exec nx run-many -t coverage --all.

---

## Notes

- All tasks follow the required checklist format with IDs and file paths.
- Story labels are included only for user-story phases.
- Tasks marked [P] are parallelizable and avoid same-file dependency conflicts.
- Coverage and full-suite stop rules are mandatory at every commit boundary.
