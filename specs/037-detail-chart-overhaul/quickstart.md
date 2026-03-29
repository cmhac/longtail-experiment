# Quickstart: Dataset Detail Chart Overhaul

## Prerequisites

- Workspace dependencies are installed.
- Frontend app runs locally.
- Discovery backend/detail API is available through the existing local environment.

## Implementation Validation Flow

1. Run focused frontend tests for chart rendering, range availability logic, and detail-page composition.
2. Run frontend static checks.
3. Manually validate the chart behavior on real dataset detail pages after restarting the local environment from a clean state.
4. Run mandatory monorepo stop gates before commit or handoff.

## Suggested Verification Commands

- Clean local restart before manual testing:
  - `docker compose down`
  - `docker compose up -d`
- Focused frontend tests:
  - `pnpm --dir apps/frontend test -- tests/ObservationsChart.test.tsx tests/detail-page.test.tsx tests/dataset-detail-view-model.test.ts`
- Frontend static quality checks:
  - `pnpm --dir apps/frontend typecheck`
  - `pnpm --dir apps/frontend exec biome check .`
- Frontend runtime:
  - `pnpm --dir apps/frontend dev`
- Mandatory monorepo stop gates:
  - `pnpm exec nx run-many -t test --all`
  - `pnpm exec nx run-many -t coverage --all`

## Manual Validation Checklist

- Open a valid dataset detail page with a long observation history and confirm the chart defaults to all-history.
- Confirm the visible range controls are ordered from longest to shortest and include `5Y` when enough history exists.
- Open a dataset with limited history and confirm unsupported ranges are hidden rather than disabled.
- Confirm the chart no longer shows a border, observation-count footnote, or point dots on the line.
- Confirm visible time-filter buttons show a pointer cursor for pointer-device users.
- Confirm the chart uses the full available trend-panel width and visually aligns downward with the adjacent metadata column.
- Confirm x-axis labels appear more separated and remain readable at desktop and mobile widths.
- Confirm datasets with no observations still show explicit empty-state messaging and no dead-end controls.
- Confirm existing generic error and not-found detail-page behavior remains unchanged.

## Completion Criteria

- Chart layout and controls satisfy the updated trend-panel contract.
- Range visibility and ordering remain deterministic across short, medium, and long dataset histories.
- Existing no-data, error, and not-found behaviors remain intact.
- Automated checks and mandatory monorepo stop gates pass.

## Validation Record

- Focused frontend tests passed:
  - `pnpm --dir apps/frontend test -- tests/ObservationsChart.test.tsx tests/detail-page.test.tsx tests/dataset-detail-view-model.test.ts`
- Frontend static checks passed:
  - `pnpm --dir apps/frontend typecheck`
  - `pnpm --dir apps/frontend exec biome check .`
- Mandatory monorepo stop gates passed:
  - `pnpm exec nx run-many -t test --all`
  - `pnpm exec nx run-many -t coverage --all`
- Repository-wide quality gate passed:
  - `pre-commit run --all-files`
- Manual validation completed after clean local restart:
  - Restarted the local stack with `docker compose down` and `docker compose up -d`.
  - Verified the live detail page at `/datasets/ENERGY.US.RETAIL_GASOLINE.SCO`.
  - Confirmed the chart defaults to `ALL`, shows `5Y`, `1Y`, `6M`, and `1M` in longest-to-shortest order, and the filter buttons expose pointer cursors.
  - Confirmed switching to `5Y` and `1M` updates both the charted date window and the insight-rail labels/values.
  - Confirmed the chart no longer shows the observation-count footnote and renders without point dots.
  - Confirmed the observed-values table and archive button still render correctly on the live page.
