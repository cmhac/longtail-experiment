# Tasks: Global Page Content Width

**Input**: Design documents from `/specs/029-global-content-width/`
**Prerequisites**: plan.md (required), spec.md (required for user stories), research.md, data-model.md, contracts/, quickstart.md

**Tests**: Test tasks are REQUIRED. Every user story and foundational component MUST include automated test coverage sufficient to maintain >= 90% coverage in affected projects. Before any commit and before any AI agent stops work, the full repository suite MUST pass via `pnpm exec nx run-many -t test --all`; targeted tests alone are never sufficient for this stop gate. Before any commit, monorepo coverage MUST pass via `pnpm exec nx run-many -t coverage --all` with >= 90% thresholds in every project.

**Organization**: Tasks are grouped by user story so each story can be implemented and validated independently.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this belongs to (US1, US2, US3)
- Include exact file paths in descriptions

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Prepare baseline task scaffolding for global width policy rollout.

- [x] T001 Audit current shell width behavior in apps/frontend/src/app/globals.css, apps/frontend/src/app/page.tsx, apps/frontend/src/app/datasets/page.tsx, apps/frontend/src/shell/site-header.tsx, and apps/frontend/src/shell/site-footer.tsx
- [x] T002 Create feature validation notes scaffold in specs/029-global-content-width/quickstart.md
- [x] T003 [P] Add layout width contract test scaffold in apps/frontend/tests/shell-structure-contract.test.tsx
- [x] T004 [P] Add home route width behavior test scaffold in apps/frontend/tests/home-page.test.tsx
- [x] T005 [P] Add datasets route width behavior test scaffold in apps/frontend/tests/catalog-page.test.tsx

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Define global width primitives and shared region modes before story delivery.

**⚠️ CRITICAL**: No user story work can begin until this phase is complete.

- [x] T006 Define global content-width tokens and utility classes in apps/frontend/src/app/globals.css
- [x] T007 [P] Define explicit width-mode class naming constants in apps/frontend/src/theme/monochrome-theme.ts
- [x] T008 [P] Apply shared shell-region width-mode classes for header/footer in apps/frontend/src/shell/site-header.tsx and apps/frontend/src/shell/site-footer.tsx
- [x] T009 Reconcile width-mode contract details in specs/029-global-content-width/contracts/global-content-width-contract.md
- [x] T010 Add foundational assertions for constrained_default and explicit_full_width markers in apps/frontend/tests/shell-structure-contract.test.tsx
- [x] T011 Verify foundational checks pass for shared width primitives in apps/frontend/tests/shell-structure-contract.test.tsx

**Checkpoint**: Shared width foundation is complete and user stories can proceed independently.

---

## Phase 3: User Story 1 - Read Comfortable Layouts on Large Screens (Priority: P1) 🎯 MVP

**Goal**: Constrain home and datasets main content to a centered readable max width on large desktop screens.

**Independent Test**: Open `/` and `/datasets` on a wide viewport and verify primary content is constrained and centered instead of spanning edge-to-edge.

### Tests for User Story 1 (REQUIRED) ⚠️

- [x] T012 [P] [US1] Add constrained_default class and structure assertions for home route in apps/frontend/tests/home-page.test.tsx
- [x] T013 [P] [US1] Add constrained_default class and structure assertions for datasets route in apps/frontend/tests/catalog-page.test.tsx
- [x] T014 [P] [US1] Add shell-level constrained content assertions in apps/frontend/tests/shell-structure-contract.test.tsx
- [x] T015 [P] [US1] Add wide-viewport layout expectation notes in specs/029-global-content-width/quickstart.md

### Implementation for User Story 1

- [x] T016 [US1] Implement global constrained content container class behavior in apps/frontend/src/app/globals.css
- [x] T017 [US1] Apply constrained default content container to home page main content in apps/frontend/src/app/page.tsx
- [x] T018 [US1] Apply constrained default content container to datasets page main content in apps/frontend/src/app/datasets/page.tsx
- [x] T019 [US1] Align recent updates feed/list sections with constrained container behavior in apps/frontend/src/components/discovery/RecentUpdatesFeed.tsx and apps/frontend/src/components/discovery/DatasetCatalogList.tsx
- [x] T020 [US1] Validate constrained content spacing and centering behavior in apps/frontend/src/app/globals.css
- [x] T021 [US1] Verify US1 focused checks in apps/frontend/tests/home-page.test.tsx, apps/frontend/tests/catalog-page.test.tsx, and apps/frontend/tests/shell-structure-contract.test.tsx

**Checkpoint**: User Story 1 is independently functional and shippable as MVP.

---

## Phase 4: User Story 2 - Preserve Intentional Full-Width Surfaces (Priority: P2)

**Goal**: Keep explicit full-width shell surfaces edge-to-edge while constrained default content is active.

**Independent Test**: Verify full-width header/footer shell bands remain edge-to-edge while page content remains constrained.

### Tests for User Story 2 (REQUIRED) ⚠️

- [x] T022 [P] [US2] Add explicit_full_width assertions for header and footer regions in apps/frontend/tests/shell-structure-contract.test.tsx
- [x] T023 [P] [US2] Add home route assertions confirming mixed constrained content plus full-width shell bands in apps/frontend/tests/home-page.test.tsx
- [x] T024 [P] [US2] Add datasets route assertions confirming mixed constrained content plus full-width shell bands in apps/frontend/tests/catalog-page.test.tsx

### Implementation for User Story 2

- [x] T025 [US2] Implement explicit full-width shell-region utility behavior in apps/frontend/src/app/globals.css
- [x] T026 [US2] Apply explicit full-width mode classes for shell header/footer regions in apps/frontend/src/theme/monochrome-theme.ts
- [x] T027 [US2] Preserve header full-width rendering behavior under new width policy in apps/frontend/src/shell/site-header.tsx
- [x] T028 [US2] Preserve footer full-width rendering behavior under new width policy in apps/frontend/src/shell/site-footer.tsx
- [x] T029 [US2] Verify no behavioral regressions for navigation/list controls/fallback states while width modes change in apps/frontend/src/app/page.tsx and apps/frontend/src/app/datasets/page.tsx
- [x] T030 [US2] Verify US2 focused checks in apps/frontend/tests/shell-structure-contract.test.tsx, apps/frontend/tests/home-page.test.tsx, and apps/frontend/tests/catalog-page.test.tsx

**Checkpoint**: User Stories 1 and 2 are independently functional.

---

## Phase 5: User Story 3 - Keep Layout Behavior Consistent Across Pages (Priority: P3)

**Goal**: Ensure shared default width policy is reusable and consistent for current and future shell pages.

**Independent Test**: Confirm shell page structure uses shared constrained default mode unless explicit full-width mode is set.

### Tests for User Story 3 (REQUIRED) ⚠️

- [x] T031 [P] [US3] Add reusable shell content-mode assertions in apps/frontend/tests/shell-structure-contract.test.tsx
- [x] T032 [P] [US3] Add home route inheritance assertions for default constrained mode in apps/frontend/tests/home-page.test.tsx
- [x] T033 [P] [US3] Add datasets route inheritance assertions for default constrained mode in apps/frontend/tests/catalog-page.test.tsx

### Implementation for User Story 3

- [x] T034 [US3] Create shared shell content region class composition in apps/frontend/src/app/globals.css
- [x] T035 [US3] Route shell page content through shared region class composition in apps/frontend/src/app/page.tsx and apps/frontend/src/app/datasets/page.tsx
- [x] T036 [US3] Normalize width-mode naming for maintainability in apps/frontend/src/theme/monochrome-theme.ts
- [x] T037 [US3] Update width behavior guidance for future routes in specs/029-global-content-width/contracts/global-content-width-contract.md and specs/029-global-content-width/quickstart.md
- [x] T038 [US3] Verify US3 focused checks in apps/frontend/tests/shell-structure-contract.test.tsx, apps/frontend/tests/home-page.test.tsx, and apps/frontend/tests/catalog-page.test.tsx

**Checkpoint**: All user stories are independently functional and testable.

---

## Phase 6: Polish & Cross-Cutting Concerns

**Purpose**: Finalize docs alignment and execute mandatory repository gates.

- [x] T039 [P] Reconcile final behavior against global width contract notes in specs/029-global-content-width/contracts/global-content-width-contract.md
- [x] T040 [P] Update quickstart validation notes and outcomes in specs/029-global-content-width/quickstart.md
- [x] T041 [P] Update AGENTS.md only if workflow/tooling/stack notes changed during implementation in AGENTS.md
- [x] T042 Run focused frontend verification commands and record results in specs/029-global-content-width/quickstart.md
- [x] T043 Run `pnpm exec nx run-many -t test --all` and record pass result in specs/029-global-content-width/quickstart.md
- [x] T044 Run `pnpm exec nx run-many -t coverage --all` and record pass result in specs/029-global-content-width/quickstart.md
- [x] T045 Run manual visual validation on `/` and `/datasets` at wide and narrow viewports and record observations in specs/029-global-content-width/quickstart.md

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

- **US1 (P1)**: No dependency on other user stories; delivers core constrained content readability.
- **US2 (P2)**: Depends on shared width foundation and US1 constrained defaults.
- **US3 (P3)**: Depends on shared width foundation and builds consistency guarantees for future routes.

### Within Each User Story

- Add story tests first and verify failing expectations before implementation.
- Implement shared layout primitives before route-specific adjustments.
- Validate story checkpoint before progressing.

### Dependency Graph

- Phase 1 -> Phase 2 -> US1 -> US2 -> US3 -> Phase 6

### Parallel Opportunities

- Setup: T003, T004, and T005 can run in parallel.
- Foundational: T007, T008, and T010 can run in parallel.
- US1: T012, T013, T014, and T015 can run in parallel.
- US2: T022, T023, and T024 can run in parallel.
- US3: T031, T032, and T033 can run in parallel.
- Polish: T039, T040, and T041 can run in parallel.

---

## Parallel Example: User Story 1

```bash
Task: "T012 [US1] Add constrained_default assertions for home route in apps/frontend/tests/home-page.test.tsx"
Task: "T013 [US1] Add constrained_default assertions for datasets route in apps/frontend/tests/catalog-page.test.tsx"
Task: "T014 [US1] Add shell-level constrained assertions in apps/frontend/tests/shell-structure-contract.test.tsx"
```

## Parallel Example: User Story 2

```bash
Task: "T022 [US2] Add explicit_full_width assertions in apps/frontend/tests/shell-structure-contract.test.tsx"
Task: "T023 [US2] Add home mixed-mode width assertions in apps/frontend/tests/home-page.test.tsx"
Task: "T024 [US2] Add datasets mixed-mode width assertions in apps/frontend/tests/catalog-page.test.tsx"
```

## Parallel Example: User Story 3

```bash
Task: "T031 [US3] Add shared content-mode assertions in apps/frontend/tests/shell-structure-contract.test.tsx"
Task: "T032 [US3] Add home inheritance assertions in apps/frontend/tests/home-page.test.tsx"
Task: "T033 [US3] Add datasets inheritance assertions in apps/frontend/tests/catalog-page.test.tsx"
```

---

## Implementation Strategy

### MVP First (User Story 1 only)

1. Complete Phase 1 and Phase 2.
2. Complete Phase 3 (US1).
3. Validate US1 independently and demo constrained readable layout on home and datasets routes.

### Incremental Delivery

1. Deliver US1 for constrained default width behavior.
2. Deliver US2 for explicit full-width exception preservation.
3. Deliver US3 for consistent shared policy and route inheritance.
4. Complete Phase 6 with stop-gate validation and docs synchronization.

### Parallel Team Strategy

1. One engineer focuses on shared shell width primitives.
2. One engineer focuses on route-level composition for home and datasets pages.
3. One engineer focuses on regression tests and validation docs.
4. Converge for stop-gate execution and final documentation.

---

## Notes

- All tasks use required checklist format with sequential IDs and explicit file paths.
- [P] markers indicate tasks that can run concurrently with minimal coupling.
- Coverage must remain >= 90% in all affected projects.
- Before commit and before agent handoff/end: run `pnpm exec nx run-many -t test --all`.
- Before commit: run `pnpm exec nx run-many -t coverage --all`.
- Relevant docs must be updated in the same change as behavior updates.
