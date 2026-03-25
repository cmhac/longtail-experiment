# Tasks: Dataset List Page

**Input**: Design documents from `/Users/hackerc/Projects/longtail-experiment/specs/027-dataset-list-page/`
**Prerequisites**: plan.md (required), spec.md (required for user stories), research.md, data-model.md, contracts/, quickstart.md

**Tests**: Test tasks are REQUIRED. Every user story and foundational component MUST include automated test coverage sufficient to maintain >= 90% coverage in affected projects. Before any commit and before any AI agent stops work, the full repository suite MUST pass via `pnpm exec nx run-many -t test --all`; targeted tests alone are never sufficient for this stop gate. Before any commit, monorepo coverage MUST pass via `pnpm exec nx run-many -t coverage --all` with >= 90% thresholds in every project.

**Organization**: Tasks are grouped by user story so each story can be implemented and validated independently.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (US1, US2, US3)
- Include exact file paths in descriptions

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Prepare dataset list page scaffolding, contract references, and test entrypoints.

- [x] T001 Audit existing dataset catalog page/component flow in apps/frontend/src/app/datasets/page.tsx, apps/frontend/src/components/discovery/DatasetCatalogList.tsx, and apps/frontend/src/components/discovery/DatasetCard.tsx
- [x] T002 Create datasets page contract checkpoints in specs/027-dataset-list-page/contracts/dataset-list-page-contract.md
- [x] T003 [P] Create datasets page integration test scaffold in apps/frontend/tests/datasets-page.test.tsx
- [x] T004 [P] Create dataset card behavior test scaffold in apps/frontend/tests/DatasetCard.test.tsx
- [x] T005 [P] Add implementation checklist placeholders in specs/027-dataset-list-page/quickstart.md

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Build shared listing-state and control infrastructure required by all user stories.

**⚠️ CRITICAL**: No user story work can begin until this phase is complete.

- [x] T006 Add page-level listing state query parsing for source/category/sort controls in apps/frontend/src/app/datasets/page.tsx
- [x] T007 [P] Add reusable dataset list controls component shell in apps/frontend/src/components/discovery/DatasetListControls.tsx
- [x] T008 [P] Extend discovery list typing and, if needed, backend discovery response contracts for category/filter/sort metadata in apps/frontend/src/lib/api/discovery-types.ts and apps/backend/src/contract/query/dataset_search_query.py
- [x] T009 Add deterministic filter/sort orchestration in apps/frontend/src/components/discovery/DatasetCatalogList.tsx and backend query parsing support if required in apps/backend/src/http_api_server.py
- [x] T010 [P] Add foundational styles for list controls and section framing in apps/frontend/src/app/globals.css
- [x] T011 Add foundational rendering contract checks for datasets page regions in apps/frontend/tests/shell-structure-contract.test.tsx

**Checkpoint**: Shared control/list infrastructure is complete and stories can proceed independently.

---

## Phase 3: User Story 1 - Browse Available Datasets (Priority: P1) 🎯 MVP

**Goal**: Render a scan-friendly datasets page with heading, total-series summary, and metadata-rich dataset cards.

**Independent Test**: Load `/datasets` and verify title, total-series summary, and cards with source/title/summary/tags/last-updated metadata.

### Tests for User Story 1 (REQUIRED) ⚠️

- [x] T012 [P] [US1] Add page-level assertions for heading and catalog-total summary invariance across filter changes in apps/frontend/tests/datasets-page.test.tsx
- [x] T013 [P] [US1] Add dataset card metadata assertions for source/title/summary/tags/updated labels in apps/frontend/tests/DatasetCard.test.tsx
- [x] T014 [P] [US1] Add list rendering assertions for consistent card structure and duplicate-entry prevention in apps/frontend/tests/datasets-page.test.tsx

### Implementation for User Story 1

- [x] T015 [US1] Refactor datasets page top section to include heading and total-series summary in apps/frontend/src/app/datasets/page.tsx
- [x] T016 [US1] Implement metadata-rich card structure (source badge, summary, tags, updated context) in apps/frontend/src/components/discovery/DatasetCard.tsx
- [x] T017 [US1] Update list rendering container semantics for consistent vertical scan layout in apps/frontend/src/components/discovery/DatasetCatalogList.tsx
- [x] T018 [US1] Add card and section typography/spacing styles for scanability in apps/frontend/src/app/globals.css
- [x] T019 [US1] Verify US1 focused checks in apps/frontend/tests/datasets-page.test.tsx and apps/frontend/tests/DatasetCard.test.tsx

**Checkpoint**: User Story 1 is independently functional and shippable as MVP.

---

## Phase 4: User Story 2 - Refine and Sort Dataset Results (Priority: P2)

**Goal**: Enable source/category filtering and sort selection with deterministic visible result updates.

**Independent Test**: Change source/category/sort controls and verify result set and order update correctly, including explicit empty-results state.

### Tests for User Story 2 (REQUIRED) ⚠️

- [x] T020 [P] [US2] Add control interaction tests for source/category filter changes in apps/frontend/tests/datasets-page.test.tsx
- [x] T021 [P] [US2] Add sort behavior tests for recency-default and alternate sort mode selection in apps/frontend/tests/datasets-page.test.tsx
- [x] T022 [P] [US2] Add empty-results state assertions for no-match filter combinations in apps/frontend/tests/datasets-page.test.tsx

### Implementation for User Story 2

- [x] T023 [US2] Implement source/category/sort control UI behavior in apps/frontend/src/components/discovery/DatasetListControls.tsx
- [x] T024 [US2] Wire control state to datasets page query params and list rendering in apps/frontend/src/app/datasets/page.tsx and apps/frontend/src/lib/api/discovery-client.ts
- [x] T025 [US2] Implement deterministic filter/sort transformation pipeline in apps/frontend/src/components/discovery/DatasetCatalogList.tsx and backend query/service updates if required in apps/backend/src/query/dataset_discovery_service.py and apps/backend/src/query/dataset_discovery_persisted_repository.py
- [x] T026 [US2] Implement explicit empty-results presentation and reset guidance in apps/frontend/src/components/discovery/EmptyState.tsx
- [x] T027 [US2] Add responsive control layout styling for desktop/mobile in apps/frontend/src/app/globals.css
- [x] T028 [US2] Verify US2 focused checks in apps/frontend/tests/datasets-page.test.tsx and backend contract coverage if backend changes were introduced in apps/backend/tests/contract/test_http_runtime_persisted_discovery_endpoints.py

**Checkpoint**: User Stories 1 and 2 are independently functional.

---

## Phase 5: User Story 3 - Take Action from the Listing Page (Priority: P3)

**Goal**: Provide a clear request-new-dataset entry point and stable per-card save/share action affordances.

**Independent Test**: Activate request action and card actions without losing page state or breaking list layout.

### Tests for User Story 3 (REQUIRED) ⚠️

- [x] T029 [P] [US3] Add request-new-dataset CTA visibility and activation assertions in apps/frontend/tests/datasets-page.test.tsx
- [x] T030 [P] [US3] Add save/share affordance assertions for every rendered card in apps/frontend/tests/DatasetCard.test.tsx
- [x] T031 [P] [US3] Add state-preservation assertions confirming controls persist during card action interactions in apps/frontend/tests/datasets-page.test.tsx

### Implementation for User Story 3

- [x] T032 [US3] Add request-new-dataset header action wiring in apps/frontend/src/app/datasets/page.tsx
- [x] T033 [US3] Implement card action affordance markup for save/share interactions in apps/frontend/src/components/discovery/DatasetCard.tsx
- [x] T034 [US3] Add non-disruptive action-area layout and focus styles in apps/frontend/src/app/globals.css
- [x] T035 [US3] Verify US3 focused checks in apps/frontend/tests/datasets-page.test.tsx and apps/frontend/tests/DatasetCard.test.tsx

**Checkpoint**: All user stories are independently functional and testable.

---

## Phase 6: Polish & Cross-Cutting Concerns

**Purpose**: Finalize documentation alignment and run mandatory repository stop gates.

- [x] T036 [P] Reconcile implemented page behavior with contract notes in specs/027-dataset-list-page/contracts/dataset-list-page-contract.md
- [x] T037 [P] Update quickstart validation and observed outcomes in specs/027-dataset-list-page/quickstart.md
- [x] T038 [P] Update AGENTS.md if workflow/stack notes changed during implementation in AGENTS.md
- [x] T039 Run focused frontend validations and backend contract tests (if backend changes introduced) and record outcomes in specs/027-dataset-list-page/quickstart.md
- [x] T040 Run `pnpm exec nx run-many -t test --all` and record pass result in specs/027-dataset-list-page/quickstart.md
- [x] T041 Run `pnpm exec nx run-many -t coverage --all` and record pass result in specs/027-dataset-list-page/quickstart.md
- [x] T042 Run `pre-commit run --all-files` and record pass result in specs/027-dataset-list-page/quickstart.md
- [x] T043 Run structured usability check for SC-001 (time-to-relevant-dataset) and record results in specs/027-dataset-list-page/quickstart.md
- [x] T044 Run interaction timing check for SC-002 (filter/sort update latency) and record results in specs/027-dataset-list-page/quickstart.md
- [x] T045 Run clarity/discoverability validation for SC-004 and SC-005 and record outcomes in specs/027-dataset-list-page/quickstart.md

---

## Dependencies & Execution Order

### Phase Dependencies

- **Phase 1 (Setup)**: No dependencies.
- **Phase 2 (Foundational)**: Depends on Phase 1 and blocks all user stories.
- **Phase 3 (US1)**: Depends on Phase 2 completion.
- **Phase 4 (US2)**: Depends on Phase 2 completion and can proceed after US1 or in parallel if staffed.
- **Phase 5 (US3)**: Depends on Phase 2 completion and can proceed after US1/US2 or in parallel if staffed.
- **Phase 6 (Polish)**: Depends on completion of selected user stories.

### User Story Dependencies

- **US1 (P1)**: No dependency on other user stories; establishes MVP listing value.
- **US2 (P2)**: Depends on foundational control/list infrastructure; independent of US3.
- **US3 (P3)**: Depends on foundational page/card action scaffolding; independent of US2.

### Within Each User Story

- Write story tests first and verify failing expectations before implementation.
- Implement page/component behavior before final styling refinements.
- Validate story checkpoint before progressing.

### Dependency Graph

- Phase 1 -> Phase 2 -> {US1, US2, US3} -> Phase 6
- Recommended order: US1 (MVP) -> US2 -> US3

### Parallel Opportunities

- Setup: T003, T004, and T005 can run in parallel.
- Foundational: T007, T008, T010 can run in parallel.
- US1: T012, T013, T014 can run in parallel.
- US2: T020, T021, T022 can run in parallel.
- US3: T029, T030, T031 can run in parallel.
- Polish: T036, T037, and T038 can run in parallel.

---

## Parallel Example: User Story 1

```bash
Task: "T012 [US1] Add heading/summary assertions in apps/frontend/tests/datasets-page.test.tsx"
Task: "T013 [US1] Add dataset card metadata assertions in apps/frontend/tests/DatasetCard.test.tsx"
Task: "T014 [US1] Add list rendering consistency assertions in apps/frontend/tests/datasets-page.test.tsx"
```

## Parallel Example: User Story 2

```bash
Task: "T020 [US2] Add source/category control interaction tests in apps/frontend/tests/datasets-page.test.tsx"
Task: "T021 [US2] Add sort behavior tests in apps/frontend/tests/datasets-page.test.tsx"
Task: "T022 [US2] Add empty-results state assertions in apps/frontend/tests/datasets-page.test.tsx"
```

## Parallel Example: User Story 3

```bash
Task: "T029 [US3] Add request CTA activation assertions in apps/frontend/tests/datasets-page.test.tsx"
Task: "T030 [US3] Add save/share card action assertions in apps/frontend/tests/DatasetCard.test.tsx"
Task: "T031 [US3] Add control-state preservation assertions in apps/frontend/tests/datasets-page.test.tsx"
```

---

## Implementation Strategy

### MVP First (User Story 1 only)

1. Complete Phase 1 and Phase 2.
2. Complete Phase 3 (US1).
3. Validate US1 independently and demo dataset listing MVP.

### Incremental Delivery

1. Deliver US1 for page hierarchy and card metadata.
2. Deliver US2 for filtering/sorting and empty-results behavior.
3. Deliver US3 for request action and per-card action affordances.
4. Complete Phase 6 gates and documentation synchronization.

### Parallel Team Strategy

1. One engineer handles page orchestration updates in apps/frontend/src/app/datasets/page.tsx.
2. One engineer handles card/list components in apps/frontend/src/components/discovery/.
3. One engineer handles tests and styles in apps/frontend/tests/ and apps/frontend/src/app/globals.css.
4. Converge for stop-gate execution and docs updates.

---

## Notes

- All tasks follow required checklist format with sequential IDs and explicit file paths.
- [P] markers indicate tasks that can execute concurrently with minimal coupling.
- Keep coverage at or above 90% for all affected projects.
- Before commit and before agent handoff/end: run `pnpm exec nx run-many -t test --all`.
- Before commit: run `pnpm exec nx run-many -t coverage --all`.
- Relevant docs must be updated in the same change as behavior updates.
