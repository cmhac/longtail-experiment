# Implementation Plan: Frontend UI Standardization Migration

**Branch**: `[036-heroui-ui-migration]` | **Date**: 2026-03-26 | **Spec**: [/Users/hackerc/Projects/longtail-experiment/specs/036-heroui-ui-migration/spec.md](/Users/hackerc/Projects/longtail-experiment/specs/036-heroui-ui-migration/spec.md)
**Input**: Feature specification from `/specs/036-heroui-ui-migration/spec.md`

**Note**: This template is filled in by the `/speckit.plan` command. See `.specify/templates/plan-template.md` for the execution workflow.

## Summary

Standardize the frontend UI around HeroUI v3 and Tailwind CSS v4 while preserving Longtail’s existing typography, color intent, and core editorial feel. The implementation approach replaces bespoke page-level HTML and CSS patterns with HeroUI primitives, compound components, Tailwind utility layout, and shared theme variables; keeps existing Next.js App Router routing and discovery data flows intact; and uses an explicit exception list for any surfaces that should remain custom for brand or product clarity reasons.

## Technical Context

**Language/Version**: TypeScript 5.x + React 19 in Next.js 15 App Router  
**Primary Dependencies**: `@heroui/react`, HeroUI v3 styling system, Tailwind CSS v4/PostCSS integration, existing Next.js routing primitives, existing discovery client/types, existing Recharts detail visualizations  
**Storage**: N/A for new persistence; existing PostgreSQL-backed discovery APIs remain the data source  
**Testing**: Vitest, Testing Library, frontend page/component/route tests under `apps/frontend/tests`, Nx run-many quality gates  
**Target Platform**: Next.js-rendered web UI for desktop and mobile browsers  
**Project Type**: Nx monorepo web application; frontend-focused refactor within `apps/frontend`  
**Performance Goals**: Preserve current perceived UI responsiveness and route rendering behavior while reducing bespoke UI code and avoiding regressions in interaction latency  
**Constraints**: Preserve existing user-facing discovery behavior; preserve typography and color identity; maintain >=90% coverage; satisfy full monorepo test and coverage stop gates; avoid introducing duplicate replacement patterns; keep existing shell/navigation semantics recognizable  
**Scale/Scope**: Frontend shell, discovery pages, discovery components, global theme/styling setup, and related frontend tests across `apps/frontend/src` and `apps/frontend/tests`

## Constitution Check

_GATE: Must pass before Phase 0 research. Re-check after Phase 1 design._

- Monorepo cohesion: PASS - Scope remains within the existing `apps/frontend` project and existing spec artifacts; no new Nx project boundaries are introduced.
- Quality gate enforcement: PASS - Plan preserves Biome, TypeScript, Vitest, Nx, and pre-commit quality gates with no suppression strategy.
- Full-suite stop rule: PASS - Plan requires `pnpm exec nx run-many -t test --all` before any commit and before any AI handoff/stop.
- Coverage stop rule: PASS - Plan requires `pnpm exec nx run-many -t coverage --all` before any commit with >=90% thresholds for every project.
- Test and coverage discipline: PASS - Plan includes route-, component-, and shell-level test updates to preserve and verify behavior throughout the migration.
- Local-first parity: PASS - No new runtime services are needed; changes remain verifiable in the existing frontend/local stack and Docker Compose environment.
- Data integrity and reliability: PASS - No backend schema or data contract change is required; the plan explicitly protects existing discovery behavior and API consumption semantics.
- Configuration integrity: PASS - No new service or credential dependency is introduced; existing environment behavior remains unchanged.
- Documentation fidelity: PASS - Plan includes required updates to feature docs and AGENTS-aligned tooling/context artifacts where the frontend stack description changes.

## Project Structure

### Documentation (this feature)

```text
specs/036-heroui-ui-migration/
├── plan.md              # This file (/speckit.plan command output)
├── research.md          # Phase 0 output (/speckit.plan command)
├── data-model.md        # Phase 1 output (/speckit.plan command)
├── quickstart.md        # Phase 1 output (/speckit.plan command)
├── contracts/           # Phase 1 output (/speckit.plan command)
│   └── ui-standardization-contract.md
└── tasks.md             # Phase 2 output (/speckit.tasks command - NOT created by /speckit.plan)
```

### Source Code (repository root)

```text
apps/
└── frontend/
    ├── package.json
    ├── postcss.config.mjs
    ├── next.config.ts
    ├── src/
    │   ├── app/
    │   │   ├── layout.tsx
    │   │   ├── globals.css
    │   │   ├── page.tsx
    │   │   ├── search/page.tsx
    │   │   ├── datasets/page.tsx
    │   │   ├── datasets/[id]/page.tsx
    │   │   ├── sources/page.tsx
    │   │   ├── sources/[sourceId]/page.tsx
    │   │   ├── topics/[topicId]/page.tsx
    │   │   └── geographies/[geographyId]/page.tsx
    │   ├── components/
    │   │   └── discovery/
    │   │       ├── UnifiedSearchSurface.tsx
    │   │       ├── DatasetSearchBox.tsx
    │   │       ├── DatasetListControls.tsx
    │   │       ├── DatasetCatalogList.tsx
    │   │       ├── InfiniteCatalogList.tsx
    │   │       ├── InfiniteSearchResults.tsx
    │   │       ├── UnifiedDatasetRow.tsx
    │   │       ├── DatasetCard.tsx
    │   │       ├── RecentUpdatesFeed.tsx
    │   │       ├── DatasetDetailHeader.tsx
    │   │       ├── DatasetDetailInsights.tsx
    │   │       ├── DatasetDetailAnalysis.tsx
    │   │       ├── TopicDetailHeader.tsx
    │   │       ├── GeographyDetailHeader.tsx
    │   │       ├── SourceDetailHeader.tsx
    │   │       ├── EmptyState.tsx
    │   │       ├── ErrorState.tsx
    │   │       ├── GroupBySourceToggle.tsx
    │   │       ├── ObservationsChart.tsx
    │   │       └── ObservationsTable.tsx
    │   ├── shell/
    │   │   ├── site-header.tsx
    │   │   ├── site-footer.tsx
    │   │   ├── navbar-config.ts
    │   │   └── footer-content.ts
    │   ├── theme/
    │   │   ├── monochrome-theme.ts
    │   │   └── theme-preference.ts
    │   └── lib/api/
    └── tests/
        ├── shell-structure-contract.test.tsx
        ├── navbar-*.test.tsx
        ├── home-page.test.tsx
        ├── search-page.test.tsx
        ├── datasets-page.test.tsx
        ├── detail-page.test.tsx
        ├── source-*.test.tsx
        ├── topic-detail-page.test.tsx
        ├── geography-detail-page.test.tsx
        ├── DatasetListControls.test.tsx
        ├── DatasetSearchBox*.test.tsx
        ├── UnifiedDatasetRow.test.tsx
        ├── DatasetCard.test.tsx
        ├── RecentUpdatesFeed.test.tsx
        └── foundation-contracts.test.tsx
```

**Structure Decision**: Keep the migration inside the current frontend application and its existing shell/discovery component boundaries. The refactor will standardize existing modules in place rather than introduce a new component library package or a parallel design-system layer.

## Phase Plan

### Phase 0: Research and Decision Consolidation

- Confirm canonical HeroUI v3 patterns to adopt:
  - no provider requirement
  - Tailwind CSS v4 + `@heroui/styles` import order
  - semantic variants over raw visual variants
  - compound component composition where applicable
  - variant functions or BEM classes when styling framework-specific roots like `next/link`
- Confirm current frontend baseline:
  - global styling currently relies on `globals.css` custom shell classes and CSS variables
  - HeroUI is already present but used selectively
  - PostCSS is configured for Tailwind v4, but the app currently imports `@heroui/react/styles` rather than the canonical Tailwind + HeroUI style stack
  - shell and discovery surfaces still rely heavily on raw HTML structures and bespoke classes
- Finalize migration boundaries:
  - in scope: shell, discovery list/detail/search surfaces, empty/error/loading surfaces, filter/search controls, page headers, recent-updates/listing rows
  - out of scope for this phase unless needed for parity: backend APIs, route contracts, data repository behavior
- Record exception policy:
  - typography families remain protected
  - current color intent remains protected
  - data-heavy charts/tables may retain limited custom structure where HeroUI does not directly fit

### Phase 1: Design and Contract Finalization

- Define the standardized UI surface model:
  - shell regions map to HeroUI surfaces/cards/navbar-like primitives plus Tailwind layout utilities
  - form/search/filter controls map to HeroUI inputs, combo boxes, buttons, surfaces, and listbox/popover patterns
  - dataset list/detail cards and headers map to shared container, heading, pill, and metadata patterns
  - state surfaces map to standardized HeroUI-aligned empty/error/unavailable cards
- Define theming approach:
  - preserve current typography and color identity by translating existing shell variables into HeroUI/Tailwind theme variables
  - move layout/spacing/chrome styling away from bespoke global selectors where practical and into Tailwind utility classes plus minimal theme-layer CSS
  - keep any required CSS variables in `globals.css` or imported theme files, but avoid one-off page-specific CSS when a utility or HeroUI token can express the same rule
- Define migration inventory and sequencing:
  - foundation first: dependencies/imports/theme/css/bootstrap
  - shell second: layout, header, footer, global regions
  - interactive shared controls third: search, filters, toggles, pills
  - content containers fourth: lists, cards, rows, headers, state components
  - page integration fifth: route pages adopt standardized surfaces after shared components stabilize
- Produce artifacts:
  - `research.md`
  - `data-model.md`
  - `contracts/ui-standardization-contract.md`
  - `quickstart.md`

### Phase 2: Implementation Planning

#### Workstream A - Foundation and Styling System

- Add explicit frontend dependencies and imports needed for canonical Tailwind CSS v4 + HeroUI v3 usage.
- Update `apps/frontend/src/app/globals.css` to:
  - import Tailwind first
  - import `@heroui/styles` second
  - preserve Longtail-specific typography and color variables
  - reduce shell-specific bespoke styling to only the rules that cannot be expressed via theme variables or utilities
- Audit `apps/frontend/src/theme/monochrome-theme.ts` and `apps/frontend/src/theme/theme-preference.ts` against HeroUI theming patterns:
  - keep preference resolution behavior
  - align variable naming and document which variables are source-of-truth
  - avoid duplicating semantic roles that HeroUI/Tailwind already provide
- Keep `apps/frontend/postcss.config.mjs` and `apps/frontend/next.config.ts` aligned with the finalized style stack.

#### Workstream B - Shell Standardization

- Refactor `apps/frontend/src/app/layout.tsx` to remain minimal but compatible with the finalized theme/class strategy.
- Refactor `apps/frontend/src/shell/site-header.tsx`:
  - replace raw button/link/search chrome where appropriate with HeroUI button/input/surface primitives
  - preserve current active-tab, profile menu, and navbar search behaviors
  - use HeroUI-friendly event APIs where component substitutions warrant them
- Refactor `apps/frontend/src/shell/site-footer.tsx` and shell container classes to align with standardized surfaces and spacing.
- Normalize shell region wrappers so route pages rely less on legacy `shell-*` CSS scaffolding.

#### Workstream C - Shared Discovery Controls

- Refactor `apps/frontend/src/components/discovery/UnifiedSearchSurface.tsx` and `apps/frontend/src/components/discovery/DatasetSearchBox.tsx`:
  - standardize hero and navbar search variants around HeroUI inputs/surfaces/popovers
  - preserve suggestion fetching, query syncing, and route navigation behavior
  - remove bespoke layout/styling where HeroUI/Tailwind defaults suffice
- Refactor `apps/frontend/src/components/discovery/DatasetListControls.tsx`:
  - keep HeroUI combo-box usage
  - remove remaining bespoke control-surface styling where possible
  - align spacing, grouping, and widths with HeroUI/Tailwind utility conventions
- Refactor `apps/frontend/src/components/discovery/GroupBySourceToggle.tsx` and any similar controls to standardized toggles/switches/buttons.

#### Workstream D - Shared Content Surfaces

- Refactor row/card/list surfaces:
  - `UnifiedDatasetRow.tsx`
  - `DatasetCard.tsx`
  - `DatasetCatalogList.tsx`
  - `SourceCatalogList.tsx`
  - `InfiniteCatalogList.tsx`
  - `InfiniteSearchResults.tsx`
  - `RecentUpdatesFeed.tsx`
- Goals for this group:
  - replace raw article/div hierarchy with HeroUI card/list/surface composition where practical
  - keep metadata pills/links behavior intact
  - keep infinite-loading/pagination behaviors intact
  - standardize headings, supporting text, metadata rails, and pill treatments
- Refactor state surfaces:
  - `EmptyState.tsx`
  - `ErrorState.tsx`
  - any embedded fallback containers in pages
- Ensure repeated surface types share one visual language rather than per-component custom treatments.

#### Workstream E - Detail and Metadata Pages

- Refactor detail/header components:
  - `DatasetDetailHeader.tsx`
  - `DatasetDetailInsights.tsx`
  - `DatasetDetailAnalysis.tsx`
  - `SourceDetailHeader.tsx`
  - `TopicDetailHeader.tsx`
  - `GeographyDetailHeader.tsx`
- Preserve readable information density while replacing bespoke wrappers with standardized sections, cards, chips, and typographic utilities.
- Keep `ObservationsChart.tsx` and `ObservationsTable.tsx` functionally intact while standardizing their surrounding labels, controls, and container surfaces.

#### Workstream F - Route Integration

- Update route pages under `apps/frontend/src/app/**/page.tsx` to consume standardized shell/content wrappers rather than page-specific layout glue.
- Preserve existing server-side data fetching and error handling.
- Ensure route-level composition stays simple: fetch data, pass props into shared components, avoid route-specific styling re-divergence.

#### Workstream G - Test and Verification Hardening

- Update unit/integration tests for components and pages whose DOM structure or accessibility semantics change.
- Maintain or strengthen tests covering:
  - shell presence and layout contracts
  - search query submission and suggestions
  - filter/sort URL parameter wiring
  - dataset list/detail rendering
  - topic/geography/source navigation
  - explicit empty/error states
- Add regression tests where standardization introduces risk of behavior drift.
- Manual verification must cover:
  - home page
  - search page
  - dataset list page
  - dataset detail page
  - source list/detail pages
  - topic and geography detail pages
  - navbar search expansion and profile dropdown behavior

#### Workstream H - Documentation and Traceability

- Keep feature artifacts current as design decisions are locked in.
- Update AGENTS-aligned stack/context only if the effective frontend setup or canonical commands materially change.
- Record documented exceptions for any retained legacy surfaces.

## Implementation Notes and Sequencing Checkpoints

- Complete the styling/bootstrap layer before refactoring high-volume components. This prevents repeated rework when Tailwind/HeroUI foundation changes.
- Land shell standardization before route-level cleanup so every page can inherit the same outer structure.
- Land shared control components before list/detail surfaces; search and filter affordances are cross-cutting and affect multiple routes.
- Refactor repeated card/row/state components before page files so route integration is mostly composition work.
- Treat charts and data tables as controlled exceptions: standardize their containers and related chrome first, then only replace their internal structure if it improves parity without harming readability.

### Checkpoint A - Foundation Ready

- `apps/frontend` uses canonical Tailwind CSS v4 + HeroUI style imports.
- Theme variables preserve existing typography and color identity.
- No provider-based HeroUI setup is introduced.

### Checkpoint B - Shell and Controls Ready

- Header, footer, search surfaces, and filter controls use standardized HeroUI/Tailwind patterns.
- Navbar/search/profile interactions still behave as before.

### Checkpoint C - Shared Surfaces Ready

- Dataset rows, cards, feeds, state surfaces, and headers share one container and spacing language.
- Documented exceptions exist for any surfaces intentionally left custom.

### Checkpoint D - Route Integration Ready

- Primary pages render standardized shared surfaces without per-page style drift.
- Existing discovery workflows remain behaviorally stable.

### Checkpoint E - Validation Ready

- Updated frontend tests pass.
- Manual page checks confirm visual consistency and preserved identity.
- Full monorepo test and coverage stop gates pass.

## Post-Design Constitution Re-Check

- Monorepo cohesion: PASS - Design remains isolated to the existing frontend app and synchronized feature artifacts.
- Quality gates and stop rules: PASS - Design requires full monorepo test and coverage gates before commit/handoff.
- Coverage discipline: PASS - Design includes targeted test updates across affected route and component suites.
- Local-first parity: PASS - Existing local stack is sufficient for verification; no compose changes are required.
- Data integrity/reliability: PASS - No data contract changes are introduced; UI behavior-preservation testing is explicit.
- Configuration integrity: PASS - No new secrets or fail-fast configuration surfaces are introduced.
- Documentation fidelity: PASS - Research, data model, contract, quickstart, and agent-context updates are included in the plan.

## Complexity Tracking

No constitution violations requiring justification.
