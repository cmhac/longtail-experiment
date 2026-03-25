# Tasks: Global Footer Component

**Input**: Design documents from `/specs/026-global-footer/`
**Prerequisites**: plan.md (required), spec.md (required for user stories), research.md, data-model.md, contracts/

**Tests**: Test tasks are REQUIRED. Every user story and foundational component MUST include automated test coverage sufficient to maintain >= 90% coverage in affected projects. Before any commit and before any AI agent stops work, the full repository suite MUST pass via `pnpm exec nx run-many -t test --all`; targeted tests alone are never sufficient for this stop gate. Before any commit, monorepo coverage MUST pass via `pnpm exec nx run-many -t coverage --all` with >= 90% thresholds in every project.

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3)
- Include exact file paths in descriptions

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Prepare shared footer constants, fixtures, and validation notes before story implementation.

- [x] T001 Audit current shell footer integration points in `apps/frontend/src/app/page.tsx`, `apps/frontend/src/shell/site-footer.tsx`, and `apps/frontend/src/shell/shell-regions.ts`
- [x] T002 Create shared footer content constants in `apps/frontend/src/shell/footer-content.ts`
- [x] T003 [P] Add footer fixture helper for shell tests in `apps/frontend/tests/fixtures/footer-fixtures.ts`
- [x] T004 [P] Add implementation checklist notes for footer rollout in `specs/026-global-footer/quickstart.md`

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Establish shared footer contract hooks and base styling primitives used by all user stories.

**⚠️ CRITICAL**: No user story work can begin until this phase is complete.

- [x] T005 [P] Add baseline footer contract assertions for shell order and landmark semantics in `apps/frontend/tests/shell-structure-contract.test.tsx`
- [x] T006 [P] Add startup contract assertion for required footer content container in `apps/frontend/tests/startup-smoke.test.tsx`
- [x] T007 Add base footer class hooks and data-testid attributes in `apps/frontend/src/shell/site-footer.tsx`
- [x] T008 Add foundational footer layout primitives in `apps/frontend/src/app/globals.css`

**Checkpoint**: Shared shell/footer foundation is complete and user stories can be implemented independently.

---

## Phase 3: User Story 1 - Read Consistent Footer Identity (Priority: P1) 🎯 MVP

**Goal**: Ensure every shell-rendered page shows a consistent footer with Longtail branding and mission copy.

**Independent Test**: Open home and another shell route and verify identical footer branding/mission content appears at the page bottom.

### Tests for User Story 1 (REQUIRED) ⚠️

- [x] T009 [P] [US1] Add homepage assertion for Longtail footer brand text in `apps/frontend/tests/home-page.test.tsx`
- [x] T010 [P] [US1] Add shell contract assertions for footer mission statement text in `apps/frontend/tests/shell-structure-contract.test.tsx`
- [x] T011 [P] [US1] Add startup smoke assertion for stable footer identity text in `apps/frontend/tests/startup-smoke.test.tsx`

### Implementation for User Story 1

- [x] T012 [US1] Replace baseline footer copy with Longtail brand heading and mission paragraph in `apps/frontend/src/shell/site-footer.tsx`
- [x] T013 [US1] Wire shared footer content constants into shell footer rendering in `apps/frontend/src/shell/site-footer.tsx` and `apps/frontend/src/shell/footer-content.ts`
- [x] T014 [US1] Ensure footer remains present in both page success and error render paths in `apps/frontend/src/app/page.tsx`
- [x] T015 [US1] Verify footer shell region metadata remains stable for all shell pages in `apps/frontend/src/shell/shell-regions.ts`
- [x] T016 [US1] Validate US1 focused checks in `apps/frontend/tests/home-page.test.tsx` and `apps/frontend/tests/shell-structure-contract.test.tsx`

**Checkpoint**: User Story 1 is independently functional and shippable as MVP.

---

## Phase 4: User Story 2 - Preserve Editorial Visual Style (Priority: P2)

**Goal**: Apply screenshot-inspired editorial hierarchy and minimalist layout to the shared footer.

**Independent Test**: Verify brand emphasis, restrained body text, and clean full-width footer region with readable internal padding.

### Tests for User Story 2 (REQUIRED) ⚠️

- [x] T017 [P] [US2] Add shell structure assertions for editorial footer hierarchy classes in `apps/frontend/tests/shell-structure-contract.test.tsx`
- [x] T018 [P] [US2] Add homepage assertions that footer avoids utility-link clutter in `apps/frontend/tests/home-page.test.tsx`
- [x] T019 [P] [US2] Add startup smoke assertions for editorial footer container rendering in `apps/frontend/tests/startup-smoke.test.tsx`

### Implementation for User Story 2

- [x] T020 [US2] Implement editorial footer markup structure (brand block + mission block) in `apps/frontend/src/shell/site-footer.tsx`
- [x] T021 [US2] Implement full-width footer spacing, padding, and typography hierarchy styles in `apps/frontend/src/app/globals.css`
- [x] T022 [US2] Align footer variant and monochrome shell usage with editorial style in `apps/frontend/src/shell/site-footer.tsx`
- [x] T023 [US2] Remove obsolete baseline footer visual elements from `apps/frontend/src/shell/site-footer.tsx`
- [x] T024 [US2] Validate US2 focused checks in `apps/frontend/tests/shell-structure-contract.test.tsx`

**Checkpoint**: User Stories 1 and 2 are independently functional.

---

## Phase 5: User Story 3 - Keep Footer Legible Across Modes and Screens (Priority: P3)

**Goal**: Keep footer readable and stable in light/dark modes and mobile/desktop viewport sizes.

**Independent Test**: Validate readable footer text contrast and wrapping across theme and viewport permutations.

### Tests for User Story 3 (REQUIRED) ⚠️

- [x] T025 [P] [US3] Add dark/light-mode footer readability assertions in `apps/frontend/tests/shell-structure-contract.test.tsx`
- [x] T026 [P] [US3] Add mobile footer wrap/no-overlap assertions in `apps/frontend/tests/home-page.test.tsx`
- [x] T027 [P] [US3] Add startup smoke assertions for theme-safe footer rendering in `apps/frontend/tests/startup-smoke.test.tsx`

### Implementation for User Story 3

- [x] T028 [US3] Implement responsive footer typography and wrapping rules in `apps/frontend/src/app/globals.css`
- [x] T029 [US3] Implement theme-aware footer contrast token usage in `apps/frontend/src/app/globals.css`
- [x] T030 [US3] Ensure footer component uses shell-readable class contract in `apps/frontend/src/shell/site-footer.tsx`
- [x] T031 [US3] Update quickstart theme/viewport validation steps in `specs/026-global-footer/quickstart.md`
- [x] T032 [US3] Validate US3 focused checks in `apps/frontend/tests/home-page.test.tsx` and `apps/frontend/tests/startup-smoke.test.tsx`

**Checkpoint**: All user stories are independently functional and testable.

---

## Phase 6: Polish & Cross-Cutting Concerns

**Purpose**: Finalize docs/contracts and run mandatory quality stop gates.

- [x] T033 [P] Sync footer shell presentation guarantees with implemented behavior in `specs/026-global-footer/contracts/footer-shell-contract.md`
- [x] T034 [P] Update final validation notes and command outcomes in `specs/026-global-footer/quickstart.md`
- [x] T035 [P] Update changed workflow/tooling stack notes in `AGENTS.md`
- [x] T036 Run full monorepo test stop gate with `pnpm exec nx run-many -t test --all` and record result in `specs/026-global-footer/quickstart.md`
- [x] T037 Run full monorepo coverage stop gate with `pnpm exec nx run-many -t coverage --all` and record result in `specs/026-global-footer/quickstart.md`
- [x] T038 Run `pre-commit run --all-files` and record result in `specs/026-global-footer/quickstart.md`

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies; can start immediately.
- **Foundational (Phase 2)**: Depends on Setup completion; blocks all user story work.
- **User Story Phases (Phase 3-5)**: Depend on Foundational completion.
- **Polish (Phase 6)**: Depends on completion of all desired user stories.

### User Story Dependencies

- **US1 (P1)**: Starts after Phase 2; no dependency on US2/US3.
- **US2 (P2)**: Starts after Phase 2; independent value with optional integration on US1 markup.
- **US3 (P3)**: Starts after Phase 2; can evolve after US1/US2 while preserving independent validation.

### Within Each User Story

- Write story tests first and ensure they fail before implementation changes.
- Implement component/markup updates before style refinements.
- Finalize story-level validation commands before moving to next story.

### Dependency Graph

- Phase 1 -> Phase 2 -> {US1, US2, US3} -> Phase 6
- Recommended order: US1 (MVP) -> US2 -> US3

### Parallel Opportunities

- Phase 1: T003 and T004 can run in parallel after T001/T002.
- Phase 2: T005 and T006 can run in parallel before T007/T008.
- US1: T009, T010, and T011 can run in parallel.
- US2: T017, T018, and T019 can run in parallel.
- US3: T025, T026, and T027 can run in parallel.
- Phase 6: T033, T034, and T035 can run in parallel before stop-gate tasks.

---

## Parallel Example: User Story 1

```bash
Task: "T009 [US1] Update homepage footer identity assertion in apps/frontend/tests/home-page.test.tsx"
Task: "T010 [US1] Update shell footer contract assertions in apps/frontend/tests/shell-structure-contract.test.tsx"
Task: "T011 [US1] Update startup footer identity assertion in apps/frontend/tests/startup-smoke.test.tsx"
```

## Parallel Example: User Story 2

```bash
Task: "T017 [US2] Add editorial hierarchy assertions in apps/frontend/tests/shell-structure-contract.test.tsx"
Task: "T018 [US2] Add no-clutter footer assertions in apps/frontend/tests/home-page.test.tsx"
Task: "T019 [US2] Add editorial footer container assertion in apps/frontend/tests/startup-smoke.test.tsx"
```

## Parallel Example: User Story 3

```bash
Task: "T025 [US3] Add theme readability assertions in apps/frontend/tests/shell-structure-contract.test.tsx"
Task: "T026 [US3] Add mobile wrap assertions in apps/frontend/tests/home-page.test.tsx"
Task: "T027 [US3] Add theme-safe startup assertions in apps/frontend/tests/startup-smoke.test.tsx"
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1 Setup.
2. Complete Phase 2 Foundational tasks.
3. Complete Phase 3 (US1) and validate independent criteria.
4. Demo MVP global footer identity.

### Incremental Delivery

1. Deliver US1 for global footer presence/identity.
2. Deliver US2 for editorial visual treatment.
3. Deliver US3 for responsive and theme resilience.
4. Complete Phase 6 stop gates and documentation sync.

### Parallel Team Strategy

1. Engineer A implements footer markup/content updates.
2. Engineer B updates shell/page test contracts in parallel.
3. Engineer C handles responsive/theme CSS and validation steps.
4. Converge for final quality gates and docs synchronization.

---

## Notes

- [P] tasks indicate independent files and minimal cross-task coupling.
- [US1]/[US2]/[US3] labels preserve story traceability and independent validation.
- Keep affected-project coverage >= 90% throughout implementation.
- Before commit and before agent handoff/stop: `pnpm exec nx run-many -t test --all` must pass.
- Before commit: `pnpm exec nx run-many -t coverage --all` must pass.
- Update relevant documentation in the same change as behavior updates.
