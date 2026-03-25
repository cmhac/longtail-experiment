# Tasks: Unified Search Page Experience

**Input**: Design documents from /specs/030-unified-search-page/
**Prerequisites**: plan.md (required), spec.md (required for user stories), research.md, data-model.md, contracts/, quickstart.md

**Tests**: Test tasks are REQUIRED. Every user story and foundational component MUST include automated test coverage sufficient to maintain >= 90% coverage in affected projects. Before any commit and before any AI agent stops work, the full repository suite MUST pass via `pnpm exec nx run-many -t test --all`; targeted tests alone are never sufficient for this stop gate. Before any commit, monorepo coverage MUST pass via `pnpm exec nx run-many -t coverage --all` with >= 90% thresholds in every project.

**Organization**: Tasks are grouped by user story so each story can be implemented and validated independently.

## Format: [ID] [P?] [Story] Description

- [P]: Can run in parallel (different files, no dependencies)
- [Story]: Which user story this belongs to (US1, US2, US3)
- Include exact file paths in descriptions

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Prepare search unification scaffolding and baseline validation coverage.

- [x] T001 Audit current search flow wiring in apps/frontend/src/app/page.tsx, apps/frontend/src/components/discovery/DatasetSearchBox.tsx, and apps/frontend/src/shell/site-header.tsx
- [x] T002 Create feature validation scaffold in specs/030-unified-search-page/quickstart.md
- [x] T003 [P] Add dedicated search page test scaffold in apps/frontend/tests/search-page.test.tsx
- [x] T004 [P] Add reusable search surface contract test scaffold in apps/frontend/tests/search-surface-contract.test.tsx
- [x] T005 [P] Add navbar search interaction regression test scaffold in apps/frontend/tests/navbar-interactions.test.tsx

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Establish shared search primitives and route/query helpers used by all stories.

**⚠️ CRITICAL**: No user story work can begin until this phase is complete.

- [x] T006 Create shared search route/query utility helpers in apps/frontend/src/components/discovery/search-route-utils.ts
- [x] T007 [P] Extract shared search surface props and state types in apps/frontend/src/components/discovery/search-surface-types.ts
- [x] T008 [P] Refactor query/suggestion handling into reusable hook in apps/frontend/src/components/discovery/useUnifiedSearchSurface.ts
- [x] T009 Create dedicated search route shell scaffold in apps/frontend/src/app/search/page.tsx
- [x] T010 [P] Add foundational route/query utility unit coverage in apps/frontend/tests/DatasetSearchBox.interaction.test.tsx
- [x] T011 [P] Add foundational shared-surface behavior assertions in apps/frontend/tests/search-surface-contract.test.tsx
- [x] T012 Reconcile foundational behavior guarantees in specs/030-unified-search-page/contracts/unified-search-page-contract.md

**Checkpoint**: Shared search foundation is complete and user stories can proceed independently.

---

## Phase 3: User Story 1 - Search From a Dedicated Results Page (Priority: P1) 🎯 MVP

**Goal**: Route homepage search submissions to a dedicated search page that keeps query input visible above results for refinement.

**Independent Test**: Submit a non-empty query from homepage and confirm navigation to /search with centered search surface and results list; refine query on /search and confirm updated results.

### Tests for User Story 1 (REQUIRED) ⚠️

- [x] T013 [P] [US1] Add homepage redirect-on-submit assertions in apps/frontend/tests/home-page.test.tsx
- [x] T014 [P] [US1] Add dedicated route render-state coverage (loaded/empty/error) in apps/frontend/tests/search-page.test.tsx
- [x] T015 [P] [US1] Add route-query synchronization assertions in apps/frontend/tests/search-surface-contract.test.tsx
- [x] T016 [P] [US1] Add dedicated-page quickstart validation notes in specs/030-unified-search-page/quickstart.md

### Implementation for User Story 1

- [x] T017 [US1] Create dedicated search page server composition using existing discovery client in apps/frontend/src/app/search/page.tsx
- [x] T018 [US1] Update homepage to remove inline result execution and keep search-entry-only behavior in apps/frontend/src/app/page.tsx
- [x] T019 [US1] Extend DatasetSearchBox to support route-targeted submit mode in apps/frontend/src/components/discovery/DatasetSearchBox.tsx
- [x] T020 [US1] Reuse existing results presentation hierarchy for dedicated route in apps/frontend/src/components/discovery/DatasetSearchResults.tsx
- [x] T021 [US1] Reuse existing empty/error fallbacks for dedicated route in apps/frontend/src/components/discovery/EmptyState.tsx and apps/frontend/src/components/discovery/ErrorState.tsx
- [x] T022 [US1] Ensure search summary behavior remains unchanged for dedicated route in apps/frontend/src/lib/api/discovery-client.ts and apps/frontend/src/app/search/page.tsx
- [x] T023 [US1] Verify US1 focused checks in apps/frontend/tests/home-page.test.tsx, apps/frontend/tests/search-page.test.tsx, and apps/frontend/tests/search-surface-contract.test.tsx

**Checkpoint**: User Story 1 is independently functional and shippable as MVP.

---

## Phase 4: User Story 2 - Use Consistent Search Behavior Across Entry Points (Priority: P2)

**Goal**: Ensure homepage and navbar entry points use one shared behavior contract for typing, suggestions, submit, and refinement outcomes.

**Independent Test**: Submit equivalent queries from homepage and navbar search controls and confirm matching route destination, query persistence, and result behavior.

### Tests for User Story 2 (REQUIRED) ⚠️

- [x] T024 [P] [US2] Add cross-entry behavior parity tests in apps/frontend/tests/search-surface-contract.test.tsx
- [x] T025 [P] [US2] Add suggestion continuity tests for homepage and navbar entry points in apps/frontend/tests/DatasetSearchBox.interaction.test.tsx
- [x] T026 [P] [US2] Add dedicated route refinement parity tests in apps/frontend/tests/search-page.test.tsx

### Implementation for User Story 2

- [x] T027 [US2] Implement unified submit-to-route helper consumption across entry points in apps/frontend/src/components/discovery/DatasetSearchBox.tsx and apps/frontend/src/components/discovery/search-route-utils.ts
- [x] T028 [US2] Implement reusable shared search surface wrapper for homepage and dedicated route in apps/frontend/src/components/discovery/UnifiedSearchSurface.tsx
- [x] T029 [US2] Integrate UnifiedSearchSurface into homepage and dedicated route in apps/frontend/src/app/page.tsx and apps/frontend/src/app/search/page.tsx
- [x] T030 [US2] Preserve likely-match suggestion behavior through shared hook integration in apps/frontend/src/components/discovery/useUnifiedSearchSurface.ts
- [x] T031 [US2] Verify summary/relevance contract parity across entry points in specs/030-unified-search-page/contracts/unified-search-page-contract.md and apps/frontend/src/lib/api/discovery-client.ts
- [x] T032 [US2] Verify US2 focused checks in apps/frontend/tests/search-surface-contract.test.tsx, apps/frontend/tests/search-page.test.tsx, and apps/frontend/tests/DatasetSearchBox.interaction.test.tsx

**Checkpoint**: User Stories 1 and 2 are independently functional.

---

## Phase 5: User Story 3 - Access Search Quickly From the Navbar (Priority: P3)

**Goal**: Replace icon-only navbar search control with compact expandable search input that submits with the same behavior as homepage search.

**Independent Test**: Activate navbar search control, confirm expanded input-ready state, submit query, and verify navigation to dedicated search route with query populated.

### Tests for User Story 3 (REQUIRED) ⚠️

- [x] T033 [P] [US3] Add compact-to-expanded navbar search behavior assertions in apps/frontend/tests/navbar-interactions.test.tsx
- [x] T034 [P] [US3] Add navbar submit-to-route assertions in apps/frontend/tests/navbar-interactions.test.tsx
- [x] T035 [P] [US3] Add responsive non-overlap assertions for navbar search control in apps/frontend/tests/shell-structure-contract.test.tsx

### Implementation for User Story 3

- [x] T036 [US3] Replace icon-only navbar search button with compact-expand control in apps/frontend/src/shell/site-header.tsx
- [x] T037 [US3] Add navbar search control style tokens/classes for compact and expanded states in apps/frontend/src/theme/monochrome-theme.ts and apps/frontend/src/app/globals.css
- [x] T038 [US3] Wire navbar expanded search submit through shared unified surface contract in apps/frontend/src/shell/site-header.tsx and apps/frontend/src/components/discovery/UnifiedSearchSurface.tsx
- [x] T039 [US3] Keep navbar control accessibility semantics (focus, labels, dismissal) in apps/frontend/src/shell/site-header.tsx
- [x] T040 [US3] Verify US3 focused checks in apps/frontend/tests/navbar-interactions.test.tsx and apps/frontend/tests/shell-structure-contract.test.tsx

**Checkpoint**: All user stories are independently functional and testable.

---

## Phase 6: Polish & Cross-Cutting Concerns

**Purpose**: Finalize docs and run mandatory quality gates.

- [x] T041 [P] Reconcile final behavior details in specs/030-unified-search-page/contracts/unified-search-page-contract.md
- [x] T042 [P] Update final verification record and command outputs in specs/030-unified-search-page/quickstart.md
- [x] T043 [P] Update AGENTS.md only if workflow/tooling/stack details changed beyond existing 030 entries in AGENTS.md
- [x] T044 Run focused frontend verification commands for unified search in apps/frontend/tests/home-page.test.tsx, apps/frontend/tests/search-page.test.tsx, apps/frontend/tests/search-surface-contract.test.tsx, and apps/frontend/tests/navbar-interactions.test.tsx
- [x] T045 Run `pnpm --dir apps/frontend typecheck` and `pnpm --dir apps/frontend exec biome check .` and record outcomes in specs/030-unified-search-page/quickstart.md
- [x] T046 Run manual validation flow from specs/030-unified-search-page/quickstart.md and record observations in specs/030-unified-search-page/quickstart.md
- [x] T047 Run `pnpm exec nx run-many -t test --all` and record pass result in specs/030-unified-search-page/quickstart.md
- [x] T048 Run `pnpm exec nx run-many -t coverage --all` and record pass result in specs/030-unified-search-page/quickstart.md

---

## Dependencies & Execution Order

### Phase Dependencies

- Phase 1 (Setup): No dependencies.
- Phase 2 (Foundational): Depends on Phase 1 and blocks all user stories.
- Phase 3 (US1): Depends on Phase 2 completion.
- Phase 4 (US2): Depends on Phase 2 completion and can proceed after US1 when shared components are available.
- Phase 5 (US3): Depends on Phase 2 completion and can proceed after US2 shared behavior is in place.
- Phase 6 (Polish): Depends on all selected user stories being complete.

### User Story Dependencies

- US1 (P1): No dependency on other user stories; establishes dedicated search route and route-driven submit flow.
- US2 (P2): Depends on foundational shared-surface primitives and builds parity behavior across homepage/navbar entry points.
- US3 (P3): Depends on shared-surface behavior from US2 to ensure navbar expand/submit behavior matches homepage behavior.

### Within Each User Story

- Write and run story tests first; verify failing expectations before implementation.
- Implement shared utilities/components before route/shell integration tasks.
- Validate story checkpoint before progressing.

### Dependency Graph

- Phase 1 -> Phase 2 -> US1 -> US2 -> US3 -> Phase 6

### Parallel Opportunities

- Setup: T003, T004, and T005 can run in parallel.
- Foundational: T007, T008, T010, and T011 can run in parallel.
- US1: T013, T014, T015, and T016 can run in parallel.
- US2: T024, T025, and T026 can run in parallel.
- US3: T033, T034, and T035 can run in parallel.
- Polish: T041, T042, and T043 can run in parallel.

---

## Parallel Example: User Story 1

```bash
Task: "T013 [US1] Add homepage redirect-on-submit assertions in apps/frontend/tests/home-page.test.tsx"
Task: "T014 [US1] Add dedicated route render-state coverage in apps/frontend/tests/search-page.test.tsx"
Task: "T015 [US1] Add route-query synchronization assertions in apps/frontend/tests/search-surface-contract.test.tsx"
```

## Parallel Example: User Story 2

```bash
Task: "T024 [US2] Add cross-entry behavior parity tests in apps/frontend/tests/search-surface-contract.test.tsx"
Task: "T025 [US2] Add suggestion continuity tests in apps/frontend/tests/DatasetSearchBox.interaction.test.tsx"
Task: "T026 [US2] Add dedicated route refinement parity tests in apps/frontend/tests/search-page.test.tsx"
```

## Parallel Example: User Story 3

```bash
Task: "T033 [US3] Add compact-to-expanded behavior assertions in apps/frontend/tests/navbar-interactions.test.tsx"
Task: "T034 [US3] Add navbar submit-to-route assertions in apps/frontend/tests/navbar-interactions.test.tsx"
Task: "T035 [US3] Add responsive non-overlap assertions in apps/frontend/tests/shell-structure-contract.test.tsx"
```

---

## Implementation Strategy

### MVP First (User Story 1 only)

1. Complete Phase 1 and Phase 2.
2. Complete Phase 3 (US1).
3. Validate US1 independently and demo dedicated route search flow from homepage submit.

### Incremental Delivery

1. Deliver US1 for dedicated route-based search execution.
2. Deliver US2 for cross-entry behavior parity.
3. Deliver US3 for compact expandable navbar search access.
4. Complete Phase 6 with stop-gate execution and final documentation sync.

### Parallel Team Strategy

1. One engineer implements shared search primitives and route/query helpers.
2. One engineer implements dedicated route composition and homepage integration.
3. One engineer implements navbar expanded search behavior and accessibility.
4. Converge for regression tests, manual flow validation, and mandatory monorepo gates.

---

## Notes

- All tasks use required checklist format with sequential IDs and explicit file paths.
- [P] markers indicate tasks that can run concurrently with minimal coupling.
- Coverage must remain >= 90% in all affected projects.
- Before commit and before agent handoff/end: run `pnpm exec nx run-many -t test --all`.
- Before commit: run `pnpm exec nx run-many -t coverage --all`.
- Relevant docs must be updated in the same change as behavior updates.
