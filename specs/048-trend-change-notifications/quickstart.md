# Quickstart: In-App Trend Change Notifications (Full-Stack)

## Prerequisites

- Workspace dependencies installed (`pnpm install`, `uv sync --project apps/backend --frozen`, `uv sync --project apps/pipeline --frozen`)
- Local secrets configured (`docker/compose/local.secrets.env`)
- Docker daemon running

## 1. Start from a clean runtime

1. `docker compose down`
2. `docker compose up -d`
3. `docker compose ps`

## 2. Database and repository foundation

1. Red: add failing migration/repository tests for notification schema and CRUD behaviors in `libs/db/tests`.
2. Green: add Alembic migration + ORM/repository implementations for:
   - reversal events
   - user dataset subscriptions
   - per-user in-app notifications
3. Run db-focused quality checks:
   - `uv run --project apps/backend pytest libs/db/tests/test_trend_notification_migration_contract.py libs/db/tests/test_notification_repository.py`

## 3. Pipeline reversal event generation

1. Red: add failing orchestration tests for reversal detection (`up <-> down`) and idempotency.
2. Green: integrate notification event emission into canonical descriptor persistence path.
3. Validate historical suppression behavior:
   - historical reprocessing writes audit records
   - historical reprocessing does not fan out unread user notifications by default
4. Run pipeline checks:
   - `uv run --project apps/pipeline ruff check apps/pipeline`
   - `uv run --project apps/pipeline ty check apps/pipeline`
   - `uv run --project apps/pipeline pytest apps/pipeline/tests/orchestration/test_trend_runtime_processor_notification_events.py apps/pipeline/tests/orchestration/test_trend_notification_service_idempotency.py`

## 4. Backend authenticated notification APIs

1. Red: add failing backend tests for notification list, unread summary, read actions, and subscription ownership rules.
2. Green: implement contracts, service/repository adapters, and authenticated HTTP endpoints.
3. Run backend checks:
   - `uv run --project apps/backend ruff check apps/backend`
   - `uv run --project apps/backend ty check apps/backend`
   - `uv run --project apps/backend pytest apps/backend/tests/contract/test_trend_notification_contract_schema.py apps/backend/tests/contract/test_trend_notification_service.py apps/backend/tests/contract/test_http_trend_notification_endpoints.py`

## 5. Frontend implementation validation

1. Red: add failing frontend tests for:
   - top-nav notification bell + unread badge
   - dropdown recent notifications interactions
   - `/notifications` management page states/actions
   - dataset-detail follow/unfollow alerts control
2. Green: implement shell notifications components, notifications page, dataset subscription controls, and notification API client/proxy routes.
3. Run frontend checks:
   - `pnpm --dir apps/frontend exec biome check .`
   - `pnpm --dir apps/frontend typecheck`
   - `pnpm --dir apps/frontend test`

## 6. Manual API and browser verification

1. Authenticate as test user and capture Bearer token.
2. Create subscription:
   - `curl -sS -X POST http://127.0.0.1:8090/api/notifications/subscriptions -H "Authorization: Bearer <TOKEN>" -H "Content-Type: application/json" -d '{"dataset_id":"<DATASET_ID>"}'`
3. Trigger/execute trend processing that causes one `up -> down` or `down -> up` canonical reversal.
4. Verify unread summary:
   - `curl -sS http://127.0.0.1:8090/api/notifications/summary -H "Authorization: Bearer <TOKEN>"`
5. Verify notification list pagination/order:
   - `curl -sS "http://127.0.0.1:8090/api/notifications?page_size=25" -H "Authorization: Bearer <TOKEN>"`
6. Mark one as read and verify count decrements:
   - `curl -sS -X POST http://127.0.0.1:8090/api/notifications/<NOTIFICATION_ID>/mark-read -H "Authorization: Bearer <TOKEN>"`
7. Mark one as unread and verify count increments:
   - `curl -sS -X POST http://127.0.0.1:8090/api/notifications/<NOTIFICATION_ID>/mark-unread -H "Authorization: Bearer <TOKEN>"`
8. Mark all read and verify unread count is zero:
   - `curl -sS -X POST http://127.0.0.1:8090/api/notifications/mark-all-read -H "Authorization: Bearer <TOKEN>"`

9. Run frontend and verify UI behavior:
   - `pnpm --dir apps/frontend dev`
   - Sign in with a test user
   - Confirm top nav shows notification bell and unread badge for authenticated session
   - Open bell dropdown and verify newest-first recent list + read/unread controls + clear-all
   - Open full notifications page and verify pagination/filter/actions
   - Open dataset detail page and verify follow/unfollow alert control updates state
   - Sign out and confirm notification/subscription actions route to sign-in without private data exposure

## 7. Mandatory full-suite stop gates

1. `pre-commit run --all-files`
2. `pnpm exec nx run-many -t test --all`
3. `pnpm exec nx run-many -t coverage --all`

All commands must pass before commit or handoff.

## 7. Runtime and operational notes

- Re-subscribe is forward-only: old events are not restored as unread.
- Unread notifications do not auto-expire by age.
- Historical reprocessing defaults to audit-only event visibility unless explicitly changed by policy.
- Frontend notifications UI uses shared shell/components; repeated patterns should be extracted under `apps/frontend/src/components/notifications`.
- Keep compose restart discipline for manual verification:
  1. `docker compose down`
  2. `docker compose up -d`
