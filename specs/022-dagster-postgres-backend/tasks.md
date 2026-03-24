# Tasks: Dagster Metadata Postgres Migration

**Input**: Design documents from `/Users/hackerc/Projects/longtail-experiment/specs/022-dagster-postgres-backend/`
**Prerequisites**: plan.md (required), spec.md (required for user stories), research.md, data-model.md, contracts/, quickstart.md

**Tests**: Test tasks are REQUIRED. Every user story and foundational component MUST include automated test coverage sufficient to maintain >= 90% coverage in affected projects. Before any commit and before any AI agent stops work, the full repository suite MUST pass via `pnpm exec nx run-many -t test --all`; targeted tests alone are never sufficient for this stop gate. Before any commit, monorepo coverage MUST pass via `pnpm exec nx run-many -t coverage --all` with >= 90% thresholds in every project.

**Organization**: Tasks are grouped by user story so each story can be implemented and validated independently.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (US1, US2, US3)
- Include exact file paths in descriptions

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Establish baseline configuration surfaces and dependency support for PostgreSQL-backed Dagster metadata storage.

- [x] T001 Add Dagster metadata database environment variables and defaults in docker/compose/stack.env
- [x] T002 Add example secrets and metadata DB credential notes in docker/compose/local.secrets.env.example
- [x] T003 Add Dagster Postgres storage dependency declarations in apps/pipeline/pyproject.toml
- [x] T004 Regenerate pipeline lockfile after dependency update in apps/pipeline/uv.lock
- [x] T005 [P] Add feature-specific verification command aliases for metadata-store checks in apps/pipeline/project.json

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Implement local-stack and runtime plumbing required before user-story behavior can be validated.

**⚠️ CRITICAL**: No user story work begins until this phase is complete.

- [x] T006 Configure dual-database topology and Dagit metadata DB wiring in docker-compose.yml
- [x] T007 Create Dagster storage backend configuration file for local runtime in apps/pipeline/dagster.yaml
- [x] T008 [P] Update local Dagit startup helper to require metadata DB settings and fail fast in tools/quality/local-stack/start-dagit-local.sh
- [x] T009 [P] Update Dagit endpoint probe to assert metadata-backed workspace health signal in tools/quality/local-stack/test-dagit-endpoint.sh
- [x] T010 Update compose stack health verification for metadata DB readiness in tools/quality/local-stack/test-compose-stack.sh
- [x] T011 [P] Extend local DB bootstrap script to verify metadata DB role initialization in tools/quality/local-stack/test-local-db-bootstrap.sh
- [x] T012 [P] Extend aggregate readiness flow to include metadata DB checks in tools/quality/local-stack/test-db-readiness.sh
- [x] T013 Add reusable orchestration metadata DB configuration guards in apps/pipeline/src/orchestration/runtime.py
- [x] T014 Add foundational coverage for metadata configuration and fail-fast guards in apps/pipeline/tests/orchestration/test_dagster_metadata_storage_config.py

**Checkpoint**: Foundation ready. User story implementation can proceed.

---

## Phase 3: User Story 1 - Run concurrent ingest jobs reliably (Priority: P1) 🎯 MVP

**Goal**: Ensure concurrent source onboarding runs persist Dagster run/event/schedule metadata without SQLite lock failures.

**Independent Test**: Launch representative concurrent source workloads and verify terminal run tracking plus run-log queryability with zero lock-protocol failures.

### Tests for User Story 1 (REQUIRED) ⚠️

- [x] T015 [P] [US1] Add orchestration integration test for concurrent metadata persistence in apps/pipeline/tests/orchestration/test_dagster_metadata_concurrency.py
- [x] T016 [P] [US1] Add regression test proving no SQLite fallback is used during Dagit runtime startup in apps/pipeline/tests/orchestration/test_dagit_runtime_fail_fast.py

### Implementation for User Story 1

- [x] T017 [US1] Wire Dagster Definitions runtime to PostgreSQL metadata configuration in apps/pipeline/src/orchestration/definitions.py
- [x] T018 [US1] Add metadata DB connection guardrails and diagnostics for runtime bootstrapping in apps/pipeline/src/orchestration/runtime.py
- [x] T019 [US1] Update compose-based Dagit command environment to consume metadata DB variables in docker-compose.yml
- [x] T020 [US1] Add concurrency validation execution/monitoring guidance for operators in specs/022-dagster-postgres-backend/quickstart.md
- [x] T021 [US1] Record US1 validation evidence and pass/fail criteria in specs/022-dagster-postgres-backend/research.md

**Checkpoint**: User Story 1 is independently testable and demonstrates lock-failure mitigation.

---

## Phase 4: User Story 2 - Operate two database roles in local stack (Priority: P2)

**Goal**: Keep orchestration metadata and canonical output-data roles operationally isolated in local workflows.

**Independent Test**: Bring up local stack from clean state, verify both DB roles are healthy, and validate metadata-only reset/troubleshooting steps do not alter canonical output data.

### Tests for User Story 2 (REQUIRED) ⚠️

- [x] T022 [P] [US2] Add local-stack script portability test coverage for dual-role bootstrap checks in libs/db/tests/test_local_stack_script_portability.py
- [x] T023 [P] [US2] Add orchestration smoke validation for dual-role workspace readiness in apps/pipeline/tests/orchestration/test_definitions_smoke.py

### Implementation for User Story 2

- [x] T024 [US2] Implement metadata/output DB role separation checks in tools/quality/local-stack/test-local-db-bootstrap.sh
- [x] T025 [US2] Implement metadata/output DB readiness assertions in tools/quality/local-stack/test-compose-stack.sh
- [x] T026 [US2] Add dual-role migration/readiness command sequence updates in tools/quality/local-stack/test-db-readiness.sh
- [x] T027 [US2] Update local stack operations guidance for dual-database role management in docs/runbooks/local-stack-baseline.md
- [x] T028 [US2] Document revised local stack architecture and commands in AGENTS.md

**Checkpoint**: User Story 2 is independently testable and verifies operational role isolation.

---

## Phase 5: User Story 3 - Diagnose configuration failures quickly (Priority: P3)

**Goal**: Provide deterministic fail-fast diagnostics for invalid metadata DB configuration and clear recovery behavior.

**Independent Test**: Inject invalid metadata DB settings, verify explicit failure diagnostics, then restore settings and verify normal startup without code edits.

### Tests for User Story 3 (REQUIRED) ⚠️

- [x] T029 [P] [US3] Add fail-fast startup-path test for missing metadata DB variables in apps/pipeline/tests/orchestration/test_dagit_runtime_fail_fast.py
- [x] T030 [P] [US3] Add endpoint probe diagnostic contract test for metadata misconfiguration in apps/pipeline/tests/orchestration/test_definitions_smoke.py

### Implementation for User Story 3

- [x] T031 [US3] Add explicit metadata configuration error categories and remediation hints in tools/quality/local-stack/start-dagit-local.sh
- [x] T032 [US3] Add metadata misconfiguration diagnostic outputs and thresholds in tools/quality/local-stack/test-dagit-endpoint.sh
- [x] T033 [US3] Update failure-matrix and remediation runbook sections for metadata DB issues in docs/runbooks/local-stack-baseline.md
- [x] T034 [US3] Align runtime contract with final diagnostics and fail-fast behavior in specs/022-dagster-postgres-backend/contracts/dagster-metadata-runtime.md

**Checkpoint**: User Story 3 is independently testable and provides clear recovery workflow.

---

## Phase 6: Polish & Cross-Cutting Concerns

**Purpose**: Final consistency, documentation, and stop-gate validation across all stories.

- [x] T035 [P] Reconcile plan/design artifacts with implementation deltas in specs/022-dagster-postgres-backend/plan.md
- [x] T036 [P] Update final validation run instructions and expected outputs in specs/022-dagster-postgres-backend/quickstart.md
- [x] T037 Execute feature-focused orchestration/local-stack verification suite and record outcomes in specs/022-dagster-postgres-backend/tasks.md
- [x] T038 Run full monorepo test stop gate and record pass result in specs/022-dagster-postgres-backend/tasks.md
- [x] T039 Run full monorepo coverage stop gate and record pass result in specs/022-dagster-postgres-backend/tasks.md

---

## Dependencies & Execution Order

### Phase Dependencies

- **Phase 1 (Setup)**: No dependencies.
- **Phase 2 (Foundational)**: Depends on Phase 1 and blocks all user stories.
- **Phase 3 (US1)**: Depends on Phase 2 completion.
- **Phase 4 (US2)**: Depends on Phase 2 completion; can run after US1 or in parallel once foundational tasks are done.
- **Phase 5 (US3)**: Depends on Phase 2 completion; can run after US1 or in parallel once foundational tasks are done.
- **Phase 6 (Polish)**: Depends on completion of targeted user stories.

### User Story Dependencies

- **US1 (P1)**: No dependency on other stories; defines MVP.
- **US2 (P2)**: Independent from US1 behavior, but shares foundational local-stack plumbing.
- **US3 (P3)**: Independent diagnostics layer, but relies on foundational configuration surfaces.

### Within Each User Story

- Tests first and failing before implementation where applicable.
- Runtime/config implementation before documentation evidence tasks.
- Story checkpoints must pass independently before moving to polish.

### Parallel Opportunities

- Setup parallel tasks: T005.
- Foundational parallel tasks: T008, T009, T011, T012.
- US1 parallel tests: T015, T016.
- US2 parallel tests: T022, T023.
- US3 parallel tests: T029, T030.
- Polish parallel tasks: T035, T036.

---

## Parallel Example: User Story 1

```bash
# Run US1 test creation tasks in parallel:
Task: "T015 [US1] Add orchestration integration test in apps/pipeline/tests/orchestration/test_dagster_metadata_concurrency.py"
Task: "T016 [US1] Add no-fallback regression test in apps/pipeline/tests/orchestration/test_dagit_runtime_fail_fast.py"

# After tests exist, implement runtime and compose wiring:
Task: "T017 [US1] Update definitions wiring in apps/pipeline/src/orchestration/definitions.py"
Task: "T019 [US1] Update Dagit metadata environment wiring in docker-compose.yml"
```

---

## Implementation Strategy

### MVP First (US1 only)

1. Complete Phase 1 and Phase 2.
2. Complete Phase 3 (US1).
3. Validate concurrent run reliability and lock-failure elimination.
4. Demo/ship MVP if acceptable.

### Incremental Delivery

1. Deliver US1 for reliability outcome.
2. Deliver US2 for operational role separation.
3. Deliver US3 for fail-fast diagnostics and recovery clarity.
4. Finish with Phase 6 polish and mandatory full-suite gates.

### Parallel Team Strategy

1. One engineer leads foundational runtime/config tasks.
2. After Phase 2, assign US1, US2, and US3 to separate engineers.
3. Merge with shared polish and final gate execution.

---

## Notes

- All tasks follow required checklist format: checkbox, sequential Task ID, optional [P], required [US#] on user-story tasks, and explicit file path.
- Coverage must remain >= 90% for all affected projects.
- Before commit and before any agent handoff/end: run `pnpm exec nx run-many -t test --all`.
- Before commit: run `pnpm exec nx run-many -t coverage --all`.
- Update documentation in the same change as behavior/configuration updates, including AGENTS.md when commands/workflows change.

## Validation Outcomes

- 2026-03-24: `pnpm exec nx run pipeline:test:orchestration:metadata-store` passed.
- 2026-03-24: `PYTHONPATH=apps/pipeline uv run --project apps/pipeline pytest --no-cov apps/pipeline/tests/orchestration/test_dagster_metadata_storage_config.py apps/pipeline/tests/orchestration/test_dagit_runtime_fail_fast.py apps/pipeline/tests/orchestration/test_dagster_metadata_concurrency.py apps/pipeline/tests/orchestration/test_definitions_smoke.py` passed.
- 2026-03-24: `uv run --project libs/db pytest --no-cov libs/db/tests/test_local_stack_script_portability.py` passed.
- 2026-03-24: `pnpm exec nx run-many -t test --all` passed.
- 2026-03-24: `pnpm exec nx run-many -t coverage --all` passed.
