# Tasks: Discovery Pagination Rollout

**Input**: Design documents from `/specs/034-api-pagination-rollout/`
**Prerequisites**: plan.md (required), spec.md (required for user stories), research.md, data-model.md, contracts/

**Tests**: Test tasks are REQUIRED. Every user story and foundational component MUST include automated test coverage sufficient to maintain >= 90% coverage in affected projects. Before any commit and before any AI agent stops work, the full repository suite MUST pass via `pnpm exec nx run-many -t test --all`; targeted tests alone are never sufficient for this stop gate. Before any commit, monorepo coverage MUST pass via `pnpm exec nx run-many -t coverage --all` with >= 90% thresholds in every project.

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3)
- Include exact file paths in descriptions

## Path Conventions

- Backend: `apps/backend/src/`, `apps/backend/tests/contract/`
- Frontend: `apps/frontend/src/`, `apps/frontend/tests/`
- Spec artifacts: `specs/034-api-pagination-rollout/`

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Establish pagination rollout inventory and task scaffolding used by all stories.

- [x] T001 Create explicit in-scope route inventory and exclusions table in specs/034-api-pagination-rollout/contracts/discovery-list-pagination-contract.md
- [x] T002 [P] Document story-level manual verification checklist in specs/034-api-pagination-rollout/quickstart.md
- [x] T003 [P] Add implementation notes and sequencing checkpoints in specs/034-api-pagination-rollout/plan.md
- [x] T004 Create shared backend pagination rollout checklist comments in apps/backend/src/query/dataset_discovery_service.py
- [x] T005 [P] Create shared frontend pagination rollout checklist comments in apps/frontend/src/lib/api/discovery-client.ts

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Build shared backend/frontend pagination primitives required by every user story.

**⚠️ CRITICAL**: No user story work can begin until this phase is complete.

- [x] T006 Define and centralize backend pagination normalization policy in apps/backend/src/query/dataset_discovery_validators.py
- [x] T007 [P] Standardize backend paginated response metadata mapping in apps/backend/src/query/dataset_discovery_service.py
- [x] T008 [P] Standardize backend list route query parsing for page/page_size in apps/backend/src/http_api_server.py
- [x] T009 Extend shared discovery pagination type coverage in apps/frontend/src/lib/api/discovery-types.ts
- [x] T010 [P] Add shared frontend pagination query serialization helpers in apps/frontend/src/lib/api/discovery-client.ts
- [x] T011 [P] Add foundational backend validator contract tests in apps/backend/tests/contract/test_dataset_discovery_validation_contract.py
- [x] T012 Add foundational frontend discovery client pagination parameter tests in apps/frontend/tests/discovery-client.test.ts

**Checkpoint**: Shared pagination primitives are complete and all user stories can proceed.

---

## Phase 3: User Story 1 - Navigate Large Result Sets (Priority: P1) 🎯 MVP

**Goal**: Apply backend page-based pagination and metadata consistency to all in-scope list routes, including currently unpaginated detail-list routes.

**Independent Test**: Call each in-scope list route with multiple page/page_size combinations and verify bounded items plus correct metadata and stable ordering.

### Tests for User Story 1 (REQUIRED) ⚠️

- [x] T013 [P] [US1] Add search pagination contract coverage for metadata and bounds in apps/backend/tests/contract/test_dataset_search_query_contract.py
- [x] T014 [P] [US1] Add catalog pagination contract coverage for metadata and bounds in apps/backend/tests/contract/test_dataset_catalog_query_contract.py
- [x] T015 [P] [US1] Add source detail paginated dataset-list runtime coverage in apps/backend/tests/contract/test_http_runtime_source_endpoints.py
- [x] T016 [P] [US1] Add topic/geography detail paginated dataset-list runtime coverage in apps/backend/tests/contract/test_http_runtime_metadata_endpoints.py
- [x] T017 [P] [US1] Add persisted repository pagination stability checks for list routes in apps/backend/tests/contract/test_dataset_discovery_persisted_repository_contract.py

### Implementation for User Story 1

- [x] T018 [US1] Apply paginated dataset-list response contract fields to source detail in apps/backend/src/contract/query/source_discovery_query.py
- [x] T019 [P] [US1] Apply paginated dataset-list response contract fields to topic/geography detail in apps/backend/src/contract/query/metadata_discovery_query.py
- [x] T020 [US1] Implement source detail list pagination behavior in apps/backend/src/query/dataset_discovery_service.py
- [x] T021 [P] [US1] Implement topic detail list pagination behavior in apps/backend/src/query/dataset_discovery_service.py
- [x] T022 [P] [US1] Implement geography detail list pagination behavior in apps/backend/src/query/dataset_discovery_service.py
- [x] T023 [US1] Add paginated repository support for source/topic/geography list routes in apps/backend/src/query/dataset_discovery_persisted_repository.py
- [x] T024 [US1] Update query entrypoints to return paginated contracts for source/topic/geography routes in apps/backend/src/query/source_detail_query.py
- [x] T025 [P] [US1] Update query entrypoints to return paginated contracts for metadata routes in apps/backend/src/query/topic_detail_query.py
- [x] T026 [P] [US1] Update query entrypoints to return paginated contracts for metadata routes in apps/backend/src/query/geography_detail_query.py
- [x] T027 [US1] Ensure list-route pagination parameter propagation for source/topic/geography endpoints in apps/backend/src/http_api_server.py
- [x] T028 [US1] Verify US1 backend coverage contribution remains >= 90% via updated assertions in apps/backend/tests/contract/test_dataset_query_entrypoints.py

**Checkpoint**: All in-scope backend list routes return bounded page results with consistent pagination metadata.

---

## Phase 4: User Story 2 - Keep Frontend and Service State Aligned (Priority: P2)

**Goal**: Add frontend pagination controls and page-state synchronization so list views request explicit pages and render metadata-driven navigation.

**Independent Test**: For each paginated frontend list view, navigate between pages and verify URL/query state, request params, and rendered records remain synchronized.

### Tests for User Story 2 (REQUIRED) ⚠️

- [x] T029 [P] [US2] Add catalog page pagination control and request-state tests in apps/frontend/tests/catalog-page.test.tsx
- [x] T030 [P] [US2] Add datasets page pagination control and request-state tests in apps/frontend/tests/datasets-page.test.tsx
- [x] T031 [P] [US2] Add source metadata list pagination client tests in apps/frontend/tests/source-discovery-client.test.ts
- [x] T032 [P] [US2] Add topic/geography pagination client tests in apps/frontend/tests/metadata-discovery-client.test.ts
- [x] T033 [P] [US2] Add search page explicit paging request and rendering tests in apps/frontend/tests/search-page.test.tsx

### Implementation for User Story 2

- [x] T034 [US2] Add reusable pagination controls component for discovery list pages in apps/frontend/src/components/discovery/DiscoveryPaginationControls.tsx
- [x] T035 [P] [US2] Extend discovery client to send pagination params for source/topic/geography detail fetches in apps/frontend/src/lib/api/discovery-client.ts
- [x] T036 [P] [US2] Extend discovery types to include paginated metadata for source/topic/geography detail responses in apps/frontend/src/lib/api/discovery-types.ts
- [x] T037 [US2] Replace oversized static page-size behavior with explicit page-state requests in apps/frontend/src/app/datasets/page.tsx
- [x] T038 [P] [US2] Add explicit page navigation wiring for search route in apps/frontend/src/app/search/page.tsx
- [x] T039 [P] [US2] Add explicit page navigation wiring for source detail dataset list in apps/frontend/src/app/sources/[sourceId]/page.tsx
- [x] T040 [P] [US2] Add explicit page navigation wiring for topic detail dataset list in apps/frontend/src/app/topics/[topicId]/page.tsx
- [x] T041 [P] [US2] Add explicit page navigation wiring for geography detail dataset list in apps/frontend/src/app/geographies/[geographyId]/page.tsx
- [x] T042 [US2] Integrate pagination controls and metadata display into dataset list rendering in apps/frontend/src/components/discovery/DatasetCatalogList.tsx
- [x] T043 [US2] Verify US2 frontend coverage contribution remains >= 90% via updated assertions in apps/frontend/tests/discovery-client.test.ts

**Checkpoint**: Frontend list pages navigate via explicit page requests and stay synchronized with backend pagination metadata.

---

## Phase 5: User Story 3 - Preserve Existing Discovery Behaviors (Priority: P3)

**Goal**: Preserve existing filter/sort semantics and empty/error experiences while rolling pagination through all list routes.

**Independent Test**: Re-run pre-existing discovery scenarios (filtering, sorting, empty states, errors) with pagination enabled and confirm parity except intended page navigation behavior.

### Tests for User Story 3 (REQUIRED) ⚠️

- [x] T044 [P] [US3] Add backend ordering invariance regression tests under pagination in apps/backend/tests/contract/test_dataset_catalog_ordering_stability.py
- [x] T045 [P] [US3] Add backend filtered pagination default behavior regression tests in apps/backend/tests/contract/test_dataset_search_default_behavior.py
- [x] T046 [P] [US3] Add frontend empty/error state pagination regression tests in apps/frontend/tests/datasets-page.test.tsx
- [x] T047 [P] [US3] Add frontend sort/filter and page-reset regression tests in apps/frontend/tests/catalog-page.test.tsx

### Implementation for User Story 3

- [x] T048 [US3] Preserve deterministic sort + filtered total behavior under pagination in apps/backend/src/query/dataset_discovery_persisted_repository.py
- [x] T049 [P] [US3] Preserve service-level filter/sort behavior while applying page reconciliation in apps/backend/src/query/dataset_discovery_service.py
- [x] T050 [US3] Preserve frontend empty/error rendering while adding pagination controls in apps/frontend/src/components/discovery/ErrorState.tsx
- [x] T051 [P] [US3] Preserve frontend empty/error rendering while adding pagination controls in apps/frontend/src/components/discovery/EmptyState.tsx
- [x] T052 [US3] Preserve discovery list row rendering semantics during paginated updates in apps/frontend/src/components/discovery/UnifiedDatasetRow.tsx
- [x] T053 [US3] Verify US3 cross-layer regression coverage remains >= 90% in apps/backend/tests/contract/test_dataset_catalog_persisted_runtime_contract.py

**Checkpoint**: Pagination rollout keeps existing discovery behavior stable across filter/sort/empty/error scenarios.

---

## Phase 6: Polish & Cross-Cutting Concerns

**Purpose**: Final documentation, verification, and full quality-gate completion.

- [x] T054 [P] Update pagination route coverage matrix and exclusions in specs/034-api-pagination-rollout/contracts/discovery-list-pagination-contract.md
- [x] T055 [P] Update execution and manual verification steps in specs/034-api-pagination-rollout/quickstart.md
- [x] T056 [P] Align implementation status notes with delivered behavior in specs/034-api-pagination-rollout/plan.md
- [x] T057 Update repository guidance if command/workflow expectations changed in AGENTS.md
- [x] T058 Run full monorepo tests and capture pass evidence in specs/034-api-pagination-rollout/quickstart.md
- [x] T059 Run full monorepo coverage and capture pass evidence in specs/034-api-pagination-rollout/quickstart.md

---

## Dependencies & Execution Order

### Phase Dependencies

- **Phase 1 (Setup)**: No dependencies.
- **Phase 2 (Foundational)**: Depends on Phase 1 and blocks all user stories.
- **Phase 3 (US1)**: Depends on Phase 2; defines backend paginated behavior needed by downstream frontend work.
- **Phase 4 (US2)**: Depends on Phase 3 for full route-level metadata consistency.
- **Phase 5 (US3)**: Depends on Phases 3 and 4 for regression stabilization.
- **Phase 6 (Polish)**: Depends on all story phases.

### User Story Dependencies

- **US1 (P1)**: Can start immediately after Foundational phase; MVP scope.
- **US2 (P2)**: Depends on US1 completion for complete backend route pagination support.
- **US3 (P3)**: Depends on US1 and US2 to validate and preserve behavior.

### Within Each User Story

- Route-level tests first, then implementation updates.
- Contract/type updates before service/page wiring.
- Service/repository behavior before HTTP/route integration.
- Story-specific coverage verification before moving to next story.

### Parallel Opportunities

- Phase 1 tasks marked [P] can run in parallel.
- Phase 2 tasks T007, T008, T010, T011 can run in parallel after T006.
- US1 test tasks T013-T017 can run in parallel; US1 contract updates T019, T021, T022, T025, T026 can run in parallel with dependency awareness.
- US2 test tasks T029-T033 can run in parallel; US2 page wiring tasks T038-T041 can run in parallel.
- US3 test tasks T044-T047 can run in parallel; US3 preservation tasks T049, T051 can run in parallel.
- Polish tasks T054-T056 can run in parallel before final full-suite gates.

---

## Parallel Example: User Story 1

```bash
# Run US1 backend pagination tests in parallel workstreams:
Task: "Add search pagination contract coverage in apps/backend/tests/contract/test_dataset_search_query_contract.py"
Task: "Add source detail paginated runtime coverage in apps/backend/tests/contract/test_http_runtime_source_endpoints.py"
Task: "Add metadata paginated runtime coverage in apps/backend/tests/contract/test_http_runtime_metadata_endpoints.py"

# Implement US1 contract updates in parallel:
Task: "Apply paginated source detail contract fields in apps/backend/src/contract/query/source_discovery_query.py"
Task: "Apply paginated metadata detail contract fields in apps/backend/src/contract/query/metadata_discovery_query.py"
```

## Parallel Example: User Story 2

```bash
# Run US2 frontend test streams in parallel:
Task: "Add catalog page pagination tests in apps/frontend/tests/catalog-page.test.tsx"
Task: "Add datasets page pagination tests in apps/frontend/tests/datasets-page.test.tsx"
Task: "Add metadata/source client pagination tests in apps/frontend/tests/metadata-discovery-client.test.ts and apps/frontend/tests/source-discovery-client.test.ts"

# Implement page wiring in parallel once shared control is in place:
Task: "Wire pagination for source detail in apps/frontend/src/app/sources/[sourceId]/page.tsx"
Task: "Wire pagination for topic detail in apps/frontend/src/app/topics/[topicId]/page.tsx"
Task: "Wire pagination for geography detail in apps/frontend/src/app/geographies/[geographyId]/page.tsx"
```

## Parallel Example: User Story 3

```bash
# Run US3 regression tests in parallel:
Task: "Add backend ordering invariance regression tests in apps/backend/tests/contract/test_dataset_catalog_ordering_stability.py"
Task: "Add frontend filter/sort page-reset regression tests in apps/frontend/tests/catalog-page.test.tsx"

# Implement preservation updates in parallel:
Task: "Preserve repository deterministic ordering in apps/backend/src/query/dataset_discovery_persisted_repository.py"
Task: "Preserve frontend empty/error rendering with pagination in apps/frontend/src/components/discovery/EmptyState.tsx and apps/frontend/src/components/discovery/ErrorState.tsx"
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1 and Phase 2.
2. Complete Phase 3 (US1) fully.
3. Validate backend route pagination for all in-scope list routes.
4. Demo backend-complete paginated contracts as MVP milestone.

### Incremental Delivery

1. Deliver US1 backend pagination contracts and runtime behavior.
2. Deliver US2 frontend pagination controls and page-state synchronization.
3. Deliver US3 regression hardening for filter/sort/empty/error parity.
4. Finish with Phase 6 full-suite validation and docs updates.

### Parallel Team Strategy

1. Team A: Backend contract/service/repository tasks (US1, US3 backend subset).
2. Team B: Frontend client/page/control tasks (US2, US3 frontend subset).
3. Team C: Cross-layer tests and documentation synchronization throughout Phases 3-6.

---

## Notes

- [P] tasks are safe for parallel execution when dependencies are satisfied.
- [US#] labels map every story-phase task back to spec user stories.
- Every task includes an explicit path and actionable change objective.
- All commits must satisfy `pnpm exec nx run-many -t test --all` and `pnpm exec nx run-many -t coverage --all` before handoff.
