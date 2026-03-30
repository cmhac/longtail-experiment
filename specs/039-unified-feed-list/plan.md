# Implementation Plan: Unified Feed List Components

**Branch**: `[039-unified-feed-list]` | **Date**: 2026-03-30 | **Spec**: [/Users/hackerc/Projects/longtail-experiment/specs/039-unified-feed-list/spec.md](/Users/hackerc/Projects/longtail-experiment/specs/039-unified-feed-list/spec.md)
**Input**: Feature specification from `/specs/039-unified-feed-list/spec.md`

**Note**: This template is filled in by the `/speckit.plan` command. See `.specify/templates/plan-template.md` for the execution workflow.

## Summary

Create a shared discovery feed/list component group that extracts the current repeated list-shell and row hierarchy into reusable composable primitives. The implementation will consolidate the current `RecentUpdatesFeed`, `DatasetCatalogList`, `SourceCatalogList`, `UnifiedDatasetRow`, and `SourceListRow` structures into one shared presentation system with an outer wrapper, optional title region, shared row, and reusable metadata/title subcomponents while preserving current page-specific behavior, ordering, navigation, and fallback states.

The technical approach is frontend-only inside `apps/frontend`, using HeroUI and Tailwind-aligned shared components under `apps/frontend/src/components/discovery`. Existing data contracts remain the source of truth; adapter and mapper layers will translate current dataset and source payloads into the new display-category/title/subtitle/date presentation contract.

## Technical Context

**Language/Version**: TypeScript 5.x + React 19 in Next.js 15 App Router  
**Primary Dependencies**: Existing discovery UI components, `@heroui/react`, Next.js routing/link primitives, existing discovery API client/types, shell theme tokens, Tailwind utility classes  
**Storage**: N/A (presentation-only refactor over existing discovery payloads)  
**Testing**: Vitest, Testing Library for client behavior, frontend typecheck, Biome, Nx monorepo stop-gate suites  
**Target Platform**: Next.js-rendered web UI for desktop and mobile browsers  
**Project Type**: Frontend web application feature in Nx monorepo  
**Performance Goals**: Preserve current perceived responsiveness for home, datasets, source, topic, and geography list surfaces while reducing duplicated UI composition  
**Constraints**: Preserve current routing and empty/error behaviors; keep HeroUI/Tailwind as the UI system; avoid new bespoke CSS except where existing shared tokens already apply; maintain >=90% coverage and pass full monorepo test and coverage stop gates  
**Scale/Scope**: Shared discovery components and tests in `apps/frontend`, affecting home recent updates, datasets catalog, source catalog, and dataset list surfaces reused on source/topic/geography detail pages

## Constitution Check

_GATE: Must pass before Phase 0 research. Re-check after Phase 1 design._

- Monorepo cohesion: PASS - scope remains entirely within `apps/frontend` and existing discovery component boundaries with no new Nx project or cross-layer contract changes.
- Quality gate enforcement: PASS - plan retains Biome, TypeScript, Vitest, and Nx quality gates with no suppression or bypass strategy.
- Full-suite stop rule: PASS - implementation plan requires `pnpm exec nx run-many -t test --all` before any commit and before AI handoff/stop.
- Coverage stop rule: PASS - implementation plan requires `pnpm exec nx run-many -t coverage --all` before any commit with >=90% thresholds for every project.
- Test and coverage discipline: PASS - plan includes component, page, and infinite-scroll regression coverage to preserve current behavior while replacing shared presentation.
- Local-first parity: PASS - no new runtime service or compose change is needed; impacted flows remain manually testable in the current frontend/local Docker Compose setup.
- Data integrity and reliability: PASS - no persistence or API schema changes are introduced; existing discovery payload semantics and navigation outcomes remain unchanged.
- Configuration integrity: PASS - no new services, credentials, or environment-variable requirements are introduced.
- Frontend UI consistency: PASS - design centers on shared abstractions under `apps/frontend/src/components` and explicitly eliminates duplicated row/wrapper markup.
- Documentation fidelity: PASS - spec, plan, contracts, quickstart, and agent context updates are included; AGENTS.md does not require update because repository structure and canonical commands remain unchanged.

## Project Structure

### Documentation (this feature)

```text
specs/039-unified-feed-list/
├── plan.md
├── research.md
├── data-model.md
├── quickstart.md
├── contracts/
│   └── discovery-feed-list-contract.md
└── tasks.md
```

### Source Code (repository root)

```text
apps/
└── frontend/
    ├── src/
    │   ├── app/
    │   │   ├── page.tsx
    │   │   ├── datasets/page.tsx
    │   │   ├── sources/page.tsx
    │   │   ├── sources/[sourceId]/page.tsx
    │   │   ├── topics/[topicId]/page.tsx
    │   │   └── geographies/[geographyId]/page.tsx
    │   ├── components/
    │   │   └── discovery/
    │   │       ├── RecentUpdatesFeed.tsx
    │   │       ├── DatasetCatalogList.tsx
    │   │       ├── SourceCatalogList.tsx
    │   │       ├── InfiniteCatalogList.tsx
    │   │       ├── UnifiedDatasetRow.tsx
    │   │       ├── SourceListRow.tsx
    │   │       ├── unified-dataset-row-mappers.ts
    │   │       ├── TagPill.tsx
    │   │       └── [new shared feed/list component group module]
    │   └── lib/api/discovery-types.ts
    └── tests/
        ├── RecentUpdatesFeed.test.tsx
        ├── UnifiedDatasetRow.test.tsx
        ├── DatasetCatalogList.test.tsx
        ├── InfiniteCatalogList.test.tsx
        ├── source-list-page.test.tsx
        ├── source-detail-page.test.tsx
        ├── topic-detail-page.test.tsx
        ├── geography-detail-page.test.tsx
        ├── catalog-page.test.tsx
        └── home-page.test.tsx
```

**Structure Decision**: Keep the feature fully inside the existing frontend discovery component area and introduce one grouped shared module for feed/list primitives rather than a new package or a second parallel row system.

## Phase 0 Research Outcomes

See /Users/hackerc/Projects/longtail-experiment/specs/039-unified-feed-list/research.md.

- Reuse the current editorial row anatomy already shared by `UnifiedDatasetRow` and `SourceListRow` as the structural baseline.
- Model the new component group as composable exports from one module so surfaces can reuse only the parts they need while preserving a standard hierarchy.
- Keep payload normalization in mappers or thin adapters rather than pushing source-specific logic into the shared presentation components.
- Preserve current surface-level fallback states outside the new component group to keep concerns separated.

## Phase 1 Design Artifacts

- Research: /Users/hackerc/Projects/longtail-experiment/specs/039-unified-feed-list/research.md
- Data model: /Users/hackerc/Projects/longtail-experiment/specs/039-unified-feed-list/data-model.md
- Interface contract: /Users/hackerc/Projects/longtail-experiment/specs/039-unified-feed-list/contracts/discovery-feed-list-contract.md
- Quickstart: /Users/hackerc/Projects/longtail-experiment/specs/039-unified-feed-list/quickstart.md
- Agent context update command: `.specify/scripts/bash/update-agent-context.sh codex`

## Implementation Phases

### Phase 2 Delivery Plan

1. Define the shared feed/list component group contract.
   - Establish the outer wrapper, optional heading region, row container, metadata rail, row title, row subtitle, update-date text, and display-category text contract.
   - Decide the grouped export shape so repeated discovery surfaces can compose the same structure without duplicating markup.

2. Build the shared feed/list primitives in `apps/frontend/src/components/discovery`.
   - Extract common wrapper and row layout from the current list/feed implementations.
   - Preserve current spacing, typography, and responsive behavior already in use across dataset and source rows.

3. Migrate dataset row consumers to the new primitives.
   - Refactor `UnifiedDatasetRow` to become a thin adapter or compatibility layer over the new component group.
   - Keep current tag-pill rendering, title-link behavior, and summary handling intact.

4. Migrate source row consumers to the new primitives.
   - Refactor `SourceListRow` to use the same underlying row structure while preserving row-wide linking and source-specific summary/count semantics.
   - Preserve `SourceCatalogList` behavior and `source-catalog-list` test contract.

5. Migrate feed/list wrapper consumers to the new shared shell.
   - Refactor `RecentUpdatesFeed`, `DatasetCatalogList`, and `SourceCatalogList` to compose the shared outer wrapper and optional title region.
   - Preserve `recent-updates-feed`, `recent-updates-header`, `catalog-flat-list`, and `source-catalog-list` surface-level contracts unless explicitly replaced by a planned compatibility wrapper.

6. Keep page-level behavior stable across all consumers.
   - Ensure `InfiniteCatalogList` still wraps `DatasetCatalogList` and preserves sentinel/loading/error behavior.
   - Preserve current routing and server-data flows on home, datasets, source list/detail, topic detail, and geography detail pages.

7. Harden regression coverage and manual verification.
   - Add or update tests for the shared component group contract, the flexible display-category slot, optional title behavior, and existing page-level rendering expectations.
   - Manually verify titled and untitled list surfaces plus responsive behavior before final stop-gate execution.

8. Run required stop-gate validation before commit or handoff.
   - `pnpm exec nx run-many -t test --all`
   - `pnpm exec nx run-many -t coverage --all`

## Verification Plan

- Focused checks during implementation:
  - `pnpm --dir apps/frontend test -- tests/RecentUpdatesFeed.test.tsx tests/UnifiedDatasetRow.test.tsx tests/DatasetCatalogList.test.tsx tests/InfiniteCatalogList.test.tsx tests/source-list-page.test.tsx tests/source-detail-page.test.tsx tests/catalog-page.test.tsx tests/home-page.test.tsx`
  - `pnpm --dir apps/frontend typecheck`
  - `pnpm --dir apps/frontend exec biome check .`
- Manual verification in local runtime:
  - `docker compose down`
  - `docker compose up -d`
  - `pnpm --dir apps/frontend dev`
  - Visit `/`, `/datasets`, `/sources`, `/sources/fred`, and one topic/geography detail page to confirm titled and untitled list surfaces preserve hierarchy and behavior.
- Required final gates before commit/handoff:
  - `pre-commit run --all-files`
  - `pnpm exec nx run-many -t test --all`
  - `pnpm exec nx run-many -t coverage --all`

Post-design constitution re-check: PASS on all gates.

## Complexity Tracking

No constitution violations or exceptional complexity justifications are required for this plan.
