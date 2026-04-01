# Tasks: Multi-Horizon Trends

**Input**: Design documents from /specs/044-multi-horizon-trends/
**Prerequisites**: plan.md (required), spec.md (required for user stories), contracts/discovery-lookback-trends.openapi.yaml

**Tests**: Test tasks are REQUIRED. Every user story and foundational component MUST include automated test coverage sufficient to maintain >= 90% coverage in affected projects. Before any commit and before any AI agent stops work, the full repository suite MUST pass via pnpm exec nx run-many -t test --all; targeted tests alone are never sufficient for this stop gate. Before any commit, monorepo coverage MUST pass via pnpm exec nx run-many -t coverage --all with >= 90% thresholds in every project.

**Organization**: Tasks are grouped by phase to enable sequential phase completion, with parallel tasks within each phase.

## Format: [ID] [P?] [Story] Description

- [P]: Can run in parallel (different files, no dependencies)
- [Story]: Which user story this task belongs to (for example US1, US2, US3)
- Include exact file paths in descriptions

## Path Conventions

- Frontend app: apps/frontend/src/, apps/frontend/tests/
- Backend app: apps/backend/src/, apps/backend/tests/
- Pipeline app: apps/pipeline/src/, apps/pipeline/tests/
- Shared DB lib: libs/db/
- Trend analysis lib: libs/trend_analysis/
- Feature docs: specs/044-multi-horizon-trends/

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Validate artifact alignment, capture pre-change schema seam notes, and establish the implementation tracking checklist before any code is written.

- [x] T001 Validate feature artifacts are aligned in specs/044-multi-horizon-trends/spec.md, specs/044-multi-horizon-trends/plan.md, and specs/044-multi-horizon-trends/contracts/discovery-lookback-trends.openapi.yaml
- [ ] T002 [P] Capture pre-change schema and repository seam notes in specs/044-multi-horizon-trends/research.md
- [ ] T003 [P] Add or update implementation tracking checklist in specs/044-multi-horizon-trends/checklists/requirements.md

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Create the persistence layer, shared protocol scaffolding, and contract stubs that all subsequent phases depend on.

**CRITICAL**: No user story work can begin until this phase is complete.

- [ ] T004 Create Alembic migration for lookback snapshots and canonical descriptors in libs/db/alembic/versions/0012_lookback_trend_snapshots.py
- [ ] T005 [P] Add SQLAlchemy model definitions for new lookback persistence tables in libs/db/src/db/models.py
- [ ] T006 [P] Add shared pipeline repository protocol types for lookback/canonical writes in apps/pipeline/src/orchestration/resources/trend_repository.py
- [ ] T007 [P] Add backend contract model scaffolding for canonical trend descriptor payloads in apps/backend/src/contract/query/dataset_detail_query.py
- [ ] T008 [P] Add frontend API type scaffolding for canonical trend descriptor payloads in apps/frontend/src/lib/api/discovery-types.ts
- [ ] T009 Add foundational migration/repository contract tests in libs/db/tests/test_lookback_trend_migration_contract.py and apps/pipeline/tests/orchestration/test_trend_repository_contract.py

**Checkpoint**: Persistence schema, shared protocol stubs, and contract scaffolds are in place — user story implementation can now begin.

---

## Phase 3: User Story 1 - Pipeline Computes Multi-Lookback Trend Snapshots (Priority: P1) 🎯 MVP

**Goal**: The ingest pipeline evaluates trend for each fixed lookback window and persists a lookback snapshot plus a canonical weighted descriptor per dataset.

**Independent Test**: Run the trend backfill service against a dataset with sufficient history and verify `lookback_trend_snapshots` rows are written for each applicable window; datasets with insufficient history receive `insufficient_data` classifications.

### Tests for User Story 1 (REQUIRED)

- [ ] T010 [P] [US1] Add classifier lookback-catalog and determinism unit tests in libs/trend_analysis/tests/test_multi_lookback_classifier.py
- [ ] T011 [P] [US1] Add canonical weighting determinism tests in libs/trend_analysis/tests/test_canonical_descriptor_weighting.py
- [ ] T012 [P] [US1] Add pipeline lookback applicability and no-signal tests in apps/pipeline/tests/orchestration/test_trend_runtime_processor_lookbacks.py
- [ ] T013 [P] [US1] Add pipeline idempotency and partial-failure isolation tests in apps/pipeline/tests/orchestration/test_trend_runtime_processor_idempotency.py

### Implementation for User Story 1

- [ ] T014 [US1] Implement multi-lookback evaluation entrypoint and result model exports in libs/trend_analysis/src/trend_analysis/__init__.py
- [ ] T015 [US1] Implement fixed lookback evaluation logic in libs/trend_analysis/src/trend_analysis/classifier.py
- [ ] T016 [US1] Implement lookback/canonical descriptor domain models in libs/trend_analysis/src/trend_analysis/models.py
- [ ] T017 [US1] Implement weighting/version metadata for canonical descriptors in libs/trend_analysis/src/trend_analysis/version.py
- [ ] T018 [US1] Implement lookback snapshot and canonical descriptor write methods in apps/pipeline/src/orchestration/resources/postgres_trend_repository.py
- [ ] T019 [US1] Replace lifecycle transition apply path with lookback snapshot apply flow in apps/pipeline/src/orchestration/jobs/trend_lifecycle_service.py
- [ ] T020 [US1] Update per-series runtime execution to evaluate all applicable lookbacks in apps/pipeline/src/orchestration/jobs/trend_runtime_processor.py
- [ ] T021 [US1] Update trend processing asset orchestration wiring for lookback outputs in apps/pipeline/src/orchestration/jobs/trend_processing_asset.py
- [ ] T022 [US1] Add/refresh runtime error mappings for per-lookback failures in apps/pipeline/src/orchestration/jobs/trend_errors.py
- [ ] T023 [US1] Add reclassification runtime coverage for lookback snapshots in apps/pipeline/src/orchestration/jobs/trend_backfill_service.py

**Checkpoint**: Pipeline computes and persists lookback snapshots and canonical descriptors; determinism and idempotency tests pass.

---

## Phase 4: User Story 2 - Backend Serves Canonical Trend Descriptor (Priority: P2)

**Goal**: The dataset detail API endpoint includes a `trend` field with canonical descriptor and per-window lookback snapshots read from pre-computed PostgreSQL rows.

**Independent Test**: Fetch a dataset detail response and confirm `trend.canonical` includes a weighted direction and version string; `trend.lookbacks` includes one entry per computed window.

### Tests for User Story 2 (REQUIRED)

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

**Checkpoint**: Dataset detail API returns `trend` payload; all backend contract and integration tests pass.

---

## Phase 5: User Story 3 - Frontend Renders Canonical Trend Chip (Priority: P3)

**Goal**: The dataset detail page renders a compact `DatasetTrendChip` from the backend canonical payload; obsolete overlay components are removed.

**Independent Test**: Open a dataset detail page that has computed trend snapshots; verify the `DatasetTrendChip` renders a direction badge; verify pages for datasets with no snapshots show unavailable state without error.

### Tests for User Story 3 (REQUIRED)

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

**Checkpoint**: Chip renders correctly; removed overlay files cause no import errors; all frontend tests pass.

---

## Phase 6: Polish

**Purpose**: Update documentation, AGENTS.md guidance, and run mandatory full-suite stop gates.

- [ ] T044 [P] Update feature documentation and execution notes in specs/044-multi-horizon-trends/quickstart.md and specs/044-multi-horizon-trends/research.md
- [ ] T045 [P] Update AGENTS guidance for canonical trend descriptor behavior in AGENTS.md
- [ ] T046 Run focused backend/pipeline/library tests for modified files via apps/backend/tests, apps/pipeline/tests/orchestration, and libs/trend_analysis/tests
- [ ] T047 Run focused frontend checks via apps/frontend/tests, `pnpm --dir apps/frontend typecheck`, and `pnpm --dir apps/frontend exec biome check .`
- [ ] T048 Run full repository stop gate `pnpm exec nx run-many -t test --all` from repository root
- [ ] T049 Run full repository coverage gate `pnpm exec nx run-many -t coverage --all` from repository root
- [ ] T050 Run end-to-end manual verification from clean stack using commands in specs/044-multi-horizon-trends/quickstart.md
