# Tasks: Source-Per-Asset Migration

**Input**: Design documents from /specs/010-source-asset-migration/
**Prerequisites**: plan.md (required), spec.md (required for user stories), research.md, data-model.md, contracts/

**Tests**: Test tasks are REQUIRED. Every user story and foundational component MUST include automated test coverage sufficient to maintain >= 90% coverage in affected projects.

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: [ID] [P?] [Story] Description

- [P]: Can run in parallel (different files, no dependencies)
- [Story]: Which user story this task belongs to (e.g., US1, US2, US3)
- Include exact file paths in descriptions

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Prepare migration scaffolding, validation entrypoints, and quality command wiring.

- [ ] T001 Create migration feature module scaffold in apps/pipeline/src/orchestration/jobs/source_assets/**init**.py
- [ ] T002 [P] Add source-asset contract type definitions in apps/pipeline/src/orchestration/jobs/source_assets/contracts.py
- [ ] T003 [P] Add source-asset discovery module skeleton in apps/pipeline/src/orchestration/jobs/source_assets/discovery.py
- [ ] T004 [P] Add cutover authority state helper skeleton in apps/pipeline/src/orchestration/jobs/source_assets/authority_state.py
- [ ] T005 Add orchestration task command aliases for this feature in apps/pipeline/project.json

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core orchestration migration infrastructure required by all user stories.

**CRITICAL**: No user story implementation can start before this phase is complete.

- [ ] T006 Implement deterministic source discovery order and registry loader in apps/pipeline/src/orchestration/jobs/source_assets/discovery.py
- [ ] T007 [P] Implement source registration contract validation and actionable error formatter in apps/pipeline/src/orchestration/jobs/source_assets/contracts.py
- [ ] T008 [P] Implement duplicate source-key rejection guard integration in apps/pipeline/src/orchestration/jobs/workflow_registry.py
- [ ] T009 Wire source-asset discovery into runtime assembly in apps/pipeline/src/orchestration/runtime.py
- [ ] T010 [P] Add foundational unit tests for discovery determinism and malformed module failures in apps/pipeline/tests/orchestration/test_source_asset_discovery.py
- [ ] T011 [P] Add foundational unit tests for duplicate source-key rejection in apps/pipeline/tests/orchestration/test_source_asset_contract_validation.py
- [ ] T012 Add foundational logging/telemetry fields for discovery and contract failures in apps/pipeline/src/orchestration/runtime.py

**Checkpoint**: Foundation ready - user story implementation can now begin.

---

## Phase 3: User Story 1 - Operators run one source at a time (Priority: P1) MVP

**Goal**: Enable explicit single-source trigger execution without running unrelated sources.

**Independent Test**: Trigger one valid source and verify only that source executes; trigger an invalid source and verify fail-fast rejection with no run started.

### Tests for User Story 1

- [ ] T013 [P] [US1] Add integration test for single-source trigger isolation in apps/pipeline/tests/orchestration/test_single_source_trigger_runtime.py
- [ ] T014 [P] [US1] Add integration test for invalid source-key rejection in apps/pipeline/tests/orchestration/test_single_source_trigger_runtime.py
- [ ] T015 [P] [US1] Add smoke assertion updates for source-targeted execution including a newly onboarded implementation-window source fixture in apps/pipeline/tests/orchestration/test_definitions_smoke.py

### Implementation for User Story 1

- [ ] T016 [US1] Implement source-targeted execution selector in apps/pipeline/src/orchestration/jobs/ingest_job.py
- [ ] T017 [US1] Wire selector validation to source registration state in apps/pipeline/src/orchestration/runtime.py
- [ ] T018 [P] [US1] Add source-trigger request normalization helper in apps/pipeline/src/orchestration/jobs/source_assets/triggering.py
- [ ] T019 [US1] Add structured failure outcome for invalid source requests in apps/pipeline/src/orchestration/jobs/source_assets/triggering.py
- [ ] T020 [US1] Verify US1 coverage contribution >=90% and record manual-trigger success-rate measurement against the >=95% criterion in specs/010-source-asset-migration/quickstart.md

**Checkpoint**: User Story 1 is independently functional and testable.

---

## Phase 4: User Story 2 - Operators monitor source outcomes directly (Priority: P2)

**Goal**: Expose source-level materialization and outcome metadata directly for operator triage.

**Independent Test**: Run successful and failing source executions and confirm source-level status and metadata visibility in orchestration views and persisted outcomes.

### Tests for User Story 2

- [ ] T021 [P] [US2] Add integration test for source-level success outcome visibility in apps/pipeline/tests/orchestration/test_source_outcome_visibility.py
- [ ] T022 [P] [US2] Add integration test for source-level failure metadata visibility in apps/pipeline/tests/orchestration/test_source_outcome_visibility.py
- [ ] T023 [P] [US2] Add forward persistence integrity test for post-cutover outcomes only (no historical parity requirement) in apps/pipeline/tests/orchestration/test_source_outcome_persistence_post_cutover.py

### Implementation for User Story 2

- [ ] T024 [US2] Emit source-level materialization metadata in apps/pipeline/src/orchestration/jobs/ingest_job.py
- [ ] T025 [US2] Map source execution outcomes to runtime persistence records in apps/pipeline/src/orchestration/runtime.py
- [ ] T026 [P] [US2] Implement failure summary payload builder for operator triage in apps/pipeline/src/orchestration/jobs/source_assets/outcomes.py
- [ ] T027 [US2] Ensure visibility metadata is attached for successful and failed source runs in apps/pipeline/src/orchestration/jobs/source_assets/outcomes.py
- [ ] T028 [US2] Verify US2 coverage contribution >=90% with targeted test run in apps/pipeline/tests/orchestration/test_source_outcome_visibility.py

**Checkpoint**: User Stories 1 and 2 are independently functional and testable.

---

## Phase 5: User Story 3 - Platform owners keep scheduling authority centralized (Priority: P3)

**Goal**: Complete big-bang cutover so Dagster is the sole scheduling authority, including partial-failure operation without legacy fallback.

**Independent Test**: Execute cadence checks post-cutover and confirm no legacy scheduling path can create runs; simulate partial source failures and confirm Dagster-only authority remains active.

### Tests for User Story 3

- [ ] T029 [P] [US3] Add regression test ensuring non-Dagster scheduler paths are disabled in apps/pipeline/tests/orchestration/test_scheduler_runtime.py
- [ ] T030 [P] [US3] Add regression test for partial-failure cutover behavior without legacy fallback in apps/pipeline/tests/orchestration/test_cutover_partial_failure_behavior.py
- [ ] T031 [P] [US3] Add cadence integration assertion for Dagster-only scheduling authority in apps/pipeline/tests/orchestration/test_ingest_job_runtime.py

### Implementation for User Story 3

- [ ] T032 [US3] Retire legacy cadence entrypoint wiring in apps/pipeline/src/orchestration/runtime.py
- [ ] T033 [US3] Implement cutover authority mode enforcement in apps/pipeline/src/orchestration/jobs/source_assets/authority_state.py
- [ ] T034 [P] [US3] Implement post-cutover failed-source recovery orchestration path in apps/pipeline/src/orchestration/jobs/source_assets/recovery.py
- [ ] T035 [US3] Wire authority mode and recovery path integration in apps/pipeline/src/orchestration/definitions.py
- [ ] T036 [US3] Verify US3 coverage contribution >=90% and capture CutoverReadinessGate go/hold evidence before release-window cutover in specs/010-source-asset-migration/quickstart.md

**Checkpoint**: All user stories are independently functional and testable.

---

## Phase 6: Polish & Cross-Cutting Concerns

**Purpose**: Final verification, documentation, and quality completion across all stories.

- [ ] T037 [P] Update source-as-asset onboarding and scheduling runbook in docs/runbooks/local-stack-baseline.md
- [ ] T038 [P] Update developer onboarding references for source-asset operations in docs/onboarding/monorepo-baseline.md
- [ ] T039 [P] Update canonical commands and architecture notes in AGENTS.md
- [ ] T040 Run full orchestration quality gates for affected scope via pnpm run affected:test and uv run --project apps/pipeline pytest apps/pipeline/tests
- [ ] T041 Run compose and Dagit verification flow in tools/quality/local-stack/test-compose-stack.sh

---

## Dependencies & Execution Order

### Phase Dependencies

- Phase 1 (Setup): no dependencies.
- Phase 2 (Foundational): depends on Phase 1; blocks all user stories.
- Phase 3 (US1): depends on Phase 2.
- Phase 4 (US2): depends on Phase 2 and remains independently testable with foundational runtime wiring.
- Phase 5 (US3): depends on Phase 2 and uses artifacts from US1 and US2.
- Phase 6 (Polish): depends on completion of all selected user stories.

### User Story Dependencies

- US1 (P1): can start immediately after Phase 2.
- US2 (P2): can start after Phase 2 and is independently executable/testable using foundational runtime wiring.
- US3 (P3): can start after Phase 2; requires source registration and outcome visibility infrastructure from earlier phases.

### Within Each User Story

- Tests first and failing before implementation.
- Runtime integration after helper/module implementation.
- Coverage verification after story functionality is complete.

## Parallel Opportunities

- Phase 1: T002, T003, and T004 can run in parallel after T001.
- Phase 2: T007, T008, and T010/T011 can run in parallel once T006 starts stabilizing interfaces.
- US1: T013-T015 can run in parallel; T018 can run in parallel with T016.
- US2: T021-T023 can run in parallel; T026 can run in parallel with T024/T025.
- US3: T029-T031 can run in parallel; T034 can run in parallel with T032/T033.
- Polish: T037-T039 can run in parallel.

## Parallel Example: User Story 1

- Run T013, T014, and T015 together while implementing T016.
- Run T018 in parallel with T016, then integrate through T017 and T019.

## Parallel Example: User Story 2

- Run T021, T022, and T023 together.
- Run T026 in parallel with T024 and merge through T025 and T027.

## Parallel Example: User Story 3

- Run T029, T030, and T031 together.
- Run T034 in parallel with T032/T033, then complete T035.

## Implementation Strategy

### MVP First (User Story 1)

1. Complete Phase 1 and Phase 2.
2. Complete Phase 3 (US1).
3. Validate independent US1 trigger behavior before moving on.

### Incremental Delivery

1. Deliver US1 for source-targeted trigger control.
2. Deliver US2 for source-level outcome visibility.
3. Deliver US3 for Dagster-only scheduling cutover.
4. Finish with Phase 6 quality/documentation verification.

### Team Parallel Strategy

1. Team completes Phase 1 and 2 together.
2. After Phase 2, split by story owner:
   - Engineer A: US1
   - Engineer B: US2
   - Engineer C: US3
3. Rejoin for Phase 6 final verification.

## Notes

- All tasks follow strict checklist format with Task ID, optional [P], optional [USx], and exact file path.
- Coverage must remain >=90% in affected projects.
- Documentation updates are required in the same change as behavior updates.
- AGENTS.md updates are mandatory when commands/workflows/architecture references change.
