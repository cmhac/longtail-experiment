# Quickstart: Unified Dataset List Item

## Purpose

Validate that homepage recent updates and datasets listing both render dataset entries through one shared visual row pattern while preserving existing page workflows.

## Prerequisites

- Monorepo dependencies installed.
- Frontend runtime available.
- Discovery API/runtime available for populated-state validation.

## 1. Start local runtime

1. Start backend/discovery runtime used by frontend pages.
2. Start frontend application.
3. Confirm `/` and `/datasets` routes load.

## 2. Validate shared row consistency

1. Open `/` and inspect the Recent Updates section.
2. Open `/datasets` and inspect listing entries.
3. Confirm source/date/title/summary/tag hierarchy matches between the two pages.

## 3. Validate page-specific behavior is preserved

1. On `/datasets`, change source/category/sort and confirm list updates still work.
2. Confirm empty-results behavior still appears when filters produce no matches.
3. On `/`, confirm recent updates fallback/empty behavior remains unchanged when data is unavailable.

## 4. Validate responsive readability

1. Check both pages at desktop width.
2. Check both pages at mobile width.
3. Confirm row content does not overlap or clip.

## 5. Focused automated checks

Suggested commands:

- `pnpm --dir apps/frontend test -- tests/RecentUpdatesFeed.test.tsx tests/datasets-page.test.tsx tests/catalog-page.test.tsx tests/home-page.test.tsx`
- `pnpm --dir apps/frontend typecheck`
- `pnpm --dir apps/frontend exec biome check .`

## 6. Required stop gates

1. `pnpm exec nx run-many -t test --all`
2. `pnpm exec nx run-many -t coverage --all`

## Completion Criteria

- Shared row hierarchy is visually consistent between home recent updates and datasets listing.
- Existing host-page behaviors (filters/sort/fallback/empty states) remain correct.
- Responsive readability is preserved.
- Full test and coverage stop gates pass.

## Implementation Checklist Notes

- Shared row component introduced and consumed by both homepage recent updates and datasets listing.
- Datasets listing now follows homepage editorial row hierarchy while keeping filter/sort controls unchanged.
- Host-specific interaction behaviors preserved:
  - Home recent updates keeps row-level link behavior.
  - Datasets listing keeps title-link behavior.

## Validation Record

- Focused frontend tests passed:
  - `pnpm --dir apps/frontend test -- tests/UnifiedDatasetRow.test.tsx tests/RecentUpdatesFeed.test.tsx tests/DatasetCard.test.tsx tests/DatasetCatalogList.test.tsx tests/catalog-page.test.tsx tests/datasets-page.test.tsx tests/shell-structure-contract.test.tsx tests/home-page.test.tsx`
- Frontend quality checks passed:
  - `pnpm --dir apps/frontend typecheck`
  - `pnpm --dir apps/frontend exec biome check .`
- Mandatory monorepo stop gates passed:
  - `pnpm exec nx run-many -t test --all`
  - `pnpm exec nx run-many -t coverage --all`
- Repository quality gate passed:
  - `pre-commit run --all-files`
- Manual visual verification completed with browser screenshots:
  - `/` recent updates section shows shared editorial row hierarchy.
  - `/datasets` listing shows matching row hierarchy with controls retained.
