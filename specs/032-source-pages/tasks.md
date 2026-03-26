# Tasks: Source Discovery Pages

**Input**: Design documents from `/specs/032-source-pages/`
**Prerequisites**: plan.md (required), spec.md (required for user stories), research.md, data-model.md, contracts/

**Tests**: Test tasks are REQUIRED. Every user story and foundational component MUST include automated test coverage sufficient to maintain >= 90% coverage in affected projects. Before any commit and before any AI agent stops work, the full repository suite MUST pass via `pnpm exec nx run-many -t test --all`. Before any commit, monorepo coverage MUST pass via `pnpm exec nx run-many -t coverage --all` with >= 90% thresholds in every project.

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (for example, `US1`, `US2`, `US3`)
- Every task includes an exact file path

## Path Conventions

- Frontend code: `apps/frontend/src/`
- Frontend tests: `apps/frontend/tests/`
- Backend code: `apps/backend/src/`
- Backend tests: `apps/backend/tests/contract/`
- Feature docs: `specs/032-source-pages/`

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Prepare feature-specific scaffolding and validation surfaces for source discovery work.

- [X] T001 Baseline source discovery validation flow in `specs/032-source-pages/quickstart.md`
- [X] T002 [P] Add source discovery fixtures for frontend page tests in `apps/frontend/tests/fixtures/source-discovery-fixtures.ts`
- [X] T003 [P] Add source discovery repository fixture helpers in `apps/backend/tests/fixtures/source_discovery_repository.py`
- [X] T004 [P] Create source discovery contract document scaffold in `specs/032-source-pages/contracts/source-discovery-contract.md`

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Build shared contracts, repository projections, and client surfaces required by all source browsing stories.

**CRITICAL**: No user story work begins until this phase is complete.

- [X] T005 Define backend source discovery contract models in `apps/backend/src/contract/query/source_discovery_query.py`
- [X] T006 [P] Add source discovery type definitions to `apps/frontend/src/lib/api/discovery-types.ts`
- [X] T007 [P] Add source list and source detail client methods to `apps/frontend/src/lib/api/discovery-client.ts`
- [X] T008 Refactor shared source projection and identifier helpers in `apps/backend/src/query/dataset_discovery_persisted_repository.py`
- [X] T009 Add source list and source detail service entrypoints in `apps/backend/src/query/dataset_discovery_service.py`
- [X] T010 Add source HTTP dispatch scaffolding in `apps/backend/src/http_api_server.py`
- [X] T011 Synchronize foundational source identifier and fallback rules in `specs/032-source-pages/contracts/source-discovery-contract.md`

**Checkpoint**: Foundation complete. User stories can now be implemented and validated independently.

---

## Phase 3: User Story 1 - Browse Available Sources (Priority: P1) MVP

**Goal**: Deliver a dedicated sources page that lists all discoverable sources with stable navigation targets and dataset counts.

**Independent Test**: Open `/sources` and verify the page shows each available source once, with readable names, dataset counts, and working links into source detail routes.

### Tests for User Story 1 (REQUIRED)

- [X] T012 [P] [US1] Add backend source list contract tests in `apps/backend/tests/contract/test_source_list_query_contract.py`
- [X] T013 [P] [US1] Add frontend source list page render tests in `apps/frontend/tests/source-list-page.test.tsx`
- [X] T014 [P] [US1] Add source discovery client list-method tests in `apps/frontend/tests/source-discovery-client.test.ts`
- [X] T015 [P] [US1] Add shell navigation contract assertions for source entry visibility in `apps/frontend/tests/shell-structure-contract.test.tsx`

### Implementation for User Story 1

- [X] T016 [US1] Implement source list query entrypoint in `apps/backend/src/query/source_list_query.py`
- [X] T017 [US1] Implement source listing projection in `apps/backend/src/query/dataset_discovery_persisted_repository.py`
- [X] T018 [US1] Wire `GET /api/sources` into `apps/backend/src/http_api_server.py`
- [X] T019 [US1] Add source list presentation component in `apps/frontend/src/components/discovery/SourceCatalogList.tsx`
- [X] T020 [US1] Add source list row component in `apps/frontend/src/components/discovery/SourceListRow.tsx`
- [X] T021 [US1] Implement `/sources` route in `apps/frontend/src/app/sources/page.tsx`
- [X] T022 [US1] Add sources navigation entry in `apps/frontend/src/shell/navbar-config.ts`
- [X] T023 [US1] Add source list layout and responsive styles in `apps/frontend/src/app/globals.css`
- [X] T024 [US1] Update source list contract details in `specs/032-source-pages/contracts/source-discovery-contract.md`

**Checkpoint**: User Story 1 is independently functional and testable.

---

## Phase 4: User Story 2 - Open a Source Detail Page (Priority: P2)

**Goal**: Deliver a source detail page that shows one source’s context and only that source’s datasets, with onward navigation into dataset detail pages.

**Independent Test**: Open `/sources/{sourceId}` for a known source and verify the page shows source context plus a filtered dataset list where every dataset belongs to that source.

### Tests for User Story 2 (REQUIRED)

- [X] T025 [P] [US2] Add backend source detail contract tests in `apps/backend/tests/contract/test_source_detail_query_contract.py`
- [X] T026 [P] [US2] Add backend HTTP source endpoint tests in `apps/backend/tests/contract/test_http_runtime_source_endpoints.py`
- [X] T027 [P] [US2] Add frontend source detail page tests in `apps/frontend/tests/source-detail-page.test.tsx`
- [X] T028 [P] [US2] Add source discovery client detail-method tests in `apps/frontend/tests/source-discovery-client.test.ts`

### Implementation for User Story 2

- [X] T029 [US2] Implement source detail query entrypoint in `apps/backend/src/query/source_detail_query.py`
- [X] T030 [US2] Implement source detail dataset-membership projection in `apps/backend/src/query/dataset_discovery_persisted_repository.py`
- [X] T031 [US2] Wire `GET /api/sources/{sourceId}` into `apps/backend/src/http_api_server.py`
- [X] T032 [US2] Add source detail header component in `apps/frontend/src/components/discovery/SourceDetailHeader.tsx`
- [X] T033 [US2] Implement `/sources/[sourceId]/page.tsx` in `apps/frontend/src/app/sources/[sourceId]/page.tsx`
- [X] T034 [US2] Reuse dataset listing hierarchy for source-owned datasets in `apps/frontend/src/components/discovery/DatasetCatalogList.tsx`
- [X] T035 [US2] Add source detail page styling in `apps/frontend/src/app/globals.css`
- [X] T036 [US2] Update source detail contract details in `specs/032-source-pages/contracts/source-discovery-contract.md`

**Checkpoint**: User Stories 1 and 2 are independently functional and testable.

---

## Phase 5: User Story 3 - Recover Gracefully from Missing or Failed Source Views (Priority: P3)

**Goal**: Deliver explicit source empty, error, and not-found behavior without breaking the shell or dataset navigation model.

**Independent Test**: Exercise empty source list, zero-dataset source detail, unknown source route, and generic source fetch failure states; verify each state is explicit and preserves navigation.

### Tests for User Story 3 (REQUIRED)

- [X] T037 [P] [US3] Add source not-found and error page assertions in `apps/frontend/tests/source-detail-page.test.tsx`
- [X] T038 [P] [US3] Add source empty-state assertions in `apps/frontend/tests/source-list-page.test.tsx`
- [X] T039 [P] [US3] Add backend source-not-found and invalid-request contract tests in `apps/backend/tests/contract/test_http_runtime_source_endpoints.py`

### Implementation for User Story 3

- [X] T040 [US3] Add source not-found error contract helpers in `apps/backend/src/contract/query/source_discovery_contracts.py`
- [X] T041 [US3] Add source detail not-found route in `apps/frontend/src/app/sources/[sourceId]/not-found.tsx`
- [X] T042 [US3] Implement empty and error-state handling in `apps/frontend/src/app/sources/page.tsx`
- [X] T043 [US3] Implement empty and error-state handling in `apps/frontend/src/app/sources/[sourceId]/page.tsx`
- [X] T044 [US3] Add source fallback and empty-state styling in `apps/frontend/src/app/globals.css`
- [X] T045 [US3] Update quickstart fallback validation steps in `specs/032-source-pages/quickstart.md`

**Checkpoint**: All user stories are independently functional and testable.

---

## Phase 6: Polish and Cross-Cutting Concerns

**Purpose**: Final quality, documentation fidelity, and stop-gate validation across the full feature.

- [X] T046 [P] Reconcile spec, plan, contract, and quickstart wording with delivered behavior in `specs/032-source-pages/spec.md`
- [X] T047 [P] Record focused backend validation evidence in `specs/032-source-pages/quickstart.md`
- [X] T048 [P] Record focused frontend validation evidence in `specs/032-source-pages/quickstart.md`
- [X] T049 Run manual source browsing validation after clean local restart and capture outcomes in `specs/032-source-pages/quickstart.md`
- [X] T050 Run `pnpm exec nx run-many -t test --all` and record pass evidence in `specs/032-source-pages/quickstart.md`
- [X] T051 Run `pnpm exec nx run-many -t coverage --all` and record pass evidence in `specs/032-source-pages/quickstart.md`
- [X] T052 [P] Review and update `AGENTS.md` if source discovery routes, commands, or active technology listings need documentation changes

---

## Dependencies and Execution Order

### Phase Dependencies

- Phase 1 (Setup): No dependencies; starts immediately.
- Phase 2 (Foundational): Depends on Phase 1 and blocks all story phases.
- Phase 3 (US1): Depends on Phase 2.
- Phase 4 (US2): Depends on Phase 2 and can follow US1 once shared source list files are stable.
- Phase 5 (US3): Depends on Phase 2 and can proceed after the primary list/detail routes exist.
- Phase 6 (Polish): Depends on completion of all user stories.

### User Story Dependencies

- US1 (P1): Independent after foundational completion; defines the MVP source browsing slice.
- US2 (P2): Depends on the shared source identifier and query/client surfaces from Phase 2 and builds on the navigation entry created in US1.
- US3 (P3): Depends on the source routes and backend endpoint behavior established in US1 and US2.

### Within Each User Story

- Tests first and expected to fail before implementation.
- Backend query and contract work before frontend route wiring.
- Shared presentation components before page-level styling finalization.
- Documentation and quickstart updates after behavior is implemented.

## Parallel Opportunities

- Setup: T002, T003, and T004 can run in parallel.
- Foundational: T006, T007, and T008 can run in parallel after T005 is defined.
- US1: T012, T013, T014, and T015 can run in parallel.
- US2: T025, T026, T027, and T028 can run in parallel.
- US3: T037, T038, and T039 can run in parallel.
- Polish: T046, T047, T048, and T052 can run in parallel with command-run validation tasks.

## Parallel Example: User Story 1

- Run in parallel:
  - T012 in `apps/backend/tests/contract/test_source_list_query_contract.py`
  - T013 in `apps/frontend/tests/source-list-page.test.tsx`
  - T014 in `apps/frontend/tests/source-discovery-client.test.ts`
  - T015 in `apps/frontend/tests/shell-structure-contract.test.tsx`
- Then continue sequentially with T016 through T024.

## Parallel Example: User Story 2

- Run in parallel:
  - T025 in `apps/backend/tests/contract/test_source_detail_query_contract.py`
  - T026 in `apps/backend/tests/contract/test_http_runtime_source_endpoints.py`
  - T027 in `apps/frontend/tests/source-detail-page.test.tsx`
  - T028 in `apps/frontend/tests/source-discovery-client.test.ts`
- Then continue sequentially with T029 through T036.

## Parallel Example: User Story 3

- Run in parallel:
  - T037 in `apps/frontend/tests/source-detail-page.test.tsx`
  - T038 in `apps/frontend/tests/source-list-page.test.tsx`
  - T039 in `apps/backend/tests/contract/test_http_runtime_source_endpoints.py`
- Then continue sequentially with T040 through T045.

## Implementation Strategy

### MVP First

1. Complete Phase 1 and Phase 2.
2. Complete Phase 3 (US1) only.
3. Validate `/sources` independently as the MVP source browsing slice.

### Incremental Delivery

1. Ship US1 for source directory discovery.
2. Add US2 for source-specific dataset browsing.
3. Add US3 for fallback resilience and route correctness.
4. Complete polish and mandatory stop gates.

### Team Parallel Strategy

1. One developer owns backend source contracts, repository projections, and HTTP routing.
2. One developer owns frontend list/detail routes and source presentation components.
3. One developer owns test coverage, fallback-state behavior, and quickstart validation capture.

## Notes

- All tasks follow the required checklist format with sequential IDs and explicit file paths.
- Story labels appear only in user-story phases.
- Parallel markers are applied only where file-level independence exists.
- Full monorepo test and coverage stop gates are mandatory before commit and before agent handoff.
