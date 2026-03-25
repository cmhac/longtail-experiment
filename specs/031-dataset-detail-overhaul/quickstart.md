# Quickstart: Dataset Detail Page Overhaul

## Prerequisites

- Workspace dependencies are installed.
- Frontend app runs locally.
- Discovery backend/detail API is available through the existing local environment.

## Implementation Validation Flow

1. Run focused frontend tests for detail page composition, section rendering, and fallback behavior.
2. Run frontend static checks (typecheck and Biome).
3. Manually validate the redesigned detail page in desktop and mobile viewport sizes.
4. Run required monorepo stop gates before commit or handoff.

## Suggested Verification Commands

- Focused frontend tests:
  - pnpm --dir apps/frontend test -- tests/detail-page.test.tsx tests/DatasetDetailHeader.test.tsx tests/ObservationsChart.test.tsx tests/ObservationsTable.test.tsx tests/not-found-page.test.tsx
- Frontend static quality checks:
  - pnpm --dir apps/frontend typecheck
  - pnpm --dir apps/frontend exec biome check .
- Mandatory monorepo stop gates:
  - pnpm exec nx run-many -t test --all
  - pnpm exec nx run-many -t coverage --all

## Manual Validation Checklist

- Open a valid dataset detail page and confirm hero source/title hierarchy plus visible utility actions.
- Confirm latest observation summary and comparative metric cards render with real dataset values.
- Switch trend time ranges and verify chart updates while preserving readable axis/inspection behavior.
- Confirm observed-values table renders date, value, and directional change/status semantics.
- Verify archive/load-more affordance appears only when additional rows exist and expands correctly.
- Verify no-data dataset behavior shows explicit empty messaging while preserving metadata context.
- Verify backend-failure behavior shows explicit error state while preserving shell navigation.
- Verify invalid dataset id still produces the expected not-found experience.
- Validate layout readability and action usability at desktop and narrow/mobile viewport widths.

## Completion Criteria

- Overhauled detail page sections (hero, insights, trend, observed values) are all present and usable.
- Directional movement semantics are consistent between summary and table rows.
- Existing not-found and error-state behavior remain intact.
- Responsive behavior is stable across target viewport sizes.
- All required automated checks and monorepo stop gates pass.

## Validation Record

- Focused detail suites passed:
  - `pnpm --dir apps/frontend test -- tests/detail-page.test.tsx tests/DatasetDetailHeader.test.tsx tests/ObservationsChart.test.tsx tests/ObservationsTable.test.tsx tests/dataset-detail-view-model.test.ts`
- Runtime regression check after manual discovery/fix:
  - `pnpm --dir apps/frontend test -- tests/detail-page.test.tsx tests/ObservationsTable.test.tsx`
- Static checks passed:
  - `pnpm --dir apps/frontend typecheck`
  - `pnpm --dir apps/frontend exec biome check .`
- Monorepo stop gates passed:
  - `pnpm exec nx run-many -t test --all`
  - `pnpm exec nx run-many -t coverage --all`
- Manual browser validation (clean restart, desktop + mobile):
  - Restarted frontend in a clean state and validated the live page at `/datasets/ENERGY.US.RETAIL_GASOLINE.SCO`.
  - Confirmed hero/source/title, utility actions, insights, metadata panel, trend controls, and observed-values table render.
  - Confirmed `ALL` range updates chart coverage to full history and `LOAD ARCHIVE` expands observed rows.
  - Confirmed mobile viewport (390x844) retains readable section layout and visible utility actions.
  - During manual testing, detected and fixed a server-render runtime bug by marking `ObservationsTable` as a client component.
- AGENTS impact check:
  - `AGENTS.md` already contains feature-031 stack context; no additional structural updates required.
