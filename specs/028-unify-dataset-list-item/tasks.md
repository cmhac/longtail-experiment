# Tasks: Unified Dataset List Item

**Input**: Design documents from `/specs/028-unify-dataset-list-item/`
**Prerequisites**: plan.md (required), spec.md (required for user stories), research.md, data-model.md, contracts/, quickstart.md

**Tests**: Test tasks are REQUIRED. Every user story and foundational component MUST include automated test coverage sufficient to maintain >= 90% coverage in affected projects. Before any commit and before any AI agent stops work, the full repository suite MUST pass via `pnpm exec nx run-many -t test --all`; targeted tests alone are never sufficient for this stop gate. Before any commit, monorepo coverage MUST pass via `pnpm exec nx run-many -t coverage --all` with >= 90% thresholds in every project.

**Organization**: Tasks are grouped by user story so each story can be implemented and validated independently.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this belongs to (US1, US2, US3)
- Include exact file paths in descriptions

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Prepare baseline files, test anchors, and contracts for shared row unification.

- [x] T001 Audit current row renderers and host surfaces in apps/frontend/src/components/discovery/RecentUpdatesFeed.tsx, apps/frontend/src/components/discovery/DatasetCard.tsx, apps/frontend/src/components/discovery/DatasetCatalogList.tsx, and apps/frontend/src/app/datasets/page.tsx
- [x] T002 Create shared-row feature checklist notes in specs/028-unify-dataset-list-item/quickstart.md
- [x] T003 [P] Create shared row component test scaffold in apps/frontend/tests/UnifiedDatasetRow.test.tsx
- [x] T004 [P] Create datasets-page row parity test scaffold in apps/frontend/tests/datasets-page.test.tsx
- [x] T005 [P] Create homepage row parity test scaffold in apps/frontend/tests/RecentUpdatesFeed.test.tsx

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Define and wire shared row infrastructure required by all stories.

**⚠️ CRITICAL**: No user story work can begin until this phase is complete.

- [x] T006 Add reusable shared row component file in apps/frontend/src/components/discovery/UnifiedDatasetRow.tsx
- [x] T007 [P] Add shared row prop mapping helpers for home and datasets contexts in apps/frontend/src/components/discovery/unified-dataset-row-mappers.ts
- [x] T008 [P] Add shared row style tokens/classes in apps/frontend/src/app/globals.css
- [x] T009 Update row presentation contract checkpoints in specs/028-unify-dataset-list-item/contracts/unified-dataset-row-contract.md
- [x] T010 Add foundational integration assertions for shared row presence across both pages in apps/frontend/tests/shell-structure-contract.test.tsx
- [x] T011 Verify foundational checks pass for shared row scaffolding in apps/frontend/tests/UnifiedDatasetRow.test.tsx and apps/frontend/tests/shell-structure-contract.test.tsx

**Checkpoint**: Shared row foundation is complete and user stories can proceed independently.

---

## Phase 3: User Story 1 - Read Consistent Dataset Entries (Priority: P1) 🎯 MVP

**Goal**: Use one reusable row presentation pattern across homepage recent updates and datasets listing.

**Independent Test**: Open `/` and `/datasets` and verify dataset rows share the same source/date/title/summary/tag hierarchy.

### Tests for User Story 1 (REQUIRED) ⚠️

- [x] T012 [P] [US1] Add shared row visual hierarchy assertions in apps/frontend/tests/UnifiedDatasetRow.test.tsx
- [x] T013 [P] [US1] Add homepage recent-updates assertions for shared row rendering in apps/frontend/tests/RecentUpdatesFeed.test.tsx
- [x] T014 [P] [US1] Add datasets-list assertions for shared row rendering in apps/frontend/tests/datasets-page.test.tsx
- [x] T015 [P] [US1] Add parity assertions confirming equivalent row hierarchy across pages in apps/frontend/tests/catalog-page.test.tsx

### Implementation for User Story 1

- [x] T016 [US1] Implement shared row markup and metadata hierarchy in apps/frontend/src/components/discovery/UnifiedDatasetRow.tsx
- [x] T017 [US1] Refactor homepage row rendering to consume shared component in apps/frontend/src/components/discovery/RecentUpdatesFeed.tsx
- [x] T018 [US1] Refactor datasets listing row rendering to consume shared component in apps/frontend/src/components/discovery/DatasetCatalogList.tsx
- [x] T019 [US1] Remove obsolete duplicated card-row structure from apps/frontend/src/components/discovery/DatasetCard.tsx and update references in apps/frontend/src/components/discovery/DatasetSearchResults.tsx if required
- [x] T020 [US1] Align list container composition for unified row output in apps/frontend/src/app/datasets/page.tsx
- [x] T021 [US1] Align shared row CSS to homepage editorial baseline in apps/frontend/src/app/globals.css
- [x] T022 [US1] Verify US1 focused checks in apps/frontend/tests/UnifiedDatasetRow.test.tsx, apps/frontend/tests/RecentUpdatesFeed.test.tsx, apps/frontend/tests/datasets-page.test.tsx, and apps/frontend/tests/catalog-page.test.tsx

**Checkpoint**: User Story 1 is independently functional and shippable as MVP.

---

## Phase 4: User Story 2 - Preserve Existing Page Workflows (Priority: P2)

**Goal**: Keep existing home feed and datasets filtering/sorting workflows while reusing shared rows.

**Independent Test**: Change datasets page filters/sort and confirm updates still work; confirm home feed populated/empty/unavailable behavior remains intact.

### Tests for User Story 2 (REQUIRED) ⚠️

- [x] T023 [P] [US2] Add datasets filter/sort regression assertions with shared rows in apps/frontend/tests/datasets-page.test.tsx
- [x] T024 [P] [US2] Add home feed fallback and ordering regressions with shared rows in apps/frontend/tests/RecentUpdatesFeed.test.tsx
- [x] T025 [P] [US2] Add discovery client interaction guard tests for unchanged datasets fetch behavior in apps/frontend/tests/discovery-client.test.ts

### Implementation for User Story 2

- [x] T026 [US2] Preserve home feed ordering/limit/fallback behavior while mapping to shared rows in apps/frontend/src/components/discovery/RecentUpdatesFeed.tsx
- [x] T027 [US2] Preserve datasets list dedupe/filter/sort behavior while mapping to shared rows in apps/frontend/src/app/datasets/page.tsx and apps/frontend/src/components/discovery/DatasetCatalogList.tsx
- [x] T028 [US2] Preserve datasets page control-strip behavior and URL state handling in apps/frontend/src/components/discovery/DatasetListControls.tsx
- [x] T029 [US2] Preserve empty-results state messaging for no-match filters in apps/frontend/src/components/discovery/EmptyState.tsx and apps/frontend/src/components/discovery/DatasetCatalogList.tsx
- [x] T030 [US2] Verify US2 focused checks in apps/frontend/tests/datasets-page.test.tsx, apps/frontend/tests/RecentUpdatesFeed.test.tsx, and apps/frontend/tests/discovery-client.test.ts

**Checkpoint**: User Stories 1 and 2 are independently functional.

---

## Phase 5: User Story 3 - Keep Presentation Readable and Stable (Priority: P3)

**Goal**: Maintain readability and stable layout for unified rows across desktop/mobile and long-content scenarios.

**Independent Test**: Validate both pages at desktop/mobile widths and with long metadata values to confirm no overlap, clipping, or hierarchy loss.

### Tests for User Story 3 (REQUIRED) ⚠️

- [x] T031 [P] [US3] Add responsive row readability assertions for home feed in apps/frontend/tests/RecentUpdatesFeed.test.tsx
- [x] T032 [P] [US3] Add responsive row readability assertions for datasets page in apps/frontend/tests/datasets-page.test.tsx
- [x] T033 [P] [US3] Add long-title/summary/tag layout stability assertions in apps/frontend/tests/UnifiedDatasetRow.test.tsx

### Implementation for User Story 3

- [x] T034 [US3] Add responsive row layout refinements in apps/frontend/src/app/globals.css
- [x] T035 [US3] Ensure optional metadata omission does not collapse row spacing in apps/frontend/src/components/discovery/UnifiedDatasetRow.tsx
- [x] T036 [US3] Ensure malformed date fallback labels remain readable in apps/frontend/src/components/discovery/UnifiedDatasetRow.tsx
- [x] T037 [US3] Verify US3 focused checks in apps/frontend/tests/UnifiedDatasetRow.test.tsx, apps/frontend/tests/RecentUpdatesFeed.test.tsx, and apps/frontend/tests/datasets-page.test.tsx

**Checkpoint**: All user stories are independently functional and testable.

---

## Phase 6: Polish & Cross-Cutting Concerns

**Purpose**: Finalize docs alignment and execute mandatory repository gates.

- [x] T038 [P] Reconcile final behavior against row contract notes in specs/028-unify-dataset-list-item/contracts/unified-dataset-row-contract.md
- [x] T039 [P] Update quickstart validation notes and outcomes in specs/028-unify-dataset-list-item/quickstart.md
- [x] T040 [P] Update AGENTS.md only if workflow/tooling/stack notes changed during implementation in AGENTS.md
- [x] T041 Run focused frontend verification commands and record results in specs/028-unify-dataset-list-item/quickstart.md
- [x] T042 Run `pnpm exec nx run-many -t test --all` and record pass result in specs/028-unify-dataset-list-item/quickstart.md
- [x] T043 Run `pnpm exec nx run-many -t coverage --all` and record pass result in specs/028-unify-dataset-list-item/quickstart.md
- [x] T044 Run `pre-commit run --all-files` and record pass result in specs/028-unify-dataset-list-item/quickstart.md
- [x] T045 Run manual visual validation on `/` and `/datasets` with screenshots and record observations in specs/028-unify-dataset-list-item/quickstart.md

---

## Dependencies & Execution Order

### Phase Dependencies

- **Phase 1 (Setup)**: No dependencies.
- **Phase 2 (Foundational)**: Depends on Phase 1 and blocks all user stories.
- **Phase 3 (US1)**: Depends on Phase 2 completion.
- **Phase 4 (US2)**: Depends on Phase 2 completion and can proceed after US1.
- **Phase 5 (US3)**: Depends on Phase 2 completion and can proceed after US1/US2.
- **Phase 6 (Polish)**: Depends on selected user stories being complete.

### User Story Dependencies

- **US1 (P1)**: No dependency on other user stories; establishes MVP unification value.
- **US2 (P2)**: Depends on shared-row foundation and US1 adoption in host pages.
- **US3 (P3)**: Depends on shared-row adoption and workflow-preservation work from US1/US2.

### Within Each User Story

- Write story tests first and verify failing expectations before implementation.
- Implement component and host-page integrations before styling refinements.
- Validate story checkpoint before progressing.

### Dependency Graph

- Phase 1 -> Phase 2 -> US1 -> US2 -> US3 -> Phase 6

### Parallel Opportunities

- Setup: T003, T004, and T005 can run in parallel.
- Foundational: T007, T008, and T009 can run in parallel.
- US1: T012, T013, T014, and T015 can run in parallel.
- US2: T023, T024, and T025 can run in parallel.
- US3: T031, T032, and T033 can run in parallel.
- Polish: T038, T039, and T040 can run in parallel.

---

## Parallel Example: User Story 1

```bash
Task: "T012 [US1] Add shared row hierarchy assertions in apps/frontend/tests/UnifiedDatasetRow.test.tsx"
Task: "T013 [US1] Add home shared-row assertions in apps/frontend/tests/RecentUpdatesFeed.test.tsx"
Task: "T014 [US1] Add datasets shared-row assertions in apps/frontend/tests/datasets-page.test.tsx"
```

## Parallel Example: User Story 2

```bash
Task: "T023 [US2] Add datasets filter/sort regressions in apps/frontend/tests/datasets-page.test.tsx"
Task: "T024 [US2] Add home fallback/ordering regressions in apps/frontend/tests/RecentUpdatesFeed.test.tsx"
Task: "T025 [US2] Add client interaction guard tests in apps/frontend/tests/discovery-client.test.ts"
```

## Parallel Example: User Story 3

```bash
Task: "T031 [US3] Add home responsive readability assertions in apps/frontend/tests/RecentUpdatesFeed.test.tsx"
Task: "T032 [US3] Add datasets responsive readability assertions in apps/frontend/tests/datasets-page.test.tsx"
Task: "T033 [US3] Add long-content stability assertions in apps/frontend/tests/UnifiedDatasetRow.test.tsx"
```

---

## Implementation Strategy

### MVP First (User Story 1 only)

1. Complete Phase 1 and Phase 2.
2. Complete Phase 3 (US1).
3. Validate US1 independently and demo unified row baseline on both pages.

### Incremental Delivery

1. Deliver US1 for visual and structural row unification.
2. Deliver US2 for workflow-preservation regressions and behavior parity.
3. Deliver US3 for responsive and readability hardening.
4. Complete Phase 6 with stop-gate validation and docs synchronization.

### Parallel Team Strategy

1. One engineer focuses on shared component and row mappers.
2. One engineer focuses on host-page integrations (home + datasets).
3. One engineer focuses on tests and CSS responsiveness.
4. Converge for stop-gate execution and documentation updates.

---

## Notes

- All tasks use required checklist format with sequential IDs and explicit file paths.
- [P] markers indicate tasks that can run concurrently with minimal coupling.
- Coverage must remain >= 90% in all affected projects.
- Before commit and before agent handoff/end: run `pnpm exec nx run-many -t test --all`.
- Before commit: run `pnpm exec nx run-many -t coverage --all`.
- Relevant docs must be updated in the same change as behavior updates.
