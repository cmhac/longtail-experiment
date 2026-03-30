# Tasks: Source Metadata and Adapter Relocation

**Input**: Design documents from `/specs/038-source-metadata-relocation/`
**Prerequisites**: `plan.md`, `spec.md`, `research.md`, `data-model.md`, `contracts/`

**Tests**: Test tasks are REQUIRED. Every user story and foundational component MUST include automated test coverage sufficient to maintain >= 90% coverage in affected projects. Before any commit and before any AI agent stops work, the full repository suite MUST pass via `pnpm exec nx run-many -t test --all`; targeted tests alone are never sufficient for this stop gate. Before any commit, monorepo coverage MUST pass via `pnpm exec nx run-many -t coverage --all` with >= 90% thresholds in every project.

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g. `US1`, `US2`, `US3`)
- Include exact file paths in descriptions

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Create the maintained source package and prepare shared test baselines for the feature.

- [X] T001 Create the maintained adapter package scaffold in `apps/pipeline/src/sources/__init__.py`
- [X] T002 [P] Prepare backend and frontend source metadata fixtures in `apps/backend/tests/fixtures/source_discovery_repository.py` and `apps/frontend/tests/fixtures/source-discovery-fixtures.ts`
- [X] T003 [P] Prepare database/model regression baselines for source profile changes in `libs/db/tests/test_models_foundation.py` and `libs/db/tests/test_ingestion_runtime_migrations.py`

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Implement core schema, manifest, and contract primitives that every user story depends on.

**⚠️ CRITICAL**: No user story work can begin until this phase is complete.

- [X] T004 [P] Add foundational database and model regression coverage for source profile metadata in `libs/db/tests/test_models_foundation.py` and `libs/db/tests/test_ingestion_runtime_migrations.py`
- [X] T005 [P] Add foundational manifest-discovery coverage for the new source package and required metadata in `apps/pipeline/tests/orchestration/test_adapter_manifest_validation.py` and `apps/pipeline/tests/orchestration/test_source_asset_discovery.py`
- [X] T006 [P] Add foundational backend contract coverage for source title and description payload fields in `apps/backend/tests/contract/test_source_list_query_contract.py` and `apps/backend/tests/contract/test_source_detail_query_contract.py`
- [X] T007 Add source profile schema fields and Alembic migration for stable source identity plus source metadata in `libs/db/src/db/models/source_profile.py` and `libs/db/alembic/versions/`
- [X] T008 Add shared source metadata persistence support keyed by stable source identity in `apps/pipeline/src/orchestration/resources/postgres_observation_repository.py`
- [X] T009 Add shared source summary contract fields for title and description in `apps/backend/src/contract/query/source_discovery_query.py` and `apps/frontend/src/lib/api/discovery-types.ts`

**Checkpoint**: Foundation ready. User story implementation can begin.

---

## Phase 3: User Story 1 - Find and Create Source Adapters Faster (Priority: P1) 🎯 MVP

**Goal**: Move maintained adapters into a shallower source package and make onboarding, bootstrap, and discovery flows point contributors to that single location.

**Independent Test**: Follow the provider onboarding flow from repository root, generate a new source adapter, and confirm the scaffold lands in `apps/pipeline/src/sources` and is discovered successfully without relying on the retired nested directory.

### Tests for User Story 1 (REQUIRED) ⚠️

- [ ] T010 [P] [US1] Add pipeline discovery smoke coverage for relocated adapters in `apps/pipeline/tests/orchestration/test_definitions_smoke.py` and `apps/pipeline/tests/orchestration/test_source_asset_discovery.py`
- [X] T011 [P] [US1] Add provider bootstrap CLI coverage for the new adapter path in `apps/pipeline/tests/integration/test_provider_bootstrap_cli_success.py`, `apps/pipeline/tests/integration/test_provider_bootstrap_cli_invalid_input.py`, and `apps/pipeline/tests/integration/test_provider_bootstrap_cli_collisions.py`
- [X] T012 [P] [US1] Add onboarding documentation and skill contract coverage for the new adapter location in `apps/pipeline/tests/contract/test_provider_onboarding_runbook_standard.py` and `apps/pipeline/tests/contract/test_onboard_provider_skill_bootstrap_standard.py`

### Implementation for User Story 1

- [X] T013 [US1] Move maintained adapter modules into `apps/pipeline/src/sources/fred_fedfunds_source.py`, `apps/pipeline/src/sources/eia_retail_fuel_prices_source.py`, and `apps/pipeline/src/sources/nyfed_college_labor_market_source.py`
- [X] T014 [US1] Update runtime discovery and registration imports to scan `apps/pipeline/src/sources` in `apps/pipeline/src/orchestration/jobs/source_assets/discovery.py`, `apps/pipeline/src/orchestration/source_asset_definitions.py`, `apps/pipeline/src/orchestration/schedules/source_asset_schedules.py`, and `apps/pipeline/src/orchestration/runtime.py`
- [X] T015 [US1] Retarget bootstrap defaults and collision scanning to the maintained source package in `tools/provider_bootstrap/bootstrap_provider.py` and `tools/provider_bootstrap/collision_checks.py`
- [X] T016 [US1] Update generated scaffold imports and package exports for the relocated adapter package in `tools/provider_bootstrap/templates/provider_source_template.py.tmpl` and `apps/pipeline/src/sources/__init__.py`
- [X] T017 [US1] Update onboarding and local-stack runbook references to the maintained source package in `docs/runbooks/provider-onboarding.md` and `docs/runbooks/local-stack-baseline.md`
- [X] T018 [US1] Update provider onboarding skill guidance and repository workflow references for the new source package in `.agents/skills/onboard-provider/SKILL.md` and `AGENTS.md`
- [X] T019 [US1] Record and verify the relocated bootstrap/discovery manual flow in `specs/038-source-metadata-relocation/quickstart.md`

**Checkpoint**: User Story 1 is independently functional when a contributor can generate, find, and discover adapters exclusively from `apps/pipeline/src/sources`.

---

## Phase 4: User Story 2 - See Human-Readable Source Information Everywhere (Priority: P2)

**Goal**: Persist source title and description as source-level metadata and expose them through backend and frontend source discovery flows while preserving stable `source_key` identity.

**Independent Test**: Ingest records from a migrated source and confirm persisted source records, source list/detail responses, and source pages show source title and description while routes and relationships remain keyed by stable source identity.

### Tests for User Story 2 (REQUIRED) ⚠️

- [X] T020 [P] [US2] Add pipeline workflow regression coverage for source metadata persistence in `apps/pipeline/tests/orchestration/test_fred_source_workflow.py`, `apps/pipeline/tests/orchestration/test_eia_retail_fuel_prices_source_workflow.py`, and `apps/pipeline/tests/orchestration/test_nyfed_college_labor_market_source_workflow.py`
- [X] T021 [P] [US2] Add backend repository, service, and HTTP coverage for source title and description in `apps/backend/tests/contract/test_source_list_query_contract.py`, `apps/backend/tests/contract/test_source_detail_query_contract.py`, and `apps/backend/tests/contract/test_http_runtime_source_endpoints.py`
- [X] T022 [P] [US2] Add frontend source list/detail rendering coverage for title and description in `apps/frontend/tests/source-list-page.test.tsx`, `apps/frontend/tests/source-detail-page.test.tsx`, and `apps/frontend/tests/discovery-types.test.ts`

### Implementation for User Story 2

- [X] T023 [US2] Add source-level title and description metadata to maintained adapter manifests in `apps/pipeline/src/sources/fred_fedfunds_source.py`, `apps/pipeline/src/sources/eia_retail_fuel_prices_source.py`, and `apps/pipeline/src/sources/nyfed_college_labor_market_source.py`
- [X] T024 [US2] Extend discovered source spec objects to carry source title and description through runtime registration in `apps/pipeline/src/orchestration/jobs/source_assets/discovery.py`
- [X] T025 [US2] Upsert stable source identity, title, and description in persisted source profiles in `apps/pipeline/src/orchestration/resources/postgres_observation_repository.py`
- [X] T026 [US2] Update backend source projections and service shaping for stable ids plus human-readable metadata in `apps/backend/src/query/dataset_discovery_persisted_repository.py`, `apps/backend/src/query/dataset_discovery_service.py`, `apps/backend/src/query/source_list_query.py`, and `apps/backend/src/query/source_detail_query.py`
- [X] T027 [US2] Update frontend discovery client and type parsing for source title and description in `apps/frontend/src/lib/api/discovery-client.ts` and `apps/frontend/src/lib/api/discovery-types.ts`
- [X] T028 [US2] Update shared source presentation components to render source title and description in `apps/frontend/src/components/discovery/SourceListRow.tsx`, `apps/frontend/src/components/discovery/SourceCatalogList.tsx`, and `apps/frontend/src/components/discovery/SourceDetailHeader.tsx`
- [X] T029 [US2] Update source list and detail routes to use stable source ids while rendering human-readable source metadata in `apps/frontend/src/app/sources/page.tsx` and `apps/frontend/src/app/sources/[sourceId]/page.tsx`
- [ ] T030 [US2] Document migration/backfill and metadata verification steps for source discovery flows in `specs/038-source-metadata-relocation/quickstart.md` and `specs/038-source-metadata-relocation/contracts/source-discovery-contract.md`

**Checkpoint**: User Story 2 is independently functional when source list/detail APIs and UI show title/description from persisted source metadata while source identity remains stable.

---

## Phase 5: User Story 3 - Enforce Complete Source Metadata at Onboarding Time (Priority: P3)

**Goal**: Make source title and description mandatory across discovery, bootstrap, and onboarding so incomplete manifests fail fast and maintained adapters remain compliant.

**Independent Test**: Attempt to register or scaffold one source without title/description and one with complete metadata, then confirm the incomplete path fails with clear validation while the complete path succeeds.

### Tests for User Story 3 (REQUIRED) ⚠️

- [X] T031 [P] [US3] Add manifest validation tests for missing and blank title/description fields in `apps/pipeline/tests/orchestration/test_adapter_manifest_validation.py`
- [X] T032 [P] [US3] Add bootstrap validation and scaffold contract tests for required source metadata inputs in `apps/pipeline/tests/unit/test_provider_bootstrap_validation.py` and `apps/pipeline/tests/contract/test_provider_bootstrap_scaffold_contract.py`
- [X] T033 [P] [US3] Add backend/frontend regression coverage ensuring source keys are no longer primary display labels in `apps/backend/tests/contract/test_source_list_query_contract.py` and `apps/frontend/tests/source-list-page.test.tsx`

### Implementation for User Story 3

- [X] T034 [US3] Extend `SourceBuilderSpec` and startup manifest validation rules for required title and description in `apps/pipeline/src/orchestration/jobs/source_assets/discovery.py`
- [X] T035 [US3] Extend bootstrap argument parsing, validation, and rendered scaffold fields for required source metadata in `tools/provider_bootstrap/bootstrap_provider.py`, `tools/provider_bootstrap/validation.py`, and `tools/provider_bootstrap/templates/provider_source_template.py.tmpl`
- [X] T036 [US3] Update manifest-validation fixtures and discovery test builders to include required source metadata in `apps/pipeline/tests/orchestration/test_adapter_manifest_validation.py` and `apps/pipeline/tests/orchestration/test_source_asset_discovery.py`
- [X] T037 [US3] Update onboarding guidance to make source title and description explicitly required in `docs/runbooks/provider-onboarding.md`, `.agents/skills/onboard-provider/SKILL.md`, and `specs/038-source-metadata-relocation/contracts/source-adapter-manifest-contract.md`
- [X] T038 [US3] Record and verify the fail-fast onboarding validation flow in `specs/038-source-metadata-relocation/quickstart.md`

**Checkpoint**: User Story 3 is independently functional when incomplete source manifests and bootstrap requests are blocked immediately with actionable validation errors.

---

## Phase 6: Polish & Cross-Cutting Concerns

**Purpose**: Final documentation, manual validation, and mandatory repository-wide gates.

- [ ] T039 [P] Refresh feature artifacts to match final implementation details in `specs/038-source-metadata-relocation/plan.md`, `specs/038-source-metadata-relocation/research.md`, `specs/038-source-metadata-relocation/data-model.md`, and `specs/038-source-metadata-relocation/quickstart.md`
- [ ] T040 [P] Execute the clean-restart manual validation flow documented in `specs/038-source-metadata-relocation/quickstart.md`
- [ ] T041 Run `pre-commit run --all-files` using `.pre-commit-config.yaml`
- [ ] T042 Run `pnpm exec nx run-many -t test --all` using `package.json` and `nx.json`
- [ ] T043 Run `pnpm exec nx run-many -t coverage --all` using `package.json` and `nx.json`

---

## Dependencies & Execution Order

### Phase Dependencies

- **Phase 1: Setup**: No dependencies, can start immediately.
- **Phase 2: Foundational**: Depends on Phase 1 and blocks all user stories.
- **Phase 3: User Story 1**: Depends on Phase 2.
- **Phase 4: User Story 2**: Depends on Phase 2 and benefits from Phase 3 completing first because metadata is sourced from relocated maintained adapters.
- **Phase 5: User Story 3**: Depends on Phase 2 and should land after Phase 3 so bootstrap/discovery enforcement targets the final maintained adapter package.
- **Phase 6: Polish**: Depends on all desired user stories being complete.

### User Story Dependencies

- **User Story 1 (P1)**: No dependency on other user stories after foundational work; this is the MVP slice.
- **User Story 2 (P2)**: Depends on the maintained adapter package from US1 so source metadata is read from the final adapter location.
- **User Story 3 (P3)**: Depends on US1 for the final maintained adapter location and should follow US2 when possible so enforcement applies to already-migrated persisted and UI flows.

### Within Each User Story

- Story tests should be written first and should fail before implementation.
- Runtime and schema primitives should be updated before downstream route and UI wiring.
- Shared components and contracts should be updated before route-level rendering changes.
- Documentation and manual verification steps should be updated before final polish gates.

### Parallel Opportunities

- Setup tasks marked `[P]` can run in parallel.
- Foundational tests `T004` to `T006` can run in parallel before foundational implementation tasks.
- In US1, bootstrap, discovery, and onboarding contract tests can run in parallel.
- In US2, pipeline, backend, and frontend test tasks can run in parallel, and UI component work can proceed in parallel with backend query shaping after contracts settle.
- In US3, manifest-validation and bootstrap-validation tests can run in parallel.

---

## Parallel Example: User Story 1

```bash
# Launch US1 tests together:
Task: "Add pipeline discovery smoke coverage for relocated adapters in apps/pipeline/tests/orchestration/test_definitions_smoke.py and apps/pipeline/tests/orchestration/test_source_asset_discovery.py"
Task: "Add provider bootstrap CLI coverage for the new adapter path in apps/pipeline/tests/integration/test_provider_bootstrap_cli_success.py, apps/pipeline/tests/integration/test_provider_bootstrap_cli_invalid_input.py, and apps/pipeline/tests/integration/test_provider_bootstrap_cli_collisions.py"
Task: "Add onboarding documentation and skill contract coverage for the new adapter location in apps/pipeline/tests/contract/test_provider_onboarding_runbook_standard.py and apps/pipeline/tests/contract/test_onboard_provider_skill_bootstrap_standard.py"

# Launch independent US1 implementation work after adapter moves begin:
Task: "Retarget bootstrap defaults and collision scanning to the maintained source package in tools/provider_bootstrap/bootstrap_provider.py and tools/provider_bootstrap/collision_checks.py"
Task: "Update onboarding and local-stack runbook references to the maintained source package in docs/runbooks/provider-onboarding.md and docs/runbooks/local-stack-baseline.md"
```

## Parallel Example: User Story 2

```bash
# Launch US2 tests together:
Task: "Add pipeline workflow regression coverage for source metadata persistence in apps/pipeline/tests/orchestration/test_fred_source_workflow.py, apps/pipeline/tests/orchestration/test_eia_retail_fuel_prices_source_workflow.py, and apps/pipeline/tests/orchestration/test_nyfed_college_labor_market_source_workflow.py"
Task: "Add backend repository, service, and HTTP coverage for source title and description in apps/backend/tests/contract/test_source_list_query_contract.py, apps/backend/tests/contract/test_source_detail_query_contract.py, and apps/backend/tests/contract/test_http_runtime_source_endpoints.py"
Task: "Add frontend source list/detail rendering coverage for title and description in apps/frontend/tests/source-list-page.test.tsx, apps/frontend/tests/source-detail-page.test.tsx, and apps/frontend/tests/discovery-types.test.ts"

# Launch independent US2 implementation work after contracts are updated:
Task: "Update backend source projections and service shaping for stable ids plus human-readable metadata in apps/backend/src/query/dataset_discovery_persisted_repository.py, apps/backend/src/query/dataset_discovery_service.py, apps/backend/src/query/source_list_query.py, and apps/backend/src/query/source_detail_query.py"
Task: "Update shared source presentation components to render source title and description in apps/frontend/src/components/discovery/SourceListRow.tsx, apps/frontend/src/components/discovery/SourceCatalogList.tsx, and apps/frontend/src/components/discovery/SourceDetailHeader.tsx"
```

## Parallel Example: User Story 3

```bash
# Launch US3 tests together:
Task: "Add manifest validation tests for missing and blank title/description fields in apps/pipeline/tests/orchestration/test_adapter_manifest_validation.py"
Task: "Add bootstrap validation and scaffold contract tests for required source metadata inputs in apps/pipeline/tests/unit/test_provider_bootstrap_validation.py and apps/pipeline/tests/contract/test_provider_bootstrap_scaffold_contract.py"
Task: "Add backend/frontend regression coverage ensuring source keys are no longer primary display labels in apps/backend/tests/contract/test_source_list_query_contract.py and apps/frontend/tests/source-list-page.test.tsx"

# Launch independent US3 implementation work after validation expectations are set:
Task: "Extend SourceBuilderSpec and startup manifest validation rules for required title and description in apps/pipeline/src/orchestration/jobs/source_assets/discovery.py"
Task: "Update onboarding guidance to make source title and description explicitly required in docs/runbooks/provider-onboarding.md, .agents/skills/onboard-provider/SKILL.md, and specs/038-source-metadata-relocation/contracts/source-adapter-manifest-contract.md"
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1: Setup.
2. Complete Phase 2: Foundational.
3. Complete Phase 3: User Story 1.
4. Validate the relocated adapter package, bootstrap output, and onboarding docs independently.
5. Stop and demo the shallower adapter-creation flow if an MVP checkpoint is needed.

### Incremental Delivery

1. Complete Setup + Foundational to establish schema, manifest, and contract primitives.
2. Deliver User Story 1 so contributors can find and create adapters in the new location.
3. Deliver User Story 2 so source metadata is persisted and rendered end to end.
4. Deliver User Story 3 so incomplete metadata is blocked at onboarding and startup.
5. Finish with polish, manual validation, and mandatory monorepo-wide stop gates.
