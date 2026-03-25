# Tasks: Homepage Search Bar Experience

**Input**: Design documents from `/Users/hackerc/Projects/longtail-experiment/specs/024-home-search-bar/`
**Prerequisites**: plan.md (required), spec.md (required for user stories), research.md, data-model.md, contracts/, quickstart.md

**Tests**: Test tasks are REQUIRED. Every user story and foundational component MUST include automated test coverage sufficient to maintain >= 90% coverage in affected projects. Before any commit and before any AI agent stops work, the full repository suite MUST pass via `pnpm exec nx run-many -t test --all`; targeted tests alone are never sufficient for this stop gate. Before any commit, monorepo coverage MUST pass via `pnpm exec nx run-many -t coverage --all` with >= 90% thresholds in every project.

**Organization**: Tasks are grouped by user story so each story can be implemented and validated independently.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (US1, US2, US3)
- Include exact file paths in descriptions

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Establish shared homepage-search contract and test scaffolding.

- [x] T001 Create homepage search contract task scaffold and acceptance notes in specs/024-home-search-bar/contracts/homepage-search-contract.md
- [x] T002 [P] Create backend summary contract test scaffold in apps/backend/tests/contract/test_homepage_search_summary_contract.py
- [x] T003 [P] Create backend suggestions contract test scaffold in apps/backend/tests/contract/test_dataset_search_suggestions_contract.py
- [x] T004 [P] Create frontend suggestion interaction test scaffold in apps/frontend/tests/DatasetSearchBox.suggestions.test.tsx

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Build core backend/frontend contract surfaces needed by all stories.

**⚠️ CRITICAL**: No user story work begins until this phase is complete.

- [x] T005 Add search summary and suggestion Pydantic response models in apps/backend/src/contract/query/dataset_search_query.py
- [x] T006 [P] Add backend query entrypoints for summary and likely suggestions in apps/backend/src/query/dataset_search_summary_query.py and apps/backend/src/query/dataset_search_suggestions_query.py
- [x] T007 [P] Extend DatasetDiscoveryService repository requirements and service methods for summary/suggestions in apps/backend/src/query/dataset_discovery_service.py
- [x] T008 Extend persisted and in-memory repositories with summary and trigram-like suggestion methods in apps/backend/src/query/dataset_discovery_persisted_repository.py and apps/backend/tests/fixtures/dataset_discovery_repository.py
- [x] T009 Add frontend API types for summary and suggestion payloads in apps/frontend/src/lib/api/discovery-types.ts
- [x] T010 Extend discovery client fetch helpers for summary and suggestions routes in apps/frontend/src/lib/api/discovery-client.ts

**Checkpoint**: Foundation ready. User story implementation can proceed.

---

## Phase 3: User Story 1 - Discover Search Entry Point (Priority: P1) 🎯 MVP

**Goal**: Render a prominent centered homepage search entry point users can identify immediately.

**Independent Test**: Load home page and verify search input is centered and visually dominant without requiring any suggestion or summary data.

### Tests for User Story 1 (REQUIRED) ⚠️

- [x] T011 [P] [US1] Add homepage hero-centric search surface assertions in apps/frontend/tests/home-page.test.tsx
- [x] T012 [P] [US1] Add CSS/layout contract assertions for centered search surface classes in apps/frontend/tests/shell-structure-contract.test.tsx

### Implementation for User Story 1

- [x] T013 [US1] Refactor homepage composition to dedicated centered hero search section in apps/frontend/src/app/page.tsx
- [x] T014 [P] [US1] Enhance DatasetSearchBox markup with hero-container semantics and stable test ids in apps/frontend/src/components/discovery/DatasetSearchBox.tsx
- [x] T015 [US1] Implement centered prominent search surface styling for desktop/mobile in apps/frontend/src/app/globals.css
- [x] T016 [US1] Ensure baseline keyboard/focus behavior remains intact for centered search input in apps/frontend/src/components/discovery/DatasetSearchBox.tsx
- [x] T017 [US1] Update UX validation steps for centered search behavior in specs/024-home-search-bar/quickstart.md

**Checkpoint**: User Story 1 is independently testable and delivers MVP centered search entry.

---

## Phase 4: User Story 2 - Understand Search Scope at a Glance (Priority: P2)

**Goal**: Render runtime aggregate counts under the search input using the required sentence pattern.

**Independent Test**: Load home page and verify "Searching X active datasets from Y sources." renders with real values from backend summary response.

### Tests for User Story 2 (REQUIRED) ⚠️

- [x] T018 [P] [US2] Add backend summary contract tests for counts and fallback constraints in apps/backend/tests/contract/test_homepage_search_summary_contract.py
- [x] T019 [P] [US2] Add frontend discovery-client tests for summary fetch shape and errors in apps/frontend/tests/discovery-client.test.ts

### Implementation for User Story 2

- [x] T020 [US2] Add /api/datasets/search/summary route handling with validated payload in apps/backend/src/http_api_server.py
- [x] T021 [US2] Implement service-level summary aggregation and response metadata in apps/backend/src/query/dataset_discovery_service.py
- [x] T022 [US2] Implement persisted repository aggregate count query for active datasets/sources in apps/backend/src/query/dataset_discovery_persisted_repository.py
- [x] T023 [US2] Fetch summary in homepage loader and pass values to search surface in apps/frontend/src/app/page.tsx
- [x] T024 [US2] Render required summary sentence with graceful fallback state in apps/frontend/src/components/discovery/DatasetSearchBox.tsx
- [x] T025 [US2] Update contract and quickstart examples for runtime scope summary behavior in specs/024-home-search-bar/contracts/homepage-search-contract.md and specs/024-home-search-bar/quickstart.md

**Checkpoint**: User Story 2 is independently testable with live aggregate scope messaging.

---

## Phase 5: User Story 3 - Get Likely Matches While Typing (Priority: P3)

**Goal**: Provide typing-time likely-match dropdown using backend trigram-oriented suggestion ranking.

**Independent Test**: Type partial query, verify dropdown suggestions refresh for latest input and stale results are not shown.

### Tests for User Story 3 (REQUIRED) ⚠️

- [x] T026 [P] [US3] Add backend suggestions contract tests covering ordering and limit bounds in apps/backend/tests/contract/test_dataset_search_suggestions_contract.py
- [x] T027 [P] [US3] Add backend HTTP route contract assertions for suggestions query parameter validation in apps/backend/tests/contract/test_http_runtime_persisted_discovery_endpoints.py
- [x] T028 [P] [US3] Add frontend interaction tests for suggestions open/update/clear behavior in apps/frontend/tests/DatasetSearchBox.suggestions.test.tsx

### Implementation for User Story 3

- [x] T029 [US3] Add /api/datasets/search/suggestions route parsing and error envelopes in apps/backend/src/http_api_server.py
- [x] T030 [US3] Implement service suggestion orchestration with stable sort semantics in apps/backend/src/query/dataset_discovery_service.py
- [x] T031 [US3] Implement persisted repository trigram-backed suggestion query with limit bounding in apps/backend/src/query/dataset_discovery_persisted_repository.py
- [x] T032 [US3] Add frontend discovery client helper for suggestions endpoint in apps/frontend/src/lib/api/discovery-client.ts
- [x] T033 [US3] Implement DatasetSearchBox dropdown state management with stale-result guard in apps/frontend/src/components/discovery/DatasetSearchBox.tsx
- [x] T034 [US3] Add dropdown visual styling and responsive anchoring behavior in apps/frontend/src/app/globals.css

**Checkpoint**: User Story 3 is independently testable with likely-match dropdown behavior.

---

## Phase 6: Polish & Cross-Cutting Concerns

**Purpose**: Ensure docs parity and run mandatory quality gates.

- [x] T035 [P] Reconcile plan/tasks/contract language for delivered behavior in specs/024-home-search-bar/plan.md and specs/024-home-search-bar/tasks.md
- [x] T036 [P] Run focused backend/frontend tests for homepage summary and suggestion flows and log outcomes in specs/024-home-search-bar/tasks.md
- [x] T037 Run `pnpm exec nx run-many -t test --all` and record pass result in specs/024-home-search-bar/tasks.md
- [x] T038 Run `pnpm exec nx run-many -t coverage --all` and record pass result in specs/024-home-search-bar/tasks.md

---

## Dependencies & Execution Order

### Phase Dependencies

- **Phase 1 (Setup)**: No dependencies.
- **Phase 2 (Foundational)**: Depends on Phase 1 and blocks all user stories.
- **Phase 3 (US1)**: Depends on Phase 2 completion.
- **Phase 4 (US2)**: Depends on Phase 2 completion; can run after US1 or in parallel if staffed.
- **Phase 5 (US3)**: Depends on Phase 2 completion; can run after US1/US2 or in parallel if staffed.
- **Phase 6 (Polish)**: Depends on completion of selected user stories.

### User Story Dependencies

- **US1 (P1)**: No dependency on other stories; defines MVP centered search value.
- **US2 (P2)**: Depends on foundational summary contracts; independent from US3.
- **US3 (P3)**: Depends on foundational suggestion contracts; independent from US2.

### Within Each User Story

- Tests first and failing before implementation where applicable.
- Backend contract and service updates before frontend wiring for that story.
- Story checkpoint must pass independently before final polish.

### Parallel Opportunities

- Setup parallel tasks: T002, T003, T004.
- Foundational parallel tasks: T006, T007, T009, T010.
- US1 parallel tasks: T011, T012, T014.
- US2 parallel tasks: T018, T019.
- US3 parallel tasks: T026, T027, T028.
- Polish parallel tasks: T035, T036.

---

## Parallel Example: User Story 2

```bash
Task: "T018 [US2] Add backend summary contract tests in apps/backend/tests/contract/test_homepage_search_summary_contract.py"
Task: "T019 [US2] Add frontend summary client tests in apps/frontend/tests/discovery-client.test.ts"
```

## Parallel Example: User Story 3

```bash
Task: "T026 [US3] Add backend suggestions contract tests in apps/backend/tests/contract/test_dataset_search_suggestions_contract.py"
Task: "T028 [US3] Add frontend suggestions interaction tests in apps/frontend/tests/DatasetSearchBox.suggestions.test.tsx"
Task: "T032 [US3] Add suggestions fetch helper in apps/frontend/src/lib/api/discovery-client.ts"
```

---

## Implementation Strategy

### MVP First (User Story 1 only)

1. Complete Phase 1 and Phase 2.
2. Complete Phase 3 (US1).
3. Validate US1 independently via homepage/search layout tests.
4. Demo centered search MVP.

### Incremental Delivery

1. Deliver US1 centered search surface.
2. Deliver US2 runtime scope summary line.
3. Deliver US3 likely-match dropdown interactions.
4. Complete polish and run mandatory stop-gate commands.

### Parallel Team Strategy

1. One engineer completes setup/foundational backend+frontend contracts.
2. After Phase 2, one engineer handles US2 aggregation while another handles US3 suggestion flows.
3. Rejoin for final polish and full-gate validation.

---

## Notes

- All tasks follow required checklist format with sequential IDs and explicit file paths.
- Coverage must remain >= 90% in affected projects.
- Before any commit and before any AI agent handoff/end: run `pnpm exec nx run-many -t test --all`.
- Before any commit: run `pnpm exec nx run-many -t coverage --all`.
- Documentation updates are required in the same change as behavior changes.

## Validation Outcomes

- 2026-03-24: `uv run --project apps/backend pytest --no-cov apps/backend/tests/contract/test_homepage_search_summary_contract.py apps/backend/tests/contract/test_dataset_search_suggestions_contract.py apps/backend/tests/contract/test_http_runtime_persisted_discovery_endpoints.py` passed.
- 2026-03-24: `pnpm --dir apps/frontend test -- tests/home-page.test.tsx tests/shell-structure-contract.test.tsx tests/discovery-client.test.ts tests/DatasetSearchBox.suggestions.test.tsx` passed.
- 2026-03-24: Manual runtime verification after clean restart passed via `docker compose down && docker compose up -d db backend` followed by successful `curl` checks for `/api/health`, `/api/datasets/search/summary`, and `/api/datasets/search/suggestions?q=fund&limit=3`.
- 2026-03-24: `pnpm exec nx run-many -t test --all` passed.
- 2026-03-24: `pnpm exec nx run-many -t coverage --all` passed.
- 2026-03-24: `pre-commit run --all-files` passed.
