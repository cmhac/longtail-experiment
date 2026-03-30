# Quickstart: Unified Feed List Components

## Goal

Verify the shared discovery feed/list component group preserves current list behavior while replacing duplicated wrapper and row presentation.

## Prerequisites

- Dependencies installed with `pnpm install`
- Frontend dependencies current in `apps/frontend`
- Local stack available for manual browser verification

## Implementation Walkthrough

1. Create the shared feed/list component group under `apps/frontend/src/components/discovery`.
2. Move current repeated wrapper and row layout into the new shared primitives.
3. Refactor current dataset-row consumers to use the shared group.
4. Refactor current source-row consumers to use the same shared group.
5. Refactor titled and untitled list wrappers to use the shared outer container and optional title region.
6. Update existing tests to validate the new shared contract without losing current page-level coverage.

## Focused Development Checks

Run during implementation:

```bash
pnpm --dir apps/frontend exec biome check .
pnpm --dir apps/frontend typecheck
pnpm --dir apps/frontend test -- tests/RecentUpdatesFeed.test.tsx tests/UnifiedDatasetRow.test.tsx tests/DatasetCatalogList.test.tsx tests/InfiniteCatalogList.test.tsx tests/source-list-page.test.tsx tests/source-detail-page.test.tsx tests/catalog-page.test.tsx tests/home-page.test.tsx
```

## Manual Verification

Start from a clean local state:

```bash
docker compose down
docker compose up -d
pnpm --dir apps/frontend dev
```

Then verify:

1. `/` still shows a titled recent-updates surface with the expected heading, row ordering, and dataset links.
2. `/datasets` still shows the untitled catalog list surface and preserves infinite-scroll behavior.
3. `/sources` still shows the source catalog list with the correct left-rail metadata hierarchy.
4. `/sources/fred` still shows the embedded dataset list using the migrated shared row structure.
5. One topic detail page and one geography detail page still render their dataset lists correctly.
6. Narrow the viewport to mobile width and confirm the metadata rail and title/subtitle hierarchy remain readable.

## Final Required Gates

Before commit or handoff:

```bash
pre-commit run --all-files
pnpm exec nx run-many -t test --all
pnpm exec nx run-many -t coverage --all
```
