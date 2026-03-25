# Quickstart: Global Page Content Width

## Prerequisites

- Workspace dependencies installed.
- Frontend project runnable in local development mode.

## Implementation Validation Flow

1. Run focused frontend tests for shell/home/datasets layout behavior.
2. Run frontend static checks (typecheck and lint/format authority).
3. Manually verify home and datasets routes on wide desktop and narrow viewport sizes.
4. Run required monorepo stop gates before commit or handoff.

## Suggested Verification Commands

- Focused layout and shell checks:
  - pnpm --dir apps/frontend test -- tests/shell-structure-contract.test.tsx tests/home-page.test.tsx tests/catalog-page.test.tsx
- Frontend static quality checks:
  - pnpm --dir apps/frontend typecheck
  - pnpm --dir apps/frontend exec biome check .
- Mandatory monorepo stop gates:
  - pnpm exec nx run-many -t test --all
  - pnpm exec nx run-many -t coverage --all

## Manual Validation Checklist

- Open home route on a wide desktop viewport and confirm default page content is constrained and centered.
- Open datasets list route on a wide desktop viewport and confirm listing content is constrained and centered.
- Confirm intentionally full-width shell regions still render edge-to-edge.
- Re-check both routes on narrow/mobile viewport widths for readability and non-overlap.

## Completion Criteria

- Global constrained default applies consistently to shell page content.
- Explicit full-width exceptions render as intended.
- Home and datasets list routes meet contract expectations.
- All required automated checks and monorepo gates pass.

## Implementation Checklist Notes

- Shared constrained content policy introduced via a reusable shell content class.
- Home and datasets page main regions now explicitly opt into constrained default mode.
- Header and footer shell regions now explicitly declare full-width exception mode.
- Width-mode expectations are covered in shell and route-level test assertions.

## Validation Record

- Focused frontend checks passed:
  - `pnpm --dir apps/frontend test -- tests/shell-structure-contract.test.tsx tests/home-page.test.tsx tests/catalog-page.test.tsx`
  - `pnpm --dir apps/frontend typecheck`
  - `pnpm --dir apps/frontend exec biome check .`
- Mandatory monorepo stop gates passed:
  - `pnpm exec nx run-many -t test --all`
  - `pnpm exec nx run-many -t coverage --all`
- Manual visual verification completed:
  - `/` content remains centered and constrained on wide viewport, while header/footer remain full-width.
  - `/datasets` content remains centered and constrained on wide viewport, while header remains full-width.
  - Narrow viewport rendering remains readable with no clipping or overlap.
