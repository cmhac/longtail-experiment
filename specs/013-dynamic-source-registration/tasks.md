# Tasks: Dynamic Source Workflow Registration

**Input**: Design documents from `/specs/013-dynamic-source-registration/`
**Prerequisites**: plan.md (required), spec.md (required for user stories), research.md, data-model.md, contracts/

**Tests**: Test tasks are REQUIRED. Every user story and foundational component MUST include automated test coverage sufficient to maintain >= 90% coverage in affected projects.

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3)
- Include exact file paths in descriptions

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Establish feature scaffolding and verification entrypoints

- [ ] T001 Confirm feature artifact readiness in specs/013-dynamic-source-registration/quickstart.md
- [ ] T002 [P] Add dynamic-registration verification command notes in apps/pipeline/project.json
- [ ] T003 [P] Prepare deterministic registration fixture notes in apps/pipeline/tests/orchestration/test_source_asset_discovery.py
- [ ] T004 [P] Document startup-failure diagnostics expectations in specs/013-dynamic-source-registration/contracts/source-registration-contract.md

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core runtime composition changes that block all user stories

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

- [ ] T005 Implement single discovery/registration orchestration path in apps/pipeline/src/orchestration/runtime.py
- [ ] T006 [P] Enforce deterministic discovery ordering policy in apps/pipeline/src/orchestration/jobs/source_assets/discovery.py
- [ ] T007 [P] Harden contract violation formatting for module-scoped diagnostics in apps/pipeline/src/orchestration/jobs/source_assets/contracts.py
- [ ] T008 Add duplicate-source-key pre-registration guard assertions in apps/pipeline/src/orchestration/jobs/source_assets/contracts.py
- [ ] T009 [P] Add foundational regression tests for runtime composition in apps/pipeline/tests/orchestration/test_source_asset_contract_validation.py
- [ ] T010 Validate foundational coverage impact and thresholds in apps/pipeline/project.json

**Checkpoint**: Foundation ready - user story implementation can now begin in parallel

---

## Phase 3: User Story 1 - Onboard Source Without Bootstrap Edits (Priority: P1) 🎯 MVP

**Goal**: A compliant adapter can be onboarded without editing runtime bootstrap wiring

**Independent Test**: Add a valid adapter registration fixture and verify runtime includes it without modifying runtime bootstrap imports/registration calls.

### Tests for User Story 1 (REQUIRED) ⚠️

- [ ] T011 [P] [US1] Add valid-adapter discovery test in apps/pipeline/tests/orchestration/test_source_asset_discovery.py
- [ ] T012 [P] [US1] Add runtime onboarding integration test in apps/pipeline/tests/orchestration/test_definitions_smoke.py
- [ ] T013 [P] [US1] Add no-bootstrap-edit contract test case in apps/pipeline/tests/orchestration/test_source_asset_contract_validation.py

### Implementation for User Story 1

- [ ] T014 [US1] Refactor adapter onboarding flow to single discovery entrypoint in apps/pipeline/src/orchestration/runtime.py
- [ ] T015 [P] [US1] Add explicit adapter candidate inclusion criteria in apps/pipeline/src/orchestration/jobs/source_assets/discovery.py
- [ ] T016 [US1] Ensure existing adapters register through discovery path in apps/pipeline/src/orchestration/jobs/source_assets/discovery.py
- [ ] T017 [US1] Update source onboarding guidance to remove manual bootstrap edits in docs/runbooks/provider-onboarding.md
- [ ] T018 [US1] Verify US1 coverage contribution remains >= 90% in apps/pipeline/project.json

**Checkpoint**: User Story 1 is independently functional and testable

---

## Phase 4: User Story 2 - Deterministic and Safe Registration (Priority: P2)

**Goal**: Registration is deterministic and contract-safe with actionable fail-fast diagnostics

**Independent Test**: Run repeated startup/discovery checks with same adapter set and verify order stability; inject malformed and duplicate adapters and verify clear startup failures.

### Tests for User Story 2 (REQUIRED) ⚠️

- [ ] T019 [P] [US2] Add deterministic-order regression tests in apps/pipeline/tests/orchestration/test_source_asset_discovery.py
- [ ] T020 [P] [US2] Add malformed-adapter fail-fast tests in apps/pipeline/tests/orchestration/test_source_asset_contract_validation.py
- [ ] T021 [P] [US2] Add duplicate-source-key rejection tests in apps/pipeline/tests/orchestration/test_source_asset_contract_validation.py

### Implementation for User Story 2

- [ ] T022 [US2] Implement non-adapter ignore behavior in apps/pipeline/src/orchestration/jobs/source_assets/discovery.py
- [ ] T023 [US2] Standardize startup contract error payload details in apps/pipeline/src/orchestration/jobs/source_assets/contracts.py
- [ ] T024 [US2] Wire deterministic registration visibility into runtime load-state checks in apps/pipeline/src/orchestration/runtime.py
- [ ] T025 [US2] Align smoke assertions with dynamic-registration expectations in apps/pipeline/tests/orchestration/test_definitions_smoke.py
- [ ] T026 [US2] Verify US2 coverage contribution remains >= 90% in apps/pipeline/project.json

**Checkpoint**: User Stories 1 and 2 both work independently

---

## Phase 5: User Story 3 - Operator and QA Confidence in Onboarding Flow (Priority: P3)

**Goal**: Operators and QA can validate onboarding behavior via updated docs and smoke workflow

**Independent Test**: Follow updated runbook/onboarding docs and execute listed tests/scripts to validate source onboarding flow and diagnostics.

### Tests for User Story 3 (REQUIRED) ⚠️

- [ ] T027 [P] [US3] Add doc-aligned smoke validation test notes in apps/pipeline/tests/orchestration/test_definitions_smoke.py
- [ ] T028 [P] [US3] Add quickstart command validation coverage in apps/pipeline/tests/orchestration/test_source_asset_discovery.py
- [ ] T029 [P] [US3] Add startup diagnostics visibility assertions in apps/pipeline/tests/orchestration/test_source_asset_contract_validation.py

### Implementation for User Story 3

- [ ] T030 [US3] Update source workflow onboarding section for dynamic registration in docs/runbooks/local-stack-baseline.md
- [ ] T031 [US3] Update onboarding baseline guidance for dynamic registration flow in docs/onboarding/monorepo-baseline.md
- [ ] T032 [US3] Align feature quickstart evidence and operator checks in specs/013-dynamic-source-registration/quickstart.md
- [ ] T033 [US3] Update architecture boundary notes for registration composition in docs/architecture/monorepo-boundaries.md
- [ ] T034 [US3] Verify US3 coverage contribution remains >= 90% in apps/pipeline/project.json

**Checkpoint**: All user stories are independently functional and testable

---

## Phase 6: Polish & Cross-Cutting Concerns

**Purpose**: Final hardening across stories

- [ ] T035 [P] Run targeted orchestration suite for this feature in apps/pipeline/tests/orchestration/test_source_asset_discovery.py
- [ ] T036 [P] Run targeted orchestration suite for this feature in apps/pipeline/tests/orchestration/test_source_asset_contract_validation.py
- [ ] T037 [P] Run targeted orchestration suite for this feature in apps/pipeline/tests/orchestration/test_definitions_smoke.py
- [ ] T038 Execute affected quality gates and record outcomes in specs/013-dynamic-source-registration/quickstart.md
- [ ] T039 [P] Verify documentation fidelity and command updates in AGENTS.md
- [ ] T040 Perform final consistency pass across spec/plan/tasks in specs/013-dynamic-source-registration/tasks.md
- [ ] T041 Run full local development stack validation sequence in tools/quality/local-stack/test-compose-stack.sh
- [ ] T042 Validate Dagit endpoint/workspace health after local run in tools/quality/local-stack/test-dagit-endpoint.sh
- [ ] T043 Use browser validation of Dagit UI asset catalog and capture evidence in specs/013-dynamic-source-registration/quickstart.md
- [ ] T044 Confirm final operator acceptance criteria that changes are visible in Dagit in specs/013-dynamic-source-registration/quickstart.md

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies - can start immediately
- **Foundational (Phase 2)**: Depends on Setup completion - BLOCKS all user stories
- **User Stories (Phase 3+)**: Depend on Foundational phase completion
  - User stories should be delivered in priority order (P1 -> P2 -> P3)
  - US2 and US3 remain independently testable increments after foundation
- **Polish (Phase 6)**: Depends on completion of desired user stories

### User Story Dependencies

- **US1 (P1)**: Starts after Foundational and defines MVP onboarding behavior
- **US2 (P2)**: Starts after Foundational, builds deterministic and fail-fast safety guarantees
- **US3 (P3)**: Starts after Foundational, finalizes docs and operator validation flow

### Within Each User Story

- Tests first, confirm failing baseline where applicable
- Runtime/discovery implementation after tests
- Documentation updates in same story phase
- Coverage threshold verification before phase completion

### Parallel Opportunities

- Setup tasks marked [P] can run in parallel
- Foundational tasks T006/T007/T009 can run in parallel after T005 starts
- Test tasks within each story marked [P] can run in parallel
- Documentation tasks T030-T033 can run in parallel
- Polish test execution tasks T035-T037 can run in parallel
- T041 and T042 are sequential runtime checks; T043 and T044 must run last after runtime checks pass

---

## Parallel Example: User Story 2

```bash
# Launch US2 tests together:
Task: "T019 [US2] Add deterministic-order regression tests in apps/pipeline/tests/orchestration/test_source_asset_discovery.py"
Task: "T020 [US2] Add malformed-adapter fail-fast tests in apps/pipeline/tests/orchestration/test_source_asset_contract_validation.py"
Task: "T021 [US2] Add duplicate-source-key rejection tests in apps/pipeline/tests/orchestration/test_source_asset_contract_validation.py"

# Launch independent US2 implementation tasks together:
Task: "T022 [US2] Implement non-adapter ignore behavior in apps/pipeline/src/orchestration/jobs/source_assets/discovery.py"
Task: "T023 [US2] Standardize startup contract error payload details in apps/pipeline/src/orchestration/jobs/source_assets/contracts.py"
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1: Setup
2. Complete Phase 2: Foundational
3. Complete Phase 3: User Story 1
4. Validate independent US1 onboarding behavior with no runtime bootstrap edits

### Incremental Delivery

1. Deliver Setup + Foundational baseline
2. Deliver US1 (MVP)
3. Deliver US2 deterministic/safety guarantees
4. Deliver US3 docs/operator confidence workflow
5. Finish with Polish and full verification
6. End with full local-stack run and Dagit browser validation evidence

### Parallel Team Strategy

1. Team aligns on Foundational runtime/discovery path
2. After Foundational completion:
   - Developer A: US1 onboarding path and tests
   - Developer B: US2 deterministic/safety tests and contracts
   - Developer C: US3 documentation and quickstart updates

---

## Notes

- [P] tasks = different files or non-blocking work
- [USx] labels map tasks to specific user stories for traceability
- Every user story contains required automated tests
- Maintain >=90% coverage in affected projects
- Keep documentation updates in the same change as behavior changes
- Keep AGENTS.md aligned when canonical commands/workflows change
