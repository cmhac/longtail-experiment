# Tasks: Unified Feed List Components

**Input**: Design documents from `/specs/039-unified-feed-list/`
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

- Frontend web app: `apps/frontend/src/`, `apps/frontend/tests/`
- Feature docs: `specs/039-unified-feed-list/`

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Prepare the feature workspace and task-facing verification references

- [X] T001 Review the implementation contract and verification flow in /Users/hackerc/Projects/longtail-experiment/specs/039-unified-feed-list/plan.md, /Users/hackerc/Projects/longtail-experiment/specs/039-unified-feed-list/contracts/discovery-feed-list-contract.md, and /Users/hackerc/Projects/longtail-experiment/specs/039-unified-feed-list/quickstart.md
- [X] T002 [P] Inventory current shared row and wrapper consumers in /Users/hackerc/Projects/longtail-experiment/apps/frontend/src/components/discovery/RecentUpdatesFeed.tsx, /Users/hackerc/Projects/longtail-experiment/apps/frontend/src/components/discovery/DatasetCatalogList.tsx, /Users/hackerc/Projects/longtail-experiment/apps/frontend/src/components/discovery/SourceCatalogList.tsx, /Users/hackerc/Projects/longtail-experiment/apps/frontend/src/components/discovery/UnifiedDatasetRow.tsx, and /Users/hackerc/Projects/longtail-experiment/apps/frontend/src/components/discovery/SourceListRow.tsx

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Establish the shared component-group contract before any story-specific migration work

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

- [X] T003 [P] Add foundational component-contract tests for titled and untitled wrapper composition in /Users/hackerc/Projects/longtail-experiment/apps/frontend/tests/RecentUpdatesFeed.test.tsx and /Users/hackerc/Projects/longtail-experiment/apps/frontend/tests/DatasetCatalogList.test.tsx
- [X] T004 [P] Add foundational component-contract tests for shared row hierarchy, metadata rail ordering, and optional subtitle behavior in /Users/hackerc/Projects/longtail-experiment/apps/frontend/tests/UnifiedDatasetRow.test.tsx
- [X] T005 Create the new shared feed/list component group module in /Users/hackerc/Projects/longtail-experiment/apps/frontend/src/components/discovery/DiscoveryFeedList.tsx
- [X] T006 Create shared feed/list view-model and composition types in /Users/hackerc/Projects/longtail-experiment/apps/frontend/src/components/discovery/discovery-feed-list-types.ts
- [X] T007 Refactor shared row title, subtitle, display-category, update-date, and metadata-rail rendering into /Users/hackerc/Projects/longtail-experiment/apps/frontend/src/components/discovery/DiscoveryFeedList.tsx
- [X] T008 Verify foundational component tests and static checks for the new shared module with /Users/hackerc/Projects/longtail-experiment/apps/frontend/tests/RecentUpdatesFeed.test.tsx, /Users/hackerc/Projects/longtail-experiment/apps/frontend/tests/DatasetCatalogList.test.tsx, /Users/hackerc/Projects/longtail-experiment/apps/frontend/tests/UnifiedDatasetRow.test.tsx, and /Users/hackerc/Projects/longtail-experiment/apps/frontend/src/components/discovery/DiscoveryFeedList.tsx

**Checkpoint**: Shared feed/list primitives are defined and tested; user story migrations can now proceed

---

## Phase 3: User Story 1 - Reuse One List Surface Pattern (Priority: P1) 🎯 MVP

**Goal**: Deliver one reusable feed/list wrapper and shared row pattern that powers titled and untitled dataset surfaces

**Independent Test**: Render the home recent-updates feed and the datasets catalog list and confirm both use the shared wrapper and row primitives while preserving heading, ordering, and navigation behavior

### Tests for User Story 1 (REQUIRED) ⚠️

- [X] T009 [P] [US1] Expand home feed regression coverage for shared wrapper/title composition in /Users/hackerc/Projects/longtail-experiment/apps/frontend/tests/RecentUpdatesFeed.test.tsx
- [X] T010 [P] [US1] Expand datasets catalog regression coverage for shared untitled wrapper composition in /Users/hackerc/Projects/longtail-experiment/apps/frontend/tests/DatasetCatalogList.test.tsx and /Users/hackerc/Projects/longtail-experiment/apps/frontend/tests/catalog-page.test.tsx
- [X] T011 [P] [US1] Add page-level regression expectations for shared feed/list adoption on the home page in /Users/hackerc/Projects/longtail-experiment/apps/frontend/tests/home-page.test.tsx

### Implementation for User Story 1

- [X] T012 [US1] Refactor /Users/hackerc/Projects/longtail-experiment/apps/frontend/src/components/discovery/UnifiedDatasetRow.tsx into a thin adapter over /Users/hackerc/Projects/longtail-experiment/apps/frontend/src/components/discovery/DiscoveryFeedList.tsx
- [X] T013 [US1] Update dataset row mapping to the shared display-category/title/subtitle/date contract in /Users/hackerc/Projects/longtail-experiment/apps/frontend/src/components/discovery/unified-dataset-row-mappers.ts
- [X] T014 [US1] Refactor the titled home feed wrapper to use the shared outer shell and optional title region in /Users/hackerc/Projects/longtail-experiment/apps/frontend/src/components/discovery/RecentUpdatesFeed.tsx
- [X] T015 [US1] Refactor the untitled dataset catalog wrapper to use the shared outer shell in /Users/hackerc/Projects/longtail-experiment/apps/frontend/src/components/discovery/DatasetCatalogList.tsx
- [X] T016 [US1] Preserve dataset list pagination integration while consuming the shared catalog wrapper in /Users/hackerc/Projects/longtail-experiment/apps/frontend/src/components/discovery/InfiniteCatalogList.tsx
- [X] T017 [US1] Verify US1 behavior on /Users/hackerc/Projects/longtail-experiment/apps/frontend/src/app/page.tsx and /Users/hackerc/Projects/longtail-experiment/apps/frontend/src/app/datasets/page.tsx with updated shared component usage
- [X] T018 [US1] Verify US1 coverage contribution maintains >= 90% threshold using /Users/hackerc/Projects/longtail-experiment/apps/frontend/tests/RecentUpdatesFeed.test.tsx, /Users/hackerc/Projects/longtail-experiment/apps/frontend/tests/DatasetCatalogList.test.tsx, /Users/hackerc/Projects/longtail-experiment/apps/frontend/tests/catalog-page.test.tsx, and /Users/hackerc/Projects/longtail-experiment/apps/frontend/tests/home-page.test.tsx

**Checkpoint**: User Story 1 should now provide one shared feed/list wrapper and dataset-row pattern for titled and untitled dataset surfaces

---

## Phase 4: User Story 2 - Support Flexible Left-Side Metadata (Priority: P2)

**Goal**: Deliver a reusable left metadata rail that supports flexible display-category text and clean subtitle/date behavior across dataset and source rows

**Independent Test**: Render rows with different display-category values, different date strings, and missing optional subtitles, then confirm the metadata rail stays ordered and readable without creating a second row family

### Tests for User Story 2 (REQUIRED) ⚠️

- [X] T019 [P] [US2] Add display-category and optional-subtitle regression coverage in /Users/hackerc/Projects/longtail-experiment/apps/frontend/tests/UnifiedDatasetRow.test.tsx
- [X] T020 [P] [US2] Add source-row metadata-rail regression coverage in /Users/hackerc/Projects/longtail-experiment/apps/frontend/tests/source-list-page.test.tsx
- [X] T021 [P] [US2] Add source-list wrapper regression coverage for the shared row hierarchy in /Users/hackerc/Projects/longtail-experiment/apps/frontend/tests/source-detail-page.test.tsx

### Implementation for User Story 2

- [X] T022 [US2] Refactor /Users/hackerc/Projects/longtail-experiment/apps/frontend/src/components/discovery/SourceListRow.tsx to use the shared row, metadata rail, display-category, and subtitle primitives from /Users/hackerc/Projects/longtail-experiment/apps/frontend/src/components/discovery/DiscoveryFeedList.tsx
- [X] T023 [US2] Refactor /Users/hackerc/Projects/longtail-experiment/apps/frontend/src/components/discovery/SourceCatalogList.tsx to use the shared outer wrapper from /Users/hackerc/Projects/longtail-experiment/apps/frontend/src/components/discovery/DiscoveryFeedList.tsx
- [X] T024 [US2] Normalize source-specific display-category, update-date text, and subtitle fallback behavior inside /Users/hackerc/Projects/longtail-experiment/apps/frontend/src/components/discovery/SourceListRow.tsx
- [X] T025 [US2] Align shared row content support so dataset pills and source rows without supporting content both render correctly in /Users/hackerc/Projects/longtail-experiment/apps/frontend/src/components/discovery/DiscoveryFeedList.tsx and /Users/hackerc/Projects/longtail-experiment/apps/frontend/src/components/discovery/TagPill.tsx
- [X] T026 [US2] Verify source list and source detail pages preserve display-category/date hierarchy through /Users/hackerc/Projects/longtail-experiment/apps/frontend/src/app/sources/page.tsx and /Users/hackerc/Projects/longtail-experiment/apps/frontend/src/app/sources/[sourceId]/page.tsx
- [X] T027 [US2] Verify US2 coverage contribution maintains >= 90% threshold using /Users/hackerc/Projects/longtail-experiment/apps/frontend/tests/UnifiedDatasetRow.test.tsx, /Users/hackerc/Projects/longtail-experiment/apps/frontend/tests/source-list-page.test.tsx, and /Users/hackerc/Projects/longtail-experiment/apps/frontend/tests/source-detail-page.test.tsx

**Checkpoint**: User Story 2 should now support flexible display-category rendering across both dataset and source rows with one shared row system

---

## Phase 5: User Story 3 - Preserve Current Discovery Surface Behavior (Priority: P3)

**Goal**: Ensure all existing discovery list surfaces retain their current page-level behavior after adopting the shared component group

**Independent Test**: Render home, datasets, source detail, topic detail, and geography detail list surfaces and confirm headings, links, ordering, fallback ownership, and infinite-scroll behavior remain intact

### Tests for User Story 3 (REQUIRED) ⚠️

- [X] T028 [P] [US3] Add source/topic/geography detail regression coverage for shared list-surface reuse in /Users/hackerc/Projects/longtail-experiment/apps/frontend/tests/source-detail-page.test.tsx, /Users/hackerc/Projects/longtail-experiment/apps/frontend/tests/topic-detail-page.test.tsx, and /Users/hackerc/Projects/longtail-experiment/apps/frontend/tests/geography-detail-page.test.tsx
- [X] T029 [P] [US3] Expand infinite-scroll regression coverage for shared list wrapper compatibility in /Users/hackerc/Projects/longtail-experiment/apps/frontend/tests/InfiniteCatalogList.test.tsx
- [X] T030 [P] [US3] Add cross-surface shell contract coverage for retained test IDs and titled/untitled list behavior in /Users/hackerc/Projects/longtail-experiment/apps/frontend/tests/shell-structure-contract.test.tsx

### Implementation for User Story 3

- [X] T031 [US3] Verify and adjust shared wrapper compatibility for embedded dataset lists in /Users/hackerc/Projects/longtail-experiment/apps/frontend/src/app/sources/[sourceId]/page.tsx, /Users/hackerc/Projects/longtail-experiment/apps/frontend/src/app/topics/[topicId]/page.tsx, and /Users/hackerc/Projects/longtail-experiment/apps/frontend/src/app/geographies/[geographyId]/page.tsx
- [X] T032 [US3] Preserve existing populated-state wrapper test IDs and fallback ownership semantics across /Users/hackerc/Projects/longtail-experiment/apps/frontend/src/components/discovery/RecentUpdatesFeed.tsx, /Users/hackerc/Projects/longtail-experiment/apps/frontend/src/components/discovery/DatasetCatalogList.tsx, and /Users/hackerc/Projects/longtail-experiment/apps/frontend/src/components/discovery/SourceCatalogList.tsx
- [X] T033 [US3] Verify current empty and unavailable behaviors remain outside the shared component group in /Users/hackerc/Projects/longtail-experiment/apps/frontend/src/components/discovery/EmptyState.tsx, /Users/hackerc/Projects/longtail-experiment/apps/frontend/src/components/discovery/ErrorState.tsx, and /Users/hackerc/Projects/longtail-experiment/apps/frontend/src/components/discovery/RecentUpdatesFeed.tsx
- [X] T034 [US3] Verify US3 coverage contribution maintains >= 90% threshold using /Users/hackerc/Projects/longtail-experiment/apps/frontend/tests/source-detail-page.test.tsx, /Users/hackerc/Projects/longtail-experiment/apps/frontend/tests/topic-detail-page.test.tsx, /Users/hackerc/Projects/longtail-experiment/apps/frontend/tests/geography-detail-page.test.tsx, /Users/hackerc/Projects/longtail-experiment/apps/frontend/tests/InfiniteCatalogList.test.tsx, and /Users/hackerc/Projects/longtail-experiment/apps/frontend/tests/shell-structure-contract.test.tsx

**Checkpoint**: All current discovery list surfaces should now be functional on the shared component group without behavior regression

---

## Phase 6: Polish & Cross-Cutting Concerns

**Purpose**: Finalize documentation and complete mandatory verification

- [X] T035 [P] Update feature implementation notes and validation outcomes in /Users/hackerc/Projects/longtail-experiment/specs/039-unified-feed-list/quickstart.md if any execution details changed during implementation
- [X] T036 [P] Run focused frontend verification from /Users/hackerc/Projects/longtail-experiment/specs/039-unified-feed-list/quickstart.md against /Users/hackerc/Projects/longtail-experiment/apps/frontend/tests/RecentUpdatesFeed.test.tsx, /Users/hackerc/Projects/longtail-experiment/apps/frontend/tests/UnifiedDatasetRow.test.tsx, /Users/hackerc/Projects/longtail-experiment/apps/frontend/tests/DatasetCatalogList.test.tsx, /Users/hackerc/Projects/longtail-experiment/apps/frontend/tests/InfiniteCatalogList.test.tsx, /Users/hackerc/Projects/longtail-experiment/apps/frontend/tests/source-list-page.test.tsx, /Users/hackerc/Projects/longtail-experiment/apps/frontend/tests/source-detail-page.test.tsx, /Users/hackerc/Projects/longtail-experiment/apps/frontend/tests/catalog-page.test.tsx, and /Users/hackerc/Projects/longtail-experiment/apps/frontend/tests/home-page.test.tsx
- [X] T037 Run `pre-commit run --all-files` from /Users/hackerc/Projects/longtail-experiment before commit or handoff
- [X] T038 Run `pnpm exec nx run-many -t test --all` from /Users/hackerc/Projects/longtail-experiment before commit or handoff
- [X] T039 Run `pnpm exec nx run-many -t coverage --all` from /Users/hackerc/Projects/longtail-experiment before commit

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies - can start immediately
- **Foundational (Phase 2)**: Depends on Setup completion - BLOCKS all user stories
- **User Story 1 (Phase 3)**: Depends on Foundational completion
- **User Story 2 (Phase 4)**: Depends on Foundational completion and can reuse the shared module introduced for US1
- **User Story 3 (Phase 5)**: Depends on Foundational completion and the migrated wrappers from US1/US2
- **Polish (Phase 6)**: Depends on all desired user stories being complete

### User Story Dependencies

- **User Story 1 (P1)**: Starts after Phase 2 and delivers the MVP shared wrapper plus dataset-row adoption
- **User Story 2 (P2)**: Starts after Phase 2 and depends on the shared component group from US1 to extend flexible display-category support to source rows
- **User Story 3 (P3)**: Starts after US1 and US2 migrations are in place so page-level behavior can be regression-hardened across all surfaces

### Within Each User Story

- Tests MUST be written and fail before implementation
- Shared component contracts before consumer migrations
- Consumer migrations before page-level verification
- Story-level coverage verification before advancing to the next story

### Parallel Opportunities

- T002 can run in parallel with T001
- T003 and T004 can run in parallel before T005-T008
- T009, T010, and T011 can run in parallel within US1
- T019, T020, and T021 can run in parallel within US2
- T028, T029, and T030 can run in parallel within US3
- T035 and T036 can run in parallel in the Polish phase

---

## Parallel Example: User Story 1

```bash
# Launch US1 test updates together:
Task: "T009 [US1] Expand home feed regression coverage in apps/frontend/tests/RecentUpdatesFeed.test.tsx"
Task: "T010 [US1] Expand datasets catalog regression coverage in apps/frontend/tests/DatasetCatalogList.test.tsx and apps/frontend/tests/catalog-page.test.tsx"
Task: "T011 [US1] Add page-level regression expectations in apps/frontend/tests/home-page.test.tsx"
```

```bash
# After the shared module exists, launch dataset-surface consumer migrations in sequence with minimal overlap:
Task: "T012 [US1] Refactor apps/frontend/src/components/discovery/UnifiedDatasetRow.tsx"
Task: "T014 [US1] Refactor apps/frontend/src/components/discovery/RecentUpdatesFeed.tsx"
Task: "T015 [US1] Refactor apps/frontend/src/components/discovery/DatasetCatalogList.tsx"
```

---

## Parallel Example: User Story 2

```bash
# Launch US2 regression tests together:
Task: "T019 [US2] Add display-category and optional-subtitle regression coverage in apps/frontend/tests/UnifiedDatasetRow.test.tsx"
Task: "T020 [US2] Add source-row metadata-rail regression coverage in apps/frontend/tests/source-list-page.test.tsx"
Task: "T021 [US2] Add source-list wrapper regression coverage in apps/frontend/tests/source-detail-page.test.tsx"
```

```bash
# Then split source-surface implementation work:
Task: "T022 [US2] Refactor apps/frontend/src/components/discovery/SourceListRow.tsx"
Task: "T023 [US2] Refactor apps/frontend/src/components/discovery/SourceCatalogList.tsx"
Task: "T025 [US2] Align shared row content support in apps/frontend/src/components/discovery/DiscoveryFeedList.tsx and apps/frontend/src/components/discovery/TagPill.tsx"
```

---

## Parallel Example: User Story 3

```bash
# Launch cross-surface regression tasks together:
Task: "T028 [US3] Add source/topic/geography detail regression coverage"
Task: "T029 [US3] Expand infinite-scroll regression coverage"
Task: "T030 [US3] Add cross-surface shell contract coverage"
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1: Setup
2. Complete Phase 2: Foundational shared component-group contract
3. Complete Phase 3: User Story 1
4. **STOP and VALIDATE**: Run the US1 focused tests and manually verify `/` and `/datasets`
5. Demo the shared wrapper and dataset-row adoption as the MVP

### Incremental Delivery

1. Complete Setup + Foundational → shared component group ready
2. Add User Story 1 → test independently → validate titled and untitled dataset surfaces
3. Add User Story 2 → test independently → validate flexible display-category support across source and dataset rows
4. Add User Story 3 → test independently → validate all remaining discovery list surfaces and regression behavior
5. Finish with Polish phase stop-gate execution and quickstart/manual verification
