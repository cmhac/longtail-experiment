# Tasks: Tag and Geography Discovery Pages

**Input**: Design documents from `/specs/033-tag-geography-pages/`
**Prerequisites**: plan.md (required), spec.md (required for user stories), research.md, data-model.md, contracts/

**Tests**: Test tasks are REQUIRED. Every user story and foundational component MUST
include automated test coverage sufficient to maintain >= 90% coverage in affected
projects. Before any commit and before any AI agent stops work, the full repository
suite MUST pass via `pnpm exec nx run-many -t test --all`; targeted tests alone are
never sufficient for this stop gate. Before any commit, monorepo coverage MUST pass via
`pnpm exec nx run-many -t coverage --all` with >= 90% thresholds in every project.

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this belongs to (e.g. US1, US2, US3)
- Include exact file paths in descriptions

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Prepare feature documentation and verify baseline repository setup before code changes

- [X] T001 Verify generated planning artifacts are present and current in `specs/033-tag-geography-pages/plan.md`, `specs/033-tag-geography-pages/research.md`, `specs/033-tag-geography-pages/data-model.md`, `specs/033-tag-geography-pages/contracts/metadata-discovery-contract.md`, and `specs/033-tag-geography-pages/quickstart.md`
- [X] T002 Verify repository ignore coverage remains sufficient for this feature in `.gitignore` and `.dockerignore`

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Add shared metadata discovery contracts and slug/lookup infrastructure that both topic and geography pages depend on

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

- [X] T003 [P] Add backend metadata discovery contract models and error helpers in `apps/backend/src/contract/query/metadata_discovery_query.py` and `apps/backend/src/contract/query/metadata_discovery_contracts.py`
- [X] T004 [P] Add frontend metadata discovery types in `apps/frontend/src/lib/api/discovery-types.ts`
- [X] T005 Add shared slug/metadata lookup helpers to `apps/backend/src/query/dataset_discovery_persisted_repository.py`
- [X] T006 Add shared metadata discovery service methods to `apps/backend/src/query/dataset_discovery_service.py`
- [X] T007 Add backend metadata query entrypoints in `apps/backend/src/query/topic_detail_query.py` and `apps/backend/src/query/geography_detail_query.py`
- [X] T008 Add frontend metadata discovery client methods in `apps/frontend/src/lib/api/discovery-client.ts`

**Checkpoint**: Shared metadata contracts and lookup behavior are ready for story implementation

---

## Phase 3: User Story 1 - Open Topic Tag Pages (Priority: P1) 🎯 MVP

**Goal**: Visitors can click topic tag pills and reach a dedicated topic detail page showing only matching datasets

**Independent Test**: Open a dataset list row or dataset detail page with topic pills, click a topic pill, and confirm `/topics/{topicId}` shows the topic label plus only datasets carrying that topic

### Tests for User Story 1 (REQUIRED) ⚠️

- [X] T009 [P] [US1] Add backend topic detail contract tests in `apps/backend/tests/contract/test_topic_detail_query_contract.py`
- [X] T010 [P] [US1] Add backend persisted-repository coverage for topic detail lookups in `apps/backend/tests/contract/test_dataset_discovery_persisted_repository_contract.py`
- [X] T011 [P] [US1] Add backend HTTP runtime topic endpoint tests in `apps/backend/tests/contract/test_http_runtime_metadata_endpoints.py`
- [X] T012 [P] [US1] Add frontend discovery client topic-detail tests in `apps/frontend/tests/metadata-discovery-client.test.ts`
- [X] T013 [P] [US1] Add frontend topic detail page tests in `apps/frontend/tests/topic-detail-page.test.tsx`
- [X] T014 [P] [US1] Add frontend linked-pill rendering tests for dataset rows and detail header in `apps/frontend/tests/UnifiedDatasetRow.test.tsx` and `apps/frontend/tests/DatasetDetailHeader.test.tsx`

### Implementation for User Story 1

- [X] T015 [US1] Implement topic detail repository query in `apps/backend/src/query/dataset_discovery_persisted_repository.py`
- [X] T016 [US1] Implement topic detail service orchestration in `apps/backend/src/query/dataset_discovery_service.py`
- [X] T017 [US1] Wire `GET /api/topics/{topicId}` into `apps/backend/src/http_api_server.py`
- [X] T018 [US1] Export topic query entrypoint updates in `apps/backend/src/query/__init__.py` and related backend query modules if needed
- [X] T019 [US1] Implement topic detail page route and not-found handling in `apps/frontend/src/app/topics/[topicId]/page.tsx` and `apps/frontend/src/app/topics/[topicId]/not-found.tsx`
- [X] T020 [US1] Add topic detail header/presentation support in `apps/frontend/src/components/discovery/TopicDetailHeader.tsx` and shared discovery components as needed
- [X] T021 [US1] Render topic pills as stable links in `apps/frontend/src/components/discovery/UnifiedDatasetRow.tsx`, `apps/frontend/src/components/discovery/unified-dataset-row-mappers.ts`, and `apps/frontend/src/components/discovery/DatasetDetailHeader.tsx`
- [X] T022 [US1] Add topic detail page styling in `apps/frontend/src/app/globals.css`
- [X] T023 [US1] Verify US1 coverage contribution remains >= 90% across affected backend/frontend projects

**Checkpoint**: Topic-pill navigation and topic detail pages are fully functional and independently testable

---

## Phase 4: User Story 2 - Open Geography Pages (Priority: P2)

**Goal**: Visitors can click geography pills and reach a dedicated geography detail page showing only matching datasets

**Independent Test**: Open a dataset list row or dataset detail page with a geography pill, click it, and confirm `/geographies/{geographyId}` shows the geography label plus only datasets carrying that geography

### Tests for User Story 2 (REQUIRED) ⚠️

- [X] T024 [P] [US2] Add backend geography detail contract tests in `apps/backend/tests/contract/test_geography_detail_query_contract.py`
- [X] T025 [P] [US2] Extend backend persisted-repository coverage for geography detail lookups in `apps/backend/tests/contract/test_dataset_discovery_persisted_repository_contract.py`
- [X] T026 [P] [US2] Extend backend HTTP runtime metadata endpoint tests for geography routes in `apps/backend/tests/contract/test_http_runtime_metadata_endpoints.py`
- [X] T027 [P] [US2] Extend frontend discovery client tests for geography detail requests in `apps/frontend/tests/metadata-discovery-client.test.ts`
- [X] T028 [P] [US2] Add frontend geography detail page tests in `apps/frontend/tests/geography-detail-page.test.tsx`

### Implementation for User Story 2

- [X] T029 [US2] Implement geography detail repository query in `apps/backend/src/query/dataset_discovery_persisted_repository.py`
- [X] T030 [US2] Implement geography detail service orchestration in `apps/backend/src/query/dataset_discovery_service.py`
- [X] T031 [US2] Wire `GET /api/geographies/{geographyId}` into `apps/backend/src/http_api_server.py`
- [X] T032 [US2] Implement geography detail page route and not-found handling in `apps/frontend/src/app/geographies/[geographyId]/page.tsx` and `apps/frontend/src/app/geographies/[geographyId]/not-found.tsx`
- [X] T033 [US2] Add geography detail header/presentation support in `apps/frontend/src/components/discovery/GeographyDetailHeader.tsx` and shared discovery components as needed
- [X] T034 [US2] Render geography pills as stable links in `apps/frontend/src/components/discovery/UnifiedDatasetRow.tsx` and `apps/frontend/src/components/discovery/DatasetDetailHeader.tsx`
- [X] T035 [US2] Add geography detail page styling in `apps/frontend/src/app/globals.css`
- [X] T036 [US2] Verify US2 coverage contribution remains >= 90% across affected backend/frontend projects

**Checkpoint**: Geography-pill navigation and geography detail pages are fully functional and independently testable

---

## Phase 5: User Story 3 - Recover Gracefully from Empty, Missing, or Failed Metadata Pages (Priority: P3)

**Goal**: Topic and geography pages handle empty, unknown, and failed lookups with explicit non-breaking states

**Independent Test**: Exercise valid-empty, unknown, and failed topic/geography routes and confirm explicit empty, not-found, and error handling with shell navigation preserved

### Tests for User Story 3 (REQUIRED) ⚠️

- [X] T037 [P] [US3] Add backend metadata not-found and empty-state contract tests in `apps/backend/tests/contract/test_topic_detail_query_contract.py` and `apps/backend/tests/contract/test_geography_detail_query_contract.py`
- [X] T038 [P] [US3] Extend backend HTTP runtime metadata endpoint tests for not-found behavior in `apps/backend/tests/contract/test_http_runtime_metadata_endpoints.py`
- [X] T039 [P] [US3] Extend frontend topic and geography detail page tests for empty/error/not-found handling in `apps/frontend/tests/topic-detail-page.test.tsx` and `apps/frontend/tests/geography-detail-page.test.tsx`

### Implementation for User Story 3

- [X] T040 [US3] Add metadata-specific not-found error helpers and service validation in `apps/backend/src/contract/query/metadata_discovery_contracts.py` and `apps/backend/src/query/dataset_discovery_service.py`
- [X] T041 [US3] Ensure backend metadata routes return explicit not-found payloads in `apps/backend/src/http_api_server.py`
- [X] T042 [US3] Implement empty/error handling in `apps/frontend/src/app/topics/[topicId]/page.tsx` and `apps/frontend/src/app/geographies/[geographyId]/page.tsx`
- [X] T043 [US3] Add metadata-page empty/error copy and reusable fallback presentation in `apps/frontend/src/components/discovery/TopicDetailHeader.tsx`, `apps/frontend/src/components/discovery/GeographyDetailHeader.tsx`, and related discovery components if needed
- [X] T044 [US3] Verify US3 coverage contribution remains >= 90% across affected backend/frontend projects

**Checkpoint**: Topic and geography pages now cover loaded, empty, not-found, and error states independently

---

## Phase 6: Polish & Cross-Cutting Concerns

**Purpose**: Complete documentation, manual verification, and repository-wide validation

- [X] T045 [P] Update feature documentation artifacts as implementation reality changes in `specs/033-tag-geography-pages/spec.md`, `specs/033-tag-geography-pages/plan.md`, `specs/033-tag-geography-pages/research.md`, `specs/033-tag-geography-pages/data-model.md`, `specs/033-tag-geography-pages/contracts/metadata-discovery-contract.md`, and `specs/033-tag-geography-pages/quickstart.md`
- [X] T046 [P] Review `AGENTS.md` and update only if canonical repository structure, commands, or workflows changed
- [X] T047 Run focused backend and frontend test commands for metadata discovery behavior
- [X] T048 Run manual quickstart validation for topic and geography detail flows against the local stack
- [X] T049 Run `pre-commit run --all-files`
- [X] T050 Run `pnpm exec nx run-many -t test --all`
- [X] T051 Run `pnpm exec nx run-many -t coverage --all`

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies
- **Foundational (Phase 2)**: Depends on Setup completion and blocks all user stories
- **User Story 1 (Phase 3)**: Depends on Foundational completion
- **User Story 2 (Phase 4)**: Depends on Foundational completion and reuses shared metadata infrastructure from US1 patterns
- **User Story 3 (Phase 5)**: Depends on US1 and US2 route/page implementations
- **Polish (Phase 6)**: Depends on all user stories being complete

### User Story Dependencies

- **US1 (P1)**: MVP slice after foundational work
- **US2 (P2)**: Shares metadata infrastructure but remains independently testable once implemented
- **US3 (P3)**: Depends on both metadata detail routes existing so fallback behavior can be validated end-to-end

### Within Each User Story

- Tests MUST be written and fail before implementation
- Backend contracts/service/repository before HTTP wiring
- Backend API/client methods before frontend routes
- Route/page behavior before cross-cutting polish

### Parallel Opportunities

- Foundational contract/type tasks T003 and T004 can run in parallel
- Story-level backend/frontend tests marked [P] can run in parallel
- Topic and geography page-specific test files can be updated in parallel
- Some shared styling/header work can proceed after route contracts stabilize, but same-file edits stay sequential

## Parallel Example: User Story 1

```bash
# Launch topic-detail tests together:
Task: "Add backend topic detail contract tests in apps/backend/tests/contract/test_topic_detail_query_contract.py"
Task: "Add frontend topic detail page tests in apps/frontend/tests/topic-detail-page.test.tsx"
Task: "Add frontend linked-pill rendering tests in apps/frontend/tests/UnifiedDatasetRow.test.tsx and apps/frontend/tests/DatasetDetailHeader.test.tsx"
```

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1: Setup
2. Complete Phase 2: Foundational
3. Complete Phase 3: Topic tag detail pages
4. Validate topic-pill navigation independently before expanding scope

### Incremental Delivery

1. Build shared metadata infrastructure
2. Deliver topic pages as the first metadata browse slice
3. Add geography pages on the same infrastructure pattern
4. Add fallback-state hardening across both metadata detail routes
5. Finish with manual validation and full repository quality gates

## Notes

- [P] tasks = different files, no unresolved dependencies
- Every task includes an exact file path for direct execution
- Tests are required for each story and must preserve >= 90% coverage in affected projects
- Before any commit and before any AI agent stops work, `pnpm exec nx run-many -t test --all` MUST pass
- Before any commit, `pnpm exec nx run-many -t coverage --all` MUST pass
- `pre-commit run --all-files` is the required monorepo-wide quality gate in the repository guidelines
