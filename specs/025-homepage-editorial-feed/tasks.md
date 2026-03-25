# Tasks: Home Page Editorial Feed

**Input**: Design documents from `/specs/025-homepage-editorial-feed/`
**Prerequisites**: plan.md (required), spec.md (required for user stories), research.md, data-model.md, contracts/

**Tests**: Test tasks are REQUIRED. Every user story and foundational component MUST include automated test coverage sufficient to maintain >= 90% coverage in affected projects. Before any commit and before any AI agent stops work, the full repository suite MUST pass via `pnpm exec nx run-many -t test --all`; targeted tests alone are never sufficient for this stop gate. Before any commit, monorepo coverage MUST pass via `pnpm exec nx run-many -t coverage --all` with >= 90% thresholds in every project.

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3)
- Include exact file paths in descriptions

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Prepare reusable fixtures and test scaffolding for editorial feed delivery.

- [x] T001 Create frontend editorial feed fixture builders in `apps/frontend/tests/fixtures/editorial-feed-fixtures.ts`
- [x] T002 [P] Extend backend discovery fixture rows for editorial metadata in `apps/backend/tests/fixtures/dataset_discovery_repository.py`
- [x] T003 [P] Add shared test utility helpers for recent-feed ordering and action assertions in `apps/frontend/tests/test-utils.ts`
- [x] T004 [P] Add feature-level implementation checklist notes in `specs/025-homepage-editorial-feed/quickstart.md`

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Establish cross-layer contracts and mappings required by all user stories.

**⚠️ CRITICAL**: No user story work can begin until this phase is complete.

- [x] T005 [P] Add backend contract test for editorial recent item payload shape in `apps/backend/tests/contract/test_homepage_editorial_feed_contract.py`
- [x] T006 [P] Add frontend discovery client/type parsing test for editorial recent payload in `apps/frontend/tests/discovery-client.test.ts`
- [x] T007 Update recent-updates response contract models for editorial item fields in `apps/backend/src/contract/query/dataset_recent_updates_query.py`
- [x] T008 Implement backend service projection for editorial row fields and defaults in `apps/backend/src/query/dataset_discovery_service.py`
- [x] T009 Update persisted repository projection to surface editorial optional text fields in `apps/backend/src/query/dataset_discovery_persisted_repository.py`
- [x] T010 Update HTTP runtime contract coverage for editorial recent payloads in `apps/backend/tests/contract/test_http_runtime_persisted_discovery_endpoints.py`
- [x] T011 Update frontend recent item and action link type definitions in `apps/frontend/src/lib/api/discovery-types.ts`
- [x] T012 Update frontend recent endpoint mapping/parsing logic in `apps/frontend/src/lib/api/discovery-client.ts`

**Checkpoint**: Contract/model foundations are complete and user stories can now be implemented independently.

---

## Phase 3: User Story 1 - Read Editorial Updates Quickly (Priority: P1) 🎯 MVP

**Goal**: Render an editorial recent-updates list with recency cue, scan-friendly hierarchy, and newest-first ordering.

**Independent Test**: Open homepage with recent data and verify heading, recency label, ordered rows, and editorial metadata hierarchy.

### Tests for User Story 1 (REQUIRED) ⚠️

- [x] T013 [P] [US1] Add component tests for heading, sort cue, and row hierarchy in `apps/frontend/tests/RecentUpdatesFeed.test.tsx`
- [x] T014 [P] [US1] Add homepage render test for editorial recent section ordering in `apps/frontend/tests/home-page.test.tsx`
- [x] T015 [P] [US1] Add backend recency-order regression test for recent updates in `apps/backend/tests/contract/test_dataset_recent_updates_contract.py`

### Implementation for User Story 1

- [x] T016 [US1] Replace card-based recent feed markup with editorial row markup in `apps/frontend/src/components/discovery/RecentUpdatesFeed.tsx`
- [x] T017 [US1] Add editorial feed section and row hierarchy styles in `apps/frontend/src/app/globals.css`
- [x] T018 [US1] Update homepage feed composition for editorial row rendering in `apps/frontend/src/app/page.tsx`
- [x] T019 [US1] Remove obsolete recent-card coupling from recent feed usage in `apps/frontend/src/components/discovery/DatasetCard.tsx`
- [x] T020 [US1] Validate US1 targeted coverage impact in `apps/frontend/tests/RecentUpdatesFeed.test.tsx`

**Checkpoint**: User Story 1 is independently functional and shippable as MVP.

---

## Phase 4: User Story 2 - Use Feed Actions to Continue Exploration (Priority: P2)

**Goal**: Provide deterministic View Table and Download CSV actions for each editorial row.

**Independent Test**: Verify both action labels exist per row and each action navigates to the expected destination.

### Tests for User Story 2 (REQUIRED) ⚠️

- [x] T021 [P] [US2] Add frontend action-label and href assertions for editorial rows in `apps/frontend/tests/RecentUpdatesFeed.test.tsx`
- [x] T022 [P] [US2] Add backend contract/runtime tests for action link generation in `apps/backend/tests/contract/test_homepage_editorial_feed_contract.py`
- [x] T023 [P] [US2] Add homepage integration assertions for row action presence in `apps/frontend/tests/home-page.test.tsx`

### Implementation for User Story 2

- [x] T024 [US2] Generate per-row view and csv action destinations in recent payload service logic in `apps/backend/src/query/dataset_discovery_service.py`
- [x] T025 [US2] Extend frontend discovery recent types with action link fields in `apps/frontend/src/lib/api/discovery-types.ts`
- [x] T026 [US2] Render View Table and Download CSV links in editorial rows in `apps/frontend/src/components/discovery/RecentUpdatesFeed.tsx`
- [x] T027 [US2] Style editorial feed action links for consistent affordance in `apps/frontend/src/app/globals.css`
- [x] T028 [US2] Validate US2 targeted coverage impact in `apps/frontend/tests/RecentUpdatesFeed.test.tsx`

**Checkpoint**: User Stories 1 and 2 both work independently.

---

## Phase 5: User Story 3 - Keep Feed Legible Across Themes and Screens (Priority: P3)

**Goal**: Ensure editorial feed remains readable and stable in light/dark modes, mobile layouts, and fallback states.

**Independent Test**: Validate theme-safe readability, responsive row reflow, and stable behavior for empty/partial/failure feed states.

### Tests for User Story 3 (REQUIRED) ⚠️

- [x] T029 [P] [US3] Add theme/readability structure assertions for editorial rows in `apps/frontend/tests/RecentUpdatesFeed.test.tsx`
- [x] T030 [P] [US3] Add mobile layout and no-overlap assertions for homepage feed region in `apps/frontend/tests/home-page.test.tsx`
- [x] T031 [P] [US3] Add partial-data, empty-state, and fallback rendering tests in `apps/frontend/tests/RecentUpdatesFeed.test.tsx`

### Implementation for User Story 3

- [x] T032 [US3] Implement responsive and theme-token editorial feed styling in `apps/frontend/src/app/globals.css`
- [x] T033 [US3] Implement partial-data-safe row rendering and explicit empty state in `apps/frontend/src/components/discovery/RecentUpdatesFeed.tsx`
- [x] T034 [US3] Decouple recent-feed failure from full homepage failure state in `apps/frontend/src/app/page.tsx`
- [x] T035 [US3] Harden backend fallback projection for optional editorial fields in `apps/backend/src/query/dataset_discovery_service.py`
- [x] T036 [US3] Validate US3 targeted coverage impact in `apps/frontend/tests/RecentUpdatesFeed.test.tsx`

**Checkpoint**: All user stories are independently functional and testable.

---

## Phase 6: Polish & Cross-Cutting Concerns

**Purpose**: Finalize documentation, validation flow, and required quality gates.

- [x] T037 [P] Sync contract examples with implemented payload shape in `specs/025-homepage-editorial-feed/contracts/homepage-editorial-feed-contract.md`
- [x] T038 [P] Update manual validation and runbook steps in `specs/025-homepage-editorial-feed/quickstart.md`
- [x] T039 Run full monorepo test stop gate and record results in `specs/025-homepage-editorial-feed/quickstart.md`
- [x] T040 Run full monorepo coverage stop gate and record results in `specs/025-homepage-editorial-feed/quickstart.md`
- [x] T041 [P] Update changed workflow/tooling notes in `AGENTS.md`

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies; can start immediately.
- **Foundational (Phase 2)**: Depends on Setup completion and blocks all user stories.
- **User Story Phases (Phase 3-5)**: Depend on Foundational completion.
- **Polish (Phase 6)**: Depends on completion of all desired user stories.

### User Story Dependencies

- **US1 (P1)**: Starts after Phase 2; no dependency on US2/US3.
- **US2 (P2)**: Starts after Phase 2; depends on foundational action-link contract fields but remains independently testable from US1 UI polish.
- **US3 (P3)**: Starts after Phase 2; can integrate with US1/US2 outputs while preserving independent fallback/readability validation.

### Within Each User Story

- Tests first and failing before implementation changes.
- Contract/type updates before rendering changes.
- Rendering and style updates before final integration checks.
- Story-level coverage validation before checkpoint completion.

### Dependency Graph

- Phase 1 -> Phase 2 -> {US1, US2, US3} -> Phase 6
- Recommended completion order: US1 (MVP) -> US2 -> US3

### Parallel Opportunities

- Phase 1: T002, T003, T004 can run in parallel after T001.
- Phase 2: T005 and T006 can run in parallel; T010 and T012 can run after their corresponding contract/type updates.
- US1: T013, T014, T015 can run in parallel.
- US2: T021, T022, T023 can run in parallel.
- US3: T029, T030, T031 can run in parallel.
- Phase 6: T037, T038, T041 can run in parallel before final gate tasks T039 and T040.

---

## Parallel Example: User Story 1

```bash
# Run US1 tests in parallel workstreams:
Task: "T013 [US1] Add component tests in apps/frontend/tests/RecentUpdatesFeed.test.tsx"
Task: "T014 [US1] Add homepage render test in apps/frontend/tests/home-page.test.tsx"
Task: "T015 [US1] Add backend ordering regression test in apps/backend/tests/contract/test_dataset_recent_updates_contract.py"

# Then implement independent files in parallel:
Task: "T016 [US1] Update apps/frontend/src/components/discovery/RecentUpdatesFeed.tsx"
Task: "T017 [US1] Update apps/frontend/src/app/globals.css"
```

## Parallel Example: User Story 2

```bash
Task: "T021 [US2] Add frontend action tests in apps/frontend/tests/RecentUpdatesFeed.test.tsx"
Task: "T022 [US2] Add backend action-link contract test in apps/backend/tests/contract/test_homepage_editorial_feed_contract.py"
Task: "T023 [US2] Add homepage action presence test in apps/frontend/tests/home-page.test.tsx"
```

## Parallel Example: User Story 3

```bash
Task: "T029 [US3] Add theme assertions in apps/frontend/tests/RecentUpdatesFeed.test.tsx"
Task: "T030 [US3] Add mobile layout assertions in apps/frontend/tests/home-page.test.tsx"
Task: "T031 [US3] Add fallback-state tests in apps/frontend/tests/RecentUpdatesFeed.test.tsx"
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1 Setup.
2. Complete Phase 2 Foundational contracts/types.
3. Complete Phase 3 (US1) and validate independent test criteria.
4. Demo or ship MVP editorial feed scan experience.

### Incremental Delivery

1. Deliver US1 for editorial readability and recency comprehension.
2. Deliver US2 for actionable continuation workflows.
3. Deliver US3 for full responsive/theme/fallback resilience.
4. Complete Phase 6 quality gates and documentation sync.

### Parallel Team Strategy

1. One engineer completes foundational backend contract/service tasks.
2. One engineer drives frontend US1/US3 rendering and styling tasks.
3. One engineer handles US2 action-link contract wiring and integration checks.
4. Converge for Phase 6 full-suite and coverage stop gates.

---

## Notes

- [P] tasks indicate separate files and no dependency on incomplete non-parallel tasks.
- [US1]/[US2]/[US3] labels maintain story traceability and independent validation.
- Keep coverage >= 90% in each affected project throughout implementation.
- Before any commit and before agent handoff/stop, run `pnpm exec nx run-many -t test --all`.
- Before any commit, run `pnpm exec nx run-many -t coverage --all`.
- Update relevant documentation in the same change as behavior updates.
