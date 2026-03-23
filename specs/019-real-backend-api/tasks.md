# Tasks: Real Backend Discovery API Runtime

**Input**: Design documents from `/specs/019-real-backend-api/`  
**Prerequisites**: plan.md (required), spec.md (required), research.md, data-model.md, contracts/, quickstart.md

**Tests**: Test tasks are REQUIRED. Every user story and foundational component MUST include automated test coverage sufficient to maintain >= 90% coverage in affected projects.

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (US1, US2, US3)
- Include exact file paths in descriptions

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Establish runtime-verification scaffolding, quality command coverage, and baseline feature files before service wiring changes.

- [ ] T001 Create feature task index and execution notes in `specs/019-real-backend-api/tasks.md`
- [ ] T002 [P] Add runtime parity verification command notes to `specs/019-real-backend-api/quickstart.md`
- [ ] T003 [P] Add feature-specific backend test command entry in `apps/backend/project.json`
- [ ] T004 [P] Add verification script stub for persisted discovery parity in `tools/quality/local-stack/test-discovery-persisted-parity.sh`
- [ ] T005 Run and document baseline backend quality commands in `specs/019-real-backend-api/quickstart.md`

**Checkpoint**: Setup assets and command references are ready for implementation.

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Introduce core runtime data-source boundaries and fixture-scope guardrails required by all user stories.

**⚠️ CRITICAL**: No user story work can begin until this phase is complete.

- [ ] T006 Add foundational unit test for runtime data-source selection and schema-readiness guard in `apps/backend/tests/contract/test_runtime_discovery_source_selection.py`
- [ ] T007 [P] Add foundational unit test that fixture repositories are test-only in `apps/backend/tests/contract/test_runtime_fixture_scope_guards.py`
- [ ] T008 Implement persisted runtime repository adapter interface in `apps/backend/src/query/dataset_discovery_persisted_repository.py`
- [ ] T009 Update discovery service composition helpers to accept persisted repository adapters in `apps/backend/src/query/dataset_discovery_service.py`
- [ ] T010 Enforce runtime startup prohibition for fixture-backed repositories and block startup when required schema/migration head is unavailable in `apps/backend/src/http_api_server.py`
- [ ] T011 Align backend fixture helpers with explicit test-only usage notes in `apps/backend/tests/fixtures/dataset_discovery_repository.py`

**Checkpoint**: Runtime source boundary is enforced and verified; user story implementation can begin.

---

## Phase 3: User Story 1 - Trustworthy Discovery Data (Priority: P1) 🎯 MVP

**Goal**: Ensure search, recent, catalog, and detail endpoints are served from persisted records instead of fixture-backed data.

**Independent Test**: Ingest a known update and verify discovery/detail endpoint payloads reflect persisted records with deterministic ordering.

### Tests for User Story 1 (REQUIRED) ⚠️

- [ ] T012 [P] [US1] Add contract test for persisted search response sourcing in `apps/backend/tests/contract/test_dataset_search_persisted_runtime_contract.py`
- [ ] T013 [P] [US1] Add contract test for persisted recent updates sourcing in `apps/backend/tests/contract/test_dataset_recent_updates_persisted_runtime_contract.py`
- [ ] T014 [P] [US1] Add contract test for persisted catalog sourcing and ordering in `apps/backend/tests/contract/test_dataset_catalog_persisted_runtime_contract.py`
- [ ] T015 [P] [US1] Add contract test for persisted detail observations and chronology in `apps/backend/tests/contract/test_dataset_detail_persisted_runtime_contract.py`
- [ ] T016 [P] [US1] Add integration test for HTTP runtime persisted sourcing across all discovery endpoints including explicit unknown-dataset not-found assertions in `apps/backend/tests/contract/test_http_runtime_persisted_discovery_endpoints.py`

### Implementation for User Story 1

- [ ] T017 [US1] Replace seed-backed `_make_service` composition with persisted repository composition in `apps/backend/src/http_api_server.py`
- [ ] T018 [US1] Implement persisted row mapping for dataset summaries and recency in `apps/backend/src/query/dataset_discovery_persisted_repository.py`
- [ ] T019 [US1] Implement persisted detail observation loading and date-range filtering in `apps/backend/src/query/dataset_discovery_persisted_repository.py`
- [ ] T020 [US1] Remove runtime dependency on seed loader in `apps/backend/src/query/dataset_discovery_seed.py`
- [ ] T021 [US1] Keep fixture loaders test-only by moving runtime imports to test modules in `apps/backend/tests/fixtures/dataset_discovery_fixture.py`
- [ ] T022 [US1] Verify US1 backend tests pass and coverage remains >= 90% in `apps/backend/tests/contract/`

**Checkpoint**: US1 is independently functional and proves runtime discovery data is persisted-data-backed.

---

## Phase 4: User Story 2 - Reliable Local Validation Loop (Priority: P2)

**Goal**: Provide a repeatable local and CI verification loop that proves ingest-to-API parity and confirms runtime fixture prohibition.

**Independent Test**: Start local stack, run ingest, rerun discovery endpoints, and verify at least one endpoint response changed due to persisted records while runtime fixture-path checks remain zero.

### Tests for User Story 2 (REQUIRED) ⚠️

- [ ] T023 [P] [US2] Add integration test for ingest-to-API parity workflow in `apps/backend/tests/contract/test_ingest_to_discovery_runtime_parity.py`
- [ ] T024 [P] [US2] Add integration test for runtime fixture fallback prohibition and pre-migration startup fail/block behavior in `apps/backend/tests/contract/test_runtime_fixture_fallback_prohibited.py`
- [ ] T025 [P] [US2] Add script-level smoke test for local parity command in `apps/backend/tests/test_quality_commands.py`

### Implementation for User Story 2

- [ ] T026 [US2] Implement end-to-end parity verification script logic in `tools/quality/local-stack/test-discovery-persisted-parity.sh`
- [ ] T027 [US2] Integrate parity verification into compose-stack validation flow in `tools/quality/local-stack/test-compose-stack.sh`
- [ ] T028 [US2] Add backend contract test target for parity suite in `apps/backend/project.json`
- [ ] T029 [US2] Add runtime verification evidence steps and expected outputs, including migration-head runtime enforcement evidence, in `specs/019-real-backend-api/quickstart.md`
- [ ] T030 [US2] Verify US2 quality gates pass via affected checks and backend tests in `specs/019-real-backend-api/quickstart.md`

**Checkpoint**: US2 is independently functional with reproducible local parity verification.

---

## Phase 5: User Story 3 - Accurate Operational Documentation (Priority: P3)

**Goal**: Ensure runbooks and feature docs describe persisted-data runtime behavior and current migration/runtime expectations without seed-backed ambiguity.

**Independent Test**: Follow updated docs end-to-end and confirm observed behavior matches documented persisted-data expectations.

### Tests for User Story 3 (REQUIRED) ⚠️

- [ ] T031 [P] [US3] Add documentation alignment test for runtime behavior claims in `apps/backend/tests/test_runtime_discovery_documentation_alignment.py`
- [ ] T032 [P] [US3] Add documentation alignment test for migration-head references in `apps/backend/tests/test_runtime_migration_head_documentation.py`

### Implementation for User Story 3

- [ ] T033 [US3] Update local stack runbook for persisted discovery runtime behavior in `docs/runbooks/local-stack-baseline.md`
- [ ] T034 [US3] Update provider onboarding runbook with persisted discovery verification expectations in `docs/runbooks/provider-onboarding.md`
- [ ] T035 [US3] Update feature quickstart execution evidence for persisted runtime checks in `specs/019-real-backend-api/quickstart.md`
- [ ] T036 [US3] Update repository command/tooling context and migration-head note in `AGENTS.md`

**Checkpoint**: US3 is independently functional with documentation that matches runtime behavior.

---

## Phase 6: Polish & Cross-Cutting Concerns

**Purpose**: Final hardening, cross-story validation, and release-ready evidence capture.

- [ ] T037 [P] Run full backend quality suite and record outputs in `specs/019-real-backend-api/quickstart.md`
- [ ] T038 [P] Run affected workspace quality gates and record outcomes in `specs/019-real-backend-api/quickstart.md`
- [ ] T039 Execute full local stack parity flow and capture command evidence in `specs/019-real-backend-api/quickstart.md`
- [ ] T040 Verify all changed behavior/docs remain aligned with the runtime contract in `specs/019-real-backend-api/contracts/runtime-discovery-contract.md`

---

## Dependencies & Execution Order

### Phase Dependencies

- **Phase 1 (Setup)**: No dependencies, starts immediately.
- **Phase 2 (Foundational)**: Depends on Phase 1; blocks all user stories.
- **Phase 3 (US1)**: Depends on Phase 2 completion.
- **Phase 4 (US2)**: Depends on US1 runtime wiring being complete.
- **Phase 5 (US3)**: Depends on US1 and US2 evidence/behavior outputs.
- **Phase 6 (Polish)**: Depends on completion of all user stories.

### User Story Dependencies

- **US1 (P1)**: First deliverable and MVP; no dependency on other user stories.
- **US2 (P2)**: Depends on persisted runtime behavior delivered by US1.
- **US3 (P3)**: Depends on implemented runtime and verification flow from US1 and US2.

### Within Each User Story

- Tests first and expected to fail before implementation.
- Runtime wiring before end-to-end parity checks.
- Documentation updates after behavior is implemented and verified.

---

## Parallel Execution Examples

### User Story 1

```text
Parallel test batch:
  T012, T013, T014, T015, T016
Then implementation sequence:
  T017 -> T018 and T019 -> T020 -> T021 -> T022
```

### User Story 2

```text
Parallel test batch:
  T023, T024, T025
Then implementation sequence:
  T026 -> T027 and T028 -> T029 -> T030
```

### User Story 3

```text
Parallel test batch:
  T031, T032
Then documentation sequence:
  T033, T034, T035, T036
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1 and Phase 2.
2. Complete Phase 3 (US1).
3. Validate persisted discovery runtime behavior independently.
4. Demo and checkpoint before continuing.

### Incremental Delivery

1. Deliver US1 for runtime correctness.
2. Deliver US2 for repeatable local/CI parity verification.
3. Deliver US3 for operational documentation fidelity.
4. Complete polish phase with full quality and stack validation.

### Parallel Team Strategy

1. Team completes Setup + Foundational together.
2. After US1 runtime wiring lands, split work:
   - Developer A: US2 verification scripts and tests.
   - Developer B: US3 documentation alignment tests and runbook updates.
3. Rejoin for polish and final evidence capture.

---

## Notes

- All tasks use strict checklist format with Task IDs and file paths.
- Story tasks include required `[US1]`, `[US2]`, or `[US3]` labels.
- `[P]` markers are used only where tasks are parallelizable.
- Coverage for affected projects must remain >= 90%.
- Fixtures are allowed only in automated tests and must remain unreachable from runtime startup paths.
