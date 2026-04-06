# Tasks: Mobile Sidebar Navigation Drawer

**Input**: Design documents from `/specs/049-mobile-sidebar-drawer/`
**Prerequisites**: `plan.md`, `spec.md`, `research.md`, `data-model.md`, `contracts/mobile-sidebar-drawer-contract.md`, `quickstart.md`

**Tests**: Test tasks are REQUIRED. Every user story and foundational component MUST include automated coverage updates that preserve >= 90% thresholds in affected projects. Before any commit and before any AI agent stops work, run `pnpm exec nx run-many -t test --all`. Before any commit, run `pnpm exec nx run-many -t coverage --all`.

**Organization**: Tasks are grouped by user story to enable independent implementation and testing.

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Prepare feature scaffolding and test surfaces for mobile drawer work.

- [ ] T001 Create feature test files `apps/frontend/tests/mobile-nav-drawer.test.tsx` and `apps/frontend/tests/mobile-nav-drawer-auth.test.tsx`
- [ ] T002 [P] Add shell drawer component module `apps/frontend/src/components/shell/MobileNavDrawer.tsx`
- [ ] T003 [P] Add shared drawer action component module `apps/frontend/src/components/shell/MobileNavDrawerAction.tsx`
- [ ] T004 [P] Extend shell class-name constants for drawer hooks in `apps/frontend/src/theme/monochrome-theme.ts`

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Establish shared header foundations used by all user stories.

**⚠️ CRITICAL**: No user story work starts until this phase is complete.

- [ ] T005 Add responsive activation contract for drawer activation range (<=1024px active, >1024px inactive) in `apps/frontend/src/app/globals.css`
- [ ] T006 [P] Add drawer state wiring scaffold and trigger control in `apps/frontend/src/shell/site-header.tsx`
- [ ] T007 [P] Add drawer menu configuration model (ordered rows + protected metadata) in `apps/frontend/src/shell/navbar-config.ts`
- [ ] T008 Add baseline drawer render/open-close tests in `apps/frontend/tests/mobile-nav-drawer.test.tsx`
- [ ] T036 Add activation-threshold contract test coverage for <=1024px active and >1024px inactive behavior in `apps/frontend/tests/mobile-nav-drawer.test.tsx`

**Checkpoint**: Shared shell foundation complete; user stories can proceed.

---

## Phase 3: User Story 1 - Replace Cluttered Mobile Top Navigation (Priority: P1) 🎯 MVP

**Goal**: Deliver right-side small-screen drawer replacing cluttered multi-row mobile top nav with required row ordering and immediate close-on-navigation behavior.

**Independent Test**: In drawer activation range (<=1024px), opening hamburger shows drawer at ~90% width with blurred visible backdrop sliver; required rows appear in exact order; tapping a destination closes drawer immediately and navigates.

### Tests for User Story 1 (REQUIRED)

- [ ] T009 [P] [US1] Add ordered-row and top-row logo/bell assertions in `apps/frontend/tests/mobile-nav-drawer.test.tsx`
- [ ] T010 [P] [US1] Add immediate-close-on-navigation interaction test in `apps/frontend/tests/mobile-nav-drawer.test.tsx`
- [ ] T011 [P] [US1] Add responsive shell contract assertions for drawer mode and desktop preservation in `apps/frontend/tests/shell-structure-contract.test.tsx`

### Implementation for User Story 1

- [ ] T012 [P] [US1] Implement drawer layout and ordered primary row rendering in `apps/frontend/src/components/shell/MobileNavDrawer.tsx`
- [ ] T013 [P] [US1] Implement reusable drawer action row behavior in `apps/frontend/src/components/shell/MobileNavDrawerAction.tsx`
- [ ] T014 [US1] Integrate drawer component with header trigger and navigation close behavior in `apps/frontend/src/shell/site-header.tsx`
- [ ] T015 [US1] Implement drawer visual behavior (~90% right tray, blur sliver, non-interactive backdrop) and preserve inactive behavior above 1024px in `apps/frontend/src/app/globals.css`
- [ ] T016 [US1] Update navbar interaction tests for new small-screen navigation path in `apps/frontend/tests/navbar-interactions.test.tsx`
- [ ] T037 [US1] Add repeated-interaction stability test (rapid open/close + navigation) in `apps/frontend/tests/mobile-nav-drawer.test.tsx`

**Checkpoint**: US1 is independently functional as MVP.

---

## Phase 4: User Story 2 - Keep Utility Actions Available In Drawer (Priority: P2)

**Goal**: Preserve account/comparison/notification/sign-out utility behavior within drawer using existing semantics and redirects.

**Independent Test**: Signed-in user sees comparison counter and bell behavior consistent with header sources; account routes correctly; sign-out clears session and lands on `/`; signed-out protected taps redirect to `/login`.

### Tests for User Story 2 (REQUIRED)

- [ ] T017 [P] [US2] Add comparison counter consistency and zero-state tests in `apps/frontend/tests/mobile-nav-drawer.test.tsx`
- [ ] T018 [P] [US2] Add sign-out redirect-to-home behavior test in `apps/frontend/tests/mobile-nav-drawer-auth.test.tsx`
- [ ] T019 [P] [US2] Add signed-out protected-action redirect-to-login tests in `apps/frontend/tests/mobile-nav-drawer-auth.test.tsx`

### Implementation for User Story 2

- [ ] T020 [US2] Reuse comparison-state source and render counter in drawer comparison row in `apps/frontend/src/shell/site-header.tsx`
- [ ] T021 [US2] Reuse notifications bell entry behavior in drawer top row in `apps/frontend/src/components/shell/MobileNavDrawer.tsx`
- [ ] T022 [US2] Implement account/search/home/sources/datasets destination handlers in `apps/frontend/src/shell/site-header.tsx`
- [ ] T023 [US2] Implement sign-out action flow and redirect-to-home behavior for drawer footer in `apps/frontend/src/shell/site-header.tsx`
- [ ] T024 [US2] Implement signed-out protected-action redirect guard to `/login` in `apps/frontend/src/shell/site-header.tsx`
- [ ] T038 [US2] Add notification loading-state and bell parity tests in `apps/frontend/tests/mobile-nav-drawer-auth.test.tsx`

**Checkpoint**: US2 is independently functional and testable.

---

## Phase 5: User Story 3 - Respect Role-Specific Actions In Drawer (Priority: P3)

**Goal**: Show admin action in drawer footer only for admin/owner users, above sign out, and route correctly.

**Independent Test**: Admin/owner session shows Admin button above Sign out and routes to `/admin`; non-admin and signed-out sessions do not show Admin button.

### Tests for User Story 3 (REQUIRED)

- [ ] T025 [P] [US3] Add admin visibility and ordering tests for drawer footer in `apps/frontend/tests/mobile-nav-drawer-auth.test.tsx`
- [ ] T026 [P] [US3] Add non-admin/signed-out admin-hidden tests in `apps/frontend/tests/mobile-nav-drawer-auth.test.tsx`
- [ ] T027 [P] [US3] Add admin route navigation test from drawer footer in `apps/frontend/tests/mobile-nav-drawer-auth.test.tsx`

### Implementation for User Story 3

- [ ] T028 [US3] Implement role-gated Admin footer action visibility in drawer rendering in `apps/frontend/src/components/shell/MobileNavDrawer.tsx`
- [ ] T029 [US3] Implement admin footer routing integration in `apps/frontend/src/shell/site-header.tsx`

**Checkpoint**: US3 is independently functional and testable.

---

## Phase 6: Polish & Cross-Cutting Concerns

**Purpose**: Final consistency, docs, and mandatory gate validation.

- [ ] T030 [P] Align quickstart verification notes with implemented behavior in `specs/049-mobile-sidebar-drawer/quickstart.md`
- [ ] T031 [P] Validate and update shell contract notes for any test-id/class changes in `specs/049-mobile-sidebar-drawer/contracts/mobile-sidebar-drawer-contract.md`
- [ ] T032 Run frontend quality checks `pnpm --dir apps/frontend exec biome check .`, `pnpm --dir apps/frontend typecheck`, and `pnpm --dir apps/frontend test`
- [ ] T033 Run repository stop gate `pnpm exec nx run-many -t test --all`
- [ ] T034 Run repository coverage gate `pnpm exec nx run-many -t coverage --all`
- [ ] T035 Run `pre-commit run --all-files` and resolve any failures
- [ ] T039 [P] Update `AGENTS.md` with finalized mobile drawer implementation/tooling deltas if workflows or canonical commands changed
- [ ] T040 [P] Update affected documentation for shell navigation behavior changes in `docs/` paths impacted by mobile header/navigation references

---

## Dependencies & Execution Order

### Phase Dependencies

- Phase 1 (Setup): no dependencies.
- Phase 2 (Foundational): depends on Phase 1; blocks all user stories.
- Phase 3 (US1): depends on Phase 2.
- Phase 4 (US2): depends on Phase 2 and US1 integration tasks T014-T015 completion.
- Phase 5 (US3): depends on Phase 2 and auth session visibility utilities from US2.
- Phase 6 (Polish): depends on all targeted user stories being complete.

### User Story Dependencies

- US1 (P1): independent after Foundational completion.
- US2 (P2): depends on US1 shell integration readiness (T014-T015) before utility parity implementation.
- US3 (P3): depends on drawer footer composition and auth role state from US2.

---

## Parallel Opportunities

- Setup: T002, T003, T004 can run in parallel.
- Foundational: T006 and T007 can run in parallel after T005 starts.
- US1 tests T009-T011 can run in parallel; implementation T012 and T013 can run in parallel.
- US2 tests T017-T019 can run in parallel.
- US3 tests T025-T027 can run in parallel.
- Polish docs T030 and T031 can run in parallel.

### Parallel Example: User Story 1

```bash
# Parallel test authoring for US1
Task: "T009 [US1] ordered-row and logo/bell assertions in apps/frontend/tests/mobile-nav-drawer.test.tsx"
Task: "T010 [US1] close-on-navigation interaction test in apps/frontend/tests/mobile-nav-drawer.test.tsx"
Task: "T011 [US1] responsive shell contract assertions in apps/frontend/tests/shell-structure-contract.test.tsx"

# Parallel component implementation for US1
Task: "T012 [US1] drawer layout in apps/frontend/src/components/shell/MobileNavDrawer.tsx"
Task: "T013 [US1] drawer action row in apps/frontend/src/components/shell/MobileNavDrawerAction.tsx"
```

### Parallel Example: User Story 2

```bash
Task: "T017 [US2] comparison counter tests in apps/frontend/tests/mobile-nav-drawer.test.tsx"
Task: "T018 [US2] sign-out redirect tests in apps/frontend/tests/mobile-nav-drawer-auth.test.tsx"
Task: "T019 [US2] protected redirect tests in apps/frontend/tests/mobile-nav-drawer-auth.test.tsx"
```

---

## Implementation Strategy

### MVP First (US1)

1. Complete Phase 1 and Phase 2.
2. Deliver Phase 3 (US1) as the first shippable increment.
3. Validate US1 independent test criteria before expanding scope.

### Incremental Delivery

1. Add US2 utility parity and auth redirects.
2. Add US3 role-specific admin visibility.
3. Finish polish and mandatory quality gates.

### Format Validation

- All tasks use required checklist format: `- [ ] T### [P?] [US?] Description with file path`.
- Story labels are used only for user story phases (US1-US3).
- Setup/Foundational/Polish tasks have no story label.
