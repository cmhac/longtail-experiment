# Tasks: Local Development Database Readiness

**Input**: Design documents from `/specs/004-local-dev-db/`
**Prerequisites**: plan.md (required), spec.md (required for user stories), research.md, data-model.md, contracts/

**Tests**: Test tasks are REQUIRED. Every user story and foundational component MUST include automated test coverage sufficient to maintain >= 90% coverage in affected projects.

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3)
- Include exact file paths in descriptions

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Prepare local DB scaffolding, migration entry points, and verification script layout.

- [x] T001 Add local DB environment variables to docker/compose/stack.env
- [x] T002 Add development PostgreSQL service scaffold with persistent volume wiring in docker-compose.yml
- [x] T003 [P] Add Alembic configuration file for shared DB migrations in libs/db/alembic.ini
- [x] T004 [P] Create local migration runner script in tools/quality/local-stack/run-db-migrations.sh
- [x] T005 [P] Create migration revision status script in tools/quality/local-stack/check-db-revision.sh
- [x] T006 [P] Add executable permissions and shell strict-mode headers for new local-stack scripts in tools/quality/local-stack/run-db-migrations.sh and tools/quality/local-stack/check-db-revision.sh

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Implement shared readiness primitives that all user stories depend on.

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

- [x] T007 Configure shared DB URL resolution for Alembic runtime in libs/db/alembic/env.py
- [x] T008 [P] Add DB connection settings helper for local migration/runtime commands in libs/db/src/db/settings.py
- [x] T009 [P] Add fail-fast migration wrapper behavior and recovery messaging in tools/quality/local-stack/run-db-migrations.sh
- [x] T010 [P] Add deterministic revision baseline assertion logic in tools/quality/local-stack/check-db-revision.sh
- [x] T011 Add local DB service health checks to stack verification flow in tools/quality/local-stack/test-compose-stack.sh
- [x] T012 [P] Add foundational migration readiness smoke test for config and command contracts in libs/db/tests/test_migration_readiness.py
- [x] T013 [P] Add foundational repeatable rerun safety test for migration wrapper scripts in libs/db/tests/test_migration_rerun_contract.py
- [x] T014 Add local defect evidence template for implementation tracking in specs/004-local-dev-db/defect-log.md
- [x] T015 Validate foundational quality gates for shared DB and local-stack tooling in libs/db/tests/test_migration_readiness.py and libs/db/tests/test_migration_rerun_contract.py

**Checkpoint**: Foundation ready - user story implementation can now begin in parallel

---

## Phase 3: User Story 1 - Boot Local Database (Priority: P1) 🎯 MVP

**Goal**: Start a healthy local DB with documented config defaults and persistent-by-default behavior.

**Independent Test**: Run documented startup flow from a clean workspace and verify DB service is healthy and reachable.

### Tests for User Story 1 (REQUIRED) ⚠️

- [x] T016 [P] [US1] Add compose service presence and health test coverage in apps/backend/tests/test_local_db_bootstrap.py
- [x] T017 [P] [US1] Add environment default/value validation test for local DB profile in apps/pipeline/tests/test_local_db_profile_defaults.py
- [x] T018 [P] [US1] Add integration shell test for bootstrap success path in tools/quality/local-stack/test-local-db-bootstrap.sh

### Implementation for User Story 1

- [x] T019 [US1] Implement full PostgreSQL local service definition with named volume and healthcheck in docker-compose.yml
- [x] T020 [US1] Define canonical local DB defaults (host/port/db/user/password source) in docker/compose/stack.env
- [x] T021 [US1] Extend stack verification to fail when local DB service is missing/unhealthy in tools/quality/local-stack/test-compose-stack.sh
- [x] T022 [US1] Add persistent-by-default behavior and explicit reset-only wording to setup runbook in docs/runbooks/local-stack-baseline.md
- [x] T023 [US1] Add development-only warning language for local DB usage in docs/onboarding/monorepo-baseline.md
- [x] T024 [US1] Capture US1 bootstrap validation evidence and timing notes in specs/004-local-dev-db/research.md
- [x] T025 [US1] Verify US1 quality gates and coverage in apps/backend/tests/test_local_db_bootstrap.py and apps/pipeline/tests/test_local_db_profile_defaults.py

**Checkpoint**: User Story 1 is independently runnable as MVP local DB bootstrap

---

## Phase 4: User Story 2 - Apply and Verify Migrations (Priority: P2)

**Goal**: Apply migrations from a fresh local DB, fail fast on errors, and verify latest revision state.

**Independent Test**: Provision fresh local DB, run migration command, then verify current revision equals expected baseline.

### Tests for User Story 2 (REQUIRED) ⚠️

- [x] T026 [P] [US2] Add migration fail-fast contract tests for first-error stop behavior in libs/db/tests/test_migration_fail_fast.py
- [x] T027 [P] [US2] Add migration revision status verification tests in libs/db/tests/test_migration_revision_status.py
- [x] T028 [P] [US2] Add backend-facing migration command smoke tests in apps/backend/tests/test_local_db_migration_commands.py

### Implementation for User Story 2

- [x] T029 [US2] Implement canonical Alembic local configuration with shared migration script location in libs/db/alembic.ini
- [x] T030 [US2] Update Alembic environment to use local DB URL and metadata safely for online/offline flows in libs/db/alembic/env.py
- [x] T031 [US2] Implement fail-fast migration apply flow and actionable recovery output in tools/quality/local-stack/run-db-migrations.sh
- [x] T032 [US2] Implement revision baseline check command and mismatch exit behavior in tools/quality/local-stack/check-db-revision.sh
- [x] T033 [US2] Document canonical migration apply/check command sequence in specs/004-local-dev-db/quickstart.md
- [x] T034 [US2] Add migration readiness command guidance and development-only warning language to docs/onboarding/monorepo-baseline.md, docs/runbooks/local-stack-baseline.md, and specs/004-local-dev-db/quickstart.md
- [x] T035 [US2] Record migration verification evidence from at least 20 fresh-run attempts (apply + current) and computed success rate target (>=95%) in specs/004-local-dev-db/research.md
- [x] T036 [US2] Verify US2 quality gates and coverage in libs/db/tests/test_migration_fail_fast.py and libs/db/tests/test_migration_revision_status.py

**Checkpoint**: User Story 2 independently verifies migration readiness and baseline schema alignment

---

## Phase 5: User Story 3 - Resolve Local Setup Defects (Priority: P3)

**Goal**: Detect, fix, document, and verify all reproducible local setup/migration defects discovered in this feature.

**Independent Test**: Reproduce tracked defects, apply fixes, and confirm rerun success with documented evidence for each defect.

### Tests for User Story 3 (REQUIRED) ⚠️

- [x] T037 [P] [US3] Add backend regression tests for reproduced local setup defects in apps/backend/tests/test_local_db_defect_regressions.py
- [x] T038 [P] [US3] Add pipeline regression tests for reproduced local setup defects in apps/pipeline/tests/test_local_db_defect_regressions.py
- [x] T039 [P] [US3] Add shared DB repeatable rerun regression test coverage in libs/db/tests/test_local_db_repeatability.py

### Implementation for User Story 3

- [x] T040 [US3] Track each reproducible defect with symptom, root cause, and fix summary in specs/004-local-dev-db/defect-log.md
- [x] T041 [US3] Implement fixes for all reproduced compose bootstrap defects in docker-compose.yml and docker/compose/stack.env
- [x] T042 [US3] Implement fixes for all reproduced migration flow defects in tools/quality/local-stack/run-db-migrations.sh and tools/quality/local-stack/check-db-revision.sh
- [x] T043 [US3] Update defect recovery guidance for each resolved issue in docs/runbooks/local-stack-baseline.md
- [x] T044 [US3] Capture per-defect verification command evidence in specs/004-local-dev-db/research.md
- [x] T045 [US3] Verify US3 quality gates and coverage in apps/backend/tests/test_local_db_defect_regressions.py and apps/pipeline/tests/test_local_db_defect_regressions.py

**Checkpoint**: User Story 3 independently proves all discovered local setup defects are fixed and documented

---

## Phase 6: Polish & Cross-Cutting Concerns

**Purpose**: Final consistency, command hardening, and full-system readiness validation.

- [x] T046 [P] Align architecture boundary documentation for local DB responsibilities in docs/architecture/monorepo-boundaries.md
- [x] T047 [P] Update AGENTS.md with canonical local DB and migration readiness commands in AGENTS.md
- [x] T048 [P] Add local DB readiness verification helper script combining bootstrap, migrate, and revision checks in tools/quality/local-stack/test-db-readiness.sh
- [x] T049 Run quickstart validation flow and record pass/fail evidence in specs/004-local-dev-db/research.md
- [x] T050 Run full affected quality suite and local stack verification via package.json scripts and tools/quality/local-stack/test-compose-stack.sh
- [x] T051 [P] Verify shell script portability and strict error behavior across local-stack scripts in tools/quality/local-stack/run-db-migrations.sh and tools/quality/local-stack/check-db-revision.sh
- [x] T052 [P] Update onboarding and runbook command matrices to include new readiness script in docs/onboarding/monorepo-baseline.md and docs/runbooks/local-stack-baseline.md

---

## Dependencies & Execution Order

### Phase Dependencies

- **Phase 1 (Setup)**: No dependencies, starts immediately.
- **Phase 2 (Foundational)**: Depends on Phase 1; blocks all user story phases.
- **Phase 3 (US1)**: Depends on Phase 2 completion.
- **Phase 4 (US2)**: Depends on Phase 2 completion; can proceed after US1 or in parallel if staffing allows.
- **Phase 5 (US3)**: Depends on Phase 2 completion and should follow US1/US2 so defect tracking covers complete flows.
- **Phase 6 (Polish)**: Depends on completion of targeted user stories.

### User Story Dependencies

- **US1 (P1)**: Independent after foundational phase; defines MVP local DB bootstrap.
- **US2 (P2)**: Independent after foundational phase; builds migration readiness and revision verification behavior.
- **US3 (P3)**: Depends on implemented bootstrap/migration flows to discover and close real defects.

### Within Each User Story

- Tests must be written first and fail before implementation tasks.
- Configuration and script wiring before documentation evidence capture.
- Story quality verification tasks complete each story before moving on.

### Parallel Opportunities

- Setup and foundational tasks marked [P] can run concurrently.
- User-story test tasks marked [P] can be developed in parallel per story.
- Documentation tasks in polish marked [P] can proceed concurrently once behavior is stable.

---

## Parallel Example: User Story 1

```bash
# Launch US1 tests in parallel
Task: "Add compose service presence and health test coverage in apps/backend/tests/test_local_db_bootstrap.py"
Task: "Add environment default/value validation test for local DB profile in apps/pipeline/tests/test_local_db_profile_defaults.py"
Task: "Add integration shell test for bootstrap success path in tools/quality/local-stack/test-local-db-bootstrap.sh"
```

## Parallel Example: User Story 2

```bash
# Launch US2 tests in parallel
Task: "Add migration fail-fast contract tests for first-error stop behavior in libs/db/tests/test_migration_fail_fast.py"
Task: "Add migration revision status verification tests in libs/db/tests/test_migration_revision_status.py"
Task: "Add backend-facing migration command smoke tests in apps/backend/tests/test_local_db_migration_commands.py"
```

## Parallel Example: User Story 3

```bash
# Launch US3 tests in parallel
Task: "Add backend regression tests for reproduced local setup defects in apps/backend/tests/test_local_db_defect_regressions.py"
Task: "Add pipeline regression tests for reproduced local setup defects in apps/pipeline/tests/test_local_db_defect_regressions.py"
Task: "Add shared DB repeatable rerun regression test coverage in libs/db/tests/test_local_db_repeatability.py"
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1: Setup.
2. Complete Phase 2: Foundational.
3. Complete Phase 3: User Story 1.
4. Validate US1 independently with T016-T018 and T025.
5. Demo local DB bootstrap readiness before migration feature expansion.

### Incremental Delivery

1. Finish Setup and Foundational phases.
2. Deliver US1 local DB bootstrap as MVP.
3. Deliver US2 migration apply and revision verification.
4. Deliver US3 all-defects remediation and evidence closure.
5. Run polish phase for full quality and documentation completeness.

### Parallel Team Strategy

1. Team aligns on setup/foundational scripts and compose changes.
2. After Phase 2:
   - Developer A leads US1 bootstrap tests and config.
   - Developer B leads US2 migration command and revision checks.
   - Developer C leads US3 defect capture and regression tests.
3. Team converges for Phase 6 full verification and documentation updates.

---

## Notes

- [P] tasks indicate no direct file conflict and no dependency on incomplete same-phase tasks.
- Story labels map each user-story task to US1, US2, or US3 for traceability.
- Every task line follows strict checklist format with checkbox, task ID, optional markers, and explicit file paths.
- Coverage must remain >= 90% in affected backend and pipeline projects.
- AGENTS.md and local-runbook/onboarding docs must be updated in the same change as workflow or command changes.
