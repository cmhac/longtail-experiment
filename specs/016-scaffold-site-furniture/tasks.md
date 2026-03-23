# Tasks: Minimal Site Furniture Shell

**Input**: Design documents from /specs/016-scaffold-site-furniture/
**Prerequisites**: plan.md (required), spec.md (required for user stories), research.md, data-model.md, contracts/, quickstart.md

**Tests**: Test tasks are REQUIRED. Every user story and foundational component MUST include automated test coverage sufficient to maintain >= 90% coverage in affected projects.

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: [ID] [P?] [Story] Description

- [P]: Can run in parallel (different files, no dependencies)
- [Story]: Which user story this task belongs to (for example, US1, US2, US3)
- Include exact file paths in descriptions

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Prepare project configuration and baseline verification surface for shell/theme work.

- [X] T001 Confirm frontend runtime and quality commands are current in apps/frontend/package.json
- [X] T002 Confirm frontend Nx targets for dev/build/start/test/coverage in apps/frontend/project.json
- [X] T003 [P] Confirm Next.js baseline configuration supports shell work in apps/frontend/next.config.ts
- [X] T004 [P] Confirm frontend TypeScript and test settings for new shell files in apps/frontend/tsconfig.json
- [X] T005 [P] Add or update frontend test utility setup for shell rendering assertions in apps/frontend/tests/test-utils.tsx

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Establish shared shell/theme foundations required by all user stories.

**CRITICAL**: No user story work can begin until this phase is complete.

- [X] T006 Create shell region constants and ordering contract in apps/frontend/src/shell/shell-regions.ts
- [X] T007 Create shared monochrome style rules module in apps/frontend/src/theme/monochrome-theme.ts
- [X] T008 [P] Add global shell layout container and semantic regions in apps/frontend/src/app/layout.tsx
- [X] T009 [P] Add global monochrome tokens and base shell styles in apps/frontend/src/app/globals.css
- [X] T010 Create root route composition boundary for shell rendering in apps/frontend/src/app/page.tsx
- [X] T011 Add foundational shell render smoke test scaffold in apps/frontend/tests/shell-structure-contract.test.tsx
- [X] T012 Add foundational light/dark preference test scaffold in apps/frontend/tests/shell-theme-preference.test.tsx

**Checkpoint**: Foundation ready. User story implementation can now begin.

---

## Phase 3: User Story 1 - Establish a Real Site Shell (Priority: P1) MVP

**Goal**: Render a real, stable site shell with header, main placeholder, and footer.

**Independent Test**: Open the app and verify the three shell regions are present, ordered correctly, and readable with placeholder-only main content.

### Tests for User Story 1 (REQUIRED)

- [X] T013 [P] [US1] Add test asserting header region presence and semantics in apps/frontend/tests/shell-structure-contract.test.tsx
- [X] T014 [P] [US1] Add test asserting main placeholder region presence and placeholder text in apps/frontend/tests/shell-structure-contract.test.tsx
- [X] T015 [P] [US1] Add test asserting footer region presence and ordering in apps/frontend/tests/shell-structure-contract.test.tsx
- [X] T016 [P] [US1] Add test asserting shell remains structurally valid during page scroll in apps/frontend/tests/shell-structure-contract.test.tsx

### Implementation for User Story 1

- [X] T017 [P] [US1] Implement site header component in apps/frontend/src/shell/site-header.tsx
- [X] T018 [P] [US1] Implement content placeholder component in apps/frontend/src/shell/content-placeholder.tsx
- [X] T019 [P] [US1] Implement site footer component in apps/frontend/src/shell/site-footer.tsx
- [X] T020 [US1] Compose header, placeholder, and footer in root page shell in apps/frontend/src/app/page.tsx
- [X] T021 [US1] Add responsive shell region spacing and ordering styles in apps/frontend/src/app/globals.css
- [X] T022 [US1] Verify US1 coverage contribution via targeted shell tests in apps/frontend/tests/shell-structure-contract.test.tsx

**Checkpoint**: User Story 1 is independently functional and testable.

---

## Phase 4: User Story 2 - Monochromatic Visual Language (Priority: P2)

**Goal**: Enforce an extremely minimal monochromatic visual language across shell furniture with no accent colors.

**Independent Test**: Inspect shell output and tests to verify all shell regions stay within monochrome rules and reject accent-style drift.

### Tests for User Story 2 (REQUIRED)

- [X] T023 [P] [US2] Add test asserting header uses monochrome classes/tokens only in apps/frontend/tests/shell-structure-contract.test.tsx
- [X] T024 [P] [US2] Add test asserting placeholder uses monochrome classes/tokens only in apps/frontend/tests/shell-structure-contract.test.tsx
- [X] T025 [P] [US2] Add test asserting footer uses monochrome classes/tokens only in apps/frontend/tests/shell-structure-contract.test.tsx
- [X] T026 [P] [US2] Add regression test rejecting accent variant usage in shell components in apps/frontend/tests/shell-structure-contract.test.tsx

### Implementation for User Story 2

- [X] T027 [P] [US2] Apply HeroUI-first neutral component composition to header in apps/frontend/src/shell/site-header.tsx
- [X] T028 [P] [US2] Apply HeroUI-first neutral component composition to placeholder in apps/frontend/src/shell/content-placeholder.tsx
- [X] T029 [P] [US2] Apply HeroUI-first neutral component composition to footer in apps/frontend/src/shell/site-footer.tsx
- [X] T030 [US2] Implement shared monochrome class helpers and export usage contract in apps/frontend/src/theme/monochrome-theme.ts
- [X] T031 [US2] Align global CSS selectors with monochrome rules and remove accent leakage paths in apps/frontend/src/app/globals.css
- [X] T032 [US2] Verify US2 coverage contribution for monochrome constraints in apps/frontend/tests/shell-structure-contract.test.tsx

**Checkpoint**: User Story 2 is independently functional and testable.

---

## Phase 5: User Story 3 - Device-Aware Theme Preference (Priority: P3)

**Goal**: Ensure shell behavior follows device/browser light-dark preference from initial render while preserving readability.

**Independent Test**: Simulate light and dark preference conditions and verify shell appearance mode and readability in both cases.

### Tests for User Story 3 (REQUIRED)

- [X] T033 [P] [US3] Add test asserting light preference renders light shell mode in apps/frontend/tests/shell-theme-preference.test.tsx
- [X] T034 [P] [US3] Add test asserting dark preference renders dark shell mode in apps/frontend/tests/shell-theme-preference.test.tsx
- [X] T035 [P] [US3] Add test asserting text readability classes are present in both modes in apps/frontend/tests/shell-theme-preference.test.tsx
- [X] T036 [P] [US3] Add regression test for preference mode switching between sessions in apps/frontend/tests/shell-theme-preference.test.tsx

### Implementation for User Story 3

- [X] T037 [US3] Implement preference-aware theme mode resolution in root layout in apps/frontend/src/app/layout.tsx
- [X] T038 [US3] Apply mode-specific monochrome token mapping in apps/frontend/src/app/globals.css
- [X] T039 [US3] Ensure header component supports mode-appropriate readable contrast in apps/frontend/src/shell/site-header.tsx
- [X] T040 [US3] Ensure placeholder component supports mode-appropriate readable contrast in apps/frontend/src/shell/content-placeholder.tsx
- [X] T041 [US3] Ensure footer component supports mode-appropriate readable contrast in apps/frontend/src/shell/site-footer.tsx
- [X] T042 [US3] Verify US3 coverage contribution for preference-aware rendering in apps/frontend/tests/shell-theme-preference.test.tsx

**Checkpoint**: User Story 3 is independently functional and testable.

---

## Phase 6: Polish and Cross-Cutting Concerns

**Purpose**: Finalize quality validation, docs, and release readiness across all stories.

- [X] T043 [P] Update shell/theme quickstart verification evidence in specs/016-scaffold-site-furniture/quickstart.md
- [X] T044 [P] Align contract language with implemented shell/theme behavior in specs/016-scaffold-site-furniture/contracts/shell-theme-contract.md
- [X] T045 [P] Update plan notes if implementation deltas are discovered in specs/016-scaffold-site-furniture/plan.md
- [X] T046 Document local shell validation workflow updates in docs/runbooks/local-stack-baseline.md
- [X] T047 Run and fix frontend lint, format, typecheck, test, and coverage commands via apps/frontend/package.json targets
- [X] T048 Run and fix workspace affected lint/format/typecheck/test/coverage commands in package.json
- [X] T049 Validate AGENTS command/tooling references remain accurate for this feature in AGENTS.md

---

## Dependencies and Execution Order

### Phase Dependencies

- Setup (Phase 1): No dependencies, can start immediately.
- Foundational (Phase 2): Depends on Setup completion and blocks all user stories.
- User Stories (Phase 3-5): Depend on Foundational completion.
- Polish (Phase 6): Depends on completion of selected user stories.

### User Story Dependencies

- US1 (P1): Starts after Phase 2 and establishes MVP shell structure.
- US2 (P2): Starts after Phase 2 and can proceed independently, but is most reliable after US1 component files exist.
- US3 (P3): Starts after Phase 2 and can proceed independently, but is most reliable after US1 shell composition exists.

### Dependency Graph

- Phase 1 -> Phase 2 -> US1 -> Phase 6
- Phase 1 -> Phase 2 -> US2 -> Phase 6
- Phase 1 -> Phase 2 -> US3 -> Phase 6

---

## Parallel Execution Opportunities

- Phase 1: T003, T004, and T005 can run in parallel after T001 and T002.
- Phase 2: T008 and T009 can run in parallel; T011 and T012 can run in parallel after shell scaffold files exist.
- US1: T013-T016 can run in parallel; T017-T019 can run in parallel.
- US2: T023-T026 can run in parallel; T027-T029 can run in parallel.
- US3: T033-T036 can run in parallel; T039-T041 can run in parallel after T037-T038.
- Polish: T043, T044, and T045 can run in parallel.

---

## Parallel Example: User Story 1

- Run T013, T014, T015, and T016 together to establish failing shell structure assertions.
- Run T017, T018, and T019 together to build shell region components in parallel.

## Parallel Example: User Story 2

- Run T023, T024, T025, and T026 together for monochrome compliance guardrails.
- Run T027, T028, and T029 together to apply HeroUI-first monochrome composition.

## Parallel Example: User Story 3

- Run T033, T034, T035, and T036 together for preference-mode behavior checks.
- Run T039, T040, and T041 together to harden readable contrast by shell region.

---

## Implementation Strategy

### MVP First (User Story 1)

1. Complete Phase 1 and Phase 2.
2. Complete Phase 3 (US1).
3. Validate US1 independent test criteria in browser and automated tests.
4. Demo MVP shell before advancing.

### Incremental Delivery

1. Deliver US1 for structure baseline.
2. Deliver US2 to enforce monochrome rules.
3. Deliver US3 to satisfy preference-aware theming.
4. Execute polish phase and final quality checks.

### Parallel Team Strategy

1. Team completes Setup and Foundational tasks.
2. After Phase 2, parallelize by story:
   - Engineer A: US1
   - Engineer B: US2
   - Engineer C: US3
3. Rejoin for Phase 6 quality/documentation closure.

---

## Notes

- All tasks follow strict checklist format with sequential IDs.
- User story tasks include required story labels and exact file paths.
- Parallel markers are only applied to tasks without direct file/dependency collisions.
- Coverage threshold must remain >= 90% for affected frontend scope.
- Documentation updates are included in the same feature flow as code changes.
