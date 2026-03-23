# Tasks: Frontend Page Furniture Baseline

**Input**: Design documents from /specs/015-scaffold-page-furniture/
**Prerequisites**: plan.md (required), spec.md (required for user stories), research.md, data-model.md, contracts/, quickstart.md

**Tests**: Test tasks are REQUIRED. Every user story and foundational component MUST include automated test coverage sufficient to maintain >= 90% coverage in affected projects.

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: [ID] [P?] [Story] Description

- [P]: Can run in parallel (different files, no dependencies)
- [Story]: Which user story this task belongs to (for example, US1, US2, US3)
- Include exact file paths in descriptions

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Prepare frontend runtime baseline dependencies and project targets.

- [x] T001 Add Next.js and React runtime dependencies and dev scripts in apps/frontend/package.json
- [x] T002 Update frontend Nx metadata and target commands for dev/build/start support in apps/frontend/project.json
- [x] T003 [P] Add Next.js base config in apps/frontend/next.config.ts
- [x] T004 [P] Add app router tsconfig compatibility settings in apps/frontend/tsconfig.json
- [x] T005 [P] Add environment template for frontend runtime startup in apps/frontend/.env.local.example

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Build shared shell contracts and baseline structure required by all user stories.

**CRITICAL**: No user story work can begin until this phase is complete.

- [x] T006 Create global app layout with root shell boundary wiring in apps/frontend/src/app/layout.tsx
- [x] T007 Create root blank page with empty main content region in apps/frontend/src/app/page.tsx
- [x] T008 [P] Add baseline shell styles for slot visibility and responsive layout in apps/frontend/src/app/globals.css
- [x] T009 [P] Define furniture adapter type contracts in apps/frontend/src/furniture/contracts.ts
- [x] T010 [P] Add shell slot identifiers and ordering constants in apps/frontend/src/shell/slots/slot-definitions.ts
- [x] T011 Implement shared app shell composition component in apps/frontend/src/shell/app-shell.tsx
- [x] T012 Add foundational shell smoke test for root shell renderability in apps/frontend/tests/startup-smoke.test.tsx
- [x] T013 Add foundational slot presence contract test scaffold in apps/frontend/tests/shell-contract.test.tsx

**Checkpoint**: Foundation ready. User story implementation can now begin.

---

## Phase 3: User Story 1 - Open the Baseline Frontend Shell (Priority: P1) MVP

**Goal**: Developers can start frontend locally and view a no-content root shell with all required furniture placeholders.

**Independent Test**: Start the frontend, open root route, and confirm shell loads without runtime errors and all required placeholders render while main content remains empty.

### Tests for User Story 1 (REQUIRED)

- [x] T014 [P] [US1] Add runtime startup test for root route health in apps/frontend/tests/startup-smoke.test.tsx
- [x] T015 [P] [US1] Add shell placeholder visibility test for all required regions in apps/frontend/tests/shell-contract.test.tsx
- [x] T016 [P] [US1] Add empty main-region assertion test in apps/frontend/tests/shell-contract.test.tsx

### Implementation for User Story 1

- [x] T017 [P] [US1] Create top navigation placeholder adapter in apps/frontend/src/furniture/placeholders/top-navigation-placeholder.tsx
- [x] T018 [P] [US1] Create secondary navigation placeholder adapter in apps/frontend/src/furniture/placeholders/secondary-navigation-placeholder.tsx
- [x] T019 [P] [US1] Create footer placeholder adapter in apps/frontend/src/furniture/placeholders/footer-placeholder.tsx
- [x] T020 [P] [US1] Create scripts and analytics placeholder adapter in apps/frontend/src/furniture/placeholders/scripts-analytics-placeholder.tsx
- [x] T021 [P] [US1] Create ads and subscription placeholder adapter in apps/frontend/src/furniture/placeholders/ads-subscription-placeholder.tsx
- [x] T022 [US1] Wire placeholder adapters into shell composition in apps/frontend/src/shell/app-shell.tsx
- [x] T023 [US1] Integrate app shell into root route rendering in apps/frontend/src/app/page.tsx
- [x] T024 [US1] Verify US1 coverage contribution and baseline tests in apps/frontend/tests/shell-contract.test.tsx

**Checkpoint**: User Story 1 is independently functional and locally verifiable.

---

## Phase 4: User Story 2 - Validate Extensible Furniture Boundaries (Priority: P2)

**Goal**: Furniture adapter boundaries are typed and replaceable without changing root page shell behavior.

**Independent Test**: Replace a placeholder adapter with a contract-compliant stub and confirm render still succeeds; invalid adapter shape is detected by tests/type checks.

### Tests for User Story 2 (REQUIRED)

- [x] T025 [P] [US2] Add adapter contract compliance test cases in apps/frontend/tests/shell-contract.test.tsx
- [x] T026 [P] [US2] Add invalid adapter rejection type test in apps/frontend/tests/shell-contract.test.tsx
- [x] T027 [P] [US2] Add adapter swap render-stability test in apps/frontend/tests/shell-contract.test.tsx

### Implementation for User Story 2

- [x] T028 [P] [US2] Create adapter registry and slot resolution module in apps/frontend/src/furniture/adapters/registry.ts
- [x] T029 [US2] Add contract-compliant adapter mapping helpers in apps/frontend/src/furniture/adapters/slot-adapter-mapper.ts
- [x] T030 [US2] Update shell composition to resolve adapters via registry in apps/frontend/src/shell/app-shell.tsx
- [x] T031 [US2] Add extension usage notes for adapter replacement in specs/015-scaffold-page-furniture/contracts/frontend-shell-contract.md

**Checkpoint**: User Story 2 remains independently testable with contract-driven adapter replacement behavior.

---

## Phase 5: User Story 3 - Confirm Ongoing Frontend Quality Readiness (Priority: P3)

**Goal**: Maintainers can validate startup, shell structure, and quality checks reliably through documented commands.

**Independent Test**: Execute frontend quality and affected checks successfully and follow docs to validate shell startup and visual structure.

### Tests for User Story 3 (REQUIRED)

- [x] T032 [P] [US3] Add quality command contract tests for lint/format/typecheck/test/coverage in apps/frontend/tests/quality-commands.test.ts
- [x] T033 [P] [US3] Add quickstart command consistency tests in apps/frontend/tests/quality-commands.test.ts
- [x] T034 [P] [US3] Add regression test ensuring all five furniture slots remain required in apps/frontend/tests/shell-contract.test.tsx

### Implementation for User Story 3

- [x] T035 [US3] Add process hook stub for environment bootstrap in apps/frontend/src/server/hooks/env-bootstrap.ts
- [x] T036 [P] [US3] Add process hook stub for data bootstrap extension in apps/frontend/src/server/hooks/data-bootstrap.ts
- [x] T037 [P] [US3] Add process hook stub for publish extension in apps/frontend/src/server/hooks/publish-extension.ts
- [x] T038 [US3] Document frontend startup and shell verification in docs/onboarding/monorepo-baseline.md
- [x] T039 [US3] Document local stack and shell validation workflow in docs/runbooks/local-stack-baseline.md
- [x] T040 [US3] Align feature quickstart evidence and verification commands in specs/015-scaffold-page-furniture/quickstart.md

**Checkpoint**: User Story 3 quality readiness and documentation workflow are independently verifiable.

---

## Phase 6: Polish and Cross-Cutting Concerns

**Purpose**: Final consistency, coverage, and verification across all stories.

- [x] T041 [P] Run and fix frontend lint and format checks referenced in apps/frontend/package.json
- [x] T042 [P] Run and fix frontend typecheck and tests referenced in apps/frontend/package.json
- [x] T043 Run affected workspace quality checks referenced in package.json
- [x] T044 Run quickstart validation flow and update execution notes in specs/015-scaffold-page-furniture/quickstart.md
- [x] T045 Verify AGENTS updates are accurate for final frontend tooling/commands in AGENTS.md

---

## Dependencies and Execution Order

### Phase Dependencies

- Setup (Phase 1): No dependencies, can start immediately.
- Foundational (Phase 2): Depends on Setup completion and blocks all user stories.
- User Stories (Phase 3-5): Depend on Foundational completion.
- Polish (Phase 6): Depends on completion of selected user stories.

### User Story Dependencies

- US1 (P1): Starts after Phase 2 and is the MVP baseline.
- US2 (P2): Starts after Phase 2 and depends on US1 shell placeholders existing.
- US3 (P3): Starts after Phase 2 and can proceed in parallel with US2 after US1 shell baseline is stable.

### Dependency Graph

- Phase 1 -> Phase 2 -> US1 -> US2 -> Phase 6
- Phase 1 -> Phase 2 -> US1 -> US3 -> Phase 6

---

## Parallel Execution Opportunities

- Phase 1: T003, T004, and T005 can run in parallel after T001 and T002.
- Phase 2: T008, T009, and T010 can run in parallel after T006 and T007.
- US1: T017 through T021 can run in parallel; tests T014-T016 can run in parallel.
- US2: T025-T027 can run in parallel; T028 can run in parallel with contract tests.
- US3: T032-T034 can run in parallel; T036 and T037 can run in parallel after T035.
- Polish: T041 and T042 can run in parallel before T043.

---

## Parallel Example: User Story 1

- Run T014, T015, and T016 together to establish failing tests for startup, slot presence, and empty-main assertions.
- Run T017, T018, T019, T020, and T021 together to build all placeholder adapters.

## Parallel Example: User Story 2

- Run T025, T026, and T027 together for contract and swap behavior tests.
- Run T028 in parallel while tests are being authored.

## Parallel Example: User Story 3

- Run T032, T033, and T034 together for quality/readiness regression checks.
- Run T036 and T037 together after T035 establishes hook contract pattern.

---

## Implementation Strategy

### MVP First (User Story 1)

1. Complete Phase 1 and Phase 2.
2. Complete Phase 3 (US1).
3. Validate local startup and shell placeholders against US1 independent test.
4. Demo and confirm baseline readiness before continuing.

### Incremental Delivery

1. Deliver US1 baseline shell first.
2. Add US2 adapter extensibility with contract guards.
3. Add US3 quality-readiness hooks and documentation.
4. Finish with Phase 6 cross-cutting validation.

### Parallel Team Strategy

1. One developer completes setup/foundational tasks.
2. After US1 baseline is stable:
   - Developer A focuses on US2 adapter boundaries.
   - Developer B focuses on US3 hooks and docs.
3. Rejoin for Phase 6 quality and final verification.

---

## Notes

- All tasks follow strict checklist format with sequential IDs.
- User story tasks include required US labels and explicit file paths.
- Parallel tasks are marked [P] only when file-level conflicts are avoidable.
- Coverage target is maintained at or above 90% for affected frontend scope.
- Documentation updates are included in the same change as behavior/tooling updates.
