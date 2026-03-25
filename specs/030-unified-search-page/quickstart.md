# Quickstart: Unified Search Page Experience

## Prerequisites

- Workspace dependencies installed.
- Frontend project runnable locally.
- Discovery backend available through existing local runtime configuration.

## Implementation Validation Flow

1. Run focused frontend tests for homepage search behavior, dedicated search page behavior, and navbar search control behavior.
2. Run frontend static checks (typecheck and Biome).
3. Manually validate route-based search flows from homepage and navbar, including refinement on dedicated search page.
4. Run required monorepo stop gates before commit or handoff.

## Suggested Verification Commands

- Focused frontend tests:
  - pnpm --dir apps/frontend test -- tests/home-page.test.tsx tests/shell-structure-contract.test.tsx
- Frontend static quality checks:
  - pnpm --dir apps/frontend typecheck
  - pnpm --dir apps/frontend exec biome check .
- Mandatory monorepo stop gates:
  - pnpm exec nx run-many -t test --all
  - pnpm exec nx run-many -t coverage --all

## Manual Validation Checklist

- From homepage, submit a valid query and confirm navigation to the dedicated search route.
- On dedicated search route, confirm centered search surface remains visible and editable above results.
- Refine query on dedicated route and confirm results refresh with same layout structure.
- Activate navbar compact search, confirm expansion, submit valid query, and confirm dedicated-route navigation.
- Verify empty-query submission is ignored and does not trigger navigation.
- Simulate no-results and error states and confirm fallback messaging preserves editable input.
- Validate desktop and narrow viewport behavior for readability and non-overlap of navbar/search controls.

## Completion Criteria

- Unified search behavior is consistent across homepage and navbar entry points.
- Dedicated search route is the canonical destination for search execution and refinement.
- Existing search summary and relevance behavior remain intact.
- Responsive and failure-state behavior remains usable.
- All required automated checks and monorepo gates pass.

## Implementation Checklist Notes

- Homepage search now acts as an entry surface only and routes submissions to `/search`.
- Dedicated `/search` page now owns query execution, refinement, and result/idle/error rendering states.
- Navbar search control now expands into an input-ready surface and submits through the same route-based behavior contract.
- Existing suggestion fetching, search summary text behavior, and result hierarchy are preserved.

## Validation Record

- Focused unified-search regression tests passed:
  - `pnpm --dir apps/frontend test -- tests/home-page.test.tsx tests/search-page.test.tsx tests/search-surface-contract.test.tsx tests/navbar-interactions.test.tsx tests/navbar-profile-dropdown.test.tsx tests/shell-structure-contract.test.tsx tests/DatasetSearchBox.test.tsx tests/DatasetSearchBox.interaction.test.tsx`
- Full frontend suite passed:
  - `pnpm --dir apps/frontend test`
- Frontend static checks passed:
  - `pnpm --dir apps/frontend typecheck`
  - `pnpm --dir apps/frontend exec biome check .`
- Mandatory monorepo stop gates passed:
  - `pnpm exec nx run-many -t test --all`
  - `pnpm exec nx run-many -t coverage --all`
  - `pre-commit run --all-files`
- Manual browser validation completed after clean environment restart (`docker compose down && docker compose up -d`):
  - Homepage query submission routed from `/` to `/search?q=inflation`.
  - Dedicated search page kept search input visible and editable above result state.
  - Navbar search control expanded, accepted query input, and routed to `/search?q=cpi`.
  - Expanded navbar search collapsed after submit and shell navigation remained usable.
