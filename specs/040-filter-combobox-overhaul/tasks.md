# Tasks: Filter Combobox Overhaul

**Input**: Design documents from `/specs/040-filter-combobox-overhaul/`
**Prerequisites**: `plan.md` (required), `spec.md` (required for user stories), `research.md`, `data-model.md`, `contracts/`

**Tests**: Test tasks are required by this feature (`FR-014`) and coverage gates in project policy.

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Prepare verification baseline and feature scaffolding for backend/frontend filter work.

- [ ] T001 Capture current regression baseline and failing scenarios in specs/040-filter-combobox-overhaul/quickstart.md
- [ ] T002 Create feature task execution log and checkpoint plan in specs/040-filter-combobox-overhaul/plan.md
- [ ] T003 [P] Add backend test matrix placeholders for filter/sort combinations in apps/backend/tests/contract/test_filter_matrix_queries.py
- [ ] T004 [P] Add frontend interaction test placeholders for dataset filters in apps/frontend/tests/DatasetListControls.test.tsx

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Build shared filter-state invariants and contracts that all user stories rely on.

- [ ] T005 Define and enforce dataset filter-state normalization (`source`, `category`, `sort`, `page`) in apps/backend/src/query/dataset_discovery_service.py
- [ ] T006 [P] Align backend catalog query contract fields with normalized filter-state expectations in apps/backend/src/contract/query/dataset_catalog_query.py
- [ ] T007 [P] Align frontend discovery request typing for filter-state parity in apps/frontend/src/lib/api/discovery-types.ts
- [ ] T008 Add URL-to-request filter mapping guardrails in apps/frontend/src/app/datasets/page.tsx
- [ ] T009 Add cross-layer stale-results prevention assertions in apps/frontend/tests/datasets-page.test.tsx

**Checkpoint**: Foundation complete; user story slices can proceed independently.

---

## Phase 3: User Story 1 - Apply Real Dataset Filters (Priority: P1) 🎯 MVP

**Goal**: Source/category/sort controls change returned dataset scope and rendered rows with no stale results.

**Independent Test**: Select source/category/sort on the datasets page and verify URL state, API query, and visible rows all match.

### Tests for User Story 1

- [ ] T010 [P] [US1] Extend backend filter+sort contract coverage in apps/backend/tests/contract/test_dataset_catalog_query_contract.py
- [ ] T011 [P] [US1] Add filter-combination regression coverage in apps/backend/tests/contract/test_filter_matrix_queries.py
- [ ] T012 [P] [US1] Add frontend dataset-result refresh assertions for filter changes in apps/frontend/tests/datasets-page.test.tsx

### Implementation for User Story 1

- [ ] T013 [US1] Implement source/category/sort normalization and dispatch in apps/backend/src/query/dataset_catalog_query.py
- [ ] T014 [US1] Fix persisted repository filter application and ordering behavior in apps/backend/src/query/dataset_discovery_persisted_repository.py
- [ ] T015 [US1] Update backend service orchestration for aligned catalog result scope in apps/backend/src/query/dataset_discovery_service.py
- [ ] T016 [US1] Update frontend dataset fetch wiring for source/category/sort parity in apps/frontend/src/lib/api/discovery-client.ts
- [ ] T017 [US1] Reconcile datasets page URL state transitions and stale-row resets in apps/frontend/src/app/datasets/page.tsx
- [ ] T018 [US1] Ensure rendered dataset rows always reflect active filter state in apps/frontend/src/components/discovery/DatasetCatalogList.tsx

**Checkpoint**: US1 is independently testable and delivers trustworthy server-backed filtering.

---

## Phase 4: User Story 2 - Narrow Combobox Options While Typing (Priority: P2)

**Goal**: Typing inside source/category comboboxes narrows visible options, supports no-match state, and restores full options on clear.

**Independent Test**: Type partial and no-match values in each combobox and verify narrowed options, no-match messaging, clear behavior, and selection behavior.

### Tests for User Story 2

- [ ] T019 [P] [US2] Add typed-input narrowing and clear-reset tests in apps/frontend/tests/DatasetListControls.test.tsx
- [ ] T020 [P] [US2] Add no-match and selection-from-narrowed-list tests in apps/frontend/tests/datasets-page.test.tsx

### Implementation for User Story 2

- [ ] T021 [US2] Implement combobox input match-state handling for source/category controls in apps/frontend/src/components/discovery/DatasetListControls.tsx
- [ ] T022 [US2] Add explicit no-match rendering contract for narrowed option lists in apps/frontend/src/components/discovery/DatasetListControls.tsx
- [ ] T023 [US2] Ensure narrowed-selection events map to canonical filter updates in apps/frontend/src/app/datasets/page.tsx
- [ ] T024 [US2] Keep discovery client request behavior unchanged for narrowed-option selection parity in apps/frontend/src/lib/api/discovery-client.ts

**Checkpoint**: US2 is independently testable and combobox narrowing is reliable.

---

## Phase 5: User Story 3 - Read And Use Filter Controls In Dark Mode (Priority: P3)

**Goal**: Dark-mode hover text remains legible and active combobox state uses thicker border treatment.

**Independent Test**: In dark mode, hover combobox options and activate/focus controls to verify readable contrast and thicker active border without layout breakage.

### Tests for User Story 3

- [ ] T025 [P] [US3] Add dark-mode hover and active-state visual behavior assertions in apps/frontend/tests/DatasetListControls.test.tsx
- [ ] T026 [P] [US3] Add datasets-page regression checks for keyboard/pointer visual-state coherence in apps/frontend/tests/datasets-page.test.tsx

### Implementation for User Story 3

- [ ] T027 [US3] Update combobox hover and active-state styling tokens/classes in apps/frontend/src/components/discovery/DatasetListControls.tsx
- [ ] T028 [US3] Adjust shared discovery row/control styling interactions for dark-mode readability in apps/frontend/src/components/discovery/DatasetCatalogList.tsx
- [ ] T029 [US3] Verify active border-width treatment does not introduce layout shift in apps/frontend/src/app/datasets/page.tsx

**Checkpoint**: US3 is independently testable and dark-mode filter interactions are legible and consistent.

---

## Phase 6: Polish & Cross-Cutting Concerns

**Purpose**: Final hardening, docs alignment, and mandatory quality gates.

- [ ] T030 [P] Update verification notes and manual steps in specs/040-filter-combobox-overhaul/quickstart.md
- [ ] T031 [P] Document final behavior/contract refinements in specs/040-filter-combobox-overhaul/contracts/dataset-filter-overhaul-contract.md
- [ ] T032 Run full validation gate `pre-commit run --all-files` from repository root in .pre-commit-config.yaml
- [ ] T033 Run mandatory monorepo tests `pnpm exec nx run-many -t test --all` and `pnpm exec nx run-many -t coverage --all` from package.json

---

## Dependencies & Execution Order

### Phase Dependencies

- Phase 1: No dependencies; can start immediately.
- Phase 2: Depends on Phase 1; blocks all user stories.
- Phase 3 (US1): Depends on Phase 2.
- Phase 4 (US2): Depends on Phase 2 and can run in parallel with/after US1 if staffed, but should integrate against the US1 filter-state contract.
- Phase 5 (US3): Depends on Phase 2 and should be applied after US2 functional behavior is stable.
- Phase 6: Depends on all selected user stories being complete.

### User Story Dependencies

- US1 (P1): Independent after foundational tasks; MVP scope.
- US2 (P2): Independent after foundational tasks, but validated against US1 filter update flow.
- US3 (P3): Independent after foundational tasks, but validated on the final US1/US2 interactive controls.

---

## Parallel Execution Examples

### User Story 1

- Run in parallel: T010 and T011 (different backend test targets)
- Run in parallel: T012 and T010/T011 (frontend vs backend tests)

### User Story 2

- Run in parallel: T019 and T020 (different frontend test concerns)

### User Story 3

- Run in parallel: T025 and T026 (component-level vs page-level test assertions)

---

## Implementation Strategy

### MVP First (US1)

1. Complete Phases 1 and 2.
2. Deliver US1 (Phase 3) end-to-end.
3. Validate US1 independently before proceeding.

### Incremental Delivery

1. Ship US1 (server-backed filter correctness).
2. Ship US2 (combobox narrowing behavior).
3. Ship US3 (dark-mode and active-state polish).
4. Execute Phase 6 gates and documentation updates.

### Commit Strategy

1. Commit after US1 is stable and validated.
2. Commit after US2 is stable and validated.
3. Commit after US3 plus Phase 6 hardening is complete.
