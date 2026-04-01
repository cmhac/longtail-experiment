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

- [ ] T004 Create Alembic migration for lookback snapshots and canonical descriptors in libs/db/alembic/versions/0012_lookback_trend_snapshots.py
- [ ] T005 [P] Add SQLAlchemy model definitions for new lookback persistence tables in libs/db/src/db/models.py
- [ ] T006 [P] Add shared pipeline repository protocol types for lookback/canonical writes in apps/pipeline/src/orchestration/resources/trend_repository.py
- [ ] T007 [P] Add backend contract model scaffolding for canonical trend descriptor payloads in apps/backend/src/contract/query/dataset_detail_query.py
- [ ] T008 [P] Add frontend API type scaffolding for canonical trend descriptor payloads in apps/frontend/src/lib/api/discovery-types.ts
- [ ] T009 Add foundational migration/repository contract tests in libs/db/tests/test_lookback_trend_migration_contract.py and apps/pipeline/tests/orchestration/test_trend_repository_contract.py

**Checkpoint**: Foundation ready. User stories can now proceed.

---

## Phase 3: User Story 1 - Persist Observation-Level Lookback Snapshots (Priority: P1) 🎯 MVP

**Goal**: Persist deterministic per-observation lookback outcomes and canonical weighted descriptor from pipeline runtime.

**Independent Test**: Materialize a new observation and verify applicable lookback rows + canonical descriptor row are persisted idempotently.

### Tests for User Story 1

- [ ] T010 [P] [US1] Add classifier lookback-catalog and determinism unit tests in libs/trend_analysis/tests/test_multi_lookback_classifier.py
- [ ] T011 [P] [US1] Add canonical weighting determinism tests in libs/trend_analysis/tests/test_canonical_descriptor_weighting.py
- [ ] T012 [P] [US1] Add pipeline lookback applicability and no-signal tests in apps/pipeline/tests/orchestration/test_trend_runtime_processor_lookbacks.py
- [ ] T013 [P] [US1] Add pipeline idempotency and partial-failure isolation tests in apps/pipeline/tests/orchestration/test_trend_runtime_processor_idempotency.py

### Implementation for User Story 1

- [ ] T014 [US1] Implement multi-lookback evaluation entrypoint and result model exports in libs/trend_analysis/src/trend_analysis/**init**.py
- [ ] T015 [US1] Implement fixed lookback evaluation logic in libs/trend_analysis/src/trend_analysis/classifier.py
- [ ] T016 [US1] Implement lookback/canonical descriptor domain models in libs/trend_analysis/src/trend_analysis/models.py
- [ ] T017 [US1] Implement weighting/version metadata for canonical descriptors in libs/trend_analysis/src/trend_analysis/version.py
- [ ] T018 [US1] Implement lookback snapshot and canonical descriptor write methods in apps/pipeline/src/orchestration/resources/postgres_trend_repository.py
- [ ] T019 [US1] Replace lifecycle transition apply path with lookback snapshot apply flow in apps/pipeline/src/orchestration/jobs/trend_lifecycle_service.py
- [ ] T020 [US1] Update per-series runtime execution to evaluate all applicable lookbacks in apps/pipeline/src/orchestration/jobs/trend_runtime_processor.py
- [ ] T021 [US1] Update trend processing asset orchestration wiring for lookback outputs in apps/pipeline/src/orchestration/jobs/trend_processing_asset.py
- [ ] T022 [US1] Add/refresh runtime error mappings for per-lookback failures in apps/pipeline/src/orchestration/jobs/trend_errors.py
- [ ] T023 [US1] Add reclassification runtime coverage for lookback snapshots in apps/pipeline/src/orchestration/jobs/trend_backfill_service.py

**Checkpoint**: US1 persists deterministic lookback snapshots + canonical descriptor and is independently testable.

---

## Phase 4: User Story 2 - Serve Current Trend by Lookback (Priority: P2)

**Goal**: Expose canonical descriptor and optional lookback snapshots via backend dataset-detail contract.

**Independent Test**: Request dataset detail API and validate canonical descriptor payload shape, applicability states, and unsupported lookback handling.

### Tests for User Story 2

- [ ] T024 [P] [US2] Add dataset detail canonical descriptor contract tests in apps/backend/tests/contract/test_dataset_detail_canonical_trend_contract.py
- [ ] T025 [P] [US2] Add lookback snapshot response validation tests in apps/backend/tests/contract/test_dataset_detail_lookback_snapshot_contract.py
- [ ] T026 [P] [US2] Add repository query integration tests for latest canonical descriptor reads in apps/backend/tests/integration/test_dataset_detail_canonical_trend_query.py
- [ ] T027 [P] [US2] Add error contract tests for invalid/missing canonical payloads in apps/backend/tests/contract/test_dataset_detail_canonical_trend_error_contract.py

### Implementation for User Story 2

- [ ] T028 [US2] Replace trend span contracts with canonical descriptor and lookback snapshot contracts in apps/backend/src/contract/discovery_trends.py
- [ ] T029 [US2] Replace dataset detail trend models with canonical payload models in apps/backend/src/contract/query/dataset_detail_query.py
- [ ] T030 [US2] Implement repository reads for canonical descriptor and lookback snapshots in apps/backend/src/query/dataset_discovery_persisted_repository.py
- [ ] T031 [US2] Replace service-level trend span projection with canonical descriptor projection in apps/backend/src/query/dataset_discovery_service.py
- [ ] T032 [US2] Remove or deprecate span normalization path no longer required in apps/backend/src/query/trend_span_mapper.py
- [ ] T033 [US2] Ensure API server contract wiring includes new canonical fields in apps/backend/src/http_api_server.py

**Checkpoint**: US2 serves canonical trend descriptor payloads and remains independently testable.

---

## Phase 5: User Story 3 - Show a Single Informative Trend Chip (Priority: P3)

**Goal**: Remove overlay UI and render one dataset-detail chip from API-provided canonical descriptor only.

**Independent Test**: Open dataset detail page and verify no overlay components render and chip displays canonical descriptor or unavailable state without client-side weighting logic.

### Tests for User Story 3

- [ ] T034 [P] [US3] Add dataset detail chip rendering tests in apps/frontend/tests/components/DatasetTrendChip.test.tsx
- [ ] T035 [P] [US3] Add dataset detail no-overlay regression tests in apps/frontend/tests/components/DatasetDetailNoOverlay.test.tsx
- [ ] T036 [P] [US3] Add discovery client canonical payload mapping tests in apps/frontend/tests/discovery-client-canonical-trend.test.ts

### Implementation for User Story 3

- [ ] T037 [US3] Add reusable canonical trend chip component in apps/frontend/src/components/discovery/DatasetTrendChip.tsx
- [ ] T038 [US3] Update dataset detail analysis composition to use DatasetTrendChip in apps/frontend/src/components/discovery/DatasetDetailAnalysis.tsx
- [ ] T039 [US3] Remove trend overlay controller usage from chart composition in apps/frontend/src/components/discovery/ObservationsChart.tsx
- [ ] T040 [US3] Remove obsolete overlay implementation in apps/frontend/src/components/trends/TrendOverlayLayer.tsx
- [ ] T041 [US3] Remove obsolete tooltip controller implementation in apps/frontend/src/components/trends/TrendTooltipController.tsx
- [ ] T042 [US3] Update frontend API response mapping for canonical descriptor fields in apps/frontend/src/lib/api/discovery-client.ts
- [ ] T043 [US3] Update frontend discovery trend type definitions for canonical descriptor in apps/frontend/src/lib/api/discovery-trend-types.ts and apps/frontend/src/lib/api/discovery-types.ts

**Checkpoint**: US3 UI is simplified to a single API-driven chip and independently testable.

---

## Phase 6: Polish & Cross-Cutting Concerns

**Purpose**: Hardening, docs, and mandatory quality gates across all stories.

- [ ] T044 [P] Update feature documentation and execution notes in specs/044-multi-horizon-trends/quickstart.md and specs/044-multi-horizon-trends/research.md
- [ ] T045 [P] Update AGENTS guidance for canonical trend descriptor behavior in AGENTS.md
- [ ] T046 Run focused backend/pipeline/library tests for modified files via apps/backend/tests, apps/pipeline/tests/orchestration, and libs/trend_analysis/tests
- [ ] T047 Run focused frontend checks via apps/frontend/tests, `pnpm --dir apps/frontend typecheck`, and `pnpm --dir apps/frontend exec biome check .`
- [ ] T048 Run full repository stop gate `pnpm exec nx run-many -t test --all` from repository root
- [ ] T049 Run full repository coverage gate `pnpm exec nx run-many -t coverage --all` from repository root
- [ ] T050 Run end-to-end manual verification from clean stack using commands in specs/044-multi-horizon-trends/quickstart.md

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
- US2: T024-T027 can run in parallel; T028/T029 can run in parallel before T030/T031.
- US3: T034-T036 can run in parallel; T042 and T043 can run in parallel while UI component work progresses.

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
```

### Parallel Example: User Story 3

```bash
# Parallel frontend test scaffolding for US3
Task: "T034 [US3] apps/frontend/tests/components/DatasetTrendChip.test.tsx"
Task: "T035 [US3] apps/frontend/tests/components/DatasetDetailNoOverlay.test.tsx"
Task: "T036 [US3] apps/frontend/tests/discovery-client-canonical-trend.test.ts"
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
2. Deliver US2 API and contract migration.
3. Deliver US3 UI simplification to chip-only rendering.
4. Finish with polish, docs, and full monorepo gates.

### Format Validation

- All tasks use required checklist format: `- [ ] T### [P?] [US?] Description with file path`.
- Story labels are present only in user-story phases.
- Parallelizable tasks are explicitly marked `[P]`.
