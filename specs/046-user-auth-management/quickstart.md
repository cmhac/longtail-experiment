# Quickstart: User Auth And Management (Spec 046 Revision)

## Prerequisites

- Dependencies installed:
  - `pnpm install`
  - `uv sync --project apps/backend --frozen`
  - `uv sync --project apps/pipeline --frozen`
- Local secrets configured in `docker/compose/local.secrets.env`
- Docker daemon running

## 1. Start local stack from clean state

1. `docker compose down`
2. `docker compose up -d db backend frontend`
3. `docker compose ps`
4. Verify backend health and frontend startup

## 2. Backend + persistence implementation loop

1. Add/adjust failing backend tests for:
   - account details retrieval/update behavior
   - admin role grant/revoke behavior on admin users surface
   - owner-protected role-governance denial behavior
   - admin landing access authorization behavior
   - audit-event emissions for admin grant/revoke and owner-denied attempts
2. Add shared DB model/migration and backend contract/repository updates.
3. Re-run backend checks:
   - `uv run --project apps/backend ruff check apps/backend`
   - `uv run --project apps/backend ty check apps/backend`
   - `uv run --project apps/backend pytest apps/backend/tests`

## 3. Frontend implementation loop

1. Add/adjust failing frontend tests for:
   - Account action visibility and routing from top-nav profile dropdown
   - account details page rendering, sign-out action, email/password actions
   - admin chip visibility rules in dropdown and account page
   - admin navigation action visibility/routing from dropdown and account page
   - admin landing page content and admin-only access controls
   - admin users page admin grant/revoke controls and owner-denial messaging
   - shared page-header usage on account details, admin landing, and admin users page
2. Implement pages/components/client calls and route handlers.
3. Re-run frontend checks:
   - `pnpm --dir apps/frontend exec biome check .`
   - `pnpm --dir apps/frontend typecheck`
   - `pnpm --dir apps/frontend test`

## 4. Manual runtime verification

1. Sign in as standard user:
   - Open profile dropdown and confirm Account action exists.
   - Open account details page and confirm minimal user details and sign-out/email/password actions.
   - Confirm admin-only controls are not visible.
2. Sign in as admin user:
   - Confirm admin chip in dropdown and account page.
   - Confirm Admin action available in dropdown and account page.
   - Open admin landing and confirm admin-only destinations list includes user management.
3. On admin users page:
   - Grant admin role to eligible user and verify privilege effects.
   - Revoke admin role from eligible user and verify privilege effects.
   - Attempt role changes for owner account and verify deterministic denial + unchanged owner role.
4. Confirm shared page-header component treatment is visible on:
   - account details page
   - admin landing page
   - admin users page

## 5. Mandatory full-suite quality gates

1. `pre-commit run --all-files`
2. `pnpm exec nx run-many -t test --all`
3. `pnpm exec nx run-many -t coverage --all`

All gates must pass before commit or handoff.
