# Tasks: Dataset Detail Chart Overhaul

**Input**: Design documents from `/specs/037-detail-chart-overhaul/`
**Prerequisites**: plan.md (required), spec.md (required for user stories), research.md, data-model.md, contracts/

**Tests**: Test tasks are REQUIRED. Every user story and foundational component MUST
include automated test coverage sufficient to maintain >= 90% coverage in affected
projects. Before any commit and before any AI agent stops work, the full repository
suite MUST pass via `pnpm exec nx run-many -t test --all`; targeted tests alone are
never sufficient for this stop gate. Before any commit, monorepo coverage MUST pass via
`pnpm exec nx run-many -t coverage --all` with >= 90% thresholds in every project.

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3)
- Include exact file paths in descriptions

## Path Conventions

- Frontend app: `apps/frontend/src/`, `apps/frontend/tests/`
- Feature docs: `specs/037-detail-chart-overhaul/`

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Confirm the feature documentation and test surfaces that implementation will use

- [X] T001 Review feature contracts and validation flow in `specs/037-detail-chart-overhaul/plan.md`, `specs/037-detail-chart-overhaul/contracts/dataset-detail-chart-contract.md`, and `specs/037-detail-chart-overhaul/quickstart.md`
- [X] T002 [P] Confirm existing chart/detail test fixtures support short- and long-history scenarios in `apps/frontend/tests/fixtures/dataset-detail-fixtures.ts`

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Establish the shared chart range logic and fixture coverage that all user stories depend on

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

- [X] T003 [P] Expand shared dataset detail fixtures for no-data, limited-history, and multi-year histories in `apps/frontend/tests/fixtures/dataset-detail-fixtures.ts`
- [X] T004 [P] Add foundational range-logic tests for supported windows and filtered observation subsets in `apps/frontend/tests/dataset-detail-view-model.test.ts`
- [X] T005 Add shared chart range derivation helpers for all-history default, 5Y support, longest-to-shortest ordering, and hidden unsupported ranges in `apps/frontend/src/components/discovery/dataset-detail-view-model.ts`
- [X] T006 [P] Extend chart-related types as needed for derived range metadata in `apps/frontend/src/components/discovery/dataset-detail-view-model.ts`

**Checkpoint**: Shared chart range logic and fixtures are ready for story implementation

---

## Phase 3: User Story 1 - Read The Trend More Clearly (Priority: P1) 🎯 MVP

**Goal**: Make the trend panel larger and cleaner by removing low-value chrome and improving chart readability

**Independent Test**: Open a dataset detail page with observations and verify the chart fills the available trend width, aligns visually to the bottom of the metadata column, shows a line without dots, renders without a chart border, omits the footnote, and presents more separated x-axis labels.

### Tests for User Story 1 (REQUIRED) ⚠️

> **NOTE: Write these tests FIRST, ensure they FAIL before implementation**

- [X] T007 [P] [US1] Add chart render contract tests for border removal, no footnote, line-only rendering, and axis-spacing markers in `apps/frontend/tests/ObservationsChart.test.tsx`
- [X] T008 [P] [US1] Add page-level layout assertions for the trend section and analysis-panel alignment hooks in `apps/frontend/tests/detail-page.test.tsx`

### Implementation for User Story 1

- [X] T009 [US1] Update trend panel layout to let the chart fill the available analysis-column space in `apps/frontend/src/components/discovery/DatasetDetailAnalysis.tsx`
- [X] T010 [US1] Refine chart rendering to remove border, remove footnote, hide line dots, and loosen x-axis label spacing in `apps/frontend/src/components/discovery/ObservationsChart.tsx`
- [X] T011 [US1] Verify US1 coverage contribution remains >= 90% for `apps/frontend/tests/ObservationsChart.test.tsx` and `apps/frontend/tests/detail-page.test.tsx`

**Checkpoint**: User Story 1 should now be fully functional and independently testable

---

## Phase 4: User Story 2 - Start With The Full Historical Picture (Priority: P2)

**Goal**: Default the chart to all-history and present meaningful time filters in the correct order, including the new 5Y option

**Independent Test**: Open dataset detail pages with short, medium, and long histories and verify all-history is selected by default, supported filters are ordered longest-to-shortest, 5Y appears only when meaningful, and visible filter buttons show a pointer cursor.

### Tests for User Story 2 (REQUIRED) ⚠️

- [X] T012 [P] [US2] Add view-model tests for all-history default, 5Y support, and ordered visible ranges in `apps/frontend/tests/dataset-detail-view-model.test.ts`
- [X] T013 [P] [US2] Add chart interaction tests for ordered visible controls, default selected state, and pointer-cursor affordance in `apps/frontend/tests/ObservationsChart.test.tsx`

### Implementation for User Story 2

- [X] T014 [US2] Extend range-selection helpers for 5Y, ordered visibility, and all-history default state in `apps/frontend/src/components/discovery/dataset-detail-view-model.ts`
- [X] T015 [US2] Update chart controls to render longest-to-shortest, include 5Y, default to all-history, and present pointer cursor styling in `apps/frontend/src/components/discovery/ObservationsChart.tsx`
- [X] T016 [US2] Update insight-range synchronization to use the new all-history default in `apps/frontend/src/components/discovery/DatasetDetailAnalysis.tsx`
- [X] T017 [US2] Verify US2 coverage contribution remains >= 90% for `apps/frontend/tests/dataset-detail-view-model.test.ts` and `apps/frontend/tests/ObservationsChart.test.tsx`

**Checkpoint**: User Stories 1 and 2 should now both work independently

---

## Phase 5: User Story 3 - Avoid Dead-End Or Misleading Controls (Priority: P3)

**Goal**: Ensure the chart hides unsupported controls and preserves explicit fallback behavior for no-data and limited-history datasets

**Independent Test**: Compare no-data, limited-history, and extensive-history datasets and verify unsupported ranges are omitted, the filter group hides when only all-history would remain, and the no-data chart state remains explicit.

### Tests for User Story 3 (REQUIRED) ⚠️

- [X] T018 [P] [US3] Add no-data and limited-history range-visibility tests in `apps/frontend/tests/dataset-detail-view-model.test.ts`
- [X] T019 [P] [US3] Add chart fallback tests for hidden control groups and explicit empty-state behavior in `apps/frontend/tests/ObservationsChart.test.tsx`
- [X] T020 [P] [US3] Add page-level regression coverage for limited-history and no-data trend behavior in `apps/frontend/tests/detail-page.test.tsx`

### Implementation for User Story 3

- [X] T021 [US3] Finalize supported-range filtering so unsupported windows and empty control groups are omitted in `apps/frontend/src/components/discovery/dataset-detail-view-model.ts`
- [X] T022 [US3] Update chart fallback rendering so limited-history and no-data states never show dead-end controls in `apps/frontend/src/components/discovery/ObservationsChart.tsx`
- [X] T023 [US3] Verify US3 coverage contribution remains >= 90% for `apps/frontend/tests/dataset-detail-view-model.test.ts`, `apps/frontend/tests/ObservationsChart.test.tsx`, and `apps/frontend/tests/detail-page.test.tsx`

**Checkpoint**: All user stories should now be independently functional

---

## Phase 6: Polish & Cross-Cutting Concerns

**Purpose**: Final validation, cleanup, and completion gates across all stories

- [X] T024 [P] Update implementation validation notes and completed command record in `specs/037-detail-chart-overhaul/quickstart.md`
- [X] T025 Run focused frontend verification commands from `specs/037-detail-chart-overhaul/quickstart.md` for `apps/frontend/tests/ObservationsChart.test.tsx`, `apps/frontend/tests/detail-page.test.tsx`, and `apps/frontend/tests/dataset-detail-view-model.test.ts`
- [X] T026 Run manual browser validation after `docker compose down` and `docker compose up -d`, then record the results in `specs/037-detail-chart-overhaul/quickstart.md`
- [X] T027 Run `pnpm --dir apps/frontend typecheck` and `pnpm --dir apps/frontend exec biome check .`
- [X] T028 Run `pnpm exec nx run-many -t test --all` and verify pass before commit and before agent handoff/end of work
- [X] T029 Run `pnpm exec nx run-many -t coverage --all` and verify >= 90% coverage thresholds are satisfied before commit

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies
- **Foundational (Phase 2)**: Depends on Setup completion and blocks all user stories
- **User Story 1 (Phase 3)**: Depends on Foundational completion
- **User Story 2 (Phase 4)**: Depends on Foundational completion and reuses shared range helpers from Phase 2
- **User Story 3 (Phase 5)**: Depends on Foundational completion and builds on the range-control behavior established in US2
- **Polish (Phase 6)**: Depends on completion of all desired user stories

### User Story Dependencies

- **User Story 1 (P1)**: Can start after Phase 2 and delivers the MVP chart visual cleanup
- **User Story 2 (P2)**: Can start after Phase 2, but benefits from US1 chart-render changes being in place
- **User Story 3 (P3)**: Depends on the range-availability model from US2 to finish hiding unsupported controls cleanly

### Within Each User Story

- Tests MUST be written and fail before implementation
- Shared range logic before chart control wiring
- Layout/container changes before page-level verification
- Story-specific implementation before coverage verification

### Parallel Opportunities

- `T002`, `T003`, `T004`, and `T006` can run in parallel during setup/foundational work
- `T007` and `T008` can run in parallel for US1
- `T012` and `T013` can run in parallel for US2
- `T018`, `T019`, and `T020` can run in parallel for US3
- `T024` can be prepared while implementation verification is underway

---

## Parallel Example: User Story 1

```bash
# Launch US1 tests together:
Task: "Add chart render contract tests in apps/frontend/tests/ObservationsChart.test.tsx"
Task: "Add page-level layout assertions in apps/frontend/tests/detail-page.test.tsx"
```

---

## Parallel Example: User Story 2

```bash
# Launch US2 tests together:
Task: "Add view-model tests in apps/frontend/tests/dataset-detail-view-model.test.ts"
Task: "Add chart interaction tests in apps/frontend/tests/ObservationsChart.test.tsx"
```

---

## Parallel Example: User Story 3

```bash
# Launch US3 regression tests together:
Task: "Add no-data and limited-history range-visibility tests in apps/frontend/tests/dataset-detail-view-model.test.ts"
Task: "Add chart fallback tests in apps/frontend/tests/ObservationsChart.test.tsx"
Task: "Add page-level regression coverage in apps/frontend/tests/detail-page.test.tsx"
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1: Setup
2. Complete Phase 2: Foundational
3. Complete Phase 3: User Story 1
4. **STOP and VALIDATE**: Verify the cleaned-up trend panel independently

### Incremental Delivery

1. Finish Setup + Foundational to establish shared range logic and fixtures
2. Deliver User Story 1 for chart layout and visual cleanup
3. Deliver User Story 2 for all-history default, 5Y support, ordering, and pointer cursor behavior
4. Deliver User Story 3 for hidden unsupported controls and no-data guardrails
5. Run polish, manual validation, and mandatory monorepo stop gates
