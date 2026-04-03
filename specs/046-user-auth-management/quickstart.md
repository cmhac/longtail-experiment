# Quickstart: User Auth And Management

## Prerequisites

- Dependencies installed:
  - pnpm install
  - uv sync --project apps/backend --frozen
  - uv sync --project apps/pipeline --frozen
- Local secrets configured in docker/compose/local.secrets.env
- Docker daemon running

## 1. Start local stack from clean state

1. docker compose down
2. docker compose up -d db backend frontend
3. docker compose ps
4. Verify backend health at /api/health and frontend load on port 3000

## 2. Backend contract + persistence implementation loop

1. Add failing backend tests for:

- register/sign-in/sign-out flows
- session restoration checks
- lockout behavior
- deactivation + session revocation
- account settings and admin authorization boundaries

2. Add shared DB models/migrations and backend handlers/contracts.
3. Re-run backend checks:

- uv run --project apps/backend ruff check apps/backend
- uv run --project apps/backend ty check apps/backend
- uv run --project apps/backend pytest apps/backend/tests

## 3. Frontend authenticated workflow implementation loop

1. Add failing frontend tests for:

- sign-in and registration forms
- protected route redirects/guards
- account settings profile/password updates
- user session management UI
- admin user-management screens and authorization handling

2. Implement pages/components/api clients and route handlers.
3. Re-run frontend checks:

- pnpm --dir apps/frontend exec biome check .
- pnpm --dir apps/frontend typecheck
- pnpm --dir apps/frontend test

## 4. Manual runtime verification

1. Register a new account and sign in.
2. Open protected pages and confirm authenticated access.
3. Open account settings and:

- update profile
- change password
- revoke one active session while keeping another active

4. Trigger failed sign-ins until lockout threshold and confirm temporary lockout.
5. As admin, deactivate a user and verify all existing sessions are revoked immediately.
6. Submit account deletion request and verify immediate deactivation + deletion-pending behavior.

## 5. Mandatory full-suite quality gates

1. pre-commit run --all-files
2. pnpm exec nx run-many -t test --all
3. pnpm exec nx run-many -t coverage --all

All gates must pass before commit or handoff.
