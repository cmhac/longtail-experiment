# Tasks: Provider Adapter Bootstrap Standard

**Input**: Design documents from /Users/hackerc/Projects/longtail-experiment/specs/021-bootstrap-provider-script/
**Prerequisites**: plan.md (required), spec.md (required for user stories), research.md, data-model.md, contracts/

**Tests**: Test tasks are required. Every user story and foundational component includes automated coverage tasks aligned with repository 90% thresholds and stop-gate commands.

**Organization**: Tasks are grouped by user story so each story can be implemented and validated independently.

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Prepare command entrypoint, bootstrap script location, and scaffold template location.

- [X] T001 Add root script entry for provider bootstrap command in /Users/hackerc/Projects/longtail-experiment/package.json
- [X] T002 Create bootstrap script module placeholder in /Users/hackerc/Projects/longtail-experiment/tools/provider-bootstrap/bootstrap_provider.py
- [X] T003 [P] Create scaffold template file in /Users/hackerc/Projects/longtail-experiment/tools/provider-bootstrap/templates/provider_source_template.py.tmpl
- [X] T004 [P] Add bootstrap tooling package marker and module exports in /Users/hackerc/Projects/longtail-experiment/tools/provider-bootstrap/**init**.py
- [X] T005 [P] Add bootstrap command usage note to repository command references in /Users/hackerc/Projects/longtail-experiment/AGENTS.md

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Build shared validation and generation infrastructure that all user stories depend on.

**Critical**: No user story implementation starts until this phase is complete.

- [X] T006 Implement ProviderBootstrapRequest argument parsing and normalization in /Users/hackerc/Projects/longtail-experiment/tools/provider-bootstrap/bootstrap_provider.py
- [X] T007 [P] Implement naming and cron validation helpers in /Users/hackerc/Projects/longtail-experiment/tools/provider-bootstrap/validation.py
- [X] T008 [P] Implement source-key and file-collision detection helpers in /Users/hackerc/Projects/longtail-experiment/tools/provider-bootstrap/collision_checks.py
- [X] T009 Implement scaffold rendering helper from template in /Users/hackerc/Projects/longtail-experiment/tools/provider-bootstrap/render.py
- [X] T010 Implement structured success and failure output formatter in /Users/hackerc/Projects/longtail-experiment/tools/provider-bootstrap/output.py
- [X] T011 [P] Add foundational unit tests for validation helpers in /Users/hackerc/Projects/longtail-experiment/apps/pipeline/tests/unit/test_provider_bootstrap_validation.py
- [X] T012 [P] Add foundational unit tests for collision checks in /Users/hackerc/Projects/longtail-experiment/apps/pipeline/tests/unit/test_provider_bootstrap_collision_checks.py
- [X] T013 Add foundational unit tests for template rendering in /Users/hackerc/Projects/longtail-experiment/apps/pipeline/tests/unit/test_provider_bootstrap_render.py

**Checkpoint**: Foundation complete; user story phases can proceed.

---

## Phase 3: User Story 1 - Generate A New Provider Scaffold (Priority: P1)

**Goal**: Provide a working root command that generates a valid provider adapter scaffold and fails safely on invalid input or collisions.

**Independent Test**: Run bootstrap command with valid input and verify one discoverable scaffold is generated; rerun with conflicting input and verify hard failure without overwrite.

### Tests for User Story 1

- [X] T014 [P] [US1] Add CLI success-path integration test in /Users/hackerc/Projects/longtail-experiment/apps/pipeline/tests/integration/test_provider_bootstrap_cli_success.py
- [X] T015 [P] [US1] Add CLI invalid-input integration test in /Users/hackerc/Projects/longtail-experiment/apps/pipeline/tests/integration/test_provider_bootstrap_cli_invalid_input.py
- [X] T016 [P] [US1] Add CLI collision integration test in /Users/hackerc/Projects/longtail-experiment/apps/pipeline/tests/integration/test_provider_bootstrap_cli_collisions.py
- [X] T017 [P] [US1] Add scaffold structure contract test in /Users/hackerc/Projects/longtail-experiment/apps/pipeline/tests/contract/test_provider_bootstrap_scaffold_contract.py

### Implementation for User Story 1

- [X] T018 [US1] Implement end-to-end CLI flow in /Users/hackerc/Projects/longtail-experiment/tools/provider-bootstrap/bootstrap_provider.py
- [X] T019 [US1] Wire root command to bootstrap module in /Users/hackerc/Projects/longtail-experiment/package.json
- [X] T020 [US1] Finalize generated adapter scaffold contract fields in /Users/hackerc/Projects/longtail-experiment/tools/provider-bootstrap/templates/provider_source_template.py.tmpl
- [X] T021 [US1] Implement non-overwrite behavior and explicit error codes in /Users/hackerc/Projects/longtail-experiment/tools/provider-bootstrap/output.py
- [X] T022 [US1] Add command-level smoke invocation test task wiring in /Users/hackerc/Projects/longtail-experiment/apps/pipeline/project.json
- [X] T023 [US1] Verify US1 coverage contribution using bootstrap-related test files in /Users/hackerc/Projects/longtail-experiment/apps/pipeline/tests/

**Checkpoint**: User Story 1 is independently executable and testable.

---

## Phase 4: User Story 2 - Enforce A Single Onboarding Standard (Priority: P2)

**Goal**: Update onboarding documentation to make bootstrap usage the required first step.

**Independent Test**: Read runbook and verify it mandates script-first adapter creation and references the command consistently.

### Tests for User Story 2

- [X] T024 [P] [US2] Add runbook content assertion test for script-first wording in /Users/hackerc/Projects/longtail-experiment/apps/pipeline/tests/contract/test_provider_onboarding_runbook_standard.py

### Implementation for User Story 2

- [X] T025 [US2] Update onboarding flow to require bootstrap command in /Users/hackerc/Projects/longtail-experiment/docs/runbooks/provider-onboarding.md
- [X] T026 [US2] Remove or reframe manual-first adapter creation guidance in /Users/hackerc/Projects/longtail-experiment/docs/runbooks/provider-onboarding.md
- [X] T027 [US2] Document root script usage and argument examples in /Users/hackerc/Projects/longtail-experiment/docs/runbooks/provider-onboarding.md
- [X] T028 [US2] Verify US2 coverage contribution using runbook contract test in /Users/hackerc/Projects/longtail-experiment/apps/pipeline/tests/contract/

**Checkpoint**: User Story 2 guidance is independently complete and verifiable.

---

## Phase 5: User Story 3 - Guide Agent-Driven Onboarding (Priority: P3)

**Goal**: Ensure onboarding skill requires runbook review and bootstrap command usage before adapter coding.

**Independent Test**: Read skill file and verify explicit instructions to read runbook first and generate scaffold via bootstrap command.

### Tests for User Story 3

- [X] T029 [P] [US3] Add skill contract assertion test for runbook-read and bootstrap-first directives in /Users/hackerc/Projects/longtail-experiment/apps/pipeline/tests/contract/test_onboard_provider_skill_bootstrap_standard.py

### Implementation for User Story 3

- [X] T030 [US3] Update onboarding skill prerequisites to require runbook read in /Users/hackerc/Projects/longtail-experiment/.agents/skills/onboard-provider/SKILL.md
- [X] T031 [US3] Update onboarding skill workflow to require bootstrap command usage in /Users/hackerc/Projects/longtail-experiment/.agents/skills/onboard-provider/SKILL.md
- [X] T032 [US3] Add explicit exception handling language when bootstrap is unavailable in /Users/hackerc/Projects/longtail-experiment/.agents/skills/onboard-provider/SKILL.md
- [X] T033 [US3] Verify US3 coverage contribution using skill contract test in /Users/hackerc/Projects/longtail-experiment/apps/pipeline/tests/contract/

**Checkpoint**: User Story 3 guidance is independently complete and verifiable.

---

## Phase 6: Polish & Cross-Cutting Concerns

**Purpose**: Final quality validation, consistency checks, and stop-gate execution.

- [X] T034 [P] Align runbook and skill terminology for command naming in /Users/hackerc/Projects/longtail-experiment/docs/runbooks/provider-onboarding.md
- [X] T035 [P] Align runbook and skill terminology for command naming in /Users/hackerc/Projects/longtail-experiment/.agents/skills/onboard-provider/SKILL.md
- [X] T036 Run quickstart verification steps and update notes in /Users/hackerc/Projects/longtail-experiment/specs/021-bootstrap-provider-script/quickstart.md
- [X] T037 Run full repository test stop gate and record pass status in /Users/hackerc/Projects/longtail-experiment/specs/021-bootstrap-provider-script/tasks.md
- [X] T038 Run full repository coverage stop gate and record pass status in /Users/hackerc/Projects/longtail-experiment/specs/021-bootstrap-provider-script/tasks.md
- [X] T039 Verify documentation impact summary remains current in /Users/hackerc/Projects/longtail-experiment/AGENTS.md

---

## Dependencies & Execution Order

### Phase Dependencies

- Phase 1 Setup: starts immediately.
- Phase 2 Foundational: depends on Phase 1 and blocks all user stories.
- Phase 3 US1: depends on Phase 2 completion.
- Phase 4 US2: depends on Phase 2 completion; can run in parallel with US1 once foundational tasks finish.
- Phase 5 US3: depends on Phase 2 completion; can run in parallel with US1 and US2 once foundational tasks finish.
- Phase 6 Polish: depends on all targeted user story phases.

### User Story Dependencies

- US1 (P1): no dependency on US2 or US3.
- US2 (P2): independent of US1 logic, but references final command naming from US1 implementation.
- US3 (P3): independent of US1 logic, but references final command naming from US1 implementation.

### Story Completion Order

1. US1 is the MVP and first delivery target.
2. US2 can ship after US1 or in parallel if command naming is stable.
3. US3 can ship after US1 or in parallel if command naming is stable.

---

## Parallel Execution Examples

### User Story 1

- Parallel lane A: T014 and T015 in /Users/hackerc/Projects/longtail-experiment/apps/pipeline/tests/integration/
- Parallel lane B: T016 and T017 in /Users/hackerc/Projects/longtail-experiment/apps/pipeline/tests/
- Parallel lane C: T019 and T020 in /Users/hackerc/Projects/longtail-experiment/package.json and /Users/hackerc/Projects/longtail-experiment/tools/provider-bootstrap/templates/provider_source_template.py.tmpl

### User Story 2

- Parallel lane A: T024 test task in /Users/hackerc/Projects/longtail-experiment/apps/pipeline/tests/contract/
- Parallel lane B: T025 and T026 documentation edits in /Users/hackerc/Projects/longtail-experiment/docs/runbooks/provider-onboarding.md

### User Story 3

- Parallel lane A: T029 test task in /Users/hackerc/Projects/longtail-experiment/apps/pipeline/tests/contract/
- Parallel lane B: T030 and T031 skill edits in /Users/hackerc/Projects/longtail-experiment/.agents/skills/onboard-provider/SKILL.md

---

## Implementation Strategy

### MVP First

1. Complete Phase 1 and Phase 2.
2. Complete US1 (Phase 3) and validate independent test criteria.
3. Validate stop-gate tests and coverage after US1 for MVP readiness.

### Incremental Delivery

1. Deliver US1 command and scaffold generation first.
2. Deliver US2 runbook standardization next.
3. Deliver US3 agent skill alignment last.
4. Run final Polish phase and full stop gates.

### Task Format Validation

- Every task follows required checklist format: checkbox, task ID, optional parallel marker, required story label in user-story phases, and explicit file path.
- Setup, Foundational, and Polish phases intentionally omit story labels per task generation rules.
