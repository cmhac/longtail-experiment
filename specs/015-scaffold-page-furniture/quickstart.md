# Quickstart: Frontend Page Furniture Baseline

## Objective

Validate that the frontend runs as a minimal shell baseline, renders all required furniture placeholders, and passes quality gates without adding product content.

## Prerequisites

- Repository dependencies installed (`pnpm install`).
- Feature branch `015-scaffold-page-furniture` checked out.
- Local environment prepared per onboarding docs.

## 1) Start the frontend development runtime

```bash
pnpm --dir apps/frontend dev
```

Expected:

- Development server starts successfully.
- Root route becomes reachable locally.
- No blocking runtime errors appear at startup.

## 2) Verify shell structure visually in browser

- Open the local root URL shown by the dev server.
- Confirm presence of these placeholders:
  - top navigation slot
  - secondary navigation slot
  - footer slot
  - scripts/analytics slot
  - ads/subscription slot
- Confirm the main content region is intentionally blank.

Expected:

- All five furniture placeholders are visible.
- No product/editorial content appears in the main region.

## 3) Run frontend quality checks

```bash
pnpm --dir apps/frontend lint
pnpm --dir apps/frontend exec biome check .
pnpm --dir apps/frontend typecheck
pnpm --dir apps/frontend test
pnpm --dir apps/frontend coverage
```

Expected:

- All frontend checks pass.
- Coverage remains at or above repository threshold for affected scope.

## 4) Run workspace affected checks

```bash
pnpm run affected:lint
pnpm run affected:format
pnpm run affected:typecheck
pnpm run affected:test
pnpm run affected:coverage
```

Expected:

- Affected commands pass without suppression/bypass changes.

## 5) Validate documentation alignment

- Confirm onboarding and runbook docs include the frontend startup and visual verification steps.
- Confirm instructions describe the shell as structure-only (no feature content).

## Acceptance Evidence Checklist

- Frontend startup succeeds locally and root route is reachable.
- Root shell renders all required furniture placeholders.
- Main content region remains empty.
- Frontend and affected quality gates pass.
- Documentation reflects startup and verification workflow.

## Execution Evidence (2026-03-22)

Validation commands executed:

- `pnpm --dir apps/frontend lint`
  - Result: passed
- `pnpm --dir apps/frontend typecheck`
  - Result: passed
- `pnpm --dir apps/frontend test`
  - Result: `7 passed`
- `pnpm --dir apps/frontend coverage`
  - Result: passed with 100% lines/statements/functions/branches
- `pnpm run affected:lint`
  - Result: passed
- `pnpm run affected:format`
  - Result: passed
- `pnpm run affected:typecheck`
  - Result: passed
- `pnpm run affected:test`
  - Result: passed
- `pnpm run affected:coverage`
  - Result: passed
