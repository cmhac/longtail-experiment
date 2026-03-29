---
description: "Task list template for feature implementation"
---

# Tasks: [FEATURE NAME]

**Input**: Design documents from `/specs/[###-feature-name]/`
**Prerequisites**: plan.md (required), spec.md (required for user stories), research.md, data-model.md, contracts/

**Tests**: Test tasks are REQUIRED. Every user story and foundational component MUST
include automated test coverage sufficient to maintain >= 90% coverage in affected
projects. Before any commit and before any AI agent stops work, the full repository
suite MUST pass via `pnpm exec nx run-many -t test --all`; targeted tests alone are
never sufficient for this stop gate. Before any commit, monorepo coverage MUST pass via
`pnpm exec nx run-many -t coverage --all` with >= 90% thresholds in every project.

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3)
- Include exact file paths in descriptions

## Path Conventions

- **Single project**: `src/`, `tests/` at repository root
- **Web app**: `backend/src/`, `frontend/src/`
- **Mobile**: `api/src/`, `ios/src/` or `android/src/`
- Paths shown below assume single project - adjust based on plan.md structure

<!--
  ============================================================================
  IMPORTANT: The tasks below are SAMPLE TASKS for illustration purposes only.

  The /speckit.tasks command MUST replace these with actual tasks based on:
  - User stories from spec.md (with their priorities P1, P2, P3...)
  - Feature requirements from plan.md
  - Entities from data-model.md
  - Endpoints from contracts/

  Tasks MUST be organized by user story so each story can be:
  - Implemented independently
  - Tested independently
  - Delivered as an MVP increment

  DO NOT keep these sample tasks in the generated tasks.md file.
  ============================================================================
-->

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Project initialization and basic structure

- [ ] T001 Create project structure per implementation plan
- [ ] T002 Initialize [language] project with [framework] dependencies
- [ ] T003 [P] Configure linting and formatting tools
- [ ] T004 [P] Configure strict type-checking and coverage gates (>= 90%) in CI and local checks
- [ ] T005 [P] Configure/verify pre-commit hooks enforcing lint, format, type-check, and tests

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core infrastructure that MUST be complete before ANY user story can be implemented

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

Examples of foundational tasks (adjust based on your project):

- [ ] T006 Setup database schema and migrations framework
- [ ] T007 [P] Implement authentication/authorization framework
- [ ] T008 [P] Setup API routing and middleware structure
- [ ] T009 Create base models/entities that all stories depend on
- [ ] T010 Configure error handling and logging infrastructure
- [ ] T011 Setup environment configuration management — required env vars MUST raise hard
      errors when absent; no soft fallbacks or silent outcomes for missing credentials
- [ ] T012 Integrate/update unified Docker Compose services for full local stack
      runability; declare `docker/compose/local.secrets.env` as `env_file` source for
      any service that requires secrets
- [ ] T013 [P] For frontend work, identify repeated UI patterns and extract/extend shared
      components in `apps/frontend/src/components` using HeroUI + Tailwind conventions

**Checkpoint**: Foundation ready - user story implementation can now begin in parallel

---

## Phase 3: User Story 1 - [Title] (Priority: P1) 🎯 MVP

**Goal**: [Brief description of what this story delivers]

**Independent Test**: [How to verify this story works on its own]

### Tests for User Story 1 (REQUIRED) ⚠️

> **NOTE: Write these tests FIRST, ensure they FAIL before implementation**

- [ ] T014 [P] [US1] Contract test for [endpoint] in tests/contract/test\_[name].py
- [ ] T015 [P] [US1] Integration test for [user journey] in tests/integration/test\_[name].py
- [ ] T016 [P] [US1] Unit tests for core logic in tests/unit/test\_[name].py

### Implementation for User Story 1

- [ ] T017 [P] [US1] Create [Entity1] model in src/models/[entity1].py
- [ ] T018 [P] [US1] Create [Entity2] model in src/models/[entity2].py
- [ ] T019 [US1] Implement [Service] in src/services/[service].py (depends on T017, T018)
- [ ] T020 [US1] Implement [endpoint/feature] in src/[location]/[file].py
- [ ] T021 [US1] Add validation and error handling
- [ ] T022 [US1] Add logging for user story 1 operations
- [ ] T023 [US1] For frontend work, extend or create shared HeroUI/Tailwind components in
      apps/frontend/src/components before duplicating route-level markup
- [ ] T024 [US1] Verify US1 coverage contribution maintains >= 90% threshold
- [ ] T0XX [US1] Update/create relevant documentation for US1 behavior changes in docs/ and AGENTS.md if applicable

**Checkpoint**: At this point, User Story 1 should be fully functional and testable independently

---

## Phase 4: User Story 2 - [Title] (Priority: P2)

**Goal**: [Brief description of what this story delivers]

**Independent Test**: [How to verify this story works on its own]

### Tests for User Story 2 (REQUIRED) ⚠️

- [ ] T025 [P] [US2] Contract test for [endpoint] in tests/contract/test\_[name].py
- [ ] T026 [P] [US2] Integration test for [user journey] in tests/integration/test\_[name].py
- [ ] T027 [P] [US2] Unit tests for core logic in tests/unit/test\_[name].py

### Implementation for User Story 2

- [ ] T028 [P] [US2] Create [Entity] model in src/models/[entity].py
- [ ] T029 [US2] Implement [Service] in src/services/[service].py
- [ ] T030 [US2] Implement [endpoint/feature] in src/[location]/[file].py
- [ ] T031 [US2] Integrate with User Story 1 components (if needed)
- [ ] T032 [US2] For frontend work, reuse or extend shared HeroUI/Tailwind components in
      apps/frontend/src/components instead of introducing parallel patterns
- [ ] T033 [US2] Verify US2 coverage contribution maintains >= 90% threshold
- [ ] T0XX [US2] Update/create relevant documentation for US2 behavior changes in docs/ and AGENTS.md if applicable

**Checkpoint**: At this point, User Stories 1 AND 2 should both work independently

---

## Phase 5: User Story 3 - [Title] (Priority: P3)

**Goal**: [Brief description of what this story delivers]

**Independent Test**: [How to verify this story works on its own]

### Tests for User Story 3 (REQUIRED) ⚠️

- [ ] T034 [P] [US3] Contract test for [endpoint] in tests/contract/test\_[name].py
- [ ] T035 [P] [US3] Integration test for [user journey] in tests/integration/test\_[name].py
- [ ] T036 [P] [US3] Unit tests for core logic in tests/unit/test\_[name].py

### Implementation for User Story 3

- [ ] T037 [P] [US3] Create [Entity] model in src/models/[entity].py
- [ ] T038 [US3] Implement [Service] in src/services/[service].py
- [ ] T039 [US3] Implement [endpoint/feature] in src/[location]/[file].py
- [ ] T040 [US3] For frontend work, consolidate repeated UI into shared
      HeroUI/Tailwind components under apps/frontend/src/components
- [ ] T041 [US3] Verify US3 coverage contribution maintains >= 90% threshold
- [ ] T0XX [US3] Update/create relevant documentation for US3 behavior changes in docs/ and AGENTS.md if applicable

**Checkpoint**: All user stories should now be independently functional

---

[Add more user story phases as needed, following the same pattern]

---

## Phase N: Polish & Cross-Cutting Concerns

**Purpose**: Improvements that affect multiple user stories

- [ ] TXXX [P] Documentation updates in docs/
- [ ] TXXX [P] Verify every changed code path has corresponding documentation updates
- [ ] TXXX Code cleanup and refactoring
- [ ] TXXX Performance optimization across all stories
- [ ] TXXX [P] Additional unit tests in tests/unit/ to protect regressions
- [ ] TXXX Security hardening
- [ ] TXXX Run quickstart.md validation
- [ ] TXXX Run full local stack via unified Docker Compose and verify end-to-end behavior
- [ ] TXXX Run `pnpm exec nx run-many -t test --all` and verify pass before commit and
      before agent handoff/end of work
- [ ] TXXX Run `pnpm exec nx run-many -t coverage --all` and verify >= 90% coverage
      thresholds are satisfied before commit

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies - can start immediately
- **Foundational (Phase 2)**: Depends on Setup completion - BLOCKS all user stories
- **User Stories (Phase 3+)**: All depend on Foundational phase completion
  - User stories can then proceed in parallel (if staffed)
  - Or sequentially in priority order (P1 → P2 → P3)
- **Polish (Final Phase)**: Depends on all desired user stories being complete

### User Story Dependencies

- **User Story 1 (P1)**: Can start after Foundational (Phase 2) - No dependencies on other stories
- **User Story 2 (P2)**: Can start after Foundational (Phase 2) - May integrate with US1 but should be independently testable
- **User Story 3 (P3)**: Can start after Foundational (Phase 2) - May integrate with US1/US2 but should be independently testable

### Within Each User Story

- Tests MUST be written and FAIL before implementation
- Models before services
- Services before endpoints
- Core implementation before integration
- Story complete before moving to next priority

### Parallel Opportunities

- All Setup tasks marked [P] can run in parallel
- All Foundational tasks marked [P] can run in parallel (within Phase 2)
- Once Foundational phase completes, all user stories can start in parallel (if team capacity allows)
- All tests for a user story marked [P] can run in parallel
- Models within a story marked [P] can run in parallel
- Different user stories can be worked on in parallel by different team members

---

## Parallel Example: User Story 1

```bash
# Launch all tests for User Story 1 together:
Task: "Contract test for [endpoint] in tests/contract/test_[name].py"
Task: "Integration test for [user journey] in tests/integration/test_[name].py"

# Launch all models for User Story 1 together:
Task: "Create [Entity1] model in src/models/[entity1].py"
Task: "Create [Entity2] model in src/models/[entity2].py"
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1: Setup
2. Complete Phase 2: Foundational (CRITICAL - blocks all stories)
3. Complete Phase 3: User Story 1
4. **STOP and VALIDATE**: Test User Story 1 independently
5. Deploy/demo if ready

### Incremental Delivery

1. Complete Setup + Foundational → Foundation ready
2. Add User Story 1 → Test independently → Deploy/Demo (MVP!)
3. Add User Story 2 → Test independently → Deploy/Demo
4. Add User Story 3 → Test independently → Deploy/Demo
5. Each story adds value without breaking previous stories

### Parallel Team Strategy

With multiple developers:

1. Team completes Setup + Foundational together
2. Once Foundational is done:
   - Developer A: User Story 1
   - Developer B: User Story 2
   - Developer C: User Story 3
3. Stories complete and integrate independently

---

## Notes

- [P] tasks = different files, no dependencies
- [Story] label maps task to specific user story for traceability
- Each user story should be independently completable and testable
- Coverage MUST remain >= 90% in every affected project
- Before any commit and before any AI agent stops work, `pnpm exec nx run-many -t test --all`
  MUST pass; targeted tests do not satisfy this requirement
- Before any commit, `pnpm exec nx run-many -t coverage --all` MUST pass with >= 90%
  coverage thresholds in every project
- Relevant documentation MUST be updated in the same change as impacted code
- AGENTS.md MUST be updated when repository structure, workflows, or canonical commands change
- Verify tests fail before implementing
- Commit after each task or logical group
- Stop at any checkpoint to validate story independently
- Avoid: vague tasks, same file conflicts, cross-story dependencies that break independence
