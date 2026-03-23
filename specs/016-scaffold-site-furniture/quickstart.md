# Quickstart: Minimal Site Furniture Shell

## Objective

Validate that the frontend renders a minimal real shell (header, main placeholder, footer), remains monochromatic, and follows device light/dark preference behavior.

## Prerequisites

- Repository dependencies installed (`pnpm install`).
- Feature branch `016-scaffold-site-furniture` checked out.
- Local environment prepared from onboarding documentation.

## 1) Start frontend runtime

```bash
pnpm --dir apps/frontend dev
```

Expected:

- Development server starts successfully.
- Root route is reachable locally.
- No runtime-blocking startup errors occur.

## 2) Verify shell structure in browser

- Open the local URL shown by the dev server.
- Confirm all required regions are visible:
  - `shell-header`
  - `shell-main-placeholder`
  - `shell-footer`
- Confirm region order remains header -> main -> footer.

Expected:

- All three regions are present and readable.
- Main region shows placeholder-only content.

## 3) Verify monochrome and theme preference behavior

- Confirm shell uses neutral monochromatic styling with no accent colors.
- Check behavior under light preference.
- Check behavior under dark preference.

Expected:

- No accent-colored shell elements appear.
- Shell stays readable in both light and dark preference modes.

Optional targeted assertions:

```bash
pnpm --dir apps/frontend test -- --run tests/shell-structure-contract.test.tsx
pnpm --dir apps/frontend test -- --run tests/shell-theme-preference.test.tsx
```

## 4) Run frontend quality checks

```bash
pnpm --dir apps/frontend lint
pnpm --dir apps/frontend exec biome check .
pnpm --dir apps/frontend typecheck
pnpm --dir apps/frontend test
pnpm --dir apps/frontend coverage
```

Expected:

- All checks pass for affected scope.
- Coverage remains at or above repository threshold.

## 5) Run workspace affected checks

```bash
pnpm run affected:lint
pnpm run affected:format
pnpm run affected:typecheck
pnpm run affected:test
pnpm run affected:coverage
```

Expected:

- Affected checks pass with no suppression or bypass changes.

## Acceptance Evidence Checklist

- Root shell shows header, main placeholder, and footer.
- Shell remains monochromatic with no accent-color violations.
- Device preference-aware light/dark behavior is observable.
- Frontend and affected quality gates pass.
- Documentation reflects verification workflow.
