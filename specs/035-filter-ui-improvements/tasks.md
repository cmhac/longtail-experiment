# Tasks: Filter UI Improvements

**Input**: Design documents from `/specs/035-filter-ui-improvements/`
**Prerequisites**: plan.md (required), spec.md (required for user stories), research.md, data-model.md, contracts/

**Tests**: Test tasks are REQUIRED. Every user story and foundational component MUST include automated test coverage sufficient to maintain >= 90% coverage in affected projects. Before any commit and before any AI agent stops work, the full repository suite MUST pass via `pnpm exec nx run-many -t test --all`; targeted tests alone are never sufficient for this stop gate. Before any commit, monorepo coverage MUST pass via `pnpm exec nx run-many -t coverage --all` with >= 90% thresholds in every project.

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3)
- Include exact file paths in descriptions

## Path Conventions

- Frontend source: `apps/frontend/src/`
- Frontend tests: `apps/frontend/tests/`
- Spec artifacts: `specs/035-filter-ui-improvements/`

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Align implementation scaffolding for filter-control visual and interaction updates.

- [X] T001 Confirm and document baseline control/test hooks in specs/035-filter-ui-improvements/quickstart.md
- [X] T002 [P] Add implementation sequencing notes for control-surface/control-type/layout rollout in specs/035-filter-ui-improvements/plan.md
- [X] T003 [P] Add story-level regression checklist comments in apps/frontend/tests/DatasetListControls.test.tsx
- [X] T004 Add story-level manual verification checklist entries in specs/035-filter-ui-improvements/contracts/dataset-list-filter-controls-ui-contract.md

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Shared control-row structure required before user-story implementation.

**⚠️ CRITICAL**: No user story work can begin until this phase is complete.

- [X] T005 Define shared filter-control group wrapper structure and stable data-testid hooks in apps/frontend/src/components/discovery/DatasetListControls.tsx
- [X] T006 [P] Define shared layout classes for left-group/right-group spacing and capped widths in apps/frontend/src/app/globals.css
- [X] T007 [P] Add foundational control-row rendering assertions for group wrappers and test IDs in apps/frontend/tests/DatasetListControls.test.tsx
- [X] T008 Add foundational datasets-page smoke assertions for control row presence in apps/frontend/tests/datasets-page.test.tsx
- [X] T009 Verify foundational coverage contribution for filter-control baseline in apps/frontend/tests/DatasetListControls.test.tsx

**Checkpoint**: Shared control-row structure and regression harness are complete.

---

## Phase 3: User Story 1 - Read Filters At A Glance (Priority: P1) 🎯 MVP

**Goal**: Unify filter-container background styling with existing shared filter/shell surface language.

**Independent Test**: Open dataset list page and verify filter-control container uses shared surface styling while existing filter behavior remains unchanged.

### Tests for User Story 1 (REQUIRED) ⚠️

- [X] T010 [P] [US1] Add control-container surface class and readability assertions in apps/frontend/tests/DatasetListControls.test.tsx
- [X] T011 [P] [US1] Add datasets-page markup assertions for unified filter-container surface styling in apps/frontend/tests/datasets-page.test.tsx

### Implementation for User Story 1

- [X] T012 [US1] Apply unified filter-container surface styling classes in apps/frontend/src/components/discovery/DatasetListControls.tsx
- [X] T013 [US1] Implement shared surface background/border token rules for filter container in apps/frontend/src/app/globals.css
- [X] T014 [US1] Preserve filter-container readability across appearance contexts in apps/frontend/src/app/globals.css
- [X] T015 [US1] Verify US1 coverage contribution remains >= 90% using apps/frontend/tests/DatasetListControls.test.tsx

**Checkpoint**: Filter controls are visually unified with shared surface styling.

---

## Phase 4: User Story 2 - Use Enhanced Filter Selection Controls (Priority: P2)

**Goal**: Replace existing dropdown controls with combo-box style controls without changing filter/sort behavior semantics.

**Independent Test**: Interact with all three selector controls and confirm combo-box interactions update URL/query behavior and dataset results equivalently to current behavior.

### Tests for User Story 2 (REQUIRED) ⚠️

- [X] T016 [P] [US2] Add combo-box interaction tests for source/category/sort selection updates in apps/frontend/tests/DatasetListControls.test.tsx
- [X] T017 [P] [US2] Add keyboard-operability tests for selector open/navigate/select paths in apps/frontend/tests/DatasetListControls.test.tsx
- [X] T018 [P] [US2] Add datasets-page behavior-regression assertions for preserved filter/sort semantics in apps/frontend/tests/datasets-page.test.tsx

### Implementation for User Story 2

- [X] T019 [US2] Replace source and category dropdown controls with combo-box style controls in apps/frontend/src/components/discovery/DatasetListControls.tsx
- [X] T020 [US2] Replace sort dropdown control with combo-box style control in apps/frontend/src/components/discovery/DatasetListControls.tsx
- [X] T021 [US2] Preserve query-param update behavior for source/category/sort and page reset after combo-box migration in apps/frontend/src/components/discovery/DatasetListControls.tsx
- [X] T022 [US2] Add combo-box-specific control styling rules for label, trigger, and option readability in apps/frontend/src/app/globals.css
- [X] T023 [US2] Verify US2 coverage contribution remains >= 90% using apps/frontend/tests/DatasetListControls.test.tsx

**Checkpoint**: Combo-box controls are active and preserve existing filter/sort behavior semantics.

---

## Phase 5: User Story 3 - Improve Filter Control Layout Balance (Priority: P3)

**Goal**: Implement left-group filters, right-group sort, visible inter-group spacing, and capped control widths with responsive usability.

**Independent Test**: Verify layout shows two filters on the left and sort on the right with a visible gap and capped widths on wider viewports, while preserving understandable reflow on narrow viewports.

### Tests for User Story 3 (REQUIRED) ⚠️

- [X] T024 [P] [US3] Add control-row layout assertions for left/right grouping and spacing classes in apps/frontend/tests/DatasetListControls.test.tsx
- [X] T025 [P] [US3] Add datasets-page markup assertions for capped-width controls and group separation in apps/frontend/tests/datasets-page.test.tsx
- [X] T026 [P] [US3] Add responsive reflow assertions for control-group readability in apps/frontend/tests/DatasetListControls.test.tsx

### Implementation for User Story 3

- [X] T027 [US3] Implement control-row group wrappers and ordering for two filters left / sort right in apps/frontend/src/components/discovery/DatasetListControls.tsx
- [X] T028 [US3] Implement inter-group spacing and capped-width rules for control row in apps/frontend/src/app/globals.css
- [X] T029 [US3] Implement responsive reflow rules preserving grouping intent on narrow widths in apps/frontend/src/app/globals.css
- [X] T030 [US3] Verify US3 coverage contribution remains >= 90% using apps/frontend/tests/datasets-page.test.tsx

**Checkpoint**: Control-row spacing, grouping, and capped-width layout behavior match the target pattern.

---

## Phase 6: Polish & Cross-Cutting Concerns

**Purpose**: Final validation, documentation synchronization, and mandatory quality gates.

- [X] T031 [P] Update implementation status and sequencing notes in specs/035-filter-ui-improvements/plan.md
- [X] T032 [P] Update story verification and runtime checks in specs/035-filter-ui-improvements/quickstart.md
- [X] T033 [P] Update UI contract notes for final control behavior in specs/035-filter-ui-improvements/contracts/dataset-list-filter-controls-ui-contract.md
- [X] T034 Run focused frontend test suite for changed discovery control behavior in apps/frontend/tests/DatasetListControls.test.tsx
- [X] T035 Run full monorepo test stop gate and capture result in specs/035-filter-ui-improvements/quickstart.md
- [X] T036 Run full monorepo coverage stop gate and capture result in specs/035-filter-ui-improvements/quickstart.md
- [X] T037 Run all-files quality gate and capture result in specs/035-filter-ui-improvements/quickstart.md

---

## Dependencies & Execution Order

### Phase Dependencies

- **Phase 1 (Setup)**: No dependencies.
- **Phase 2 (Foundational)**: Depends on Phase 1 and blocks all user stories.
- **Phase 3 (US1)**: Depends on Phase 2; provides shared visual baseline.
- **Phase 4 (US2)**: Depends on Phase 3 to avoid mixing control migration with unresolved container styling.
- **Phase 5 (US3)**: Depends on Phase 4 because final spacing/grouping targets combo-box controls.
- **Phase 6 (Polish)**: Depends on completion of selected user stories.

### User Story Dependencies

- **US1 (P1)**: Can start immediately after Foundational phase; MVP scope.
- **US2 (P2)**: Depends on US1 completion for stable visual baseline.
- **US3 (P3)**: Depends on US2 completion because layout targets modernized controls.

### Within Each User Story

- Tests MUST be written and fail first before implementation updates.
- Component structural updates before CSS alignment updates.
- Behavior-preservation checks before coverage verification.
- Story-specific verification complete before moving to next phase.

### Parallel Opportunities

- Setup tasks T002 and T003 can run in parallel.
- Foundational tasks T006 and T007 can run in parallel after T005.
- US1 tests T010 and T011 can run in parallel.
- US2 tests T016, T017, and T018 can run in parallel.
- US3 tests T024, T025, and T026 can run in parallel.
- Polish docs tasks T031, T032, and T033 can run in parallel.

---

## Parallel Example: User Story 1

```bash
Task: "Add control-container surface class assertions in apps/frontend/tests/DatasetListControls.test.tsx"
Task: "Add datasets-page surface styling markup assertions in apps/frontend/tests/datasets-page.test.tsx"
```

## Parallel Example: User Story 2

```bash
Task: "Add combo-box selection interaction tests in apps/frontend/tests/DatasetListControls.test.tsx"
Task: "Add datasets-page behavior-regression assertions in apps/frontend/tests/datasets-page.test.tsx"
```

## Parallel Example: User Story 3

```bash
Task: "Add control-row grouping/spacing assertions in apps/frontend/tests/DatasetListControls.test.tsx"
Task: "Add capped-width and layout assertions in apps/frontend/tests/datasets-page.test.tsx"
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1 and Phase 2.
2. Complete Phase 3 (US1).
3. Validate filter-container visual parity and behavior stability.
4. Demo MVP visual baseline update.

### Incremental Delivery

1. Deliver US1 shared surface alignment.
2. Deliver US2 combo-box control modernization.
3. Deliver US3 spacing/grouping/capped-width layout refinement.
4. Complete polish phase with full monorepo gates.

### Parallel Team Strategy

1. One stream focuses on component structure/behavior in apps/frontend/src/components/discovery/DatasetListControls.tsx.
2. One stream focuses on styling and responsive rules in apps/frontend/src/app/globals.css.
3. One stream focuses on regression tests in apps/frontend/tests/DatasetListControls.test.tsx and apps/frontend/tests/datasets-page.test.tsx.

---

## Notes

- [P] tasks are safe for parallel execution when dependencies are satisfied.
- [US#] labels map tasks directly to spec user stories.
- Every task includes a concrete file path and executable objective.
- Full-suite and coverage stop gates remain mandatory before commit and before agent handoff/end-of-work.
