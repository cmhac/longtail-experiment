# Tasks: Frontend UI Standardization Migration

**Input**: Design documents from `/specs/036-heroui-ui-migration/`
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

- Frontend application work lives under `apps/frontend/src/` and `apps/frontend/tests/`
- Feature artifacts live under `specs/036-heroui-ui-migration/`

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Confirm and prepare the frontend styling/tooling baseline for the migration

- [ ] T001 Audit and update frontend dependency declarations in `/Users/hackerc/Projects/longtail-experiment/apps/frontend/package.json`
- [ ] T002 Verify Tailwind CSS v4/PostCSS configuration remains compatible in `/Users/hackerc/Projects/longtail-experiment/apps/frontend/postcss.config.mjs`
- [ ] T003 [P] Confirm Next.js frontend runtime configuration remains compatible with the migration in `/Users/hackerc/Projects/longtail-experiment/apps/frontend/next.config.ts`
- [ ] T004 [P] Record canonical HeroUI/Tailwind bootstrap and validation steps in `/Users/hackerc/Projects/longtail-experiment/specs/036-heroui-ui-migration/quickstart.md`

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Establish the shared styling, theming, and shell contracts that block all user stories

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

- [ ] T005 Add required foundational regression assertions for layout/bootstrap behavior in `/Users/hackerc/Projects/longtail-experiment/apps/frontend/tests/foundation-contracts.test.tsx`
- [ ] T006 [P] Add shell structure and theme regression assertions for the standardized shell in `/Users/hackerc/Projects/longtail-experiment/apps/frontend/tests/shell-structure-contract.test.tsx`
- [ ] T007 Update the global styling bootstrap to canonical Tailwind CSS v4 plus HeroUI imports while preserving identity tokens in `/Users/hackerc/Projects/longtail-experiment/apps/frontend/src/app/globals.css`
- [ ] T008 [P] Refactor shared theme token and class exports for the standardized shell in `/Users/hackerc/Projects/longtail-experiment/apps/frontend/src/theme/monochrome-theme.ts`
- [ ] T009 [P] Align root theme-preference behavior with the finalized shell/theme strategy in `/Users/hackerc/Projects/longtail-experiment/apps/frontend/src/theme/theme-preference.ts`
- [ ] T010 Refactor the root app wrapper to use the new theme/bootstrap assumptions in `/Users/hackerc/Projects/longtail-experiment/apps/frontend/src/app/layout.tsx`
- [ ] T011 Define and document the approved migration surface inventory and exception policy in `/Users/hackerc/Projects/longtail-experiment/specs/036-heroui-ui-migration/contracts/ui-standardization-contract.md`

**Checkpoint**: Foundation ready - user story implementation can now begin in parallel

---

## Phase 3: User Story 1 - Use A More Consistent Interface (Priority: P1) 🎯 MVP

**Goal**: Standardize the main frontend surfaces so equivalent controls, containers, and page chrome look and feel like one system while preserving Longtail identity

**Independent Test**: Open the primary routes and confirm shared shell, search, filter, row, card, and header surfaces use one consistent HeroUI/Tailwind-based language without changing the expected workflows

### Tests for User Story 1 (REQUIRED) ⚠️

- [ ] T012 [P] [US1] Update homepage shell and hero search expectations in `/Users/hackerc/Projects/longtail-experiment/apps/frontend/tests/home-page.test.tsx`
- [ ] T013 [P] [US1] Update search page standardized-surface expectations in `/Users/hackerc/Projects/longtail-experiment/apps/frontend/tests/search-page.test.tsx`
- [ ] T014 [P] [US1] Update dataset list page and filter-surface expectations in `/Users/hackerc/Projects/longtail-experiment/apps/frontend/tests/datasets-page.test.tsx`
- [ ] T015 [P] [US1] Update navbar interaction and dropdown/search surface assertions in `/Users/hackerc/Projects/longtail-experiment/apps/frontend/tests/navbar-interactions.test.tsx`
- [ ] T016 [P] [US1] Update shared component regression tests for standardized controls and rows in `/Users/hackerc/Projects/longtail-experiment/apps/frontend/tests/DatasetSearchBox.test.tsx`, `/Users/hackerc/Projects/longtail-experiment/apps/frontend/tests/DatasetListControls.test.tsx`, and `/Users/hackerc/Projects/longtail-experiment/apps/frontend/tests/UnifiedDatasetRow.test.tsx`

### Implementation for User Story 1

- [ ] T017 [US1] Refactor the global shell header to standardized HeroUI/Tailwind navigation patterns in `/Users/hackerc/Projects/longtail-experiment/apps/frontend/src/shell/site-header.tsx`
- [ ] T018 [P] [US1] Refactor the global footer surface and layout in `/Users/hackerc/Projects/longtail-experiment/apps/frontend/src/shell/site-footer.tsx`
- [ ] T019 [P] [US1] Refactor the homepage and navbar search experience around standardized HeroUI surfaces in `/Users/hackerc/Projects/longtail-experiment/apps/frontend/src/components/discovery/UnifiedSearchSurface.tsx` and `/Users/hackerc/Projects/longtail-experiment/apps/frontend/src/components/discovery/DatasetSearchBox.tsx`
- [ ] T020 [P] [US1] Refactor dataset filter and toggle controls to the shared HeroUI/Tailwind language in `/Users/hackerc/Projects/longtail-experiment/apps/frontend/src/components/discovery/DatasetListControls.tsx` and `/Users/hackerc/Projects/longtail-experiment/apps/frontend/src/components/discovery/GroupBySourceToggle.tsx`
- [ ] T021 [P] [US1] Refactor shared listing and content surfaces in `/Users/hackerc/Projects/longtail-experiment/apps/frontend/src/components/discovery/UnifiedDatasetRow.tsx`, `/Users/hackerc/Projects/longtail-experiment/apps/frontend/src/components/discovery/DatasetCard.tsx`, and `/Users/hackerc/Projects/longtail-experiment/apps/frontend/src/components/discovery/RecentUpdatesFeed.tsx`
- [ ] T022 [US1] Refactor list container components to reuse the new shared surface language in `/Users/hackerc/Projects/longtail-experiment/apps/frontend/src/components/discovery/DatasetCatalogList.tsx`, `/Users/hackerc/Projects/longtail-experiment/apps/frontend/src/components/discovery/SourceCatalogList.tsx`, `/Users/hackerc/Projects/longtail-experiment/apps/frontend/src/components/discovery/InfiniteCatalogList.tsx`, and `/Users/hackerc/Projects/longtail-experiment/apps/frontend/src/components/discovery/InfiniteSearchResults.tsx`
- [ ] T023 [US1] Integrate the standardized shell and shared surfaces into primary route pages in `/Users/hackerc/Projects/longtail-experiment/apps/frontend/src/app/page.tsx`, `/Users/hackerc/Projects/longtail-experiment/apps/frontend/src/app/search/page.tsx`, `/Users/hackerc/Projects/longtail-experiment/apps/frontend/src/app/datasets/page.tsx`, and `/Users/hackerc/Projects/longtail-experiment/apps/frontend/src/app/sources/page.tsx`
- [ ] T024 [US1] Verify US1 coverage contribution and update any affected feature documentation in `/Users/hackerc/Projects/longtail-experiment/specs/036-heroui-ui-migration/quickstart.md` and `/Users/hackerc/Projects/longtail-experiment/AGENTS.md` if needed

**Checkpoint**: At this point, User Story 1 should be fully functional and testable independently

---

## Phase 4: User Story 2 - Trust Stable Behavior During The Migration (Priority: P2)

**Goal**: Preserve search, browsing, navigation, detail flows, and explicit fallback states while the UI structure and styling system are standardized

**Independent Test**: Execute existing primary discovery journeys and confirm route behavior, empty/error handling, and responsive usability remain stable after the refactor

### Tests for User Story 2 (REQUIRED) ⚠️

- [ ] T025 [P] [US2] Update route-level regression coverage for detail and metadata pages in `/Users/hackerc/Projects/longtail-experiment/apps/frontend/tests/detail-page.test.tsx`, `/Users/hackerc/Projects/longtail-experiment/apps/frontend/tests/source-detail-page.test.tsx`, `/Users/hackerc/Projects/longtail-experiment/apps/frontend/tests/topic-detail-page.test.tsx`, and `/Users/hackerc/Projects/longtail-experiment/apps/frontend/tests/geography-detail-page.test.tsx`
- [ ] T026 [P] [US2] Update explicit empty and error state regression coverage in `/Users/hackerc/Projects/longtail-experiment/apps/frontend/tests/EmptyState.test.tsx` and `/Users/hackerc/Projects/longtail-experiment/apps/frontend/tests/ErrorState.test.tsx`
- [ ] T027 [P] [US2] Update detail-view supporting component regression coverage in `/Users/hackerc/Projects/longtail-experiment/apps/frontend/tests/DatasetDetailHeader.test.tsx`, `/Users/hackerc/Projects/longtail-experiment/apps/frontend/tests/ObservationsChart.test.tsx`, and `/Users/hackerc/Projects/longtail-experiment/apps/frontend/tests/ObservationsTable.test.tsx`

### Implementation for User Story 2

- [ ] T028 [US2] Refactor explicit empty and error state surfaces to standardized HeroUI/Tailwind containers in `/Users/hackerc/Projects/longtail-experiment/apps/frontend/src/components/discovery/EmptyState.tsx` and `/Users/hackerc/Projects/longtail-experiment/apps/frontend/src/components/discovery/ErrorState.tsx`
- [ ] T029 [P] [US2] Refactor shared detail and metadata headers to the standardized surface language in `/Users/hackerc/Projects/longtail-experiment/apps/frontend/src/components/discovery/DatasetDetailHeader.tsx`, `/Users/hackerc/Projects/longtail-experiment/apps/frontend/src/components/discovery/SourceDetailHeader.tsx`, `/Users/hackerc/Projects/longtail-experiment/apps/frontend/src/components/discovery/TopicDetailHeader.tsx`, and `/Users/hackerc/Projects/longtail-experiment/apps/frontend/src/components/discovery/GeographyDetailHeader.tsx`
- [ ] T030 [P] [US2] Refactor detail-analysis supporting surfaces while preserving information density in `/Users/hackerc/Projects/longtail-experiment/apps/frontend/src/components/discovery/DatasetDetailInsights.tsx`, `/Users/hackerc/Projects/longtail-experiment/apps/frontend/src/components/discovery/DatasetDetailAnalysis.tsx`, `/Users/hackerc/Projects/longtail-experiment/apps/frontend/src/components/discovery/ObservationsChart.tsx`, and `/Users/hackerc/Projects/longtail-experiment/apps/frontend/src/components/discovery/ObservationsTable.tsx`
- [ ] T031 [US2] Integrate the standardized detail and fallback surfaces into route pages in `/Users/hackerc/Projects/longtail-experiment/apps/frontend/src/app/datasets/[id]/page.tsx`, `/Users/hackerc/Projects/longtail-experiment/apps/frontend/src/app/sources/[sourceId]/page.tsx`, `/Users/hackerc/Projects/longtail-experiment/apps/frontend/src/app/topics/[topicId]/page.tsx`, and `/Users/hackerc/Projects/longtail-experiment/apps/frontend/src/app/geographies/[geographyId]/page.tsx`
- [ ] T032 [US2] Verify responsive and state-behavior parity for the migrated routes using the feature audit guidance in `/Users/hackerc/Projects/longtail-experiment/specs/036-heroui-ui-migration/quickstart.md`
- [ ] T033 [US2] Verify US2 coverage contribution maintains >= 90% thresholds for the frontend project via the affected Vitest suites and stop-gate commands documented in `/Users/hackerc/Projects/longtail-experiment/specs/036-heroui-ui-migration/quickstart.md`

**Checkpoint**: At this point, User Stories 1 AND 2 should both work independently

---

## Phase 5: User Story 3 - Reduce One-Off UI Patterns (Priority: P3)

**Goal**: Remove remaining fragmented UI patterns, document exceptions, and leave the frontend with one reusable standardized system for future work

**Independent Test**: Audit the in-scope frontend surfaces against the UI standardization contract and confirm all remaining non-standard patterns are either removed or explicitly documented as approved exceptions

### Tests for User Story 3 (REQUIRED) ⚠️

- [ ] T034 [P] [US3] Update shared component regression coverage for remaining standardized content surfaces in `/Users/hackerc/Projects/longtail-experiment/apps/frontend/tests/DatasetCard.test.tsx`, `/Users/hackerc/Projects/longtail-experiment/apps/frontend/tests/RecentUpdatesFeed.test.tsx`, and `/Users/hackerc/Projects/longtail-experiment/apps/frontend/tests/DatasetCatalogList.test.tsx`
- [ ] T035 [P] [US3] Add or update shell and navigation regression coverage for final standardized patterns in `/Users/hackerc/Projects/longtail-experiment/apps/frontend/tests/navbar-profile-dropdown.test.tsx` and `/Users/hackerc/Projects/longtail-experiment/apps/frontend/tests/navbar-theme-mode.test.tsx`
- [ ] T036 [P] [US3] Add migration-audit regression assertions for remaining standardized route patterns in `/Users/hackerc/Projects/longtail-experiment/apps/frontend/tests/catalog-page.test.tsx` and `/Users/hackerc/Projects/longtail-experiment/apps/frontend/tests/source-list-page.test.tsx`

### Implementation for User Story 3

- [ ] T037 [US3] Audit and remove remaining bespoke shared-surface divergences across `/Users/hackerc/Projects/longtail-experiment/apps/frontend/src/components/discovery` and `/Users/hackerc/Projects/longtail-experiment/apps/frontend/src/shell`
- [ ] T038 [P] [US3] Consolidate repeated route-level layout glue into reusable standardized wrappers in `/Users/hackerc/Projects/longtail-experiment/apps/frontend/src/app/page.tsx`, `/Users/hackerc/Projects/longtail-experiment/apps/frontend/src/app/search/page.tsx`, `/Users/hackerc/Projects/longtail-experiment/apps/frontend/src/app/datasets/page.tsx`, `/Users/hackerc/Projects/longtail-experiment/apps/frontend/src/app/sources/page.tsx`, `/Users/hackerc/Projects/longtail-experiment/apps/frontend/src/app/topics/[topicId]/page.tsx`, and `/Users/hackerc/Projects/longtail-experiment/apps/frontend/src/app/geographies/[geographyId]/page.tsx`
- [ ] T039 [P] [US3] Document every retained exception and final standardized pattern expectations in `/Users/hackerc/Projects/longtail-experiment/specs/036-heroui-ui-migration/contracts/ui-standardization-contract.md` and `/Users/hackerc/Projects/longtail-experiment/specs/036-heroui-ui-migration/research.md`
- [ ] T040 [US3] Update the migration validation guide and final audit steps in `/Users/hackerc/Projects/longtail-experiment/specs/036-heroui-ui-migration/quickstart.md`
- [ ] T041 [US3] Verify US3 coverage contribution maintains >= 90% thresholds for the frontend project via the affected Vitest suites and stop-gate commands documented in `/Users/hackerc/Projects/longtail-experiment/specs/036-heroui-ui-migration/quickstart.md`

**Checkpoint**: All user stories should now be independently functional

---

## Phase 6: Polish & Cross-Cutting Concerns

**Purpose**: Final validation, cleanup, and repository-wide stop-gate enforcement

- [ ] T042 [P] Review changed frontend files for dead bespoke classes and remove leftover obsolete styling from `/Users/hackerc/Projects/longtail-experiment/apps/frontend/src/app/globals.css` and related component files
- [ ] T043 [P] Run the feature manual audit from `/Users/hackerc/Projects/longtail-experiment/specs/036-heroui-ui-migration/quickstart.md` and record any required follow-up updates in `/Users/hackerc/Projects/longtail-experiment/specs/036-heroui-ui-migration/quickstart.md`
- [ ] T044 Run `pnpm exec nx run-many -t test --all` and verify pass before commit and before agent handoff/end of work from `/Users/hackerc/Projects/longtail-experiment`
- [ ] T045 Run `pnpm exec nx run-many -t coverage --all` and verify >= 90% coverage thresholds are satisfied before commit from `/Users/hackerc/Projects/longtail-experiment`
- [ ] T046 Run `pre-commit run --all-files` and verify the all-files quality gate passes from `/Users/hackerc/Projects/longtail-experiment`

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies - can start immediately
- **Foundational (Phase 2)**: Depends on Setup completion - BLOCKS all user stories
- **User Story 1 (Phase 3)**: Depends on Foundational completion
- **User Story 2 (Phase 4)**: Depends on Foundational completion and should build on the shared surfaces stabilized in US1
- **User Story 3 (Phase 5)**: Depends on Foundational completion and is safest after US1 and US2 establish the main standardized patterns
- **Polish (Phase 6)**: Depends on all desired user stories being complete

### User Story Dependencies

- **User Story 1 (P1)**: Can start after Foundational (Phase 2) - MVP for the migration
- **User Story 2 (P2)**: Can start after Foundational, but should follow the shared shell/control changes from US1 to minimize rework
- **User Story 3 (P3)**: Depends on the main pattern inventory from US1 and the behavior-preserving detail work from US2

### Within Each User Story

- Tests MUST be written and fail before implementation
- Shared components before route integration
- Theme/surface work before polish cleanup
- Documentation and coverage verification before story signoff

### Parallel Opportunities

- Setup tasks marked [P] can run in parallel
- Foundational theme/shell contract tests and token updates marked [P] can run in parallel
- Within US1, shell, controls, and some shared-surface tasks can proceed in parallel after the bootstrap work lands
- Within US2, detail headers and analysis-container updates can proceed in parallel
- Within US3, final audit/documentation tasks and some route-wrapper cleanup can proceed in parallel

---

## Parallel Example: User Story 1

```bash
# Launch US1 test updates together:
Task: "Update homepage shell and hero search expectations in apps/frontend/tests/home-page.test.tsx"
Task: "Update search page standardized-surface expectations in apps/frontend/tests/search-page.test.tsx"
Task: "Update dataset list page and filter-surface expectations in apps/frontend/tests/datasets-page.test.tsx"

# Launch US1 shared-surface refactors together after shell/bootstrap work stabilizes:
Task: "Refactor the global footer surface and layout in apps/frontend/src/shell/site-footer.tsx"
Task: "Refactor homepage and navbar search experience in apps/frontend/src/components/discovery/UnifiedSearchSurface.tsx and DatasetSearchBox.tsx"
Task: "Refactor dataset filter and toggle controls in apps/frontend/src/components/discovery/DatasetListControls.tsx and GroupBySourceToggle.tsx"
```

---

## Parallel Example: User Story 2

```bash
# Launch US2 test updates together:
Task: "Update route-level regression coverage for detail and metadata pages"
Task: "Update explicit empty and error state regression coverage"
Task: "Update detail-view supporting component regression coverage"

# Launch US2 component refactors together:
Task: "Refactor shared detail and metadata headers"
Task: "Refactor detail-analysis supporting surfaces"
```

---

## Parallel Example: User Story 3

```bash
# Launch US3 final audit tasks together:
Task: "Update shared component regression coverage for remaining standardized content surfaces"
Task: "Add or update shell and navigation regression coverage for final standardized patterns"
Task: "Add migration-audit regression assertions for remaining standardized route patterns"

# Launch US3 documentation/audit tasks together:
Task: "Document every retained exception and final standardized pattern expectations"
Task: "Update the migration validation guide and final audit steps"
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1: Setup
2. Complete Phase 2: Foundational
3. Complete Phase 3: User Story 1
4. **STOP and VALIDATE**: Verify the main shell, search, filters, and listing surfaces independently
5. Demo the standardized UI baseline before expanding to detail and cleanup work

### Incremental Delivery

1. Complete Setup + Foundational → theme/bootstrap/shell foundation ready
2. Add User Story 1 → validate consistency on primary routes
3. Add User Story 2 → validate behavior stability on detail and fallback flows
4. Add User Story 3 → complete exception audit and final pattern consolidation
5. Finish with cross-cutting validation and stop-gate commands

### Parallel Team Strategy

With multiple developers:

1. One developer handles foundation/theme bootstrap
2. One developer handles shell and shared controls
3. One developer handles content/detail surface migrations
4. After shared patterns stabilize, route integration and final audit work can split by page group

---

## Notes

- [P] tasks = different files, no dependencies
- [Story] label maps task to specific user story for traceability
- Each user story should remain independently testable
- Coverage MUST remain >= 90% in every affected project
- Before any commit and before any AI agent stops work, `pnpm exec nx run-many -t test --all`
  MUST pass; targeted tests do not satisfy this requirement
- Before any commit, `pnpm exec nx run-many -t coverage --all` MUST pass with >= 90%
  coverage thresholds in every project
- Relevant documentation MUST be updated in the same change as impacted code
- AGENTS.md MUST be updated when repository structure, workflows, or canonical commands change
- Manual validation must follow the routes and audit criteria documented in `quickstart.md`
