# Tasks: Initial UI Design

**Input**: Design documents from `/Users/hackerc/Projects/longtail-experiment/specs/023-initial-ui-design/`
**Prerequisites**: plan.md (required), spec.md (required for user stories), research.md, data-model.md, contracts/, quickstart.md

**Tests**: Test tasks are REQUIRED. Every user story and foundational component MUST include automated test coverage sufficient to maintain >= 90% coverage in affected projects. Before any commit and before any AI agent stops work, the full repository suite MUST pass via `pnpm exec nx run-many -t test --all`; targeted tests alone are never sufficient for this stop gate. Before any commit, monorepo coverage MUST pass via `pnpm exec nx run-many -t coverage --all` with >= 90% thresholds in every project.

**Organization**: Tasks are grouped by user story so each story can be implemented and validated independently.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (US1, US2, US3)
- Include exact file paths in descriptions

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Establish shared navbar implementation surfaces and test file scaffolding.

- [x] T001 Create navbar state/config module for tabs and utility controls in apps/frontend/src/shell/navbar-config.ts
- [x] T002 [P] Create navbar interaction test scaffold in apps/frontend/tests/navbar-interactions.test.tsx
- [x] T003 [P] Create profile dropdown interaction test scaffold in apps/frontend/tests/navbar-profile-dropdown.test.tsx
- [x] T004 [P] Create navbar appearance-mode test scaffold in apps/frontend/tests/navbar-theme-mode.test.tsx

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Build shared structure, styles, and shell contracts required before story-specific behavior.

**⚠️ CRITICAL**: No user story work begins until this phase is complete.

- [x] T005 Add semantic navbar region container and slot class hooks in apps/frontend/src/shell/site-header.tsx
- [x] T006 [P] Add shared navbar class tokens and helper types in apps/frontend/src/theme/monochrome-theme.ts
- [x] T007 [P] Add full-width navbar baseline styles and responsive layout rules in apps/frontend/src/app/globals.css
- [x] T008 Update home shell contract assertions for navbar structure in apps/frontend/tests/shell-structure-contract.test.tsx
- [x] T009 Add baseline accessibility/test-id expectations for navbar contract in specs/023-initial-ui-design/contracts/navbar-ui-contract.md

**Checkpoint**: Foundation ready. User story implementation can proceed.

---

## Phase 3: User Story 1 - Render Baseline Navigation Bar (Priority: P1) 🎯 MVP

**Goal**: Render the full-width top navbar with Longtail branding, three tabs, and two utility icons.

**Independent Test**: Load homepage markup and verify navbar includes brand text `Longtail`, tabs `Home`/`Datasets`/`Trends`, and search/profile icon controls in the header region.

### Tests for User Story 1 (REQUIRED) ⚠️

- [x] T010 [P] [US1] Add structural contract assertions for brand/tabs/icons in apps/frontend/tests/shell-structure-contract.test.tsx
- [x] T011 [P] [US1] Add homepage render assertions for navbar composition in apps/frontend/tests/home-page.test.tsx

### Implementation for User Story 1

- [x] T012 [US1] Implement navbar brand area and primary tab rendering in apps/frontend/src/shell/site-header.tsx
- [x] T013 [P] [US1] Implement icon control rendering (search/profile) with accessible labels in apps/frontend/src/shell/site-header.tsx
- [x] T014 [US1] Wire navbar config data into header rendering flow in apps/frontend/src/shell/navbar-config.ts
- [x] T015 [US1] Refine navbar spacing/typography for full-width shell behavior in apps/frontend/src/app/globals.css
- [x] T016 [US1] Update feature quickstart verification notes for baseline render checks in specs/023-initial-ui-design/quickstart.md

**Checkpoint**: User Story 1 is independently testable and delivers the MVP navbar shell.

---

## Phase 4: User Story 2 - Enforce Limited-Scope Interactions (Priority: P2)

**Goal**: Keep Home and brand navigation active while Datasets, Trends, and search remain visible but disabled and inert.

**Independent Test**: Interact with navbar controls and verify only brand/Home navigate to `/`; Datasets/Trends/search do not trigger navigation or feature behavior.

### Tests for User Story 2 (REQUIRED) ⚠️

- [x] T017 [P] [US2] Add disabled-control behavior tests for tabs/search in apps/frontend/tests/navbar-interactions.test.tsx
- [x] T018 [P] [US2] Add route behavior assertions for brand/Home navigation in apps/frontend/tests/navbar-interactions.test.tsx

### Implementation for User Story 2

- [x] T019 [US2] Implement Home and brand homepage navigation behavior in apps/frontend/src/shell/site-header.tsx
- [x] T020 [US2] Implement disabled states for Datasets and Trends tabs in apps/frontend/src/shell/site-header.tsx
- [x] T021 [US2] Implement disabled state for search icon control in apps/frontend/src/shell/site-header.tsx
- [x] T022 [US2] Add disabled-control visual state styling and pointer behavior in apps/frontend/src/app/globals.css
- [x] T023 [US2] Update navbar interaction contract details for disabled controls in specs/023-initial-ui-design/contracts/navbar-ui-contract.md

**Checkpoint**: User Story 2 is independently testable with clear in-scope vs out-of-scope interaction behavior.

---

## Phase 5: User Story 3 - Show Profile Dropdown Placeholder (Priority: P3)

**Goal**: Provide profile dropdown toggle behavior with exactly one placeholder message.

**Independent Test**: Click profile icon and confirm dropdown opens/closes reliably with only `dropdown coming soon` content in light and dark modes.

### Tests for User Story 3 (REQUIRED) ⚠️

- [x] T024 [P] [US3] Add profile dropdown open/close interaction tests in apps/frontend/tests/navbar-profile-dropdown.test.tsx
- [x] T025 [P] [US3] Add dropdown content and mode-readability assertions in apps/frontend/tests/navbar-theme-mode.test.tsx

### Implementation for User Story 3

- [x] T026 [US3] Implement profile dropdown anchored interaction in apps/frontend/src/shell/site-header.tsx
- [x] T027 [US3] Enforce exact placeholder content `dropdown coming soon` in apps/frontend/src/shell/site-header.tsx
- [x] T028 [US3] Add dropdown surface styling for light/dark readability in apps/frontend/src/app/globals.css
- [x] T029 [US3] Add responsive safeguards for narrow viewport navbar/dropdown layout in apps/frontend/src/app/globals.css
- [x] T030 [US3] Update profile dropdown behavior contract language in specs/023-initial-ui-design/contracts/navbar-ui-contract.md

**Checkpoint**: User Story 3 is independently testable and completes the initial profile interaction scaffold.

---

## Phase 6: Polish & Cross-Cutting Concerns

**Purpose**: Final consistency checks, documentation alignment, and mandatory quality gate execution.

- [x] T031 [P] Reconcile tasks and plan wording with delivered implementation details in specs/023-initial-ui-design/plan.md
- [x] T032 [P] Update end-to-end validation steps and expected outcomes in specs/023-initial-ui-design/quickstart.md
- [x] T033 Execute focused frontend validation commands and record outcomes in specs/023-initial-ui-design/tasks.md
- [x] T034 Run `pnpm exec nx run-many -t test --all` and record pass result in specs/023-initial-ui-design/tasks.md
- [x] T035 Run `pnpm exec nx run-many -t coverage --all` and record pass result in specs/023-initial-ui-design/tasks.md

---

## Dependencies & Execution Order

### Phase Dependencies

- **Phase 1 (Setup)**: No dependencies.
- **Phase 2 (Foundational)**: Depends on Phase 1 and blocks all user stories.
- **Phase 3 (US1)**: Depends on Phase 2 completion.
- **Phase 4 (US2)**: Depends on Phase 2 completion; can run after US1 or in parallel if staffed.
- **Phase 5 (US3)**: Depends on Phase 2 completion; can run after US1 or in parallel if staffed.
- **Phase 6 (Polish)**: Depends on completion of selected user stories.

### User Story Dependencies

- **US1 (P1)**: No dependency on other stories; defines MVP shell value.
- **US2 (P2)**: Independent interaction slice using shared navbar structure.
- **US3 (P3)**: Independent profile interaction slice using shared navbar structure.

### Within Each User Story

- Tests first and failing before implementation where applicable.
- Shared config/state definitions before final UI polish for that story.
- Story checkpoint must pass independently before moving to final polish.

### Parallel Opportunities

- Setup parallel tasks: T002, T003, T004.
- Foundational parallel tasks: T006, T007.
- US1 parallel tasks: T010, T011, T013.
- US2 parallel tasks: T017, T018.
- US3 parallel tasks: T024, T025.
- Polish parallel tasks: T031, T032.

---

## Parallel Example: User Story 1

```bash
Task: "T010 [US1] Add structural contract assertions in apps/frontend/tests/shell-structure-contract.test.tsx"
Task: "T011 [US1] Add homepage render assertions in apps/frontend/tests/home-page.test.tsx"
Task: "T013 [US1] Implement icon control rendering in apps/frontend/src/shell/site-header.tsx"
```

## Parallel Example: User Story 2

```bash
Task: "T017 [US2] Add disabled-control behavior tests in apps/frontend/tests/navbar-interactions.test.tsx"
Task: "T018 [US2] Add route behavior assertions in apps/frontend/tests/navbar-interactions.test.tsx"
```

## Parallel Example: User Story 3

```bash
Task: "T024 [US3] Add profile dropdown interaction tests in apps/frontend/tests/navbar-profile-dropdown.test.tsx"
Task: "T025 [US3] Add dropdown mode-readability assertions in apps/frontend/tests/navbar-theme-mode.test.tsx"
Task: "T029 [US3] Add responsive safeguards in apps/frontend/src/app/globals.css"
```

---

## Implementation Strategy

### MVP First (User Story 1 only)

1. Complete Phase 1 and Phase 2.
2. Complete Phase 3 (US1).
3. Validate US1 independently via structural/homepage tests.
4. Demo or ship MVP navbar shell.

### Incremental Delivery

1. Deliver US1 baseline navbar.
2. Deliver US2 disabled/in-scope interactions.
3. Deliver US3 profile dropdown placeholder and mode/readability support.
4. Complete polish and run mandatory stop-gate commands.

### Parallel Team Strategy

1. One engineer completes setup/foundational work.
2. After Phase 2, separate engineers can deliver US2 and US3 in parallel while US1 stabilizes.
3. Rejoin for final polish and gate verification.

---

## Notes

- All tasks follow the required checklist format: checkbox, sequential ID, optional [P], required [US#] for story tasks, and explicit file path.
- Coverage must remain >= 90% in affected projects.
- Before any commit and before any AI agent handoff/end: run `pnpm exec nx run-many -t test --all`.
- Before any commit: run `pnpm exec nx run-many -t coverage --all`.
- Documentation updates are required in the same change as behavior changes.

## Validation Outcomes

- 2026-03-24: `pnpm --dir apps/frontend test -- tests/shell-structure-contract.test.tsx tests/home-page.test.tsx tests/navbar-interactions.test.tsx tests/navbar-profile-dropdown.test.tsx tests/navbar-theme-mode.test.tsx` passed.
- 2026-03-24: `pnpm --dir apps/frontend typecheck` passed.
- 2026-03-24: `pnpm exec nx run-many -t test --all` passed.
- 2026-03-24: `pnpm exec nx run-many -t coverage --all` passed.
