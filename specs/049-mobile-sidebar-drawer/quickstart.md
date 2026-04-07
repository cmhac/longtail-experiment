# Quickstart: Mobile Sidebar Navigation Drawer

## Goal

Verify the mobile sidebar drawer behavior end-to-end in local development for signed-out, signed-in non-admin, and signed-in admin states.

## Prerequisites

- Dependencies installed for monorepo.
- Frontend app runnable locally.
- Ability to sign in with both non-admin and admin test accounts.

## 1) Run frontend locally

```bash
pnpm --dir apps/frontend dev
```

Open the app in a browser and test using phone and small-tablet viewport sizes.

## 2) Verify drawer open/close baseline

1. In activation range, confirm hamburger control is visible.
   - Activation threshold: viewport widths <=1024px.
2. Open drawer and confirm:
   - Right-side tray appears
   - Width is about 90% viewport
   - Background sliver remains visible and blurred
   - Background is not interactable
3. Close drawer and confirm normal page interaction resumes.
4. Resize above threshold (>1024px) and confirm the drawer trigger is unavailable.

## 3) Verify ordered rows and navigation behavior

1. Open drawer and confirm row order:
   - Header row (Longtail left, bell right)
   - Account
   - Comparison (+ counter)
   - Search
   - Home
   - Sources
   - Datasets
2. Tap each destination row and confirm:
   - Drawer closes immediately
   - Navigation lands on expected route

## 4) Verify role and auth behavior

### Signed-out

1. Open drawer.
2. Tap protected actions (e.g., Account).
3. Confirm redirect to `/login`.
4. Confirm Admin action is not visible.

### Signed-in non-admin

1. Sign in as non-admin and open drawer.
2. Confirm Admin action is not visible.
3. Confirm Sign out clears session and redirects to `/`.

### Signed-in admin/owner

1. Sign in as admin (or owner) and open drawer.
2. Confirm Admin action appears above Sign out.
3. Tap Admin and confirm navigation to `/admin`.

## 5) Verify utility consistency

1. Comparison count in drawer matches existing header comparison count semantics.
2. Bell icon interaction matches existing notification entry behavior.
3. Repeated open/close interactions do not produce duplicate or broken drawer state.

## 6) Run quality gates

During development:

```bash
pnpm --dir apps/frontend exec biome check .
pnpm --dir apps/frontend typecheck
pnpm --dir apps/frontend test
```

Required before handoff/commit:

```bash
pre-commit run --all-files
pnpm exec nx run-many -t test --all
pnpm exec nx run-many -t coverage --all
```
