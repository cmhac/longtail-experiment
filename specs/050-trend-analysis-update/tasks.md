# Tasks: Trend Analysis Upgrade

**Input**: Design documents from `/specs/050-trend-analysis-update/`
**Prerequisites**: plan.md (required), spec.md (required), research.md, data-model.md, contracts/discovery-trend-v2.openapi.yaml, quickstart.md

**Tests**: Test tasks are REQUIRED for each phase and user story.

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Prepare shared fixtures, benchmarks, and implementation scaffolding for spec 050.

- [X] T001 Create benchmark scenario manifest in `specs/050-trend-analysis-update/research/benchmark_scenarios.md`
- [X] T002 [P] Add trend-analysis test fixtures for noisy/flat/irregular/sub-daily series in `libs/trend_analysis/tests/fixtures/spec050_series.py`
- [X] T003 [P] Add backend contract fixture payloads for v2 descriptor/evidence shapes in `apps/backend/tests/fixtures/trend_v2_payloads.py`
- [X] T004 [P] Add frontend fixture payloads for v2 canonical/evidence states in `apps/frontend/tests/fixtures/trend-v2-fixtures.ts`

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Complete shared persistence and contract plumbing required by all user stories.

**⚠️ CRITICAL**: No user story implementation starts until this phase is complete.

- [X] T005 Add migration test for v2 descriptor schema changes in `libs/db/tests/test_trend_descriptor_v2_migration_contract.py`
- [X] T006 Implement v2 trend schema migration in `libs/db/alembic/versions/0016_trend_descriptor_v2_contract.py`
- [X] T007 [P] Update trend ORM models for `flat`, numeric confidence, and evidence fields in `libs/db/src/db/models/trends.py`
- [X] T008 [P] Update shared trend repository interfaces for v2 descriptors/snapshots in `libs/db/src/db/repositories/interfaces.py`
- [X] T009 Implement Postgres repository mappings for v2 persistence fields in `libs/db/src/db/repositories/postgres_trend_repository.py`
- [X] T010 [P] Add backend contract models for v2 canonical/evidence payloads in `apps/backend/src/contract/query/trend_descriptor_v2.py`
- [X] T011 [P] Add frontend API types for v2 canonical/evidence payloads in `apps/frontend/src/lib/api/trend-v2-types.ts`
- [X] T012 Validate baseline repository and contract plumbing with tests in `libs/db/tests/test_postgres_trend_repository_v2.py`

**Checkpoint**: Foundation ready; user stories can proceed.

---

## Phase 3: User Story 1 - Stable Current Trend Signal (Priority: P1) 🎯 MVP

**Goal**: Produce stable current canonical trend outputs with robust statistics, explicit `flat`, and numeric confidence.

**Independent Test**: Evaluate representative noisy and smooth series and verify current canonical direction/confidence stabilizes and correctly emits `flat` when movement is not meaningful.

### Tests for User Story 1 (REQUIRED)

- [X] T013 [P] [US1] Add Theil-Sen and confidence modifier unit tests in `libs/trend_analysis/tests/test_scoring_theilsen_kendall.py`
- [X] T014 [P] [US1] Add EWMA + cadence seasonal routing unit tests in `libs/trend_analysis/tests/test_preprocessing_and_seasonal_adjustment.py`
- [X] T015 [P] [US1] Add canonical arbitration weighting and rejection precedence tests in `libs/trend_analysis/tests/test_canonical_arbitration_v2.py`
- [X] T052 [P] [US1] Add deterministic tie-break activation threshold tests (`<= 0.05` confidence gap) in `libs/trend_analysis/tests/test_canonical_tiebreak_threshold_v2.py`
- [X] T016 [P] [US1] Add pipeline integration test for current canonical v2 output in `apps/pipeline/tests/orchestration/test_trend_runtime_processor_current_v2.py`
- [X] T017 [P] [US1] Add backend contract test for summary/detail canonical v2 shape in `apps/backend/tests/contract/test_discovery_trend_v2_current_contract.py`
- [X] T018 [P] [US1] Add frontend trend-chip state test for `up/down/flat/unavailable` in `apps/frontend/tests/discovery-trend-chip-v2.test.tsx`

### Implementation for User Story 1

- [X] T019 [P] [US1] Implement EWMA preprocessing metadata pipeline in `libs/trend_analysis/src/trend_analysis/preprocessing.py`
- [X] T020 [P] [US1] Implement Theil-Sen + Kendall-based scoring in `libs/trend_analysis/src/trend_analysis/scoring.py`
- [X] T021 [P] [US1] Implement STL/MSTL cadence routing and fallback logic in `libs/trend_analysis/src/trend_analysis/seasonal_adjustment.py`
- [X] T022 [US1] Implement weighted canonical arbitration with explicit `flat` support in `libs/trend_analysis/src/trend_analysis/arbitration.py`
- [X] T053 [US1] Implement explicit tie-break threshold constant and arbitration guardrail in `libs/trend_analysis/src/trend_analysis/arbitration.py`
- [X] T023 [US1] Integrate v2 scoring/arbitration into runtime processing flow in `apps/pipeline/src/orchestration/jobs/trend_runtime_processor.py`
- [X] T024 [US1] Propagate current canonical v2 fields through backend discovery query service in `apps/backend/src/query/discovery_service.py`
- [X] T025 [US1] Update frontend trend descriptor normalizer for current views in `apps/frontend/src/lib/api/discovery-normalizers.ts`
- [X] T026 [US1] Update primary trend chip rendering states for v2 semantics in `apps/frontend/src/components/discovery/TrendDirectionChip.tsx`

**Checkpoint**: US1 is independently functional and testable.

---

## Phase 4: User Story 2 - Reliable Historical As-Of Trend Inspection (Priority: P2)

**Goal**: Provide reproducible as-of canonical and lookback evidence payloads with explicit applicability reasons and supplementary diagnostics.

**Independent Test**: Request historical as-of points across multiple series and confirm consistent applicable/inapplicable lookbacks, reproducible canonical outputs, and evidence payload completeness.

### Tests for User Story 2 (REQUIRED)

- [X] T027 [P] [US2] Add lookback applicability coverage tests across full catalog in `libs/trend_analysis/tests/test_lookback_applicability_catalog_v2.py`
- [X] T028 [P] [US2] Add as-of reproducibility and ordering tests in `apps/pipeline/tests/orchestration/test_asof_snapshot_reproducibility_v2.py`
- [X] T029 [P] [US2] Add backend as-of endpoint contract test for v2 evidence payload in `apps/backend/tests/contract/test_dataset_asof_trend_v2_contract.py`
- [X] T030 [P] [US2] Add backend detail endpoint evidence visibility test in `apps/backend/tests/contract/test_dataset_detail_trend_evidence_visibility_v2.py`
- [X] T054 [P] [US2] Add discovery endpoint parity contract matrix test (`datasets/search/recent/detail/as-of`) in `apps/backend/tests/contract/test_discovery_trend_v2_endpoint_parity.py`
- [X] T031 [P] [US2] Add frontend secondary evidence section rendering test in `apps/frontend/tests/dataset-detail-trend-evidence-v2.test.tsx`

### Implementation for User Story 2

- [X] T032 [US2] Persist per-lookback applicability reason and evidence fields in `apps/pipeline/src/orchestration/jobs/trend_lifecycle_service.py`
- [X] T033 [US2] Add change-point context metadata computation and tie-break hooks in `libs/trend_analysis/src/trend_analysis/arbitration.py`
- [X] T034 [US2] Add OLS diagnostics fields to detail/as-of query contracts in `apps/backend/src/contract/query/trend_descriptor_v2.py`
- [X] T035 [US2] Implement as-of v2 evidence response assembly in `apps/backend/src/query/discovery_service.py`
- [X] T036 [US2] Wire observation as-of v2 endpoint handling in `apps/backend/src/http_api_server.py`
- [X] T037 [US2] Update frontend API client for detail/as-of evidence payloads in `apps/frontend/src/lib/api/discovery-client.ts`
- [X] T038 [US2] Render OLS/evidence details in expandable section only in `apps/frontend/src/components/discovery/TrendEvidencePanel.tsx`

**Checkpoint**: US2 is independently functional and testable.

---

## Phase 5: User Story 3 - Lower-Noise Reversal Notifications (Priority: P3)

**Goal**: Preserve directional-only reversal events with lower-noise trigger semantics under new canonical logic.

**Independent Test**: Replay incremental and historical runs and verify idempotent `up <-> down` events are preserved while transitions involving `flat` remain non-event and user-visible noise is reduced.

### Tests for User Story 3 (REQUIRED)

- [X] T039 [P] [US3] Add transition eligibility tests for `up/down` only and `flat` exclusions in `apps/pipeline/tests/orchestration/test_trend_transition_eligibility_v2.py`
- [X] T040 [P] [US3] Add replay/backfill visibility and idempotency tests in `apps/pipeline/tests/orchestration/test_trend_transition_replay_idempotency_v2.py`
- [X] T041 [P] [US3] Add backend notification payload formatting threshold test in `apps/backend/tests/contract/test_notification_copy_confidence_threshold_v2.py`
- [X] T055 [P] [US3] Add backend contract test for `flat`/unavailable non-directional notification semantics in `apps/backend/tests/contract/test_notification_contract_flat_unavailable_v2.py`
- [X] T042 [P] [US3] Add frontend notification line rendering test for optional confidence detail in `apps/frontend/tests/notifications-confidence-copy-v2.test.tsx`

### Implementation for User Story 3

- [X] T043 [US3] Update transition evaluator to ignore `flat`/unavailable descriptor transitions in `apps/pipeline/src/orchestration/jobs/trend_runtime_processor.py`
- [X] T044 [US3] Keep replay/backfill visibility semantics aligned with v2 canonical transitions in `apps/pipeline/src/orchestration/jobs/trend_lifecycle_service.py`
- [X] T045 [US3] Update backend notification mapper for direction-first with confidence threshold in `apps/backend/src/query/trend_notification_service.py`
- [X] T046 [US3] Update frontend notification message formatter for optional numeric confidence in `apps/frontend/src/lib/notifications/notification-copy.ts`
- [X] T056 [US3] Define and wire `confidence_score >= 0.70` threshold constant in `apps/backend/src/query/trend_notification_service.py`

**Checkpoint**: US3 is independently functional and testable.

---

## Phase 6: Polish & Cross-Cutting Concerns

**Purpose**: Final validation, documentation, and release hardening across all stories.

- [X] T047 [P] Update implementation notes and rollout checklist in `specs/050-trend-analysis-update/quickstart.md`
- [X] T048 [P] Record replay comparison outcomes against success criteria in `specs/050-trend-analysis-update/research/replay_comparison_results.md`
- [X] T049 [P] Document contract cutover and local reset procedure in `docs/runbooks/trend-descriptor-v2-cutover.md`
- [X] T050 Execute manual verification checklist and record evidence in `specs/050-trend-analysis-update/research/manual_verification_log.md`
- [X] T051 Run full quality gates and capture results in `specs/050-trend-analysis-update/research/quality_gate_results.md`
- [X] T057 [P] Define daily seasonal-adjustment future phase-gate criteria (divergence/event/contracts) in `specs/050-trend-analysis-update/research/daily-seasonal-adjustment-phase-gate.md`
- [X] T058 Implement and verify executable local reset validation script for v2 cutover in `tools/verification/spec050_trend_v2_reset_validation.sh`

---

## Dependencies & Execution Order

### Phase Dependencies

- **Phase 1 (Setup)**: No dependencies.
- **Phase 2 (Foundational)**: Depends on Phase 1; blocks all user stories.
- **Phase 3 (US1)**: Depends on Phase 2; MVP delivery target.
- **Phase 4 (US2)**: Depends on Phase 2 and reuses US1 compute primitives.
- **Phase 5 (US3)**: Depends on Phase 2 and updated canonical semantics from US1.
- **Phase 6 (Polish)**: Depends on all selected user stories.

### User Story Dependencies

- **US1 (P1)**: Independent after foundational work.
- **US2 (P2)**: Independent after foundational work, but benefits from US1 computation completion.
- **US3 (P3)**: Independent after foundational work, but depends on v2 canonical transition semantics introduced in US1.

### Within Each User Story

- Write tests first and confirm failures.
- Implement compute/model/service changes.
- Wire API and UI consumption.
- Re-run story-scoped tests, then full gates.

### Parallel Opportunities

- Setup fixture tasks T002-T004 run in parallel.
- Foundational contract/type tasks T007, T008, T010, T011 run in parallel.
- Per-story test tasks marked [P] run in parallel.
- US1 library implementation tasks T019-T021 run in parallel before arbitration integration.
- US2 backend and frontend consumption tasks T037-T038 run in parallel after T035.
- Polish documentation/result-capture tasks T047-T049 run in parallel.

---

## Parallel Example: User Story 1

```bash
# Run US1 test authoring tasks in parallel:
Task: "T013 [US1] libs/trend_analysis/tests/test_scoring_theilsen_kendall.py"
Task: "T014 [US1] libs/trend_analysis/tests/test_preprocessing_and_seasonal_adjustment.py"
Task: "T015 [US1] libs/trend_analysis/tests/test_canonical_arbitration_v2.py"

# Run core compute implementation tasks in parallel:
Task: "T019 [US1] libs/trend_analysis/src/trend_analysis/preprocessing.py"
Task: "T020 [US1] libs/trend_analysis/src/trend_analysis/scoring.py"
Task: "T021 [US1] libs/trend_analysis/src/trend_analysis/seasonal_adjustment.py"
```

---

## Parallel Example: User Story 2

```bash
# Run US2 tests in parallel:
Task: "T027 [US2] libs/trend_analysis/tests/test_lookback_applicability_catalog_v2.py"
Task: "T029 [US2] apps/backend/tests/contract/test_dataset_asof_trend_v2_contract.py"
Task: "T031 [US2] apps/frontend/tests/dataset-detail-trend-evidence-v2.test.tsx"
```

---

## Parallel Example: User Story 3

```bash
# Run US3 tests in parallel:
Task: "T039 [US3] apps/pipeline/tests/orchestration/test_trend_transition_eligibility_v2.py"
Task: "T040 [US3] apps/pipeline/tests/orchestration/test_trend_transition_replay_idempotency_v2.py"
Task: "T041 [US3] apps/backend/tests/contract/test_notification_copy_confidence_threshold_v2.py"
```

---

## Implementation Strategy

### MVP First (User Story 1)

1. Complete Phase 1 and Phase 2.
2. Deliver Phase 3 (US1) fully.
3. Validate SC-001/SC-002 for current trend stability before expanding scope.

### Incremental Delivery

1. Add US2 for historical as-of evidence and reproducibility.
2. Add US3 for transition-event and notification noise controls.
3. Run Phase 6 cross-cutting validation and cutover documentation.

### Quality Gate Strategy

1. During implementation: run story-scoped tests after each task group.
2. No intermediate commit is allowed without full-suite test and coverage stop gates passing.
3. Before commit or handoff: run `pre-commit run --all-files`, `pnpm exec nx run-many -t test --all`, and `pnpm exec nx run-many -t coverage --all`.
4. Record outputs in `specs/050-trend-analysis-update/research/quality_gate_results.md`.
