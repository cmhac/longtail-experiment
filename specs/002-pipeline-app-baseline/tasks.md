# Tasks: Pipeline App Baseline

**Input**: Design documents from `/specs/002-pipeline-app-baseline/`
**Prerequisites**: plan.md (required), spec.md (required for user stories), research.md, data-model.md, contracts/, quickstart.md

**Tests**: Test tasks are REQUIRED. Every user story and foundational component MUST include automated test coverage sufficient to maintain >= 90% coverage in affected projects.

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3)
- Include exact file paths in descriptions

## Path Conventions

- Monorepo applications: `apps/backend/`, `apps/frontend/`, `apps/pipeline/`
- Workspace tooling: `tools/quality/`
- Stack/runtime config: `docker-compose.yml`, `docker/compose/stack.env`
- Documentation: `docs/`, `AGENTS.md`, `specs/002-pipeline-app-baseline/`

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Initialize the pipeline app skeleton and baseline workspace registration entry points.

- [ ] T001 Create pipeline project directories in apps/pipeline/src and apps/pipeline/tests
- [ ] T002 Create pipeline placeholder module in apps/pipeline/src/**init**.py
- [ ] T003 [P] Create pipeline smoke test scaffold in apps/pipeline/tests/test_smoke.py
- [ ] T004 [P] Create pipeline workspace registration test scaffold in apps/pipeline/tests/test_workspace_registration.py
- [ ] T005 [P] Create pipeline quality command test scaffold in apps/pipeline/tests/test_quality_commands.py
- [ ] T006 [P] Create pipeline container health test scaffold in apps/pipeline/tests/test_container_health.py
- [ ] T007 Register pipeline Nx project shell in apps/pipeline/project.json
- [ ] T008 Add pipeline project placeholder references in docs/architecture/monorepo-boundaries.md

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Establish blocking quality/runtime foundations required by all user stories.

**⚠️ CRITICAL**: No user story work can begin until this phase is complete.

- [ ] T009 Create pipeline uv project manifest in apps/pipeline/pyproject.toml
- [ ] T010 [P] Generate and pin pipeline lockfile in apps/pipeline/uv.lock
- [ ] T011 Configure ruff lint and format policy for pipeline in apps/pipeline/pyproject.toml
- [ ] T012 [P] Configure ty and pytest settings for pipeline in apps/pipeline/pyproject.toml
- [ ] T013 [P] Add Dagster baseline dependency entry in apps/pipeline/pyproject.toml
- [ ] T014 Register pipeline lint/format/typecheck/test/coverage targets in apps/pipeline/project.json
- [ ] T015 [P] Extend workspace affected inputs for pipeline paths in nx.json
- [ ] T016 [P] Add pipeline-aware affected lint verification in tools/quality/verification/affected-backend.sh
- [ ] T017 [P] Add pipeline-aware affected test verification in tools/quality/verification/affected-frontend.sh
- [ ] T018 [P] Add pipeline-aware workspace verification in tools/quality/verification/affected-workspace.sh
- [ ] T019 Extend workspace quality scripts to include pipeline checks in package.json
- [ ] T020 [P] Extend duplication scan scope to include pipeline source paths in tools/quality/cpd/run-cpd.sh
- [ ] T021 [P] Add pipeline path coverage to duplication test script in tools/quality/cpd/test-cpd.sh
- [ ] T022 Add pipeline quality gate enforcement to pre-commit flow in .pre-commit-config.yaml
- [ ] T023 [P] Add pipeline setup commands to onboarding baseline in docs/onboarding/monorepo-baseline.md
- [ ] T024 [P] Add pipeline baseline context to architecture notes in docs/architecture/monorepo-boundaries.md

**Checkpoint**: Foundation ready. User story work can now proceed.

---

## Phase 3: User Story 1 - Register Pipeline Workspace Project (Priority: P1) 🎯 MVP

**Goal**: Pipeline is a first-class Nx app visible in workspace discovery with baseline-only implementation.

**Independent Test**: From a clean clone, run workspace listing commands and confirm backend, frontend, and pipeline are all registered and discoverable.

### Tests for User Story 1 (REQUIRED)

- [ ] T025 [P] [US1] Implement pipeline workspace registration test assertions in apps/pipeline/tests/test_workspace_registration.py
- [ ] T026 [P] [US1] Add backend test coverage for pipeline project visibility in apps/backend/tests/test_workspace_registration.py
- [ ] T027 [P] [US1] Add frontend test coverage for pipeline project visibility in apps/frontend/tests/workspace-registration.test.ts

### Implementation for User Story 1

- [ ] T028 [US1] Finalize pipeline project metadata and tags in apps/pipeline/project.json
- [ ] T029 [US1] Add pipeline placeholder package markers in apps/pipeline/src/**init**.py
- [ ] T030 [US1] Add workspace registration quickstart steps in specs/002-pipeline-app-baseline/quickstart.md
- [ ] T031 [US1] Document pipeline app boundary and ownership in docs/architecture/monorepo-boundaries.md
- [ ] T032 [US1] Update feature contracts for registration verification in specs/002-pipeline-app-baseline/contracts/pipeline-quality-contract.md
- [ ] T033 [US1] Verify and record US1 baseline-only scope evidence in specs/002-pipeline-app-baseline/research.md

**Checkpoint**: User Story 1 is independently testable and delivers MVP value.

---

## Phase 4: User Story 2 - Establish Pipeline Tooling Baseline (Priority: P2)

**Goal**: Pipeline has backend-parity Python quality gates with deterministic affected-only execution.

**Independent Test**: Run pipeline lint, format, typecheck, test, and coverage commands plus workspace affected quality commands and confirm deterministic outcomes.

### Tests for User Story 2 (REQUIRED)

- [ ] T034 [P] [US2] Implement pipeline quality command smoke tests in apps/pipeline/tests/test_quality_commands.py
- [ ] T035 [P] [US2] Add workspace-level quality command assertions for pipeline in apps/backend/tests/test_quality_commands.py
- [ ] T036 [P] [US2] Add workspace-level quality command assertions for pipeline in apps/frontend/tests/quality-commands.test.ts
- [ ] T037 [P] [US2] Add pipeline duplication coverage assertion in tools/quality/cpd/test-cpd.sh

### Implementation for User Story 2

- [ ] T038 [US2] Enforce pipeline coverage threshold >= 90 in apps/pipeline/pyproject.toml
- [ ] T039 [US2] Wire uv-based lint/format/typecheck/test scripts for pipeline in apps/pipeline/pyproject.toml
- [ ] T040 [US2] Finalize pipeline target command wiring in apps/pipeline/project.json
- [ ] T041 [US2] Integrate pipeline targets into workspace quality orchestration in package.json
- [ ] T042 [US2] Add affected-only pipeline quality verification guidance in specs/002-pipeline-app-baseline/quickstart.md
- [ ] T043 [US2] Update pipeline quality contract with canonical command set in specs/002-pipeline-app-baseline/contracts/pipeline-quality-contract.md
- [ ] T044 [US2] Add pipeline baseline quality runbook guidance in docs/runbooks/local-stack-baseline.md

**Checkpoint**: User Stories 1 and 2 are independently functional.

---

## Phase 5: User Story 3 - Define Baseline Data Flow Hand-Off (Priority: P3)

**Goal**: Three-app local stack and handoff boundaries are documented and verifiable without business data logic.

**Independent Test**: Start and verify the local stack and confirm pipeline, backend, and frontend placeholders become healthy while boundary docs align with runtime behavior.

### Tests for User Story 3 (REQUIRED)

- [ ] T045 [P] [US3] Implement pipeline container health smoke test in apps/pipeline/tests/test_container_health.py
- [ ] T046 [P] [US3] Extend backend container health expectations for pipeline service in apps/backend/tests/test_container_health.py
- [ ] T047 [P] [US3] Extend frontend container health expectations for pipeline service in apps/frontend/tests/container-health.test.ts
- [ ] T048 [P] [US3] Update compose stack verification for three services in tools/quality/local-stack/test-compose-stack.sh

### Implementation for User Story 3

- [ ] T049 [US3] Add pipeline placeholder service and healthcheck in docker-compose.yml
- [ ] T050 [US3] Add pipeline-related compose environment values in docker/compose/stack.env
- [ ] T051 [US3] Update handoff boundary contract details in specs/002-pipeline-app-baseline/contracts/pipeline-backend-handoff-contract.md
- [ ] T052 [US3] Update three-app local stack contract in specs/002-pipeline-app-baseline/contracts/local-stack-three-app-contract.md
- [ ] T053 [US3] Add three-app startup and shutdown verification steps in specs/002-pipeline-app-baseline/quickstart.md
- [ ] T054 [US3] Add pipeline-focused troubleshooting scenarios in docs/runbooks/local-stack-baseline.md

**Checkpoint**: All user stories are independently functional and verified.

---

## Phase 6: Polish & Cross-Cutting Concerns

**Purpose**: Final validation, benchmarking, and documentation fidelity checks across all stories.

- [ ] T055 [P] Run and record pipeline affected lint benchmark in tools/quality/verification/benchmark-affected-lint.sh
- [ ] T056 [P] Run and record pipeline affected test benchmark in tools/quality/verification/benchmark-affected-test.sh
- [ ] T057 Run full quality pipeline and capture evidence in specs/002-pipeline-app-baseline/research.md
- [ ] T058 Run full three-app local stack verification and capture outputs in specs/002-pipeline-app-baseline/quickstart.md
- [ ] T059 [P] Update onboarding command matrix for pipeline workflows in docs/onboarding/monorepo-baseline.md
- [ ] T060 [P] Update AGENTS baseline structure, toolchain, and canonical commands in AGENTS.md
- [ ] T061 [P] Update feature data model to reflect final implementation naming in specs/002-pipeline-app-baseline/data-model.md
- [ ] T062 Final documentation consistency pass across contracts and plan in specs/002-pipeline-app-baseline/plan.md

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies; starts immediately.
- **Foundational (Phase 2)**: Depends on Phase 1 and blocks all user stories.
- **User Story phases (Phases 3-5)**: Depend on Phase 2 completion.
- **Polish (Phase 6)**: Depends on all user stories completing.

### User Story Dependencies

- **US1 (P1)**: Starts after Phase 2; no dependency on US2/US3.
- **US2 (P2)**: Starts after Phase 2; can run independently but consumes US1 registration artifacts.
- **US3 (P3)**: Starts after Phase 2; can run independently but composes with US1/US2 outputs.

### Dependency Graph

- Foundation path: Phase 1 -> Phase 2
- Delivery path: Phase 2 -> US1 -> US2 -> US3
- Finalization path: US1 + US2 + US3 -> Phase 6

### Within Each User Story

- Tests before implementation updates.
- Project/config contracts before stack/documentation integration.
- Story checkpoint validation before advancing.

### Parallel Opportunities

- Setup tasks marked [P] can run in parallel.
- Foundational tasks marked [P] can run in parallel once baseline manifests exist.
- Test tasks within each story marked [P] can run in parallel.
- Cross-doc updates in Phase 6 marked [P] can run in parallel.

---

## Parallel Example: User Story 1

```bash
Task: "T025 [US1] apps/pipeline/tests/test_workspace_registration.py"
Task: "T026 [US1] apps/backend/tests/test_workspace_registration.py"
Task: "T027 [US1] apps/frontend/tests/workspace-registration.test.ts"
```

## Parallel Example: User Story 2

```bash
Task: "T034 [US2] apps/pipeline/tests/test_quality_commands.py"
Task: "T035 [US2] apps/backend/tests/test_quality_commands.py"
Task: "T036 [US2] apps/frontend/tests/quality-commands.test.ts"
Task: "T037 [US2] tools/quality/cpd/test-cpd.sh"
```

## Parallel Example: User Story 3

```bash
Task: "T045 [US3] apps/pipeline/tests/test_container_health.py"
Task: "T046 [US3] apps/backend/tests/test_container_health.py"
Task: "T047 [US3] apps/frontend/tests/container-health.test.ts"
Task: "T048 [US3] tools/quality/local-stack/test-compose-stack.sh"
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1 and Phase 2.
2. Complete Phase 3 (US1).
3. Validate US1 independently with workspace registration checks.
4. Demo and confirm baseline-only scope.

### Incremental Delivery

1. Deliver US1 to establish pipeline workspace presence.
2. Deliver US2 to establish deterministic quality parity.
3. Deliver US3 to establish three-app handoff and local-stack verification.
4. Execute Phase 6 cross-cutting validation and docs updates.

### Parallel Team Strategy

1. Team aligns on Phase 1 and Phase 2 foundations.
2. After foundation completion, split ownership:
   - Developer A: US1
   - Developer B: US2
   - Developer C: US3
3. Rejoin for Phase 6 verification and final documentation pass.

---

## Notes

- Every task follows required checklist format: checkbox + ID + optional [P] + optional [US#] + description with file path.
- Coverage target remains >= 90% for all affected scopes.
- No suppression/bypass paths are permitted.
- Documentation updates, including AGENTS.md, are mandatory where behavior/workflows change.
