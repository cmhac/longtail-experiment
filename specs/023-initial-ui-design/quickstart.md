# Quickstart: Initial UI Design Navbar Slice

## Purpose

Use this guide to implement and verify the initial navbar slice end-to-end for feature 023.

## Prerequisites

- Dependencies installed at repository root (`pnpm install`).
- Frontend workspace available (`apps/frontend`).
- Working tree on branch `023-initial-ui-design`.

## 1. Implement navbar slice in shell header

Update the shell header surface to render:

- Serif brand text: `Longtail`
- Tabs: Home, Datasets, Trends
- Utility icons: search (disabled), profile (enabled)
- Profile dropdown placeholder text: `dropdown coming soon`

Keep Home and brand navigation bound to homepage (`/`).

## 2. Apply style and theme behavior

- Ensure full-width navbar layout in header region.
- Preserve legibility for both light and dark modes.
- Confirm narrow viewport behavior keeps required controls visible and readable.

## 3. Add or update tests

Add/adjust frontend tests to assert:

- Required navbar structure and labels/icons.
- Disabled state and inert behavior for search/Datasets/Trends.
- Homepage navigation for brand and Home tab.
- Profile dropdown content and toggle behavior.

## 4. Run focused frontend checks

1. `pnpm --dir apps/frontend typecheck`
2. `pnpm --dir apps/frontend test -- tests/shell-structure-contract.test.tsx`
3. `pnpm --dir apps/frontend test -- tests/home-page.test.tsx tests/navbar-interactions.test.tsx tests/navbar-profile-dropdown.test.tsx tests/navbar-theme-mode.test.tsx`

## 5. Manual runtime verification

1. Start frontend dev server: `pnpm --dir apps/frontend dev`
2. Open home page and verify full-width navbar in light mode.
   - Confirm brand shows `Longtail` and links to `/`.
   - Confirm tabs show Home (active), Datasets (disabled), Trends (disabled).
   - Confirm right controls show search (disabled) and profile (enabled).
3. Switch to dark mode and re-verify readability.
4. Click disabled controls (search, Datasets, Trends) and confirm no navigation/action.
5. Click profile icon and verify dropdown text is exactly `dropdown coming soon`.
6. Resize to a narrow viewport and verify controls remain visible/readable.

## 6. Required stop-gate checks

Before commit or handoff, run:

1. `pnpm exec nx run-many -t test --all`
2. `pnpm exec nx run-many -t coverage --all`

## Completion Criteria

- Navbar renders with all required controls and states.
- Disabled controls are visible but inert.
- Brand/Home navigation returns to homepage.
- Profile dropdown placeholder appears correctly.
- Light/dark and narrow viewport checks pass.
- Monorepo test and coverage stop gates pass.
