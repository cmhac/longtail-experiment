# Tasks: Core Pipeline Data Contract

**Input**: Design documents from `/specs/003-define-data-contract/`
**Prerequisites**: plan.md (required), spec.md (required for user stories), research.md, data-model.md, contracts/

**Tests**: Test tasks are REQUIRED. Every user story and foundational component MUST include automated test coverage sufficient to maintain >= 90% coverage in affected projects.

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3)
- Include exact file paths in descriptions

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Create contract-focused module structure and workspace verification entry points.

- [ ] T001 Create contract package layout in apps/pipeline/src/contract/__init__.py and apps/backend/src/contract/__init__.py
- [ ] T002 [P] Create schema package layout in apps/pipeline/src/contract/schemas/__init__.py and libs/db/src/db/models/__init__.py
- [ ] T003 [P] Create shared DB package layout in libs/db/src/db/__init__.py and libs/db/src/db/repositories/__init__.py
- [ ] T004 [P] Create shared test package layout in apps/pipeline/tests/contract/__init__.py and apps/backend/tests/contract/__init__.py
- [ ] T005 Add contract verification command documentation to tools/quality/verification/affected-backend.sh and tools/quality/verification/affected-workspace.sh

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Implement shared domain objects and persistence abstractions required by all stories.

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

- [ ] T006 Create shared source profile and series ORM entities in libs/db/src/db/models/source_profile.py and libs/db/src/db/models/data_series.py
- [ ] T007 [P] Create shared observation, provenance, revision ORM entities in libs/db/src/db/models/observation.py and libs/db/src/db/models/lineage.py
- [ ] T008 [P] Create shared category and geography hierarchy ORM entities in libs/db/src/db/models/taxonomy.py
- [ ] T009 Define DB engine/session lifecycle and repository interfaces in libs/db/src/db/engine.py, libs/db/src/db/session.py, and libs/db/src/db/repositories/interfaces.py
- [ ] T010 [P] Implement Alembic migration environment and base revision scaffolding in libs/db/alembic/env.py and libs/db/alembic/versions/0001_contract_baseline.py
- [ ] T011 [P] Implement contract validation error types in apps/pipeline/src/contract/errors.py and apps/backend/src/contract/errors.py
- [ ] T012 [P] Implement structured logging and tracing modules in apps/pipeline/src/contract/observability/logging.py and apps/pipeline/src/contract/observability/tracing.py
- [ ] T013 [P] Add observability contract tests for ingest trace propagation in apps/pipeline/tests/contract/test_observability_contract.py
- [ ] T014 [P] Add foundational unit tests for shared entities and invariants in libs/db/tests/test_models_foundation.py
- [ ] T015 Add foundational repository interface, session lifecycle, and migration smoke tests in libs/db/tests/test_repository_interfaces.py and libs/db/tests/test_migrations.py

**Checkpoint**: Foundation ready - user story implementation can now begin in parallel

---

## Phase 3: User Story 1 - Define a Unified Time-Series Contract (Priority: P1) 🎯 MVP

**Goal**: Ingest mixed-frequency sources into one canonical observation contract with deterministic validation.

**Independent Test**: Submit representative daily and monthly source payload fixtures and confirm accepted observations map to the same canonical fields with no missing mandatory attributes.

### Tests for User Story 1 (REQUIRED) ⚠️

- [ ] T016 [P] [US1] Create canonical contract schema validation tests in apps/pipeline/tests/contract/test_canonical_schema_validation.py
- [ ] T017 [P] [US1] Create mixed-frequency ingest integration tests in apps/pipeline/tests/contract/test_ingest_frequency_handling.py
- [ ] T018 [P] [US1] Create backend canonical read contract tests in apps/backend/tests/contract/test_canonical_observation_reads.py

### Implementation for User Story 1

- [ ] T019 [P] [US1] Implement canonical observation schema and validators in apps/pipeline/src/contract/schemas/canonical_observation.py
- [ ] T020 [P] [US1] Implement source payload normalization mappers in apps/pipeline/src/contract/normalizers/source_payload_mapper.py
- [ ] T021 [US1] Implement ingest contract service using shared DB session boundaries in apps/pipeline/src/contract/services/canonical_ingest_service.py
- [ ] T022 [US1] Implement quarantine/reject handling and invalid-payload fixtures in apps/pipeline/src/contract/services/ingest_outcome_service.py and apps/pipeline/tests/fixtures/canonical_sources.json
- [ ] T023 [US1] Implement shared observation persistence repository in libs/db/src/db/repositories/observation_repository.py
- [ ] T024 [US1] Implement backend query projection for canonical fields via shared repositories in apps/backend/src/contract/query/canonical_query.py
- [ ] T025 [US1] Verify US1 quality gates and coverage in apps/pipeline/tests/contract/test_canonical_schema_validation.py and apps/backend/tests/contract/test_canonical_observation_reads.py

**Checkpoint**: User Story 1 is independently ingesting and validating canonical observations

---

## Phase 4: User Story 2 - Preserve Data Provenance and Auditability (Priority: P2)

**Goal**: Guarantee immutable provenance metadata and explicit revision lineage between superseded and current observations.

**Independent Test**: Load an initial observation and a revised publication for the same reference period, then verify immutable provenance and bidirectional revision traceability.

### Tests for User Story 2 (REQUIRED) ⚠️

- [ ] T026 [P] [US2] Create provenance immutability tests in apps/pipeline/tests/contract/test_provenance_immutability.py
- [ ] T027 [P] [US2] Create revision lineage integrity tests in apps/pipeline/tests/contract/test_revision_lineage.py
- [ ] T028 [P] [US2] Create backend audit retrieval tests in apps/backend/tests/contract/test_provenance_audit_queries.py

### Implementation for User Story 2

- [ ] T029 [P] [US2] Implement provenance schema and write guards in apps/pipeline/src/contract/schemas/provenance_record.py
- [ ] T030 [P] [US2] Implement revision record schema and linkage rules in apps/pipeline/src/contract/schemas/revision_record.py
- [ ] T031 [US2] Implement lineage service for supersede and replace workflows in apps/pipeline/src/contract/services/revision_lineage_service.py
- [ ] T032 [US2] Implement provenance persistence adapter with immutable field enforcement in libs/db/src/db/repositories/provenance_repository.py
- [ ] T033 [US2] Implement backend audit query service for provenance and revisions in apps/backend/src/contract/query/provenance_audit_query.py
- [ ] T034 [US2] Add revised-publication fixtures and restatement scenarios in apps/pipeline/tests/fixtures/revision_events.json
- [ ] T035 [US2] Verify US2 quality gates and coverage in apps/pipeline/tests/contract/test_revision_lineage.py and apps/backend/tests/contract/test_provenance_audit_queries.py

**Checkpoint**: User Story 2 is independently preserving immutable provenance and revision lineage

---

## Phase 5: User Story 3 - Support Hierarchical Search and Filtering (Priority: P3)

**Goal**: Enable category and geography hierarchy mapping with reliable parent/child filtering semantics.

**Independent Test**: Load taxonomy and geography trees with mixed-depth series assignments, then verify parent-level queries return expected descendant data and non-geographic series handling.

### Tests for User Story 3 (REQUIRED) ⚠️

- [ ] T036 [P] [US3] Create taxonomy hierarchy validation tests in apps/pipeline/tests/contract/test_taxonomy_hierarchy_validation.py
- [ ] T037 [P] [US3] Create geography hierarchy and non-geographic tests in apps/pipeline/tests/contract/test_geography_hierarchy_validation.py
- [ ] T038 [P] [US3] Create backend hierarchical query filter tests in apps/backend/tests/contract/test_hierarchy_filter_queries.py

### Implementation for User Story 3

- [ ] T039 [P] [US3] Implement category hierarchy schema and integrity checks in apps/pipeline/src/contract/schemas/category_hierarchy.py
- [ ] T040 [P] [US3] Implement geography hierarchy schema and non-geographic marker rules in apps/pipeline/src/contract/schemas/geography_hierarchy.py
- [ ] T041 [US3] Implement taxonomy mapping service for series onboarding in apps/pipeline/src/contract/services/taxonomy_mapping_service.py
- [ ] T042 [US3] Implement hierarchy-aware backend query filters and shared hierarchy repositories in apps/backend/src/contract/query/hierarchy_query.py and libs/db/src/db/repositories/hierarchy_repository.py
- [ ] T043 [US3] Add taxonomy and geography fixture trees in apps/pipeline/tests/fixtures/hierarchy_trees.json
- [ ] T044 [US3] Verify US3 quality gates and coverage in apps/pipeline/tests/contract/test_taxonomy_hierarchy_validation.py and apps/backend/tests/contract/test_hierarchy_filter_queries.py

**Checkpoint**: User Story 3 is independently providing hierarchical search and filtering behavior

---

## Phase 6: Polish & Cross-Cutting Concerns

**Purpose**: Final consistency, contract evolution guidance, and full-system verification.

- [ ] T045 [P] Update contract implementation notes and migration guidance for libs/db Alembic flow in specs/003-define-data-contract/contracts/canonical-observation-contract.md and specs/003-define-data-contract/contracts/provenance-and-revision-contract.md
- [ ] T046 [P] Update architecture and runbook docs for contract workflows in docs/architecture/monorepo-boundaries.md and docs/runbooks/local-stack-baseline.md
- [ ] T047 [P] Update onboarding guidance and canonical commands in docs/onboarding/monorepo-baseline.md and AGENTS.md
- [ ] T048 [P] Implement backend and pipeline observability integration checks in apps/backend/tests/contract/test_observability_queries.py and apps/pipeline/tests/contract/test_observability_contract.py
- [ ] T049 [P] Add SC-001 onboarding-rate verification tests in apps/pipeline/tests/contract/test_sc001_onboarding_rate.py and apps/pipeline/tests/fixtures/sc001_onboarding_samples.json
- [ ] T050 [P] Add SC-003 manual-workflow timing verification tests (from filter selection to first complete result set display) in apps/backend/tests/contract/test_sc003_query_time.py and apps/backend/tests/fixtures/sc003_query_scenarios.json
- [ ] T051 [P] Add SC-005 ambiguity-rate verification tests in apps/pipeline/tests/contract/test_sc005_ambiguity_rate.py and apps/pipeline/tests/fixtures/sc005_ambiguity_samples.json
- [ ] T052 Run quickstart validation flow in specs/003-define-data-contract/quickstart.md and record SC evidence in specs/003-define-data-contract/research.md
- [ ] T053 Run full affected quality suite and local stack verification via package.json scripts and tools/quality/local-stack/test-compose-stack.sh
- [ ] T054 [P] Add FR-009 source-type labeling contract tests in apps/pipeline/tests/contract/test_source_type_labeling.py and apps/backend/tests/contract/test_source_type_query_filters.py
- [ ] T055 [P] Add FR-010 full filter-matrix contract tests in apps/backend/tests/contract/test_filter_matrix_queries.py and apps/backend/tests/fixtures/filter_matrix_scenarios.json

---

## Dependencies & Execution Order

### Phase Dependencies

- **Phase 1 (Setup)**: No dependencies, starts immediately.
- **Phase 2 (Foundational)**: Depends on Phase 1, blocks all user story phases.
- **Phase 3 (US1)**: Depends on Phase 2 completion.
- **Phase 4 (US2)**: Depends on Phase 2 completion; can run after US1 or in parallel once foundational components are stable.
- **Phase 5 (US3)**: Depends on Phase 2 completion; can run after US1 or in parallel with US2.
- **Phase 6 (Polish)**: Depends on completion of all targeted user stories.

### User Story Dependencies

- **US1 (P1)**: Independent after foundational phase; suggested MVP scope.
- **US2 (P2)**: Independent after foundational phase; integrates with canonical observations from US1 but remains independently testable.
- **US3 (P3)**: Independent after foundational phase; uses shared entities and query layers without requiring US2 completion.

### Within Each User Story

- Tests must be written first and fail before implementation tasks.
- Schemas/models before services.
- Services before repository adapters and query projections.
- Implementation complete before coverage/quality verification task.

### Parallel Opportunities

- Phase 1 tasks marked [P] can run concurrently.
- Phase 2 model and test tasks marked [P] can run concurrently after base packages are created.
- In each user story, test tasks marked [P] can be developed together.
- Schema/model tasks marked [P] can run concurrently before service integration tasks.
- US2 and US3 can execute in parallel after foundational phase if team capacity allows.

---

## Parallel Example: User Story 1

```bash
# Launch US1 tests in parallel
Task: "Create canonical contract schema validation tests in apps/pipeline/tests/contract/test_canonical_schema_validation.py"
Task: "Create mixed-frequency ingest integration tests in apps/pipeline/tests/contract/test_ingest_frequency_handling.py"
Task: "Create backend canonical read contract tests in apps/backend/tests/contract/test_canonical_observation_reads.py"

# Launch US1 schema work in parallel
Task: "Implement canonical observation schema and validators in apps/pipeline/src/contract/schemas/canonical_observation.py"
Task: "Implement source payload normalization mappers in apps/pipeline/src/contract/normalizers/source_payload_mapper.py"
```

## Parallel Example: User Story 2

```bash
# Launch US2 tests in parallel
Task: "Create provenance immutability tests in apps/pipeline/tests/contract/test_provenance_immutability.py"
Task: "Create revision lineage integrity tests in apps/pipeline/tests/contract/test_revision_lineage.py"
Task: "Create backend audit retrieval tests in apps/backend/tests/contract/test_provenance_audit_queries.py"

# Launch US2 schema work in parallel
Task: "Implement provenance schema and write guards in apps/pipeline/src/contract/schemas/provenance_record.py"
Task: "Implement revision record schema and linkage rules in apps/pipeline/src/contract/schemas/revision_record.py"
```

## Parallel Example: User Story 3

```bash
# Launch US3 tests in parallel
Task: "Create taxonomy hierarchy validation tests in apps/pipeline/tests/contract/test_taxonomy_hierarchy_validation.py"
Task: "Create geography hierarchy and non-geographic tests in apps/pipeline/tests/contract/test_geography_hierarchy_validation.py"
Task: "Create backend hierarchical query filter tests in apps/backend/tests/contract/test_hierarchy_filter_queries.py"

# Launch US3 hierarchy schema work in parallel
Task: "Implement category hierarchy schema and integrity checks in apps/pipeline/src/contract/schemas/category_hierarchy.py"
Task: "Implement geography hierarchy schema and non-geographic marker rules in apps/pipeline/src/contract/schemas/geography_hierarchy.py"
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1: Setup.
2. Complete Phase 2: Foundational.
3. Complete Phase 3: User Story 1.
4. Validate US1 independently with T016-T018 and T025.
5. Demo MVP ingest/validation behavior before expanding scope.

### Incremental Delivery

1. Finish Setup and Foundational phases to unlock parallel work.
2. Deliver US1 as the first production slice.
3. Deliver US2 for auditability and historical trust guarantees.
4. Deliver US3 for discovery/filtering capabilities.
5. Run Phase 6 polish and full quality verification before merge.

### Parallel Team Strategy

1. Team aligns on foundational models and interfaces (Phase 2).
2. After Phase 2:
   - Developer A leads US1 canonical ingest tasks.
   - Developer B leads US2 provenance and revision tasks.
   - Developer C leads US3 taxonomy and query tasks.
3. Team reconverges for Phase 6 quality, docs, and compose verification.

---

## Notes

- [P] tasks indicate no direct file conflict and no dependency on incomplete same-phase tasks.
- Story labels map every user-story task to US1, US2, or US3 for traceability.
- Every task line follows the checklist format with checkbox, task ID, optional markers, and file path.
- Coverage must remain >= 90% for affected backend and pipeline projects.
- Update documentation in the same change as behavior changes, including AGENTS.md when canonical commands or workflows evolve.
