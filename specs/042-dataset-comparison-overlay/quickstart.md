# Quickstart: Dataset Comparison Overlay

## Prerequisites

- Local dependencies installed (`pnpm install` and Python environments synced per repo baseline).
- Discovery API base URL configured for frontend runtime.
- Local stack available via Docker Compose when exercising backend-backed pages.

## Implementation Validation Workflow

### 1. Start from clean local state

- `docker compose down`
- `docker compose up -d`
- `docker compose ps`

### 2. Run automated checks during development

- `pnpm --dir apps/frontend test`
- `pnpm --dir apps/frontend typecheck`
- `pnpm --dir apps/frontend exec biome check .`

### 3. Manual browser verification

- Start frontend dev server:
  - `pnpm --dir apps/frontend dev`
- Validate detail-page selection actions:
  - Add dataset to comparison from detail page
  - Remove dataset from detail page
  - Confirm top-nav count updates immediately
- Validate cap behavior:
  - Attempt to add a 6th dataset and confirm rejection message with unchanged set
- Validate comparison page behavior:
  - Open from top-nav indicator
  - Confirm full-width chart
  - Confirm no metadata side rail
  - Confirm no observation table
  - Confirm `<2` selected state shows instructional prompt
- Validate compatibility behavior:
  - Mixed-unit set auto-switches to relative mode
  - Observed mode disabled with clear explanation while incompatible
- Validate relative baseline behavior:
  - Shared rolling offset applies to all series
  - Shared fixed baseline with fallback resolution is applied consistently
- Validate timeline behavior:
  - Union-of-dates timeline with gaps for missing values
- Validate state persistence:
  - Refresh and revisit preserve selection + chart settings
- Validate corrupted state behavior:
  - Inject invalid persisted payload, confirm comparison is blocked until manual reset

### 4. Mandatory stop-gate checks before commit/handoff

- `pre-commit run --all-files`
- `pnpm exec nx run-many -t test --all`
- `pnpm exec nx run-many -t coverage --all`

## Suggested Frontend Test Targets

- `apps/frontend/tests/detail-page.test.tsx`
- `apps/frontend/tests/ObservationsChart.test.tsx`
- `apps/frontend/tests/dataset-detail-view-model.test.ts`
- comparison-page specific tests to be added for selection and eligibility flows
