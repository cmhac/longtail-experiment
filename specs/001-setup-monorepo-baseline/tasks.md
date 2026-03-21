# Tasks: Initial Monorepo Baseline

**Input**: Design documents from `/specs/001-setup-monorepo-baseline/`
**Prerequisites**: plan.md (required), spec.md (required for user stories), research.md, data-model.md, contracts/, quickstart.md

**Tests**: Test tasks are REQUIRED by feature requirements and constitution quality gates.

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3)
- Include exact file paths in descriptions

## Path Conventions

- Monorepo projects: `apps/backend/`, `apps/frontend/`
- Workspace/infrastructure: `tools/`, `docker/`, root config files
- Specs: `specs/001-setup-monorepo-baseline/`

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Initialize Nx monorepo skeleton, baseline project layout, and root workspace config.

- [x] T001 Initialize Nx workspace root configuration in nx.json
- [x] T002 Create pnpm workspace definition in pnpm-workspace.yaml
- [x] T003 Create backend project skeleton in apps/backend/src/**init**.py
- [x] T004 [P] Create backend tests package skeleton in apps/backend/tests/test_smoke.py
- [x] T005 [P] Create frontend project skeleton in apps/frontend/src/main.ts
- [x] T006 [P] Create frontend test skeleton in apps/frontend/tests/smoke.test.ts
- [x] T007 Create root local stack file in docker-compose.yml
- [x] T008 [P] Create compose environment baseline in docker/compose/stack.env

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Establish non-negotiable quality gates, affected-only Nx execution, and shared tooling.

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

- [x] T009 Create backend dependency manifest with uv metadata in apps/backend/pyproject.toml
- [x] T010 [P] Generate and pin backend lockfile in apps/backend/uv.lock
- [x] T011 Configure exact ruff lint selectors and ignore list in apps/backend/pyproject.toml
- [x] T012 [P] Add backend type-check and test tool config in apps/backend/pyproject.toml
- [x] T013 Create frontend package manifest with pnpm scripts in apps/frontend/package.json
- [x] T014 [P] Configure strict TypeScript compiler settings in apps/frontend/tsconfig.json
- [x] T015 [P] Configure Vitest runner and coverage thresholds in apps/frontend/vitest.config.ts
- [x] T016 [P] Configure Biome lint/format policy in apps/frontend/biome.json
- [x] T017 Create PMD installation script with pinned 7.22.0 commands in tools/quality/pmd/install-pmd.sh
- [x] T018 [P] Create PMD CPD execution script with minimum token threshold 50 in tools/quality/cpd/run-cpd.sh
- [x] T019 Define Nx named inputs and target defaults for affected-only execution in nx.json
- [x] T020 [P] Register backend project targets (lint, format, typecheck, test, coverage) in apps/backend/project.json
- [x] T021 [P] Register frontend project targets (lint, format, typecheck, test, coverage) in apps/frontend/project.json
- [x] T022 Register workspace duplication target and affected integration in tools/quality/project.json
- [x] T023 Define pre-commit hook pipeline for required gates in .pre-commit-config.yaml
- [x] T024 Add root quality orchestration scripts for affected checks in package.json

**Checkpoint**: Foundation ready - user story implementation can now begin in parallel

---

## Phase 3: User Story 1 - Create Empty Full-Stack Workspace (Priority: P1) 🎯 MVP

**Goal**: Backend and frontend projects are both discoverable and valid in Nx while containing no business implementation.

**Independent Test**: Clone repository, run workspace graph/listing and project validation commands, and verify both projects are recognized with only placeholder logic.

### Tests for User Story 1

- [x] T025 [P] [US1] Add workspace discovery smoke test for backend registration in apps/backend/tests/test_workspace_registration.py
- [x] T026 [P] [US1] Add workspace discovery smoke test for frontend registration in apps/frontend/tests/workspace-registration.test.ts

### Implementation for User Story 1

- [x] T027 [US1] Add integration verification command doc for workspace listing in specs/001-setup-monorepo-baseline/quickstart.md
- [x] T028 [P] [US1] Add backend placeholder module declaration in apps/backend/src/**init**.py
- [x] T029 [P] [US1] Add frontend placeholder bootstrap export in apps/frontend/src/main.ts
- [x] T030 [US1] Add Nx project tagging and boundary metadata for backend in apps/backend/project.json
- [x] T031 [US1] Add Nx project tagging and boundary metadata for frontend in apps/frontend/project.json
- [x] T032 [US1] Add monorepo project boundary notes in docs/architecture/monorepo-boundaries.md
- [x] T033 [US1] Verify no product endpoints/workflows exist and document evidence in specs/001-setup-monorepo-baseline/research.md

**Checkpoint**: User Story 1 is fully functional and independently testable.

---

## Phase 4: User Story 2 - Establish Developer Tooling Baseline (Priority: P2)

**Goal**: Both stacks have deterministic lint/format/type/test/coverage and duplication gates with no suppression path.

**Independent Test**: Run backend and frontend quality commands plus workspace duplication check and confirm deterministic pass/fail output.

### Tests for User Story 2

- [x] T034 [P] [US2] Add backend gate command smoke tests in apps/backend/tests/test_quality_commands.py
- [x] T035 [P] [US2] Add frontend gate command smoke tests in apps/frontend/tests/quality-commands.test.ts
- [x] T036 [P] [US2] Add duplication gate smoke test script in tools/quality/cpd/test-cpd.sh

### Implementation for User Story 2

- [x] T037 [US2] Enforce backend coverage threshold >= 90 in apps/backend/pyproject.toml
- [x] T038 [US2] Enforce frontend coverage threshold >= 90 in apps/frontend/vitest.config.ts
- [x] T039 [US2] Enforce TypeScript strict mode and strict companion flags in apps/frontend/tsconfig.json
- [x] T040 [US2] Wire Biome lint and format scripts in apps/frontend/package.json
- [x] T041 [US2] Wire uv-based lint/format/type/test scripts in apps/backend/pyproject.toml
- [x] T042 [US2] Add no-suppression policy checks to pre-commit hooks in .pre-commit-config.yaml
- [x] T043 [US2] Wire PMD CPD command into Nx duplication target in tools/quality/project.json
- [x] T044 [US2] Add affected-only quality command examples in specs/001-setup-monorepo-baseline/quickstart.md

**Checkpoint**: User Stories 1 and 2 both work independently.

---

## Phase 5: User Story 3 - Validate Local Full-Stack Run Path (Priority: P3)

**Goal**: One command starts the placeholder stack and health verification confirms both services are ready.

**Independent Test**: Start local stack, verify health for all placeholder services, then stop stack cleanly with one shutdown command.

### Tests for User Story 3

- [x] T045 [P] [US3] Add backend container health smoke check test in apps/backend/tests/test_container_health.py
- [x] T046 [P] [US3] Add frontend container health smoke check test in apps/frontend/tests/container-health.test.ts
- [x] T047 [P] [US3] Add compose startup verification script in tools/quality/local-stack/test-compose-stack.sh

### Implementation for User Story 3

- [x] T048 [US3] Define backend placeholder service and healthcheck in docker-compose.yml
- [x] T049 [US3] Define frontend placeholder service and healthcheck in docker-compose.yml
- [x] T050 [US3] Add shared compose environment variables for stack startup in docker/compose/stack.env
- [x] T051 [US3] Add stack startup/shutdown verification steps in specs/001-setup-monorepo-baseline/quickstart.md
- [x] T052 [US3] Add failure troubleshooting guidance for unhealthy services in docs/runbooks/local-stack-baseline.md

**Checkpoint**: All user stories are independently functional.

---

## Phase 6: Polish & Cross-Cutting Concerns

**Purpose**: Final validation, documentation cleanup, and baseline acceptance checks.

- [x] T053 [P] Validate Nx affected behavior for backend-only changes in tools/quality/verification/affected-backend.sh
- [x] T054 [P] Validate Nx affected behavior for frontend-only changes in tools/quality/verification/affected-frontend.sh
- [x] T055 [P] Validate Nx affected behavior for root-config changes in tools/quality/verification/affected-workspace.sh
- [x] T056 Run full baseline quality pipeline and capture evidence in specs/001-setup-monorepo-baseline/research.md
- [x] T057 Finalize onboarding instructions and command matrix in docs/onboarding/monorepo-baseline.md
- [x] T058 Run full local stack baseline verification and capture outputs in specs/001-setup-monorepo-baseline/quickstart.md
- [x] T059 [P] Validate affected lint runtime under 3 minutes for backend-only changes in tools/quality/verification/benchmark-affected-lint.sh
- [x] T060 [P] Validate affected test runtime under 3 minutes for frontend-only changes in tools/quality/verification/benchmark-affected-test.sh

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies - can start immediately
- **Foundational (Phase 2)**: Depends on Setup completion - blocks all user stories
- **User Stories (Phases 3-5)**: Depend on Foundational completion
- **Polish (Phase 6)**: Depends on all user stories being complete

### User Story Dependencies

- **US1 (P1)**: Starts after Foundational, no dependency on other stories
- **US2 (P2)**: Starts after Foundational; may consume US1 project registration but remains independently testable
- **US3 (P3)**: Starts after Foundational; may consume US1/US2 artifacts but remains independently testable

### Dependency Graph

- Foundation: Phase 1 -> Phase 2
- Story path: Phase 2 -> US1 -> US2 -> US3
- Delivery checkpoints: (US1 MVP) -> (US1+US2 quality baseline) -> (US1+US2+US3 local stack baseline)

### Within Each User Story

- Tests before implementation tasks
- Project registration and models before service wiring
- Service/config wiring before end-to-end verification
- Story checkpoint validation before advancing to next story

### Parallel Opportunities

- Setup: T004, T005, T006, T008 can run in parallel after T001-T003
- Foundational: T010, T012, T014, T015, T016, T018, T020, T021 can run in parallel after base manifests exist
- US1: T025 and T026 in parallel; T028 and T029 in parallel
- US2: T034, T035, T036 in parallel
- US3: T045, T046, T047 in parallel
- Polish: T053, T054, T055, T059, T060 in parallel

---

## Parallel Example: User Story 1

```bash
# Run US1 tests in parallel
Task: "T025 [US1] apps/backend/tests/test_workspace_registration.py"
Task: "T026 [US1] apps/frontend/tests/workspace-registration.test.ts"

# Run US1 placeholder implementation in parallel
Task: "T028 [US1] apps/backend/src/__init__.py"
Task: "T029 [US1] apps/frontend/src/main.ts"
```

## Parallel Example: User Story 2

```bash
# Run US2 gate smoke tests in parallel
Task: "T034 [US2] apps/backend/tests/test_quality_commands.py"
Task: "T035 [US2] apps/frontend/tests/quality-commands.test.ts"
Task: "T036 [US2] tools/quality/cpd/test-cpd.sh"
```

## Parallel Example: User Story 3

```bash
# Run US3 health tests in parallel
Task: "T045 [US3] apps/backend/tests/test_container_health.py"
Task: "T046 [US3] apps/frontend/tests/container-health.test.ts"
Task: "T047 [US3] tools/quality/local-stack/test-compose-stack.sh"
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1: Setup
2. Complete Phase 2: Foundational
3. Complete Phase 3: User Story 1
4. Validate workspace discoverability and no-implementation baseline
5. Demo MVP baseline

### Incremental Delivery

1. Deliver US1 for monorepo registration baseline
2. Deliver US2 for strict quality gate baseline
3. Deliver US3 for local stack runtime baseline
4. Finalize Phase 6 cross-cutting verification

### Parallel Team Strategy

1. Team aligns on Phase 1 and Phase 2 foundations
2. Then split stories by ownership:
   - Developer A: US1
   - Developer B: US2
   - Developer C: US3
3. Rejoin for Phase 6 validation and documentation

---

## Notes

- All tasks follow required checklist format: checkbox + task ID + optional [P] + optional [US#] + exact file path.
- Suggested MVP scope: Phase 1 + Phase 2 + Phase 3 (US1).
- No task includes rule suppression or quality-gate bypass paths.
