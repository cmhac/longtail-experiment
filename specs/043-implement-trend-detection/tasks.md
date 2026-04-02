# Tasks: End-to-End Trend Detection

**Input**: Design documents from `/specs/043-implement-trend-detection/`
**Prerequisites**: plan.md, spec.md, research.md, data-model.md, contracts/discovery-trends.openapi.yaml, quickstart.md

**Tests**: Test tasks are REQUIRED. This feature explicitly requires red/green TDD at each stage and repeated quality checks. Before any commit and before agent handoff/stop, `pnpm exec nx run-many -t test --all` MUST pass. Before any commit, `pnpm exec nx run-many -t coverage --all` MUST pass with >= 90% thresholds.

**Organization**: Tasks are grouped by user story so each story is independently implementable and testable.

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Establish feature scaffolding, shared fixtures, and quality workflow anchors.

- [x] T001 Create trend-analysis library package scaffold in libs/trend_analysis/pyproject.toml
- [x] T002 [P] Create trend-analysis source package init in libs/trend_analysis/src/trend_analysis/**init**.py
- [x] T003 [P] Create trend-analysis test package init in libs/trend_analysis/tests/**init**.py
- [x] T004 [P] Add feature-local test fixtures for trend scenarios in libs/trend_analysis/tests/fixtures/trend_series_fixtures.py
- [x] T005 [P] Add feature-level quality command section for developers in specs/043-implement-trend-detection/quickstart.md
- [x] T006 Add monorepo execution wiring for the new trend library targets in libs/trend_analysis/project.json

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Cross-story foundation for persistence, contracts, and orchestration wiring.

**CRITICAL**: Complete this phase before user story work.

- [x] T007 Add trend lifecycle table migration script in libs/db/alembic/versions/0011_trend_lifecycle_tables.py
- [x] T008 [P] Add SQLAlchemy models for trend persistence in libs/db/src/db/models/trends.py
- [x] T009 [P] Add DB repository interface for trend lifecycle operations in apps/pipeline/src/orchestration/resources/trend_repository.py
- [x] T010 [P] Add backend contract types for trend payloads in apps/backend/src/contract/discovery_trends.py
- [x] T011 [P] Add shared frontend trend payload types in apps/frontend/src/lib/api/discovery-trend-types.ts
- [x] T012 Define/verify Dagster asset dependency entry point for trend stage in apps/pipeline/src/orchestration/definitions.py
- [x] T013 Add trend feature toggles/required env validation guardrails in apps/pipeline/src/orchestration/runtime.py
- [x] T014 Add foundational regression test for trend table schema invariants in libs/db/tests/test_trend_schema_invariants.py
- [x] T015 Add foundational contract smoke test for discovery trend schemas in apps/backend/tests/contract/test_discovery_trend_contract_schema.py

**Checkpoint**: DB, contract, and orchestration foundations are ready.

---

## Phase 3: User Story 1 - Persist Current and Historical Trends (Priority: P1) 🎯 MVP

**Goal**: Persist deterministic trend lifecycle state from newly ingested observations through downstream trend asset processing.

**Independent Test**: Ingest one dataset with known transitions; verify lifecycle row create/continue/end behavior, branch-scoped failures, and retry idempotency.

### Tests for User Story 1 (REQUIRED)

- [x] T016 [P] [US1] Add library unit tests for deterministic outcomes in libs/trend_analysis/tests/test_deterministic_outputs.py
- [x] T017 [P] [US1] Add library unit tests for insufficient_data/no_significant_trend outcomes and hardcoded-defaults-only behavior (no runtime config overrides) in libs/trend_analysis/tests/test_terminal_outcomes.py
- [x] T018 [P] [US1] Add library unit tests for cadence inference and explicit failure cases in libs/trend_analysis/tests/test_cadence_and_failures.py
- [x] T019 [P] [US1] Add pipeline unit tests for signature change transitions and analysis-version identity coupled to library version in apps/pipeline/tests/orchestration/test_trend_transition_logic.py
- [x] T020 [P] [US1] Add pipeline integration tests for branch-scoped failure handling in apps/pipeline/tests/orchestration/test_trend_asset_failure_scope.py
- [x] T021 [P] [US1] Add pipeline integration tests for state-based idempotent retries in apps/pipeline/tests/orchestration/test_trend_asset_retry_idempotency.py
- [x] T022 [P] [US1] Add pipeline integration tests for no-op successful outcomes in apps/pipeline/tests/orchestration/test_trend_asset_noop_outcomes.py

### Implementation for User Story 1

- [x] T023 [US1] Implement trend analysis result models with analysis-version identity derived from released library version in libs/trend_analysis/src/trend_analysis/models.py
- [x] T024 [US1] Implement trend classification core algorithm in libs/trend_analysis/src/trend_analysis/classifier.py
- [x] T025 [US1] Implement cadence inference and seasonality validation helpers in libs/trend_analysis/src/trend_analysis/cadence.py
- [x] T026 [US1] Implement trend signature comparison logic in apps/pipeline/src/orchestration/jobs/trend_signature.py
- [x] T027 [US1] Implement trend lifecycle persistence service in apps/pipeline/src/orchestration/jobs/trend_lifecycle_service.py
- [x] T028 [US1] Implement per-series downstream trend asset execution in apps/pipeline/src/orchestration/jobs/trend_processing_asset.py
- [x] T029 [US1] Wire fetch/update to trend downstream asset dependency in apps/pipeline/src/orchestration/definitions.py
- [x] T030 [US1] Implement branch-scoped failure mapping in apps/pipeline/src/orchestration/jobs/parallel_source_executor.py
- [x] T031 [US1] Implement first-run historical backfill decision path and library-release-change full rerun/re-backfill trigger flow in apps/pipeline/src/orchestration/jobs/trend_backfill_service.py
- [x] T032 [US1] Implement trend repository SQL operations in libs/db/src/db/repositories/postgres_trend_repository.py
- [x] T033 [US1] Add explicit no-op outcome metadata emission in apps/pipeline/src/orchestration/jobs/trend_processing_asset.py
- [x] T034 [US1] Add prototype-guided regression scenarios derived from real-data spike in libs/trend_analysis/tests/test_real_series_behavior.py
- [x] T035 [US1] Add prototype-guided multi-horizon regression scenarios in libs/trend_analysis/tests/test_multi_horizon_behavior.py

### Verification and Quality Loop for User Story 1

- [x] T036 [US1] Run red/green TDD cycle checkpoints for library and pipeline tests in specs/043-implement-trend-detection/quickstart.md
- [x] T037 [US1] Run repeated project quality checks during US1 iteration in specs/043-implement-trend-detection/quickstart.md
- [x] T038 [US1] Perform manual local-stack validation for US1 using one-off ingest commands in specs/043-implement-trend-detection/quickstart.md

**Checkpoint**: US1 provides full trend persistence and lifecycle behavior independently.

---

## Phase 4: User Story 2 - Serve Trends Through Discovery API and Feed (Priority: P2)

**Goal**: Expose trend lifecycle data through discovery API surfaces and unified recent updates ordering.

**Independent Test**: Call dataset detail and recent updates APIs after trend writes; verify payload shapes, ordering by trend start period, and malformed-payload error semantics.

### Tests for User Story 2 (REQUIRED)

- [x] T039 [P] [US2] Add contract tests for trend feed item schema in apps/backend/tests/contract/test_recent_updates_trend_contract.py
- [x] T040 [P] [US2] Add contract tests for dataset detail trend span schema and no-trend baseline response compatibility in apps/backend/tests/contract/test_dataset_detail_trend_spans_contract.py
- [x] T041 [P] [US2] Add contract test for malformed trend payload error response in apps/backend/tests/contract/test_dataset_detail_trend_payload_error_contract.py
- [x] T042 [P] [US2] Add integration test for unified recent feed ordering by trend start period while preserving baseline behavior for datasets without trend records in apps/backend/tests/integration/test_recent_updates_trend_ordering.py
- [x] T043 [P] [US2] Add integration test for trend span non-overlap normalization output in apps/backend/tests/integration/test_dataset_detail_trend_normalization.py

### Implementation for User Story 2

- [x] T044 [US2] Implement trend feed query composition in apps/backend/src/query/dataset_discovery_persisted_repository.py
- [x] T045 [US2] Implement trend span normalization mapper in apps/backend/src/query/trend_span_mapper.py
- [x] T046 [US2] Extend recent updates service to include trend events in apps/backend/src/query/dataset_discovery_service.py
- [x] T047 [US2] Extend dataset detail service to include trend spans in apps/backend/src/query/dataset_discovery_service.py
- [x] T048 [US2] Implement deterministic malformed trend payload error handling in apps/backend/src/query/dataset_discovery_service.py
- [x] T049 [US2] Update API contract definitions to match implemented fields in apps/backend/src/contract/discovery_trends.py
- [x] T050 [US2] Reconcile OpenAPI contract document with backend implementation in specs/043-implement-trend-detection/contracts/discovery-trends.openapi.yaml

### Verification and Quality Loop for User Story 2

- [x] T051 [US2] Run red/green TDD cycle checkpoints for backend contract/service tests in specs/043-implement-trend-detection/quickstart.md
- [x] T052 [US2] Run repeated backend quality checks and pre-commit during US2 iteration in specs/043-implement-trend-detection/quickstart.md
- [x] T053 [US2] Perform manual API verification for US2 via one-off local-stack requests in specs/043-implement-trend-detection/quickstart.md

**Checkpoint**: US2 independently serves trend-aware API payloads and ordering.

---

## Phase 5: User Story 3 - Visualize Trends in UI (Priority: P3)

**Goal**: Render trend overlays and interactions in discovery feed and dataset detail UI with clarified accessibility and interaction constraints.

**Independent Test**: In UI, verify interleaved trend feed entries, non-overlapping overlays, color + pattern/icon encoding, hover/tap tooltip parity, single active tooltip, and error-state behavior.

### Tests for User Story 3 (REQUIRED)

- [x] T054 [P] [US3] Add component tests for feed trend item rendering in apps/frontend/tests/components/TrendFeedItem.test.tsx
- [x] T055 [P] [US3] Add component tests for non-overlapping trend span rendering in apps/frontend/tests/components/TrendOverlayLayer.test.tsx
- [x] T056 [P] [US3] Add component tests for single active tooltip behavior in apps/frontend/tests/components/TrendTooltipController.test.tsx
- [x] T057 [P] [US3] Add component tests for desktop hover and touch tap-to-pin behavior in apps/frontend/tests/components/TrendOverlayInteractions.test.tsx
- [x] T058 [P] [US3] Add accessibility tests for dual direction encoding in apps/frontend/tests/components/TrendDirectionAccessibility.test.tsx
- [x] T059 [P] [US3] Add route tests for malformed trend-payload hard-fail and no-trend baseline non-error dataset detail behavior in apps/frontend/tests/app/dataset-detail-trend-error-state.test.tsx

### Implementation for User Story 3

- [x] T060 [US3] Implement shared trend overlay primitives in apps/frontend/src/components/trends/TrendOverlayLayer.tsx
- [x] T061 [US3] Implement shared trend tooltip controller with single-active policy in apps/frontend/src/components/trends/TrendTooltipController.tsx
- [x] T062 [US3] Implement shared trend direction visual tokens (color + pattern/icon) in apps/frontend/src/components/trends/trendDirectionTokens.ts
- [x] T063 [US3] Integrate trend overlays into dataset detail chart in apps/frontend/src/components/discovery/ObservationsChart.tsx
- [x] T064 [US3] Implement desktop hover and touch tap-to-pin handlers in apps/frontend/src/components/trends/TrendTooltipController.tsx
- [x] T065 [US3] Implement dataset detail hard-fail UI state for malformed trend payload in apps/frontend/src/app/datasets/[id]/page.tsx
- [x] T066 [US3] Render trend events in unified recent feed items in apps/frontend/src/components/discovery/RecentUpdatesFeed.tsx
- [x] T067 [US3] Remove unused trends tab from navigation in apps/frontend/src/shell/navbar-config.ts
- [x] T068 [US3] Enforce default dataset detail navigation behavior from trend feed item clicks in apps/frontend/src/components/discovery/RecentUpdatesFeed.tsx

### Verification and Quality Loop for User Story 3

- [x] T069 [US3] Run red/green TDD cycle checkpoints for frontend tests in specs/043-implement-trend-detection/quickstart.md
- [x] T070 [US3] Run repeated frontend quality checks and pre-commit during US3 iteration in specs/043-implement-trend-detection/quickstart.md
- [x] T071 [US3] Perform manual desktop and touch-viewport UI validation for US3 in specs/043-implement-trend-detection/quickstart.md

**Checkpoint**: US3 independently delivers chart and feed trend UI behavior.

---

## Phase 6: Polish & Cross-Cutting Concerns

**Purpose**: End-to-end hardening, documentation alignment, and mandatory gates.

- [x] T072 [P] Reconcile feature docs with final implementation details in specs/043-implement-trend-detection/research.md
- [x] T073 [P] Reconcile feature docs with final implementation details in specs/043-implement-trend-detection/data-model.md
- [x] T074 [P] Reconcile feature docs with final implementation details in specs/043-implement-trend-detection/quickstart.md
- [x] T075 [P] Reconcile API contract docs with implemented endpoints in specs/043-implement-trend-detection/contracts/discovery-trends.openapi.yaml
- [x] T076 Run full pre-commit hooks after cross-story integration in .pre-commit-config.yaml
- [x] T077 Run full monorepo tests stop gate and capture results in specs/043-implement-trend-detection/quickstart.md
- [x] T078 Run full monorepo coverage stop gate and capture results in specs/043-implement-trend-detection/quickstart.md
- [x] T079 Perform end-to-end manual stack validation across ingestion->API->UI in specs/043-implement-trend-detection/quickstart.md

---

## Dependencies & Execution Order

### Phase Dependencies

- Phase 1 (Setup): starts immediately.
- Phase 2 (Foundational): depends on Phase 1 and blocks all user stories.
- Phase 3 (US1): depends on Phase 2.
- Phase 4 (US2): depends on Phase 2 and consumes US1 persistence outputs for realistic integration tests.
- Phase 5 (US3): depends on Phase 2 and consumes US2 API payloads.
- Phase 6 (Polish): depends on completion of US1, US2, and US3.

### User Story Dependencies

- US1 (P1): no story dependency after foundational phase; MVP scope.
- US2 (P2): depends on US1 trend persistence data for full validation, but service work can begin once foundational phase is complete.
- US3 (P3): depends on US2 API payload shape and US1 data availability for full independent verification.

### Within Each User Story

- Write tests first and verify they fail.
- Implement minimum code to pass tests.
- Refactor safely with tests passing.
- Re-run quality checks and manual validations before marking story complete.

## Parallel Execution Examples

### US1 Parallel Example

- T016, T017, T018 can run in parallel (library tests in separate files).
- T019, T020, T021, T022 can run in parallel (pipeline tests in separate files).
- T023 and T025 can run in parallel; T024 depends on them.

### US2 Parallel Example

- T039, T040, T041 can run in parallel (contract tests in separate files).
- T042 and T043 can run in parallel (integration tests in separate files).
- T044 and T045 can run in parallel; T046 and T047 depend on them.

### US3 Parallel Example

- T054, T055, T056, T057, T058, T059 can run in parallel (frontend tests in separate files).
- T060, T061, T062 can run in parallel (shared component primitives).
- T066 and T067 can run in parallel after shared primitives are available.

## Implementation Strategy

### MVP First

1. Complete Phase 1 and Phase 2.
2. Complete US1 (Phase 3) end-to-end.
3. Validate US1 independently via automated + manual tests.
4. Demo/deploy MVP behavior before expanding scope.

### Incremental Delivery

1. Add US2 after US1 stabilizes; validate API contracts and feed behavior.
2. Add US3 after US2 stabilizes; validate frontend interactions and accessibility.
3. Run Phase 6 global hardening and mandatory stop gates.

### Quality and Manual-Testing Discipline

- Repeat `pre-commit run --all-files` throughout implementation, not just at the end.
- Use red/green TDD loops for every stage and story.
- Restart and use the local Docker Compose environment for one-off manual validation at each stage.
- Treat any manual-test failure as blocking and fix before continuing.
