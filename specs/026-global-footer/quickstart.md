# Quickstart: Global Footer Component

## Purpose

Validate the new global footer experience at the bottom of all shell-rendered pages.

## Prerequisites

- Frontend dependencies installed.
- Frontend app can be started locally.

## Implementation Rollout Checklist

1. Confirm shell integration points remain `SiteHeader -> main -> SiteFooter` in `apps/frontend/src/app/page.tsx`.
2. Keep `data-shell-region="footer"` and `data-testid="shell-footer"` stable in `apps/frontend/src/shell/site-footer.tsx`.
3. Keep shell region metadata in sync with tests through `apps/frontend/src/shell/shell-regions.ts`.

## 1. Start local frontend runtime

1. Start the frontend development runtime.
2. Open the home page and one additional shell-rendered route.

## 2. Validate core footer rendering

1. Scroll to page bottom.
2. Confirm footer appears after main content.
3. Confirm footer includes:
   - Longtail brand text
   - Mission statement paragraph

## 3. Validate screenshot-inspired presentation

1. Confirm editorial hierarchy: brand text has stronger emphasis than body copy.
2. Confirm footer spans full width while content remains in a readable padded block.
3. Confirm layout appears minimal and uncluttered (no unexpected dense utility sections).

## 4. Validate responsive and theme behavior

1. Validate readability in light mode.
2. Validate readability in dark mode.
3. Validate mobile viewport wrapping without clipping or overlap at <= 720px width.
4. Confirm brand and mission text remain visible in both success and global error page states.

## 5. Automated checks

Suggested focused commands:

- `pnpm --dir apps/frontend test -- tests/shell-structure-contract.test.tsx tests/home-page.test.tsx`
- `pnpm --dir apps/frontend lint`
- `pnpm --dir apps/frontend typecheck`

Mandatory stop gates before commit:

- `pnpm exec nx run-many -t test --all`
- `pnpm exec nx run-many -t coverage --all`

## Command Outcomes

- Focused frontend tests:
   - `pnpm --dir apps/frontend test -- tests/home-page.test.tsx tests/shell-structure-contract.test.tsx tests/startup-smoke.test.tsx` -> PASS
- Full monorepo test suite:
   - `pnpm exec nx run-many -t test --all` -> PASS
- Full monorepo coverage:
   - `pnpm exec nx run-many -t coverage --all` -> PASS
- Pre-commit all files:
   - `pre-commit run --all-files` -> PASS
