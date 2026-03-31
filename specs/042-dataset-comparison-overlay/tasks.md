# Tasks: Dataset Comparison Overlay

**Input**: Design documents from /specs/042-dataset-comparison-overlay/
**Prerequisites**: plan.md (required), spec.md (required for user stories), research.md, data-model.md, contracts/

**Tests**: Test tasks are REQUIRED. Every user story and foundational component MUST include automated test coverage sufficient to maintain >= 90% coverage in affected projects. Before any commit and before any AI agent stops work, the full repository suite MUST pass via pnpm exec nx run-many -t test --all; targeted tests alone are never sufficient for this stop gate. Before any commit, monorepo coverage MUST pass via pnpm exec nx run-many -t coverage --all with >= 90% thresholds in every project.

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: [ID] [P?] [Story] Description

- [P]: Can run in parallel (different files, no dependencies)
- [Story]: Which user story this task belongs to (for example US1, US2, US3)
- Include exact file paths in descriptions

## Path Conventions

- Frontend app: apps/frontend/src/, apps/frontend/tests/
- Backend app: apps/backend/src/, apps/backend/tests/
- Feature docs: specs/042-dataset-comparison-overlay/

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Establish task scaffolding, fixtures, and verification surfaces for implementation.

- [ ] T001 Confirm feature artifacts are present in specs/042-dataset-comparison-overlay/spec.md, specs/042-dataset-comparison-overlay/plan.md, specs/042-dataset-comparison-overlay/research.md, and specs/042-dataset-comparison-overlay/contracts/comparison-overlay-contract.md
- [ ] T002 [P] Add comparison-overlay fixture builders for unit compatibility and mixed-date cases in apps/frontend/tests/fixtures/dataset-detail-fixtures.ts
- [ ] T003 [P] Add comparison-overlay quick verification checklist section in specs/042-dataset-comparison-overlay/quickstart.md
- [ ] T004 [P] Add placeholder test describe blocks for comparison flows in apps/frontend/tests/detail-page.test.tsx, apps/frontend/tests/ObservationsChart.test.tsx, and apps/frontend/tests/dataset-detail-view-model.test.ts

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core state and projection primitives required before story implementation.

**CRITICAL**: No user story work can begin until this phase is complete.

- [ ] T005 Define comparison state/types and persistence schema in apps/frontend/src/lib/api/discovery-types.ts
- [ ] T006 Create single-source max-selection constant and shared storage keys in apps/frontend/src/components/discovery/comparison-state.ts
- [ ] T007 [P] Implement comparison selection store helpers (add/remove/reset/validate uniqueness) in apps/frontend/src/components/discovery/comparison-state.ts
- [ ] T008 [P] Implement corrupted-state detection and fail-hard state result helpers in apps/frontend/src/components/discovery/comparison-state.ts
- [ ] T009 Implement shared multi-series timeline projection helpers (union dates + gaps) in apps/frontend/src/components/discovery/dataset-detail-view-model.ts
- [ ] T010 Implement fixed-baseline fallback resolver (nearest prior else nearest any) in apps/frontend/src/components/discovery/dataset-detail-view-model.ts
- [ ] T011 Add foundational unit tests for constants, persistence validation, and projection rules in apps/frontend/tests/dataset-detail-view-model.test.ts
- [ ] T012 Add comparison indicator shell extension points (between search and profile controls) in apps/frontend/src/shell/site-header.tsx

**Checkpoint**: Foundation ready - user story implementation can now begin.

---

## Phase 3: User Story 1 - Build A Comparison Set (Priority: P1) 🎯 MVP

**Goal**: Allow users to add/remove datasets into a persisted comparison set and keep top-nav count synchronized.

**Independent Test**: Open multiple dataset detail pages, add/remove datasets, observe nav count updates, refresh browser, and verify selection persists with max-cap enforcement.

### Tests for User Story 1 (REQUIRED)

- [ ] T013 [P] [US1] Add detail-page tests for add/remove comparison action replacing CSV action in apps/frontend/tests/detail-page.test.tsx
- [ ] T014 [P] [US1] Add shell header tests for comparison count indicator visibility and updates in apps/frontend/tests/SiteHeader.test.tsx
- [ ] T015 [P] [US1] Add persistence tests for reload continuity and corrupted-state block behavior in apps/frontend/tests/detail-page.test.tsx
- [ ] T016 [P] [US1] Add max-cap (5) enforcement tests and unchanged-selection assertions in apps/frontend/tests/detail-page.test.tsx

### Implementation for User Story 1

- [ ] T017 [US1] Replace DatasetDetailHeader export action with add/remove comparison action wiring in apps/frontend/src/app/datasets/[id]/page.tsx and apps/frontend/src/components/discovery/DatasetDetailHeader.tsx
- [ ] T018 [US1] Implement comparison selection action UI and status messaging on detail page in apps/frontend/src/components/discovery/DatasetDetailAnalysis.tsx
- [ ] T019 [US1] Implement top-nav comparison count indicator between search and profile controls in apps/frontend/src/shell/site-header.tsx
- [ ] T020 [US1] Persist and restore comparison selection + chart settings in browser-local state via apps/frontend/src/components/discovery/comparison-state.ts
- [ ] T021 [US1] Implement corrupted-state fail-hard block + manual reset entry point in apps/frontend/src/components/discovery/comparison-state.ts and apps/frontend/src/shell/site-header.tsx
- [ ] T022 [US1] Enforce max-selection constant and rejection messaging in apps/frontend/src/components/discovery/comparison-state.ts and apps/frontend/src/components/discovery/DatasetDetailAnalysis.tsx
- [ ] T023 [US1] Verify US1 targeted tests in apps/frontend/tests/detail-page.test.tsx and apps/frontend/tests/SiteHeader.test.tsx
- [ ] T024 [US1] Manually verify add/remove, count sync, persistence, max-cap, and fail-hard reset flows using specs/042-dataset-comparison-overlay/quickstart.md
- [ ] T025 [US1] Run full gates before US1 commit using specs/042-dataset-comparison-overlay/quickstart.md

**Checkpoint**: User Story 1 is independently functional and testable (MVP).

---

## Phase 4: User Story 2 - Compare Trends On A Dedicated Page (Priority: P2)

**Goal**: Provide a dedicated comparison page with full-width chart and in-page selection management, without metadata rail or observation table.

**Independent Test**: With >=2 selected datasets, open comparison page from nav icon and verify full-width chart rendering; with <2, verify instructional empty state; remove datasets from page and verify count sync.

### Tests for User Story 2 (REQUIRED)

- [ ] T026 [P] [US2] Add route/page tests for comparison page rendering and empty eligibility state in apps/frontend/tests/comparison-page.test.tsx
- [ ] T027 [P] [US2] Add tests ensuring no metadata rail and no observation table on comparison page in apps/frontend/tests/comparison-page.test.tsx
- [ ] T028 [P] [US2] Add tests for in-page remove actions and nav count synchronization in apps/frontend/tests/comparison-page.test.tsx
- [ ] T029 [P] [US2] Add navigation tests for clicking top-nav comparison indicator to open comparison page in apps/frontend/tests/SiteHeader.test.tsx

### Implementation for User Story 2

- [ ] T030 [US2] Create dedicated comparison page route and layout shell in apps/frontend/src/app/comparison/page.tsx
- [ ] T031 [US2] Implement comparison-page selected-dataset list with remove actions in apps/frontend/src/components/discovery/ComparisonSelectionList.tsx
- [ ] T032 [US2] Implement minimum-selection eligibility flow (<2) and instructional empty state in apps/frontend/src/app/comparison/page.tsx
- [ ] T033 [US2] Wire top-nav comparison indicator navigation to comparison route in apps/frontend/src/shell/site-header.tsx
- [ ] T034 [US2] Render comparison page chart area as full-width and exclude detail metadata rail + observations table in apps/frontend/src/app/comparison/page.tsx
- [ ] T035 [US2] Reuse/extend chart container composition for comparison mode in apps/frontend/src/components/discovery/ComparisonChartPanel.tsx
- [ ] T036 [US2] Verify US2 targeted tests in apps/frontend/tests/comparison-page.test.tsx and apps/frontend/tests/SiteHeader.test.tsx
- [ ] T037 [US2] Manually verify dedicated comparison-page UX and in-page removal behavior using specs/042-dataset-comparison-overlay/quickstart.md
- [ ] T038 [US2] Run full gates before US2 commit using specs/042-dataset-comparison-overlay/quickstart.md

**Checkpoint**: User Stories 1 and 2 both work independently.

---

## Phase 5: User Story 3 - Safe Mode Handling For Unit Compatibility (Priority: P3)

**Goal**: Enforce compatibility-aware observed/relative modes, shared baseline behavior, union timeline gaps, and stable per-selection color mapping.

**Independent Test**: Build mixed-unit and matched-unit selections, confirm auto-switch/disable behavior, confirm shared baseline rules, and verify union-date chart with gaps and stable in-selection colors.

### Tests for User Story 3 (REQUIRED)

- [ ] T039 [P] [US3] Add compatibility-mode tests for observed/relative gating and auto-switch messaging in apps/frontend/tests/ObservationsChart.test.tsx
- [ ] T040 [P] [US3] Add tests for disabling observed mode while selection is unit-incompatible in apps/frontend/tests/ObservationsChart.test.tsx
- [ ] T041 [P] [US3] Add multi-series union timeline + gap rendering tests in apps/frontend/tests/dataset-detail-view-model.test.ts
- [ ] T042 [P] [US3] Add fixed-baseline fallback tests (nearest prior else nearest any) in apps/frontend/tests/dataset-detail-view-model.test.ts
- [ ] T043 [P] [US3] Add stable per-selection color mapping tests in apps/frontend/tests/ObservationsChart.test.tsx

### Implementation for User Story 3

- [ ] T044 [US3] Extend ObservationsChart props and rendering to support multi-series overlays in apps/frontend/src/components/discovery/ObservationsChart.tsx
- [ ] T045 [US3] Implement absolute-mode compatibility gate, auto-switch to relative mode, and disabled observed toggle in apps/frontend/src/components/discovery/ObservationsChart.tsx
- [ ] T046 [US3] Implement shared relative baseline controls applied to all compared series in apps/frontend/src/components/discovery/ObservationsChart.tsx and apps/frontend/src/components/discovery/dataset-detail-view-model.ts
- [ ] T047 [US3] Implement union timeline projection with null-gap series points in apps/frontend/src/components/discovery/dataset-detail-view-model.ts
- [ ] T048 [US3] Implement per-series fixed-baseline fallback resolution in apps/frontend/src/components/discovery/dataset-detail-view-model.ts
- [ ] T049 [US3] Implement stable color assignment scoped to current selection in apps/frontend/src/components/discovery/comparison-state.ts and apps/frontend/src/components/discovery/ObservationsChart.tsx
- [ ] T050 [US3] Update comparison page integration to pass multi-series data and shared mode state in apps/frontend/src/app/comparison/page.tsx
- [ ] T051 [US3] Verify US3 targeted tests in apps/frontend/tests/ObservationsChart.test.tsx and apps/frontend/tests/dataset-detail-view-model.test.ts
- [ ] T052 [US3] Manually verify compatibility switching, baseline behavior, and multi-line chart semantics using specs/042-dataset-comparison-overlay/quickstart.md
- [ ] T053 [US3] Run full gates before US3 commit using specs/042-dataset-comparison-overlay/quickstart.md

**Checkpoint**: All user stories are independently functional.

---

## Phase 6: Polish & Cross-Cutting Concerns

**Purpose**: Hardening, docs parity, and full-stack validation.

- [ ] T054 [P] Update feature documentation with implementation outcomes in specs/042-dataset-comparison-overlay/quickstart.md and specs/042-dataset-comparison-overlay/research.md
- [ ] T055 [P] Validate/update contract wording for delivered behavior in specs/042-dataset-comparison-overlay/contracts/comparison-overlay-contract.md
- [ ] T056 [P] Update AGENTS.md only if implementation changes tooling/workflow conventions in AGENTS.md
- [ ] T057 Run local stack restart and browser regression walkthrough per specs/042-dataset-comparison-overlay/quickstart.md
- [ ] T058 Run final mandatory gates: pre-commit run --all-files, pnpm exec nx run-many -t test --all, pnpm exec nx run-many -t coverage --all and record outcomes in specs/042-dataset-comparison-overlay/quickstart.md
- [ ] T059 Create final feature integration commit covering all remaining implementation and docs in specs/042-dataset-comparison-overlay/
- [ ] T060 Validate SC-006 performance target (95% of sampled mode/baseline/add/remove interactions update chart within 1 second for <=5 selections) and record evidence in specs/042-dataset-comparison-overlay/quickstart.md

---

## Dependencies & Execution Order

### Phase Dependencies

- Setup (Phase 1): No dependencies.
- Foundational (Phase 2): Depends on Setup completion and blocks all user stories.
- User Story phases (Phases 3-5): Depend on Foundational completion.
- Polish (Phase 6): Depends on all desired user stories being complete.

### User Story Dependencies

- US1 (P1): Starts after Foundational; establishes the MVP comparison-set flow.
- US2 (P2): Starts after Foundational and benefits from US1 selection/nav state, but remains independently testable with prepared selection state.
- US3 (P3): Starts after Foundational and depends on established selection and comparison page surfaces from US1/US2 for integration validation.

### Within Each User Story

- Tests first and failing (red) before implementation.
- State/data primitives before route integration.
- Route integration before manual verification.
- Full-suite and coverage gates before story checkpoint commit.

---

## Parallel Opportunities

- Setup: T002, T003, T004 can run in parallel.
- Foundational: T007 and T008 can run in parallel; T009 and T010 can run in parallel after T005.
- US1: T013-T016 can run in parallel test-first workflow.
- US2: T026-T029 can run in parallel; T031 and T032 can run in parallel after T030.
- US3: T039-T043 can run in parallel; T047 and T048 can run in parallel after baseline scaffolding.
- Polish: T054, T055, T056 can run in parallel.

### Parallel Example: User Story 1

- [ ] T013 [P] [US1] Add detail-page tests for add/remove comparison action replacing CSV action in apps/frontend/tests/detail-page.test.tsx
- [ ] T014 [P] [US1] Add shell header tests for comparison count indicator visibility and updates in apps/frontend/tests/SiteHeader.test.tsx
- [ ] T015 [P] [US1] Add persistence tests for reload continuity and corrupted-state block behavior in apps/frontend/tests/detail-page.test.tsx

### Parallel Example: User Story 2

- [ ] T026 [P] [US2] Add route/page tests for comparison page rendering and empty eligibility state in apps/frontend/tests/comparison-page.test.tsx
- [ ] T027 [P] [US2] Add tests ensuring no metadata rail and no observation table on comparison page in apps/frontend/tests/comparison-page.test.tsx
- [ ] T029 [P] [US2] Add navigation tests for clicking top-nav comparison indicator to open comparison page in apps/frontend/tests/SiteHeader.test.tsx

### Parallel Example: User Story 3

- [ ] T039 [P] [US3] Add compatibility-mode tests for observed/relative gating and auto-switch messaging in apps/frontend/tests/ObservationsChart.test.tsx
- [ ] T041 [P] [US3] Add multi-series union timeline + gap rendering tests in apps/frontend/tests/dataset-detail-view-model.test.ts
- [ ] T042 [P] [US3] Add fixed-baseline fallback tests (nearest prior else nearest any) in apps/frontend/tests/dataset-detail-view-model.test.ts

---

## Implementation Strategy

### MVP First (US1)

1. Complete Phase 1 and Phase 2.
2. Deliver User Story 1 comparison-set behavior (add/remove, nav count, persistence, cap, fail-hard reset).
3. Validate independently via targeted tests and manual browser checks.
4. Run full gates and commit MVP slice.

### Incremental Delivery

1. Deliver US1 for selection and shared state.
2. Deliver US2 for dedicated comparison page and in-page management.
3. Deliver US3 for compatibility/multi-series chart semantics.
4. Complete Phase 6 polish and final verification.

### Parallel Team Strategy

1. Team completes Setup + Foundational.
2. Then split by story:
   - Developer A: US1
   - Developer B: US2
   - Developer C: US3
3. Rejoin for polish and final full-suite validation.

---

## Notes

- All tasks follow required checklist format with Task ID, optional [P], and [US#] labels only in user story phases.
- Every task description includes a concrete file path.
- Coverage and full-suite stop rules are mandatory at each commit boundary.
- Reuse HeroUI/Tailwind and shared component patterns; avoid route-local duplication when patterns repeat.
