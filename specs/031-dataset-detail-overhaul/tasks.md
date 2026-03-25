# Tasks: Dataset Detail Page Overhaul

**Input**: Design documents from /specs/031-dataset-detail-overhaul/
**Prerequisites**: plan.md (required), spec.md (required for user stories), research.md, data-model.md, contracts/

**Tests**: Test tasks are REQUIRED. Every user story and foundational component MUST include automated test coverage sufficient to maintain >= 90% coverage in affected projects. Before any commit and before any AI agent stops work, the full repository suite MUST pass via pnpm exec nx run-many -t test --all. Before any commit, monorepo coverage MUST pass via pnpm exec nx run-many -t coverage --all with >= 90% thresholds in every project.

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: [ID] [P?] [Story] Description

- [P]: Can run in parallel (different files, no dependencies)
- [Story]: Which user story this task belongs to (for example, US1, US2, US3)
- Every task includes an exact file path

## Path Conventions

- Frontend code: apps/frontend/src/
- Frontend tests: apps/frontend/tests/
- Feature docs: specs/031-dataset-detail-overhaul/

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Prepare shared scaffolding and test fixtures for the detail-page overhaul.

- [X] T001 Baseline current detail-page composition checkpoints in specs/031-dataset-detail-overhaul/quickstart.md
- [X] T002 [P] Add detail-page style section scaffold in apps/frontend/src/app/globals.css
- [X] T003 [P] Create derived detail view-model utility in apps/frontend/src/components/discovery/dataset-detail-view-model.ts
- [X] T004 [P] Add reusable detail observation fixtures in apps/frontend/tests/fixtures/dataset-detail-fixtures.ts

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Build shared derived-state and composition infrastructure required by all stories.

**CRITICAL**: No user story work begins until this phase is complete.

- [X] T005 Define derived-state interfaces for insight metrics and movement states in apps/frontend/src/components/discovery/dataset-detail-view-model.ts
- [X] T006 [P] Implement date/value/change formatting helpers in apps/frontend/src/components/discovery/dataset-detail-view-model.ts
- [X] T007 [P] Add unit tests for detail view-model derivations in apps/frontend/tests/dataset-detail-view-model.test.ts
- [X] T008 Create section-slot composition shell for hero, insights, trend, and table in apps/frontend/src/app/datasets/[id]/page.tsx
- [X] T009 Preserve existing 404 and non-404 fallback semantics while refactoring composition in apps/frontend/src/app/datasets/[id]/page.tsx
- [X] T010 Synchronize foundational contract assumptions for section order and fallback behavior in specs/031-dataset-detail-overhaul/contracts/dataset-detail-page-contract.md

**Checkpoint**: Foundation complete. User stories can now be implemented and validated independently.

---

## Phase 3: User Story 1 - Understand Dataset At A Glance (Priority: P1) MVP

**Goal**: Deliver hero identity, insight summary, and interactive historical trend controls for immediate comprehension.

**Independent Test**: Open a known dataset route and verify source/title hero, latest summary metrics, and range-switching trend section all render and behave correctly without touching table archive behavior.

### Tests for User Story 1 (REQUIRED)

- [X] T011 [P] [US1] Add page-level contract assertions for hero, insight summary, and trend sections in apps/frontend/tests/detail-page.test.tsx
- [X] T012 [P] [US1] Add hero metadata and fallback rendering tests in apps/frontend/tests/DatasetDetailHeader.test.tsx
- [X] T013 [P] [US1] Add trend range-control and point-inspection tests in apps/frontend/tests/ObservationsChart.test.tsx

### Implementation for User Story 1

- [X] T014 [US1] Implement editorial hero structure and source/title hierarchy in apps/frontend/src/components/discovery/DatasetDetailHeader.tsx
- [X] T015 [US1] Create insight summary component for latest value and comparative metrics in apps/frontend/src/components/discovery/DatasetDetailInsights.tsx
- [X] T016 [US1] Wire hero plus insight summary into detail route composition in apps/frontend/src/app/datasets/[id]/page.tsx
- [X] T017 [US1] Implement time-range selection and filtered trend rendering in apps/frontend/src/components/discovery/ObservationsChart.tsx
- [X] T018 [US1] Add hero/insight/trend editorial layout and responsive styles in apps/frontend/src/app/globals.css
- [X] T019 [US1] Update overview contract language for hero and trend interactions in specs/031-dataset-detail-overhaul/contracts/dataset-detail-page-contract.md

**Checkpoint**: User Story 1 is independently functional and testable.

---

## Phase 4: User Story 2 - Inspect Recent Observation History (Priority: P2)

**Goal**: Deliver richer observed-values rows with directional change semantics and progressive archive access.

**Independent Test**: Load a dataset with sufficient observations and verify date/value/change/status rows, plus archive disclosure behavior, without depending on utility action work.

### Tests for User Story 2 (REQUIRED)

- [X] T020 [P] [US2] Add observed-values row movement-state tests in apps/frontend/tests/ObservationsTable.test.tsx
- [X] T021 [US2] Add page assertions for observed-values ordering and archive affordance in apps/frontend/tests/detail-page.test.tsx

### Implementation for User Story 2

- [X] T022 [US2] Implement row-level period-change and movement-state derivation in apps/frontend/src/components/discovery/dataset-detail-view-model.ts
- [X] T023 [US2] Implement expanded observed-values schema with status indicators in apps/frontend/src/components/discovery/ObservationsTable.tsx
- [X] T024 [US2] Implement archive or load-more disclosure behavior in apps/frontend/src/components/discovery/ObservationsTable.tsx
- [X] T025 [US2] Add observed-values table styling for movement cues and status markers in apps/frontend/src/app/globals.css
- [X] T026 [US2] Update observed-values contract details for movement and archive semantics in specs/031-dataset-detail-overhaul/contracts/dataset-detail-page-contract.md

**Checkpoint**: User Stories 1 and 2 are independently functional and testable.

---

## Phase 5: User Story 3 - Use Utility Actions Without Friction (Priority: P3)

**Goal**: Provide clear export/share utility actions in the hero while preserving responsive usability.

**Independent Test**: On desktop and mobile viewport sizes, verify utility actions are visible and usable in the hero and do not break section readability.

### Tests for User Story 3 (REQUIRED)

- [X] T027 [P] [US3] Add utility-action visibility and fallback tests in apps/frontend/tests/DatasetDetailHeader.test.tsx
- [X] T028 [US3] Add responsive layout assertions for utility controls in apps/frontend/tests/detail-page.test.tsx

### Implementation for User Story 3

- [X] T029 [US3] Implement export/share action controls in the hero action region in apps/frontend/src/components/discovery/DatasetDetailHeader.tsx
- [X] T030 [US3] Wire utility action destinations and labels from detail payload context in apps/frontend/src/app/datasets/[id]/page.tsx
- [X] T031 [US3] Add responsive action layout and interaction styling in apps/frontend/src/app/globals.css
- [X] T032 [US3] Update utility-action validation checklist steps in specs/031-dataset-detail-overhaul/quickstart.md

**Checkpoint**: All user stories are independently functional and testable.

---

## Phase 6: Polish and Cross-Cutting Concerns

**Purpose**: Final quality, documentation fidelity, and gate validation across all stories.

- [X] T033 [P] Reconcile contract/spec/quickstart wording with delivered behavior in specs/031-dataset-detail-overhaul/spec.md
- [X] T034 Run focused detail-page frontend tests and capture command evidence in specs/031-dataset-detail-overhaul/quickstart.md
- [X] T035 Run frontend static checks and capture command evidence in specs/031-dataset-detail-overhaul/quickstart.md
- [X] T036 Run manual desktop and mobile validation and record outcomes in specs/031-dataset-detail-overhaul/quickstart.md
- [X] T037 Run full monorepo test stop gate and record pass evidence in specs/031-dataset-detail-overhaul/quickstart.md
- [X] T038 Run full monorepo coverage stop gate and record pass evidence in specs/031-dataset-detail-overhaul/quickstart.md
- [X] T039 [P] Validate AGENTS update requirement and document any needed edits in AGENTS.md

---

## Dependencies and Execution Order

### Phase Dependencies

- Phase 1 (Setup): No dependencies; starts immediately.
- Phase 2 (Foundational): Depends on Phase 1 and blocks all story phases.
- Phase 3 (US1): Depends on Phase 2.
- Phase 4 (US2): Depends on Phase 2 and can run after US1 if shared files create sequencing needs.
- Phase 5 (US3): Depends on Phase 2 and can run after US1 where shared hero files overlap.
- Phase 6 (Polish): Depends on completion of all user stories.

### User Story Dependencies

- US1 (P1): Independent after foundational completion; defines MVP slice.
- US2 (P2): Independent functional slice after foundational completion; integrates with shared view-model helpers.
- US3 (P3): Independent functional slice after foundational completion; integrates with hero composition from US1.

### Within Each User Story

- Tests first and expected to fail before implementation.
- Derived model updates before component wiring.
- Component implementation before route integration and styling finalization.
- Story docs and contract updates after behavior is implemented.

## Parallel Opportunities

- Setup: T002, T003, and T004 can run in parallel.
- Foundational: T006 and T007 can run in parallel.
- US1: T011, T012, and T013 can run in parallel.
- US2: T020 can run in parallel with early implementation prep once foundational work is complete.
- US3: T027 can run in parallel with non-overlapping polish work.
- Polish: T033 and T039 can run in parallel with command-run tasks.

## Parallel Example: User Story 1

- Run in parallel:
  - T011 in apps/frontend/tests/detail-page.test.tsx
  - T012 in apps/frontend/tests/DatasetDetailHeader.test.tsx
  - T013 in apps/frontend/tests/ObservationsChart.test.tsx
- Then continue sequentially with T014 through T019.

## Parallel Example: User Story 2

- Run in parallel:
  - T020 in apps/frontend/tests/ObservationsTable.test.tsx
  - T022 in apps/frontend/src/components/discovery/dataset-detail-view-model.ts
- Then complete T021 and T023 through T026.

## Parallel Example: User Story 3

- Run in parallel:
  - T027 in apps/frontend/tests/DatasetDetailHeader.test.tsx
  - T031 in apps/frontend/src/app/globals.css (after hero action structure exists)
- Then complete T028 through T032.

## Implementation Strategy

### MVP First

1. Complete Phase 1 and Phase 2.
2. Complete Phase 3 (US1) only.
3. Validate US1 independently and demo hero plus insight plus trend behavior.

### Incremental Delivery

1. Ship US1 for core comprehension workflow.
2. Add US2 for tabular inspection and archive behavior.
3. Add US3 for utility-action polish.
4. Complete polish and mandatory stop gates.

### Team Parallel Strategy

1. One developer owns shared foundational derivation logic and route composition.
2. One developer owns trend and insight UI behavior (US1 focus).
3. One developer owns observed-values table semantics (US2 focus).
4. One developer finalizes utility actions and responsive fit-and-finish (US3 focus).

## Notes

- All tasks follow the required checklist format with sequential IDs and explicit file paths.
- Story labels appear only in user-story phases.
- Parallel markers are applied only where file-level independence exists.
- Full monorepo test and coverage stop gates are mandatory before commit and before agent handoff.
