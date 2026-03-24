# Tasks: Self-Describing Source Adapters

**Input**: Design documents from /specs/020-self-describing-adapters/
**Prerequisites**: plan.md, spec.md, quickstart.md

**Tests**: Test tasks are REQUIRED. Every user story and foundational component MUST include automated test coverage sufficient to maintain >= 90% coverage in affected projects.

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: [ID] [P?] [Story] Description

- [P] indicates tasks that can run in parallel
- [Story] labels are used only for user story phases
- Every task includes an exact file path or directory path

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Prepare the pipeline workspace for self-describing adapter implementation.

- [ ] T001 Verify current adapter discovery baseline in apps/pipeline/src/orchestration/jobs/source_assets/discovery.py
- [ ] T002 Verify current schedule baseline in apps/pipeline/src/orchestration/schedules/source_asset_schedules.py
- [ ] T003 Verify current Dagit asset baseline in apps/pipeline/src/orchestration/source_asset_definitions.py
- [ ] T004 [P] Verify current workspace catalog baseline in apps/pipeline/src/orchestration/definitions.py
- [ ] T005 [P] Verify current runtime expected-source baseline in apps/pipeline/src/orchestration/runtime.py

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Build shared discovery and manifest infrastructure required by all stories.

**CRITICAL**: No user story work starts before this phase is complete.

- [x] T006 Add SourceAdapterManifestError and move ObservationCheckpointRepository protocol in apps/pipeline/src/orchestration/jobs/source_assets/discovery.py
- [x] T007 Extend SourceBuilderSpec with cron_schedule and cadence_label in apps/pipeline/src/orchestration/jobs/source_assets/discovery.py
- [x] T008 Implement scan_adapter_modules cache entrypoint in apps/pipeline/src/orchestration/jobs/source_assets/discovery.py
- [x] T009 Implement adapter module filesystem scan and import flow in apps/pipeline/src/orchestration/jobs/source_assets/discovery.py
- [x] T010 Implement manifest validation rules including duplicate-key detection and cron syntax validation in apps/pipeline/src/orchestration/jobs/source_assets/discovery.py
- [x] T011 Add test-only cache reset helper in apps/pipeline/src/orchestration/jobs/source_assets/discovery.py
- [x] T012 [P] Add foundational scan and validation unit tests in apps/pipeline/tests/orchestration/test_adapter_manifest_validation.py
- [x] T013 [P] Update existing discovery tests for scan-based defaults in apps/pipeline/tests/orchestration/test_source_asset_discovery.py

**Checkpoint**: Shared manifest discovery infrastructure is complete and tested.

---

## Phase 3: User Story 1 - Onboard a Source With No Edits Outside the Adapter (Priority: P1) 🎯 MVP

**Goal**: A compliant adapter module alone is enough for discovery, schedule wiring, and Dagit asset visibility.

**Independent Test**: Add one compliant adapter module in jobs/sources and verify the runtime auto-registers it with matching schedule and asset keys without editing any non-adapter file.

### Tests for User Story 1

- [x] T014 [P] [US1] Add dynamic schedule derivation smoke assertions in apps/pipeline/tests/orchestration/test_definitions_smoke.py
- [x] T015 [P] [US1] Add dynamic asset catalog derivation smoke assertions in apps/pipeline/tests/orchestration/test_definitions_smoke.py
- [x] T016 [P] [US1] Add deterministic registration-order test based on discovered specs in apps/pipeline/tests/orchestration/test_source_asset_discovery.py
- [x] T048 [P] [US1] Refactor schedule and asset primitive tests for manifest-driven APIs in apps/pipeline/tests/orchestration/test_execution_primitives.py
- [x] T049 [P] [US1] Replace static cadence-dictionary assertions with manifest-derived cadence checks in apps/pipeline/tests/orchestration/test_source_cadence_selection.py

### Implementation for User Story 1

- [x] T017 [US1] Replace hardcoded schedule dictionaries with manifest-driven schedule factory in apps/pipeline/src/orchestration/schedules/source_asset_schedules.py
- [x] T018 [US1] Replace hand-written per-series assets with manifest-driven asset factory in apps/pipeline/src/orchestration/source_asset_definitions.py
- [x] T019 [US1] Derive workspace definition catalog assets and schedules from discovered adapters in apps/pipeline/src/orchestration/definitions.py
- [x] T020 [US1] Derive expected runtime source keys from discovered adapters in apps/pipeline/src/orchestration/runtime.py
- [x] T021 [US1] Update runtime wiring verification to use derived expected keys in apps/pipeline/src/orchestration/runtime.py
- [x] T022 [US1] Ensure discover_source_registrations and discover_series_catalog_entries default to scan_adapter_modules in apps/pipeline/src/orchestration/jobs/source_assets/discovery.py
- [x] T050 [US1] Add one-file onboarding acceptance harness that validates add-one-adapter/no-other-edits behavior in apps/pipeline/tests/orchestration/test_single_file_onboarding_guard.py

**Checkpoint**: US1 works end-to-end with a single adapter file and no non-adapter edits.

---

## Phase 4: User Story 2 - Adapter Self-Description Is Validated at Startup (Priority: P2)

**Goal**: Startup fails fast with actionable module-scoped diagnostics for invalid or conflicting manifests.

**Independent Test**: Inject invalid manifest variants (missing fields, empty series, duplicate source key) and verify startup-time errors include adapter module identity and rule violation.

### Tests for User Story 2

- [x] T023 [P] [US2] Add missing SOURCE_SPEC negative-path test in apps/pipeline/tests/orchestration/test_adapter_manifest_validation.py
- [x] T024 [P] [US2] Add missing required field negative-path tests (source_key, provider_group_key, cron, cadence) in apps/pipeline/tests/orchestration/test_adapter_manifest_validation.py
- [x] T025 [P] [US2] Add tuple length mismatch and empty-series negative-path tests in apps/pipeline/tests/orchestration/test_adapter_manifest_validation.py
- [x] T026 [P] [US2] Add duplicate source_key conflict test naming both modules in apps/pipeline/tests/orchestration/test_adapter_manifest_validation.py
- [x] T027 [P] [US2] Add multi-error aggregation test in apps/pipeline/tests/orchestration/test_adapter_manifest_validation.py
- [x] T051 [P] [US2] Add invalid cron syntax negative-path test with module-scoped diagnostics in apps/pipeline/tests/orchestration/test_adapter_manifest_validation.py

### Implementation for User Story 2

- [x] T028 [US2] Implement aggregated manifest error formatting for all violations in apps/pipeline/src/orchestration/jobs/source_assets/discovery.py
- [x] T029 [US2] Ensure non-adapter modules are ignored by filename contract during scan in apps/pipeline/src/orchestration/jobs/source_assets/discovery.py
- [x] T030 [US2] Ensure adapter scan ordering is deterministic by source_key in apps/pipeline/src/orchestration/jobs/source_assets/discovery.py

**Checkpoint**: Invalid adapters fail startup with clear module-scoped diagnostics.

---

## Phase 5: User Story 3 - Existing FRED Adapter Migrated to Self-Describing Format (Priority: P3)

**Goal**: FRED becomes the reference self-describing adapter; all hardcoded FRED bootstrap entries are removed from non-adapter files.

**Independent Test**: With FRED migrated to SOURCE_SPEC, verify FRED registration, schedule behavior, and Dagit visibility remain unchanged.

### Tests for User Story 3

- [x] T031 [P] [US3] Add FRED SOURCE_SPEC discovery assertion in apps/pipeline/tests/orchestration/test_adapter_manifest_validation.py
- [x] T032 [P] [US3] Update runtime source registration expectations to derived keys in apps/pipeline/tests/orchestration/test_definitions_smoke.py
- [x] T033 [P] [US3] Add regression assertion that FRED asset keys remain fred/fedfunds and fred/gasregw in apps/pipeline/tests/orchestration/test_definitions_smoke.py

### Implementation for User Story 3

- [x] T034 [US3] Add SOURCE_SPEC manifest export to FRED adapter in apps/pipeline/src/orchestration/jobs/sources/fred_fedfunds_source.py
- [x] T035 [US3] Remove FRED-specific discovery imports and default-spec hardcoding in apps/pipeline/src/orchestration/jobs/source_assets/discovery.py
- [x] T036 [US3] Remove FRED-specific expected-source import constant usage in apps/pipeline/src/orchestration/runtime.py
- [x] T037 [US3] Implement automated anti-hardcoding guard that scans all five bootstrap surfaces in apps/pipeline/tests/orchestration/test_single_file_onboarding_guard.py
- [x] T038 [US3] Add guard assertions for source-specific imports/literals in discovery/schedules/assets/definitions/runtime files in apps/pipeline/tests/orchestration/test_single_file_onboarding_guard.py
- [x] T039 [US3] Wire guard expectations for zero bootstrap artifacts into orchestration regression checks in apps/pipeline/tests/orchestration/test_single_file_onboarding_guard.py

**Checkpoint**: FRED is fully migrated; no bootstrap hardcoding remains in non-adapter files.

---

## Phase 6: Polish & Cross-Cutting Concerns

**Purpose**: Documentation alignment, quality gates, and full-suite verification.

- [x] T040 [P] Update single-file onboarding instructions in docs/runbooks/provider-onboarding.md
- [x] T052 [P] Update local stack onboarding instructions to match single-file model in docs/runbooks/local-stack-baseline.md
- [x] T041 [P] Update repository workflow guidance for feature 020 in AGENTS.md
- [x] T042 [P] Update onboarding skill workflow to single-file model in .agents/skills/onboard-provider/SKILL.md
- [x] T043 Run pipeline lint and format checks for changed files in apps/pipeline/
- [x] T044 Run pipeline type checks for changed files in apps/pipeline/
- [x] T045 Run orchestration-focused tests for changed behavior in apps/pipeline/tests/orchestration/
- [x] T046 Run mandatory full monorepo tests with pnpm exec nx run-many -t test --all from /Users/hackerc/Projects/longtail-experiment
- [x] T047 Run mandatory full monorepo coverage with pnpm exec nx run-many -t coverage --all from /Users/hackerc/Projects/longtail-experiment

---

## Dependencies & Execution Order

### Phase Dependencies

- Phase 1 (Setup): no dependencies
- Phase 2 (Foundational): depends on Phase 1; blocks all user stories
- Phase 3 (US1): depends on Phase 2
- Phase 4 (US2): depends on Phase 2 and benefits from Phase 3 scan behavior
- Phase 5 (US3): depends on Phases 2 and 3
- Phase 6 (Polish): depends on completion of all user stories

### User Story Dependencies

- US1 (P1): first delivery slice (MVP)
- US2 (P2): depends on manifest scan path built in foundational work
- US3 (P3): depends on manifest model and dynamic derivation already in place

### Within Each User Story

- Tests first, fail before implementation
- Discovery/manifest core before schedule and asset derivation
- Runtime and definitions derivation before smoke/regression validation

---

## Parallel Opportunities

- Foundational phase: T012 and T013 can run in parallel after T006-T011
- US1 tests: T014, T015, T016, T048, and T049 can run in parallel
- US2 tests: T023-T027 and T051 can run in parallel
- US3 tests: T031, T032, T033 can run in parallel
- Documentation updates: T040, T041, T042, and T052 can run in parallel

---

## Parallel Example: User Story 2

```bash
# Launch US2 negative-path tests in parallel:
Task: "T023 Add missing SOURCE_SPEC negative-path test in apps/pipeline/tests/orchestration/test_adapter_manifest_validation.py"
Task: "T024 Add missing required field negative-path tests in apps/pipeline/tests/orchestration/test_adapter_manifest_validation.py"
Task: "T025 Add tuple length mismatch and empty-series negative-path tests in apps/pipeline/tests/orchestration/test_adapter_manifest_validation.py"
Task: "T026 Add duplicate source_key conflict test in apps/pipeline/tests/orchestration/test_adapter_manifest_validation.py"
Task: "T027 Add multi-error aggregation test in apps/pipeline/tests/orchestration/test_adapter_manifest_validation.py"
```

---

## Implementation Strategy

### MVP First (US1 Only)

1. Complete Phase 1 and Phase 2
2. Complete US1 (Phase 3)
3. Validate single-file onboarding behavior end-to-end
4. Stop for MVP review

### Incremental Delivery

1. Deliver US1 (single-file onboarding)
2. Deliver US2 (strict startup validation)
3. Deliver US3 (FRED migration and hardcoding removal)
4. Complete polish and full-suite quality gates

### Team Parallelization

1. One engineer handles foundational discovery internals (T006-T011)
2. One engineer prepares discovery/smoke tests in parallel (T012-T016)
3. Another engineer executes runtime/definitions/schedule/asset derivation (T017-T022)
4. Documentation and skill updates run in parallel during polish (T040-T042, T052)
