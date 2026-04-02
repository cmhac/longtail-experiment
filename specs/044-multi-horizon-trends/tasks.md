# Tasks: Current-State Multi-Lookback Trends

**Input**: Design documents from `/specs/044-multi-horizon-trends/`
**Prerequisites**: plan.md (required), spec.md (required for user stories), research.md, data-model.md, contracts/

**Tests**: Test tasks are REQUIRED. Every user story and foundational component MUST include automated coverage sufficient to maintain >= 90% coverage in affected projects.

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3)
- Every task includes exact file path(s)

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Confirm baseline artifacts and quality guardrails before code changes.

- [x] T001 Validate feature artifacts are aligned in specs/044-multi-horizon-trends/spec.md, specs/044-multi-horizon-trends/plan.md, and specs/044-multi-horizon-trends/contracts/discovery-lookback-trends.openapi.yaml
- [x] T002 [P] Capture pre-change schema and repository seam notes in specs/044-multi-horizon-trends/research.md
- [x] T003 [P] Add or update implementation tracking checklist in specs/044-multi-horizon-trends/checklists/requirements.md

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core shared infrastructure that MUST complete before user-story delivery.

- [x] T004 Create Alembic migration for lookback snapshots and canonical descriptors in libs/db/alembic/versions/0012_lookback_trend_snapshots.py
- [x] T005 [P] Add SQLAlchemy model definitions for new lookback persistence tables in libs/db/src/db/models.py
- [x] T006 [P] Add shared pipeline repository protocol types for lookback/canonical writes in apps/pipeline/src/orchestration/resources/trend_repository.py
- [x] T007 [P] Add backend contract model scaffolding for canonical trend descriptor payloads in apps/backend/src/contract/query/dataset_detail_query.py
- [x] T008 [P] Add frontend API type scaffolding for canonical trend descriptor payloads in apps/frontend/src/lib/api/discovery-types.ts
- [x] T009 Add foundational migration/repository contract tests in libs/db/tests/test_lookback_trend_migration_contract.py and apps/pipeline/tests/orchestration/test_trend_repository_contract.py

**Checkpoint**: Foundation ready. User stories can now proceed.

---

## Phase 3: User Story 1 - Persist Observation-Level Lookback Snapshots (Priority: P1) 🎯 MVP

**Goal**: Persist deterministic per-observation lookback outcomes and canonical weighted descriptor from pipeline runtime.

**Independent Test**: Materialize a new observation and verify applicable lookback rows + canonical descriptor row are persisted idempotently.

### Tests for User Story 1

- [x] T010 [P] [US1] Add classifier lookback-catalog and determinism unit tests in libs/trend_analysis/tests/test_multi_lookback_classifier.py
- [x] T011 [P] [US1] Add canonical weighting determinism tests in libs/trend_analysis/tests/test_canonical_descriptor_weighting.py
- [x] T012 [P] [US1] Add pipeline lookback applicability and no-signal tests in apps/pipeline/tests/orchestration/test_trend_runtime_processor_lookbacks.py
- [x] T013 [P] [US1] Add pipeline idempotency and partial-failure isolation tests in apps/pipeline/tests/orchestration/test_trend_runtime_processor_idempotency.py

### Implementation for User Story 1

- [x] T014 [US1] Implement multi-lookback evaluation entrypoint and result model exports in libs/trend_analysis/src/trend_analysis/**init**.py
- [x] T015 [US1] Implement fixed lookback evaluation logic in libs/trend_analysis/src/trend_analysis/classifier.py
- [x] T016 [US1] Implement lookback/canonical descriptor domain models in libs/trend_analysis/src/trend_analysis/models.py
- [x] T017 [US1] Implement weighting/version metadata for canonical descriptors in libs/trend_analysis/src/trend_analysis/version.py
- [x] T018 [US1] Implement lookback snapshot and canonical descriptor write methods in apps/pipeline/src/orchestration/resources/postgres_trend_repository.py
- [x] T019 [US1] Replace lifecycle transition apply path with lookback snapshot apply flow in apps/pipeline/src/orchestration/jobs/trend_lifecycle_service.py
- [x] T020 [US1] Update per-series runtime execution to evaluate all applicable lookbacks in apps/pipeline/src/orchestration/jobs/trend_runtime_processor.py
- [x] T021 [US1] Update trend processing asset orchestration wiring for lookback outputs in apps/pipeline/src/orchestration/jobs/trend_processing_asset.py
- [x] T022 [US1] Add/refresh runtime error mappings for per-lookback failures in apps/pipeline/src/orchestration/jobs/trend_errors.py
- [x] T023 [US1] Add reclassification runtime coverage for lookback snapshots in apps/pipeline/src/orchestration/jobs/trend_backfill_service.py

**Checkpoint**: US1 persists deterministic lookback snapshots + canonical descriptor and is independently testable.

---

## Phase 4: User Story 2 - Serve Current Trend Across List and Detail Responses (Priority: P2)

**Goal**: Expose canonical descriptor on all dataset-summary responses and preserve dataset-detail canonical + lookback snapshot responses for direct client rendering.

**Independent Test**: Request dataset list and dataset detail APIs and validate every dataset row includes canonical descriptor data for direct rendering, while detail responses still include lookback applicability context.

### Tests for User Story 2

- [x] T024 [P] [US2] Add dataset detail canonical descriptor contract tests in apps/backend/tests/contract/test_dataset_detail_canonical_trend_contract.py
- [x] T025 [P] [US2] Add lookback snapshot response validation tests in apps/backend/tests/contract/test_dataset_detail_lookback_snapshot_contract.py
- [x] T026 [P] [US2] Add repository query integration tests for latest canonical descriptor reads in apps/backend/tests/integration/test_dataset_detail_canonical_trend_query.py
- [x] T027 [P] [US2] Add error contract tests for invalid/missing canonical payloads in apps/backend/tests/contract/test_dataset_detail_canonical_trend_error_contract.py

### Implementation for User Story 2

- [x] T028 [US2] Replace trend span contracts with canonical descriptor and lookback snapshot contracts in apps/backend/src/contract/discovery_trends.py
- [x] T029 [US2] Replace dataset detail trend models with canonical payload models in apps/backend/src/contract/query/dataset_detail_query.py
- [x] T030 [US2] Implement repository reads for canonical descriptor and lookback snapshots in apps/backend/src/query/dataset_discovery_persisted_repository.py
- [x] T031 [US2] Replace service-level trend span projection with canonical descriptor projection in apps/backend/src/query/dataset_discovery_service.py
- [x] T032 [US2] Remove or deprecate span normalization path no longer required in apps/backend/src/query/trend_span_mapper.py
- [x] T033 [US2] Ensure API server contract wiring includes new canonical fields in apps/backend/src/http_api_server.py

**Checkpoint**: US2 serves canonical trend descriptor payloads and remains independently testable.

### Additional Tests for User Story 2 Scope Revision

- [ ] T051 [P] [US2] Add dataset summary contract tests for canonical trend descriptors in apps/backend/tests/contract/test_dataset_summary_canonical_trend_contract.py
- [ ] T052 [P] [US2] Add recent dataset updates contract tests for summary-level canonical trends in apps/backend/tests/contract/test_dataset_recent_updates_canonical_trend_contract.py
- [ ] T053 [P] [US2] Add persisted repository integration tests for list-surface canonical descriptor projection in apps/backend/tests/contract/test_dataset_discovery_persisted_repository_contract.py
- [ ] T054 [P] [US2] Add discovery client mapping tests for summary-level canonical descriptors in apps/frontend/tests/discovery-client-catalog-trend.test.ts

### Additional Implementation for User Story 2 Scope Revision

- [ ] T055 [US2] Extend shared dataset summary contracts to require canonical trend descriptors in apps/backend/src/contract/query/dataset_search_query.py and apps/backend/src/contract/query/dataset_recent_updates_query.py
- [ ] T056 [US2] Add summary-level canonical trend projection helpers to persisted discovery queries in apps/backend/src/query/dataset_discovery_persisted_repository.py
- [ ] T057 [US2] Update discovery service list/search/recent response assembly to include canonical trend descriptors in apps/backend/src/query/dataset_discovery_service.py
- [ ] T058 [US2] Extend frontend dataset summary and recent-update types for canonical descriptors in apps/frontend/src/lib/api/discovery-types.ts
- [ ] T059 [US2] Update frontend discovery client normalization for dataset list and recent dataset payloads in apps/frontend/src/lib/api/discovery-client.ts

---

## Phase 5: User Story 3 - Show a Single Informative Trend Indicator (Priority: P3)

**Goal**: Render one shared arrow-based trend indicator at the far right of dataset rows and adjacent to the `Historical Trend` heading from API-provided canonical descriptor data only.

**Independent Test**: Open dataset list and detail pages and verify the arrow indicator renders the correct directional state or unavailable state in the required positions, with no overlay components and no client-side weighting logic.

### Tests for User Story 3

- [x] T034 [P] [US3] Add dataset detail chip rendering tests in apps/frontend/tests/components/DatasetTrendChip.test.tsx
- [x] T035 [P] [US3] Add dataset detail no-overlay regression tests in apps/frontend/tests/components/DatasetDetailNoOverlay.test.tsx
- [x] T036 [P] [US3] Add discovery client canonical payload mapping tests in apps/frontend/tests/discovery-client-canonical-trend.test.ts

### Implementation for User Story 3

- [x] T037 [US3] Add reusable canonical trend chip component in apps/frontend/src/components/discovery/DatasetTrendChip.tsx
- [x] T038 [US3] Update dataset detail analysis composition to use DatasetTrendChip in apps/frontend/src/components/discovery/DatasetDetailAnalysis.tsx
- [x] T039 [US3] Remove trend overlay controller usage from chart composition in apps/frontend/src/components/discovery/ObservationsChart.tsx
- [x] T040 [US3] Remove obsolete overlay implementation in apps/frontend/src/components/trends/TrendOverlayLayer.tsx
- [x] T041 [US3] Remove obsolete tooltip controller implementation in apps/frontend/src/components/trends/TrendTooltipController.tsx
- [x] T042 [US3] Update frontend API response mapping for canonical descriptor fields in apps/frontend/src/lib/api/discovery-client.ts
- [x] T043 [US3] Update frontend discovery trend type definitions for canonical descriptor in apps/frontend/src/lib/api/discovery-trend-types.ts and apps/frontend/src/lib/api/discovery-types.ts

**Checkpoint**: US3 UI is simplified to a single API-driven chip and independently testable.

### Additional Tests for User Story 3 Scope Revision

- [ ] T060 [P] [US3] Add shared trend indicator state-mapping tests in apps/frontend/tests/components/DatasetTrendIndicator.test.tsx
- [ ] T061 [P] [US3] Add shared dataset-row indicator placement tests in apps/frontend/tests/components/UnifiedDatasetRowTrendIndicator.test.tsx
- [ ] T062 [P] [US3] Add dataset-detail heading indicator placement tests in apps/frontend/tests/components/DatasetDetailTrendIndicatorPlacement.test.tsx
- [ ] T063 [P] [US3] Add responsive/unavailable indicator regression tests in apps/frontend/tests/components/DatasetTrendIndicatorResponsive.test.tsx

### Additional Implementation for User Story 3 Scope Revision

- [ ] T064 [US3] Add shared directional trend indicator component in apps/frontend/src/components/discovery/DatasetTrendIndicator.tsx
- [ ] T065 [US3] Update shared dataset-row props and layout to render the right-aligned trend indicator in apps/frontend/src/components/discovery/UnifiedDatasetRow.tsx and apps/frontend/src/components/discovery/DiscoveryFeedList.tsx
- [ ] T066 [US3] Update unified row mappers to pass canonical trend descriptor data into shared row rendering in apps/frontend/src/components/discovery/unified-dataset-row-mappers.ts
- [ ] T067 [US3] Update dataset detail analysis heading composition to render DatasetTrendIndicator beside `Historical Trend` in apps/frontend/src/components/discovery/DatasetDetailAnalysis.tsx
- [ ] T068 [US3] Remove or deprecate obsolete chip-only detail rendering in apps/frontend/src/components/discovery/DatasetTrendChip.tsx and related imports under apps/frontend/src/components/discovery/
- [ ] T069 [US3] Update recent updates and catalog list consumers to rely on shared row-level trend indicator rendering in apps/frontend/src/components/discovery/RecentUpdatesFeed.tsx and apps/frontend/src/components/discovery/DatasetCatalogList.tsx

---

## Phase 6: Polish & Cross-Cutting Concerns

**Purpose**: Hardening, docs, and mandatory quality gates across all stories.

- [x] T044 [P] Update feature documentation and execution notes in specs/044-multi-horizon-trends/quickstart.md and specs/044-multi-horizon-trends/research.md
- [x] T045 [P] Update AGENTS guidance for canonical trend descriptor behavior in AGENTS.md
- [x] T046 Run focused backend/pipeline/library tests for modified files via apps/backend/tests, apps/pipeline/tests/orchestration, and libs/trend_analysis/tests
- [x] T047 Run focused frontend checks via apps/frontend/tests, `pnpm --dir apps/frontend typecheck`, and `pnpm --dir apps/frontend exec biome check .`
- [x] T048 Run full repository stop gate `pnpm exec nx run-many -t test --all` from repository root
- [x] T049 Run full repository coverage gate `pnpm exec nx run-many -t coverage --all` from repository root
- [x] T050 Run end-to-end manual verification from clean stack using commands in specs/044-multi-horizon-trends/quickstart.md
- [ ] T070 [P] Update revised feature documentation and execution notes for list/detail indicator behavior in specs/044-multi-horizon-trends/quickstart.md and specs/044-multi-horizon-trends/research.md
- [ ] T071 [P] Update contract and planning artifacts to reflect completed scope revision in specs/044-multi-horizon-trends/contracts/discovery-lookback-trends.openapi.yaml, specs/044-multi-horizon-trends/plan.md, and specs/044-multi-horizon-trends/data-model.md
- [ ] T072 Run focused backend verification for revised list/detail trend payload paths via apps/backend/tests and apps/backend/tests/contract
- [ ] T073 Run focused frontend verification for shared indicator rendering via apps/frontend/tests, `pnpm --dir apps/frontend typecheck`, and `pnpm --dir apps/frontend exec biome check .`
- [ ] T074 Run full repository stop gate `pnpm exec nx run-many -t test --all` from repository root after revised list/detail indicator changes
- [ ] T075 Run full repository coverage gate `pnpm exec nx run-many -t coverage --all` from repository root after revised list/detail indicator changes
- [ ] T076 Run end-to-end manual verification from clean stack for dataset lists + dataset detail indicator behavior using commands in specs/044-multi-horizon-trends/quickstart.md

---

## Dependencies & Execution Order

### Phase Dependencies

- **Phase 1 (Setup)**: No dependencies.
- **Phase 2 (Foundational)**: Depends on Phase 1 and blocks all user stories.
- **Phase 3 (US1)**: Depends on Phase 2.
- **Phase 4 (US2)**: Depends on Phase 2 and US1 persistence artifacts.
- **Phase 5 (US3)**: Depends on Phase 4 API contract completion.
- **Phase 6 (Polish)**: Depends on all user stories.

### User Story Dependencies

- **US1 (P1)**: No dependency on other user stories; this is MVP scope.
- **US2 (P2)**: Depends on US1 data persistence model and canonical descriptor writes.
- **US3 (P3)**: Depends on US2 API payload availability.

### Within Each User Story

- Write tests first and confirm they fail.
- Implement model/repository logic before service/controller wiring.
- Complete story-level checks before advancing.

## Parallel Opportunities

- Phase 1: T002 and T003 can run in parallel.
- Phase 2: T005, T006, T007, and T008 can run in parallel after T004 starts.
- US1: T010-T013 can run in parallel; T014-T017 can be split between library model and weighting logic.
- US2: T024-T027 and T051-T054 can run in parallel; T028/T029 and T055 can run in parallel before T056/T057.
- US3: T034-T036 and T060-T063 can run in parallel; T064 and T066 can progress in parallel before T065/T067 integration.

### Parallel Example: User Story 1

```bash
# Parallel test authoring for US1
Task: "T010 [US1] libs/trend_analysis/tests/test_multi_lookback_classifier.py"
Task: "T011 [US1] libs/trend_analysis/tests/test_canonical_descriptor_weighting.py"
Task: "T012 [US1] apps/pipeline/tests/orchestration/test_trend_runtime_processor_lookbacks.py"
Task: "T013 [US1] apps/pipeline/tests/orchestration/test_trend_runtime_processor_idempotency.py"
```

### Parallel Example: User Story 2

```bash
# Parallel contract + integration test setup for US2
Task: "T024 [US2] apps/backend/tests/contract/test_dataset_detail_canonical_trend_contract.py"
Task: "T025 [US2] apps/backend/tests/contract/test_dataset_detail_lookback_snapshot_contract.py"
Task: "T026 [US2] apps/backend/tests/integration/test_dataset_detail_canonical_trend_query.py"
Task: "T051 [US2] apps/backend/tests/contract/test_dataset_summary_canonical_trend_contract.py"
Task: "T052 [US2] apps/backend/tests/contract/test_dataset_recent_updates_canonical_trend_contract.py"
Task: "T053 [US2] apps/backend/tests/contract/test_dataset_discovery_persisted_repository_contract.py"
```

### Parallel Example: User Story 3

```bash
# Parallel frontend test scaffolding for US3
Task: "T034 [US3] apps/frontend/tests/components/DatasetTrendChip.test.tsx"
Task: "T035 [US3] apps/frontend/tests/components/DatasetDetailNoOverlay.test.tsx"
Task: "T036 [US3] apps/frontend/tests/discovery-client-canonical-trend.test.ts"
Task: "T060 [US3] apps/frontend/tests/components/DatasetTrendIndicator.test.tsx"
Task: "T061 [US3] apps/frontend/tests/components/UnifiedDatasetRowTrendIndicator.test.tsx"
Task: "T062 [US3] apps/frontend/tests/components/DatasetDetailTrendIndicatorPlacement.test.tsx"
```

---

## Implementation Strategy

### MVP First (US1 Only)

1. Complete Phase 1 and Phase 2.
2. Complete Phase 3 (US1).
3. Validate ingest -> pipeline persistence for lookback snapshots and canonical descriptor.
4. Run relevant tests and quality checks before moving on.

### Incremental Delivery

1. Deliver US1 persistence model (MVP).
2. Deliver US2 API and contract migration for list + detail canonical descriptor payloads.
3. Deliver US3 shared arrow-indicator rendering across dataset rows and dataset detail.
4. Finish with polish, docs, and full monorepo gates.

### Format Validation

- All tasks use required checklist format: `- [ ] T### [P?] [US?] Description with file path`.
- Story labels are present only in user-story phases.
- Parallelizable tasks are explicitly marked `[P]`.
