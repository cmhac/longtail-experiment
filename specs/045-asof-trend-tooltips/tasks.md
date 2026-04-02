# Tasks: Historical As-Of Trend Tooltips

**Input**: Design documents from `/specs/045-asof-trend-tooltips/`
**Prerequisites**: plan.md (required), spec.md (required for user stories), research.md, data-model.md, contracts/

**Tests**: Test tasks are REQUIRED. Every user story and foundational component MUST include automated coverage sufficient to maintain >= 90% coverage in affected projects. Before any commit and before any AI agent stops work, run `pnpm exec nx run-many -t test --all`. Before any commit, run `pnpm exec nx run-many -t coverage --all`.

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3)
- Every task includes exact file path(s)

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Align implementation artifacts, contracts, and quality workflow before code changes.

- [x] T001 Validate feature artifact alignment in specs/045-asof-trend-tooltips/spec.md, specs/045-asof-trend-tooltips/plan.md, specs/045-asof-trend-tooltips/data-model.md, and specs/045-asof-trend-tooltips/contracts/discovery-asof-trend-tooltips.openapi.yaml
- [x] T002 [P] Capture backend and frontend implementation seam notes in specs/045-asof-trend-tooltips/research.md
- [x] T003 [P] Create implementation checklist baseline in specs/045-asof-trend-tooltips/checklists/requirements.md

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Shared contract and mapping prerequisites that block all user stories.

- [ ] T004 Add observation-level descriptor model and validators in apps/backend/src/contract/query/dataset_detail_query.py
- [ ] T005 [P] Add frontend API type support for observation-level as-of descriptors in apps/frontend/src/lib/api/discovery-types.ts
- [ ] T006 [P] Add shared parsing/mapping helper for observation-level descriptor normalization in apps/backend/src/query/dataset_discovery_service.py
- [ ] T007 [P] Add deterministic fixture builders for as-of descriptor test scenarios in apps/backend/tests/contract/fixtures/dataset_detail_asof_trend_fixtures.py
- [ ] T008 Add foundational contract regression tests for required observation descriptor presence in apps/backend/tests/contract/test_dataset_detail_observation_asof_contract.py

**Checkpoint**: Foundation ready. User stories can now proceed.

---

## Phase 3: User Story 1 - Retrieve Historical As-Of Trend State (Priority: P1) 🎯 MVP

**Goal**: Resolve deterministic observation-level trend state from persisted historical trend data.

**Independent Test**: Request one dataset detail payload with multiple observations and verify each observation resolves the correct available/unavailable as-of trend state deterministically.

### Tests for User Story 1

- [ ] T009 [P] [US1] Add service-layer deterministic as-of resolution tests in apps/backend/tests/contract/test_dataset_detail_asof_resolution_contract.py
- [ ] T010 [P] [US1] Add repository-level candidate ordering tests for same-date multi-report observations in apps/backend/tests/integration/test_dataset_asof_trend_candidate_ordering.py
- [ ] T011 [P] [US1] Add mixed-availability resolution tests in apps/backend/tests/contract/test_dataset_detail_asof_mixed_availability.py

### Implementation for User Story 1

- [ ] T012 [US1] Implement observation-context as-of candidate retrieval in apps/backend/src/query/dataset_discovery_persisted_repository.py
- [ ] T013 [US1] Implement deterministic tie-break logic for as-of descriptor selection in apps/backend/src/query/dataset_discovery_service.py
- [ ] T014 [US1] Implement explicit unavailable descriptor fallback generation in apps/backend/src/query/dataset_discovery_service.py
- [ ] T015 [US1] Wire per-observation as-of descriptor assembly into detail payload construction in apps/backend/src/query/dataset_discovery_service.py
- [ ] T016 [US1] Add reason-code mapping for unavailable as-of states in apps/backend/src/query/dataset_discovery_service.py

**Checkpoint**: US1 resolves observation-level as-of trend states deterministically and is independently testable.

---

## Phase 4: User Story 2 - Expose As-Of Trend Data In Detail Contract (Priority: P2)

**Goal**: Return observation-level as-of trend payloads in dataset detail responses while preserving existing top-level trend fields.

**Independent Test**: Validate detail response schema includes `as_of_trend_descriptor` on every observation, preserves top-level trend fields, and surfaces explicit contract errors for malformed payloads.

### Tests for User Story 2

- [ ] T017 [P] [US2] Add dataset detail contract coverage for observation-level as-of descriptor fields in apps/backend/tests/contract/test_dataset_detail_asof_descriptor_shape.py
- [ ] T018 [P] [US2] Add malformed payload validation failure test in apps/backend/tests/contract/test_dataset_detail_asof_validation_errors.py
- [ ] T019 [P] [US2] Add API route regression test for detail contract serialization in apps/backend/tests/contract/test_http_dataset_detail_asof_contract.py

### Implementation for User Story 2

- [ ] T020 [US2] Extend detail contract response model to require observation-level as-of descriptor in apps/backend/src/contract/query/dataset_detail_query.py
- [ ] T021 [US2] Update dataset detail response assembly to keep top-level canonical and lookback fields unchanged in apps/backend/src/query/dataset_discovery_service.py
- [ ] T022 [US2] Ensure HTTP API detail response wiring validates updated contract in apps/backend/src/http_api_server.py
- [ ] T023 [US2] Update contract documentation for observation-level as-of fields in specs/045-asof-trend-tooltips/contracts/discovery-asof-trend-tooltips.openapi.yaml

**Checkpoint**: US2 exposes a stable, validated observation-level as-of contract and remains independently testable.

---

## Phase 5: User Story 3 - Show As-Of Trend Chip In Historical Tooltip (Priority: P3)

**Goal**: Render one observation-specific trend chip at the bottom of each dataset-detail chart tooltip.

**Independent Test**: Hover multiple observations in a dataset-detail chart and confirm each tooltip shows one bottom chip reflecting that observation’s as-of trend state (including unavailable state).

### Tests for User Story 3

- [x] T024 [P] [US3] Add tooltip unit tests for observation-specific trend chip rendering in apps/frontend/tests/components/ObservationsChartAsOfTrendTooltip.test.tsx
- [x] T025 [P] [US3] Add unavailable tooltip chip regression tests in apps/frontend/tests/components/ObservationsChartAsOfTrendUnavailable.test.tsx
- [x] T026 [P] [US3] Add discovery client mapping tests for observation-level as-of descriptor parsing in apps/frontend/tests/discovery-client-dataset-detail-asof.test.ts

### Implementation for User Story 3

- [x] T027 [US3] Extend dataset detail API type definitions to include `observations[].as_of_trend_descriptor` in apps/frontend/src/lib/api/discovery-types.ts
- [x] T028 [US3] Update dataset detail API client normalization for observation-level as-of descriptors in apps/frontend/src/lib/api/discovery-client.ts
- [x] T029 [US3] Extend chart tooltip point model to carry as-of descriptor per observation in apps/frontend/src/components/discovery/ObservationsChart.tsx
- [x] T030 [US3] Render shared DatasetTrendIndicator at tooltip bottom using hovered observation descriptor in apps/frontend/src/components/discovery/ObservationsChart.tsx
- [x] T031 [US3] Ensure unavailable descriptor maps to explicit unavailable chip state in apps/frontend/src/components/discovery/DatasetTrendIndicator.tsx

**Checkpoint**: US3 renders an observation-specific tooltip chip with no regression to existing chart behavior.

---

## Phase 6: Polish & Cross-Cutting Concerns

**Purpose**: Hardening, manual validation, documentation, and mandatory stop gates.

- [ ] T032 [P] Update feature execution notes and validation steps in specs/045-asof-trend-tooltips/quickstart.md and specs/045-asof-trend-tooltips/research.md
- [ ] T033 Run focused backend quality gates in apps/backend using `uv run --project apps/backend ruff check apps/backend`, `uv run --project apps/backend ty check apps/backend`, and `uv run --project apps/backend pytest apps/backend/tests`
- [ ] T034 Run focused frontend quality gates in apps/frontend using `pnpm --dir apps/frontend exec biome check .`, `pnpm --dir apps/frontend typecheck`, and `pnpm --dir apps/frontend test`
- [ ] T035 Run clean-stack manual verification for dataset-detail API and tooltip behavior using specs/045-asof-trend-tooltips/quickstart.md
- [ ] T036 Run full repository stop gate `pnpm exec nx run-many -t test --all` from repository root
- [ ] T037 Run full repository coverage gate `pnpm exec nx run-many -t coverage --all` from repository root
- [ ] T038 Run `pre-commit run --all-files` and resolve all hook failures before handoff

---

## Dependencies & Execution Order

### Phase Dependencies

- **Phase 1 (Setup)**: No dependencies.
- **Phase 2 (Foundational)**: Depends on Phase 1 and blocks all user stories.
- **Phase 3 (US1)**: Depends on Phase 2.
- **Phase 4 (US2)**: Depends on Phase 3.
- **Phase 5 (US3)**: Depends on Phase 4.
- **Phase 6 (Polish)**: Depends on all user stories.

### User Story Dependencies

- **US1 (P1)**: No dependency on other user stories; this is the MVP scope.
- **US2 (P2)**: Depends on US1 as-of resolution behavior to expose stable contract data.
- **US3 (P3)**: Depends on US2 contract payload availability for tooltip rendering.

### Within Each User Story

- Write tests first and confirm they fail.
- Implement resolver/mapping logic before response wiring.
- Complete story-specific quality checks before advancing.

## Parallel Opportunities

- Phase 1: T002 and T003 can run in parallel.
- Phase 2: T004/T005/T006/T007 can run in parallel before T008.
- US1: T009/T010/T011 can run in parallel; T012 and T013 can overlap before T015.
- US2: T017/T018/T019 can run in parallel before T020-T023.
- US3: T024/T025/T026 can run in parallel before T027-T031.

### Parallel Example: User Story 1

```bash
Task: "T009 [US1] apps/backend/tests/contract/test_dataset_detail_asof_resolution_contract.py"
Task: "T010 [US1] apps/backend/tests/integration/test_dataset_asof_trend_candidate_ordering.py"
Task: "T011 [US1] apps/backend/tests/contract/test_dataset_detail_asof_mixed_availability.py"
```

### Parallel Example: User Story 3

```bash
Task: "T024 [US3] apps/frontend/tests/components/ObservationsChartAsOfTrendTooltip.test.tsx"
Task: "T025 [US3] apps/frontend/tests/components/ObservationsChartAsOfTrendUnavailable.test.tsx"
Task: "T026 [US3] apps/frontend/tests/discovery-client-dataset-detail-asof.test.ts"
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1 and Phase 2.
2. Complete Phase 3 (US1).
3. Validate deterministic observation-level as-of resolution through backend tests and one manual detail API check.
4. Run quality checks before expanding scope.

### Incremental Delivery

1. Deliver US1 backend as-of retrieval.
2. Deliver US2 contract exposure and validation.
3. Deliver US3 tooltip chip rendering.
4. Finish with polish, manual verification, and full monorepo gates.

### Format Validation

- All tasks follow required checklist format: `- [ ] T### [P?] [US?] Description with file path`.
- Story labels appear only on user-story tasks.
- Setup/foundational/polish tasks have no story labels.
- Parallelizable tasks are explicitly marked `[P]`.
