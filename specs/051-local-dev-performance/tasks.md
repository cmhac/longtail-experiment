# Tasks: Local Development Performance Stabilization

**Input**: Design documents from `/specs/051-local-dev-performance/`
**Prerequisites**: plan.md (required), spec.md (required for user stories), research.md, data-model.md, contracts/, quickstart.md

**Tests**: Test tasks are required for this feature to preserve contract behavior and maintain >=90% coverage in affected projects.

**Organization**: Tasks are grouped by user story so each story can be implemented and validated independently.

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Establish measurement and validation scaffolding used by all stories.

- [X] T001 Create local detail performance sample dataset list and baseline note template in `specs/051-local-dev-performance/research.md`
- [X] T002 Add repeatable local timing capture helper notes in `specs/051-local-dev-performance/quickstart.md`
- [X] T003 [P] Add backend detail-path verification command list to `specs/051-local-dev-performance/quickstart.md`
- [X] T004 [P] Add frontend detail-page verification command list to `specs/051-local-dev-performance/quickstart.md`
- [X] T005 [P] Confirm contract invariants checklist in `specs/051-local-dev-performance/contracts/dataset-detail-performance-contract.md`

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Baseline safeguards and shared backend test harness required before user-story changes.

**CRITICAL**: No user story implementation starts until this phase is complete.

- [X] T006 Add failing backend contract test for dataset-detail response shape invariance in `apps/backend/tests/contract/test_dataset_detail_performance_contract.py`
- [X] T007 [P] Add failing backend contract test for dataset-detail not-found/error invariance in `apps/backend/tests/contract/test_dataset_detail_performance_errors.py`
- [X] T008 [P] Add failing backend integration test for repeated detail requests timing envelope in `apps/backend/tests/integration/test_dataset_detail_local_runtime_latency.py`
- [X] T009 Add shared backend fixture helpers for detail request timing capture in `apps/backend/tests/contract/fixtures/dataset_detail_performance_fixtures.py`
- [X] T010 [P] Add frontend integration test harness for detail-page loading-state duration assertions in `apps/frontend/tests/app/dataset-detail-local-load.test.tsx`
- [X] T011 Document baseline measurement results section in `specs/051-local-dev-performance/research.md`
- [X] T012 Define fixed representative sample in `specs/051-local-dev-performance/research.md` as exactly 9 datasets (3 small, 3 medium, 3 large observation histories)

**Checkpoint**: Foundational tests and baseline harness are ready.

---

## Phase 3: User Story 1 - Fast Dataset Detail Loading (Priority: P1) 🎯 MVP

**Goal**: Make dataset detail pages load quickly and consistently in local development.

**Independent Test**: Load representative dataset detail pages locally and verify page content appears within target thresholds without prolonged loading indicators.

### Tests for User Story 1

- [X] T013 [P] [US1] Add failing backend contract test asserting dataset-scoped detail metadata retrieval behavior in `apps/backend/tests/contract/test_dataset_detail_targeted_metadata_contract.py`
- [X] T014 [P] [US1] Add failing backend integration test for median detail endpoint latency improvement in `apps/backend/tests/integration/test_dataset_detail_local_latency_improvement.py`
- [X] T015 [P] [US1] Add failing frontend test for reduced loading-state dwell on detail route in `apps/frontend/tests/app/dataset-detail-local-load.test.tsx`

### Implementation for User Story 1

- [X] T016 [US1] Implement dataset-targeted detail metadata query path in `apps/backend/src/query/dataset_discovery_persisted_repository.py`
- [X] T017 [US1] Replace full-catalog scan usage for detail lookup in `apps/backend/src/query/dataset_discovery_service.py`
- [X] T018 [US1] Preserve detail payload compatibility validation in `apps/backend/src/query/dataset_detail_query.py`
- [X] T019 [US1] Keep frontend detail route behavior unchanged while using faster backend response in `apps/frontend/src/app/datasets/[id]/page.tsx`
- [X] T020 [US1] Update local baseline-vs-after timing evidence for US1 in `specs/051-local-dev-performance/research.md`

**Checkpoint**: US1 delivers fast, stable local detail-page loading for MVP scope.

---

## Phase 4: User Story 2 - Faster Backend Response Path for Detail Requests (Priority: P2)

**Goal**: Ensure detail requests only perform dataset-relevant work and avoid broad catalog operations.

**Independent Test**: Request detail for fixed datasets and verify backend processing does not execute full-catalog retrieval behavior while preserving response correctness.

### Tests for User Story 2

- [X] T021 [P] [US2] Add failing backend contract test for detail-path scaling with dataset scope in `apps/backend/tests/contract/test_dataset_detail_scope_scaling_contract.py`
- [X] T022 [P] [US2] Add failing backend contract test for as-of descriptor mapping correctness under optimized candidate selection in `apps/backend/tests/contract/test_dataset_detail_asof_candidate_contract.py`
- [X] T023 [P] [US2] Add failing backend integration test for unchanged canonical and lookback evidence semantics in `apps/backend/tests/integration/test_dataset_detail_trend_evidence_invariance.py`

### Implementation for User Story 2

- [X] T024 [US2] Optimize as-of trend candidate assembly/filtering path in `apps/backend/src/query/dataset_discovery_persisted_repository.py`
- [X] T025 [US2] Keep canonical descriptor and lookback evidence resolution invariants in `apps/backend/src/query/dataset_discovery_service.py`
- [X] T026 [US2] Verify detail contract mapping invariants in `apps/backend/src/contract/query/dataset_discovery_contracts.py`
- [X] T027 [US2] Record US2 before/after response-path verification notes in `specs/051-local-dev-performance/research.md`

**Checkpoint**: US2 ensures backend detail assembly is scoped and contract-safe.

---

## Phase 5: User Story 3 - Smoother Local Stack Runtime Behavior (Priority: P3)

**Goal**: Reduce avoidable per-request local runtime overhead so repeated detail loads remain responsive.

**Independent Test**: Run repeated local detail requests and confirm bounded latency without repeated expensive setup behavior.

### Tests for User Story 3

- [X] T028 [P] [US3] Add failing backend integration test for repeated detail request runtime stability in `apps/backend/tests/integration/test_dataset_detail_repeated_request_stability.py`
- [X] T029 [P] [US3] Add failing backend contract test ensuring schema readiness safety behavior remains intact in `apps/backend/tests/contract/test_http_runtime_detail_safety_guards.py`

### Implementation for User Story 3

- [X] T030 [US3] Reduce avoidable local request setup overhead in backend service construction path in `apps/backend/src/http_api_server.py`
- [X] T031 [US3] Ensure detail query entrypoint behavior stays unchanged after runtime optimization in `apps/backend/src/query/dataset_detail_query.py`
- [X] T032 [US3] Validate frontend discovery client compatibility with optimized local runtime behavior in `apps/frontend/src/lib/api/discovery-client.ts`
- [X] T033 [US3] Record repeated-load local runtime verification evidence in `specs/051-local-dev-performance/research.md`

**Checkpoint**: US3 provides stable repeated-request performance in local runtime.

---

## Phase 6: Polish & Cross-Cutting Concerns

**Purpose**: Final regression protection, documentation, and quality gates across all stories.

- [X] T034 [P] Add regression contract test for catalog/search/source/topic/geography non-regression in `apps/backend/tests/contract/test_discovery_endpoint_performance_regression_guard.py`
- [X] T035 [P] Add frontend regression test covering detail page error-state parity in `apps/frontend/tests/app/dataset-detail-trend-error-state.test.tsx`
- [X] T036 Add explicit SC-004 before/after error-rate measurement task and results table in `specs/051-local-dev-performance/research.md`
- [X] T037 Update end-to-end verification procedure and expected outputs in `specs/051-local-dev-performance/quickstart.md`
- [X] T038 Run pre-commit stop gate (`pre-commit run --all-files`) and record result in `specs/051-local-dev-performance/research.md`
- [X] T039 Run full repository test stop gate command and record result in `specs/051-local-dev-performance/research.md`
- [X] T040 Run full repository coverage stop gate command and record result in `specs/051-local-dev-performance/research.md`

---

## Dependencies & Execution Order

### Phase Dependencies

- Phase 1 (Setup): starts immediately.
- Phase 2 (Foundational): depends on Phase 1 completion; blocks all user stories.
- Phase 3 (US1): depends on Phase 2; MVP first.
- Phase 4 (US2): depends on Phase 2; can run after US1 or in parallel once foundation is complete.
- Phase 5 (US3): depends on Phase 2; can run after US1 or in parallel once foundation is complete.
- Phase 6 (Polish): depends on completion of US1, US2, and US3.

### User Story Dependencies

- US1 (P1): no dependency on other stories after foundational completion.
- US2 (P2): no strict dependency on US1, but should reuse US1 detail-path safeguards.
- US3 (P3): no strict dependency on US2, but should validate combined behavior with US1/US2 changes.

### Within Each User Story

- Tests first and failing before implementation.
- Backend repository/service changes before endpoint/query integration validation.
- Contract and regression verification before story completion.

---

## Parallel Execution Examples

### User Story 1

```bash
# Parallel test tasks
T013, T014, T015

# Then implementation sequence
T016 -> T017 -> T018 -> T019 -> T020
```

### User Story 2

```bash
# Parallel test tasks
T021, T022, T023

# Parallel-safe implementation tasks
T024 and T026

# Then finalize
T025 -> T027
```

### User Story 3

```bash
# Parallel test tasks
T028, T029

# Implementation sequence
T030 -> T031

# Parallel-safe follow-up
T032 and T033
```

---

## Implementation Strategy

### MVP First (US1 only)

1. Complete Phase 1 and Phase 2.
2. Complete Phase 3 (US1).
3. Validate US1 independent test criteria and performance outcomes.
4. Demo/ship MVP improvement for local detail-page speed.

### Incremental Delivery

1. Deliver US1 for immediate developer impact.
2. Add US2 to lock backend request-path scalability and contract safety.
3. Add US3 to stabilize repeated-request runtime behavior.
4. Finish with Phase 6 cross-cutting regression and quality gates.

### Parallel Team Strategy

1. Team completes Setup + Foundational together.
2. After foundational checkpoint:
   - Engineer A: US1 core backend path.
   - Engineer B: US2 as-of/evidence optimization and contracts.
   - Engineer C: US3 runtime overhead stabilization and repeated-load validation.
3. Merge at Phase 6 with full-stop gate verification.

---

## Notes

- All tasks use required checklist format with Task ID and exact file path.
- `[P]` tasks are parallelizable because they touch different files or independent test surfaces.
- User-story tasks include `[US1]`, `[US2]`, or `[US3]` labels for traceability.
- Full-suite and coverage stop rules are mandatory before commit/handoff.
