# Tasks: Local Dagit Access

**Input**: Design documents from `/specs/009-dagit-local-dev/`
**Prerequisites**: plan.md (required), spec.md (required for user stories), research.md, data-model.md, contracts/

**Tests**: Test tasks are REQUIRED. Every user story and foundational component MUST include automated test coverage sufficient to maintain >= 90% coverage in affected projects.

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3)
- Include exact file paths in descriptions

## Path Conventions

- Pipeline source: `apps/pipeline/src/`
- Pipeline tests: `apps/pipeline/tests/`
- Local stack tooling: `tools/quality/local-stack/`
- Runbook and onboarding docs: `docs/runbooks/`, `docs/onboarding/`
- Feature docs: `specs/009-dagit-local-dev/`

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Prepare local Dagit command entrypoints and documentation scaffolding.

- [ ] T001 Add Dagit local startup helper script in tools/quality/local-stack/start-dagit-local.sh
- [ ] T002 [P] Add Dagit local stop helper script in tools/quality/local-stack/stop-dagit-local.sh
- [ ] T003 [P] Add Dagit endpoint readiness probe helper in tools/quality/local-stack/test-dagit-endpoint.sh
- [ ] T004 [P] Add Dagit quickstart placeholders aligned to this feature in specs/009-dagit-local-dev/quickstart.md
- [ ] T005 [P] Add runbook section stub for Dagit local workflow in docs/runbooks/local-stack-baseline.md

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Implement shared runtime wiring and validation infrastructure required by all user stories.

**⚠️ CRITICAL**: No user story work can begin until this phase is complete.

- [ ] T006 Wire Dagit workspace entrypoint to existing definitions in apps/pipeline/src/orchestration/definitions.py
- [ ] T007 Add Dagit runtime resource wiring verification in apps/pipeline/src/orchestration/runtime.py
- [ ] T008 [P] Add foundational package export coverage for Dagit entrypoint in apps/pipeline/tests/orchestration/test_orchestration_package_exports.py
- [ ] T009 [P] Add foundational definitions smoke checks for Dagit loadability in apps/pipeline/tests/orchestration/test_definitions_smoke.py
- [ ] T010 Implement failure category mapping utility for local Dagit startup checks in apps/pipeline/src/orchestration/jobs/workflow_result.py
- [ ] T011 [P] Add unit tests for Dagit failure category mapping in apps/pipeline/tests/orchestration/test_workflow_registry.py
- [ ] T012 Add local-stack verification command for Dagit endpoint checks in tools/quality/local-stack/test-compose-stack.sh
- [ ] T013 Run foundational quality gates and capture verified commands in specs/009-dagit-local-dev/quickstart.md

**Checkpoint**: Foundation ready - user story implementation can now begin in parallel.

---

## Phase 3: User Story 1 - Launch Dagit Locally (Priority: P1) 🎯 MVP

**Goal**: Enable developers to start Dagit from the repository and reach a healthy local UI endpoint.

**Independent Test**: From a fresh local environment, run the documented startup flow and confirm the endpoint becomes reachable with ready status.

### Tests for User Story 1 (REQUIRED) ⚠️

- [ ] T014 [P] [US1] Add integration test for Dagit startup command success path in apps/pipeline/tests/orchestration/test_ingest_job_runtime.py
- [ ] T015 [P] [US1] Add integration test for endpoint readiness probe behavior in apps/pipeline/tests/orchestration/test_definitions_smoke.py
- [ ] T016 [P] [US1] Add failure-path test for incorrect working directory startup in apps/pipeline/tests/orchestration/test_orchestration_package_exports.py

### Implementation for User Story 1

- [ ] T017 [US1] Implement startup command invocation flow for local Dagit in tools/quality/local-stack/start-dagit-local.sh
- [ ] T018 [US1] Implement startup readiness output and exit semantics in tools/quality/local-stack/start-dagit-local.sh
- [ ] T019 [US1] Implement stop command behavior for local Dagit process cleanup in tools/quality/local-stack/stop-dagit-local.sh
- [ ] T020 [US1] Implement endpoint probe retry and timeout behavior in tools/quality/local-stack/test-dagit-endpoint.sh
- [ ] T021 [US1] Document startup and endpoint verification workflow in specs/009-dagit-local-dev/quickstart.md
- [ ] T022 [US1] Verify US1 coverage contribution maintains >= 90% in apps/pipeline/tests/orchestration/test_definitions_smoke.py

**Checkpoint**: User Story 1 is independently functional and demo-ready.

---

## Phase 4: User Story 2 - View Existing Definitions (Priority: P2)

**Goal**: Ensure local Dagit session loads and displays existing repository definitions, including detail navigation.

**Independent Test**: Launch Dagit and confirm the definitions listing is populated and one detail view opens without blocking errors.

### Tests for User Story 2 (REQUIRED) ⚠️

- [ ] T023 [P] [US2] Add integration test asserting definitions listing visibility in apps/pipeline/tests/orchestration/test_definitions_smoke.py
- [ ] T024 [P] [US2] Add integration test asserting definition detail navigation success in apps/pipeline/tests/orchestration/test_ingest_job_runtime.py
- [ ] T025 [P] [US2] Add regression test for empty-workspace detection in apps/pipeline/tests/orchestration/test_orchestration_package_exports.py

### Implementation for User Story 2

- [ ] T026 [US2] Ensure definitions catalog registration includes existing jobs and schedules in apps/pipeline/src/orchestration/definitions.py
- [ ] T027 [US2] Ensure runtime startup surfaces workspace load state for local UI checks in apps/pipeline/src/orchestration/runtime.py
- [ ] T028 [US2] Implement definition visibility verification helper for local workflow in tools/quality/local-stack/test-dagit-endpoint.sh
- [ ] T029 [US2] Document definition visibility and detail-view verification steps in specs/009-dagit-local-dev/quickstart.md
- [ ] T030 [US2] Verify US2 coverage contribution maintains >= 90% in apps/pipeline/tests/orchestration/test_ingest_job_runtime.py

**Checkpoint**: User Stories 1 and 2 are independently functional with local UI visibility verified.

---

## Phase 5: User Story 3 - Troubleshoot Common Local Failures (Priority: P3)

**Goal**: Provide actionable remediation for common local startup and workspace loading failures.

**Independent Test**: Simulate each documented failure category and confirm runbook guidance restores local Dagit access.

### Tests for User Story 3 (REQUIRED) ⚠️

- [ ] T031 [P] [US3] Add test coverage for prerequisite-missing failure categorization in apps/pipeline/tests/orchestration/test_workflow_registry.py
- [ ] T032 [P] [US3] Add test coverage for endpoint-unavailable failure categorization in apps/pipeline/tests/orchestration/test_definitions_smoke.py
- [ ] T033 [P] [US3] Add test coverage for workspace-load-failed and partial-environment categorization in apps/pipeline/tests/orchestration/test_ingest_job_runtime.py

### Implementation for User Story 3

- [ ] T034 [US3] Implement troubleshooting classification output in tools/quality/local-stack/start-dagit-local.sh
- [ ] T035 [US3] Implement remediation hint output per failure category in tools/quality/local-stack/test-dagit-endpoint.sh
- [ ] T036 [US3] Add complete troubleshooting matrix and recovery verification steps in docs/runbooks/local-stack-baseline.md
- [ ] T037 [US3] Add troubleshooting validation walkthrough in specs/009-dagit-local-dev/quickstart.md
- [ ] T038 [US3] Verify US3 coverage contribution maintains >= 90% in apps/pipeline/tests/orchestration/test_workflow_registry.py

**Checkpoint**: All user stories are independently functional with repeatable troubleshooting.

---

## Phase 6: Polish & Cross-Cutting Concerns

**Purpose**: Final hardening, documentation fidelity, and quality verification across all stories.

- [ ] T039 [P] Align plan and research artifacts with implementation-final decisions in specs/009-dagit-local-dev/plan.md
- [ ] T040 [P] Capture final verified startup/verification command outputs in specs/009-dagit-local-dev/quickstart.md
- [ ] T041 [P] Update onboarding notes for local Dagit workflow in docs/onboarding/monorepo-baseline.md
- [ ] T042 [P] Ensure command/toolchain references remain current in AGENTS.md
- [ ] T043 Run full affected quality suite and record pass outcomes in specs/009-dagit-local-dev/quickstart.md
- [ ] T044 Run local stack verification including Dagit startup and endpoint checks in tools/quality/local-stack/test-compose-stack.sh
- [ ] T045 Execute timed startup benchmark (5 runs) and record median and p95 startup-to-landing-page duration against the <=10 minute criterion in specs/009-dagit-local-dev/quickstart.md
- [ ] T046 Execute and document one uninterrupted end-to-end validation (start UI, confirm listing, open one detail page) with pass/fail evidence in specs/009-dagit-local-dev/quickstart.md
- [ ] T047 Define troubleshooting validation sample protocol (issue set, pass criteria, denominator) and record measured resolution rate in specs/009-dagit-local-dev/quickstart.md

---

## Dependencies & Execution Order

### Phase Dependencies

- **Phase 1 (Setup)**: No dependencies.
- **Phase 2 (Foundational)**: Depends on Phase 1 and blocks all user stories.
- **Phase 3 (US1)**: Starts after Phase 2.
- **Phase 4 (US2)**: Starts after Phase 2; integrates with US1 startup flow.
- **Phase 5 (US3)**: Starts after Phase 2; can run in parallel with US2.
- **Phase 6 (Polish)**: Starts after selected user stories are complete.

### User Story Dependencies

- **US1 (P1)**: Independent after foundational tasks complete.
- **US2 (P2)**: Depends on US1 startup baseline and foundational workspace wiring.
- **US3 (P3)**: Depends on foundational failure classification utilities; can proceed alongside US2.

### Within Each User Story

- Tests MUST be written and fail before implementation.
- Startup/runtime wiring before user-facing verification helpers.
- Implementation before documentation finalization and coverage verification.

## Parallel Opportunities

- Setup: T002, T003, T004, and T005 can run in parallel after T001 starts.
- Foundational: T008, T009, and T011 can run in parallel after T006/T007/T010.
- US1: T014, T015, and T016 can run in parallel.
- US2: T023, T024, and T025 can run in parallel.
- US3: T031, T032, and T033 can run in parallel.
- Polish: T039, T040, T041, and T042 can run in parallel before final verification tasks.

## Parallel Example: User Story 1

```bash
# Parallel test authoring for US1
Task: "T014 [US1] Add startup success path integration test in apps/pipeline/tests/orchestration/test_ingest_job_runtime.py"
Task: "T015 [US1] Add endpoint readiness probe test in apps/pipeline/tests/orchestration/test_definitions_smoke.py"
Task: "T016 [US1] Add incorrect working directory failure-path test in apps/pipeline/tests/orchestration/test_orchestration_package_exports.py"

# Parallel implementation slices for US1
Task: "T019 [US1] Implement stop command behavior in tools/quality/local-stack/stop-dagit-local.sh"
Task: "T020 [US1] Implement endpoint probe retry logic in tools/quality/local-stack/test-dagit-endpoint.sh"
```

## Parallel Example: User Story 2

```bash
# Parallel tests for US2
Task: "T023 [US2] Add definitions listing visibility test in apps/pipeline/tests/orchestration/test_definitions_smoke.py"
Task: "T024 [US2] Add definition detail navigation test in apps/pipeline/tests/orchestration/test_ingest_job_runtime.py"
Task: "T025 [US2] Add empty-workspace detection regression test in apps/pipeline/tests/orchestration/test_orchestration_package_exports.py"
```

## Parallel Example: User Story 3

```bash
# Parallel tests for US3
Task: "T031 [US3] Add prerequisite-missing categorization test in apps/pipeline/tests/orchestration/test_workflow_registry.py"
Task: "T032 [US3] Add endpoint-unavailable categorization test in apps/pipeline/tests/orchestration/test_definitions_smoke.py"
Task: "T033 [US3] Add workspace-load-failed categorization test in apps/pipeline/tests/orchestration/test_ingest_job_runtime.py"
```

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phases 1-2.
2. Complete Phase 3 (US1).
3. Validate startup and endpoint readiness independently.
4. Demo MVP and confirm readiness to proceed.

### Incremental Delivery

1. Build setup and foundational wiring.
2. Deliver US1 startup and endpoint availability.
3. Deliver US2 definition visibility and detail navigation.
4. Deliver US3 troubleshooting and recovery guidance.
5. Finish polish and full quality verification.

### Parallel Team Strategy

1. Team completes Phases 1-2 together.
2. After Phase 2:
   - Developer A: US1 startup and endpoint workflow
   - Developer B: US2 definition visibility checks
   - Developer C: US3 troubleshooting and remediation flow
3. Converge for Phase 6 quality and documentation closure.

## Notes

- [P] tasks indicate no same-file dependency on incomplete tasks.
- Every task line follows strict checklist format with task ID and exact file path.
- User story tasks always include [US#] labels.
- Coverage MUST remain >= 90% in affected projects.
- Documentation and AGENTS updates must ship with behavior/workflow changes.
