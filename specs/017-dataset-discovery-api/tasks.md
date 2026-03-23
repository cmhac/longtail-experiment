# Tasks: Dataset Discovery Backend API

**Input**: Design documents from /specs/017-dataset-discovery-api/
**Prerequisites**: plan.md (required), spec.md (required for user stories), research.md, data-model.md, contracts/, quickstart.md

**Tests**: Test tasks are REQUIRED. Every user story and foundational component MUST include automated test coverage sufficient to maintain >= 90% coverage in affected projects.

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: [ID] [P?] [Story] Description

- [P]: Can run in parallel (different files, no dependencies)
- [Story]: Which user story this task belongs to (for example, US1, US2, US3)
- Include exact file paths in descriptions

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Prepare backend discovery module scaffolding and test harness entries.

- [x] T001 Create dataset discovery query package scaffold in apps/backend/src/query/**init**.py
- [x] T002 Create dataset discovery contract package scaffold in apps/backend/src/contract/query/dataset_discovery_contracts.py
- [x] T003 [P] Add backend test fixture helpers for discovery scenarios in apps/backend/tests/fixtures/dataset_discovery_fixture.py
- [x] T004 [P] Register discovery contract test target in apps/backend/project.json
- [x] T005 [P] Add discovery test data factory utilities in apps/backend/tests/fixtures/dataset_discovery_factory.py

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Build shared persistence/query infrastructure required by all user stories.

**CRITICAL**: No user story work can begin until this phase is complete.

- [x] T006 Create additive discovery index migration in libs/db/alembic/versions/0008_dataset_discovery_indexes.py
- [x] T007 [P] Add discovery repository protocol interfaces in libs/db/src/db/repositories/interfaces.py
- [x] T008 Implement dataset discovery repository reads in libs/db/src/db/repositories/dataset_discovery_repository.py
- [x] T009 [P] Export dataset discovery repository in libs/db/src/db/repositories/**init**.py
- [x] T010 Create shared request validation helpers in apps/backend/src/query/dataset_discovery_validators.py
- [x] T011 Create shared discovery service orchestration in apps/backend/src/query/dataset_discovery_service.py
- [x] T012 Create shared API error mapping for discovery queries in apps/backend/src/contract/query/dataset_discovery_contracts.py
- [x] T013 Add foundational validation and error contract tests in apps/backend/tests/contract/test_dataset_discovery_validation_contract.py

**Checkpoint**: Foundation ready. User story implementation can now begin.

---

## Phase 3: User Story 1 - Search and Recent Updates for Landing Page (Priority: P1) MVP

**Goal**: Deliver landing-page search and recent dataset updates with deterministic ordering.

**Independent Test**: Execute search with populated metadata/tag fixtures and verify matching fields plus deterministic ordering; execute recent updates and verify maximum five records sorted by recency.

### Tests for User Story 1 (REQUIRED)

- [x] T014 [P] [US1] Add contract test for search matching fields in apps/backend/tests/contract/test_dataset_search_query_contract.py
- [x] T015 [P] [US1] Add contract test for recent-updates limit and ordering in apps/backend/tests/contract/test_dataset_recent_updates_contract.py
- [x] T016 [P] [US1] Add integration test for empty-search default behavior in apps/backend/tests/contract/test_dataset_search_default_behavior.py

### Implementation for User Story 1

- [x] T017 [P] [US1] Define search request and response contracts in apps/backend/src/contract/query/dataset_search_query.py
- [x] T018 [P] [US1] Define recent-updates response contract in apps/backend/src/contract/query/dataset_recent_updates_query.py
- [x] T019 [P] [US1] Implement metadata and tag search query logic in apps/backend/src/query/dataset_search_query.py
- [x] T020 [P] [US1] Implement recent-updates query logic in apps/backend/src/query/dataset_recent_updates_query.py
- [x] T021 [US1] Wire search and recent service handlers in apps/backend/src/query/dataset_discovery_service.py
- [x] T022 [US1] Enforce deterministic tie-break ordering rules in apps/backend/src/query/dataset_search_query.py
- [x] T023 [US1] Verify US1 coverage contribution in apps/backend/tests/contract/test_dataset_search_query_contract.py

**Checkpoint**: User Story 1 is independently functional and testable.

---

## Phase 4: User Story 2 - Browse Full Dataset Catalog by Source (Priority: P2)

**Goal**: Deliver paginated dataset catalog browsing with source organization and composable search/filtering.

**Independent Test**: Request catalog with and without source/search filters and verify deterministic pagination, source attribution, and grouping output.

### Tests for User Story 2 (REQUIRED)

- [x] T024 [P] [US2] Add contract test for catalog pagination and metadata in apps/backend/tests/contract/test_dataset_catalog_query_contract.py
- [x] T025 [P] [US2] Add contract test for source filtering and grouping in apps/backend/tests/contract/test_dataset_catalog_source_grouping.py
- [x] T026 [P] [US2] Add integration test for deterministic catalog ordering stability in apps/backend/tests/contract/test_dataset_catalog_ordering_stability.py

### Implementation for User Story 2

- [x] T027 [P] [US2] Define catalog request and response contracts in apps/backend/src/contract/query/dataset_catalog_query.py
- [x] T028 [P] [US2] Implement catalog list query with search and source filters in apps/backend/src/query/dataset_catalog_query.py
- [x] T029 [US2] Implement source-group projection helpers in apps/backend/src/query/dataset_catalog_grouping.py
- [x] T030 [US2] Wire catalog service handlers in apps/backend/src/query/dataset_discovery_service.py
- [x] T031 [US2] Add pagination and source filter validation rules in apps/backend/src/query/dataset_discovery_validators.py
- [x] T032 [US2] Verify US2 coverage contribution in apps/backend/tests/contract/test_dataset_catalog_query_contract.py

**Checkpoint**: User Story 2 is independently functional and testable.

---

## Phase 5: User Story 3 - View Dataset Detail and Full Time Series (Priority: P3)

**Goal**: Deliver dataset detail metadata and chronological observation retrieval with explicit not-found semantics.

**Independent Test**: Request a known dataset and verify metadata plus chronological observations; request unknown dataset and verify explicit not-found response.

### Tests for User Story 3 (REQUIRED)

- [x] T033 [P] [US3] Add contract test for dataset detail metadata payload in apps/backend/tests/contract/test_dataset_detail_query_contract.py
- [x] T034 [P] [US3] Add contract test for dataset-not-found behavior in apps/backend/tests/contract/test_dataset_detail_not_found_contract.py
- [x] T035 [P] [US3] Add integration test for chronological observation ordering in apps/backend/tests/contract/test_dataset_detail_observation_order.py

### Implementation for User Story 3

- [x] T036 [P] [US3] Define detail request and response contracts in apps/backend/src/contract/query/dataset_detail_query.py
- [x] T037 [P] [US3] Implement dataset detail metadata query logic in apps/backend/src/query/dataset_detail_query.py
- [x] T038 [US3] Implement observation range filters and chronological ordering in apps/backend/src/query/dataset_detail_query.py
- [x] T039 [US3] Wire detail service handlers and empty-observation semantics in apps/backend/src/query/dataset_discovery_service.py
- [x] T040 [US3] Add explicit not-found error mapping in apps/backend/src/contract/query/dataset_discovery_contracts.py
- [x] T041 [US3] Verify US3 coverage contribution in apps/backend/tests/contract/test_dataset_detail_query_contract.py

**Checkpoint**: User Story 3 is independently functional and testable.

---

## Phase 6: Polish and Cross-Cutting Concerns

**Purpose**: Final verification, documentation alignment, and quality gate completion.

- [x] T042 [P] Update discovery contract examples and edge-case notes in specs/017-dataset-discovery-api/contracts/dataset-discovery-api-contract.md
- [x] T043 [P] Update execution evidence and validation notes in specs/017-dataset-discovery-api/quickstart.md
- [x] T044 [P] Add discovery endpoint operational guidance in docs/runbooks/provider-onboarding.md
- [x] T045 Run backend quality command suite and resolve findings in apps/backend/project.json
- [x] T046 Run affected workspace checks and capture outcomes in specs/017-dataset-discovery-api/quickstart.md
- [x] T047 Verify AGENTS command/technology updates remain accurate in AGENTS.md

---

## Dependencies and Execution Order

### Phase Dependencies

- Setup (Phase 1): No dependencies, can start immediately.
- Foundational (Phase 2): Depends on Setup completion and blocks all user stories.
- User Stories (Phase 3-5): Depend on Foundational completion.
- Polish (Phase 6): Depends on completion of selected user stories.

### User Story Dependencies

- US1 (P1): Starts after Phase 2 and is the MVP scope.
- US2 (P2): Starts after Phase 2 and is independently testable from US1.
- US3 (P3): Starts after Phase 2 and is independently testable from US1 and US2.

### Dependency Graph

- Phase 1 -> Phase 2 -> US1 -> Phase 6
- Phase 1 -> Phase 2 -> US2 -> Phase 6
- Phase 1 -> Phase 2 -> US3 -> Phase 6

---

## Parallel Execution Opportunities

- Phase 1: T003, T004, and T005 can run in parallel.
- Phase 2: T007 and T009 can run in parallel; T010 and T012 can run in parallel after T006.
- US1: T014-T016 can run in parallel; T017-T020 can run in parallel.
- US2: T024-T026 can run in parallel; T027 and T028 can run in parallel.
- US3: T033-T035 can run in parallel; T036 and T037 can run in parallel.
- Phase 6: T042, T043, and T044 can run in parallel.

---

## Parallel Example: User Story 1

- Run T014, T015, and T016 together to establish failing search/recent contract tests.
- Run T017, T018, T019, and T020 together to build contracts and query modules.

## Parallel Example: User Story 2

- Run T024, T025, and T026 together for catalog contract and integration coverage.
- Run T027 and T028 together while keeping T030 dependent on their completion.

## Parallel Example: User Story 3

- Run T033, T034, and T035 together for detail behavior coverage.
- Run T036 and T037 together, then complete T038-T040 sequentially.

---

## Implementation Strategy

### MVP First (User Story 1)

1. Complete Phase 1 and Phase 2.
2. Complete Phase 3 (US1).
3. Validate US1 independently using search and recent-updates tests.
4. Demo landing-page backend readiness.

### Incremental Delivery

1. Deliver US1 search and recent updates.
2. Deliver US2 catalog browsing and source grouping.
3. Deliver US3 detail and chronological observations.
4. Finish with Phase 6 quality and documentation checks.

### Parallel Team Strategy

1. One developer completes Setup and Foundational tasks.
2. After foundation is complete:
   - Developer A executes US1.
   - Developer B executes US2.
   - Developer C executes US3.
3. Team converges for Phase 6 verification.

---

## Notes

- All tasks follow strict checklist format with sequential IDs.
- User story tasks include required [USx] labels and exact file paths.
- Parallel markers [P] are only applied to tasks that can avoid file conflicts.
- Coverage MUST remain >= 90% for affected projects.
- Documentation updates MUST ship in the same change as behavior changes.
- AGENTS.md MUST be updated when canonical commands, structure, or active technologies change.
