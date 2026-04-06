# Implementation Plan: In-App Trend Change Notifications (Full-Stack)

**Branch**: `048-trend-change-notifications` | **Date**: 2026-04-05 | **Spec**: `/root/snap/longtail-experiment/specs/048-trend-change-notifications/spec.md`
**Input**: Feature specification from `/specs/048-trend-change-notifications/spec.md`

## Summary

Implement full-stack in-app trend-reversal notifications: pipeline detects canonical `up <-> down` flips and persists idempotent events; backend serves authenticated notification/subscription APIs; frontend adds top-nav notifications icon with unread badge, recent-notifications dropdown, full notification management UI (read/unread, clear-all unread), and dataset-level alert subscription controls. Event data remains channel-ready for future email/Slack without changing reversal semantics.

## Technical Context

**Language/Version**: Python 3.12 (libs, pipeline, backend), TypeScript 5.x + React 19 + Next.js 15 App Router (frontend)  
**Primary Dependencies**: SQLAlchemy 2.x, Alembic, Pydantic 2.x, Dagster runtime orchestration, HeroUI 3 (`@heroui/react`), Tailwind utilities, existing auth/session and discovery client contracts, pytest, Ruff, Ty, Vitest, Biome  
**Storage**: PostgreSQL 16 via `libs/db` migrations and shared model authority (`trend_canonical_descriptors`, auth tables, and new notification tables)  
**Testing**: `libs/db` migration + repository tests, `apps/pipeline` orchestration tests, `apps/backend` contract/service/http tests, `apps/frontend` Vitest + route/component tests, plus full monorepo stop gates (`pre-commit run --all-files`, `pnpm exec nx run-many -t test --all`, `pnpm exec nx run-many -t coverage --all`)  
**Target Platform**: Linux local development with unified Docker Compose services and browser-based frontend runtime  
**Project Type**: Nx monorepo full-stack web application vertical slice (libs + pipeline + backend + frontend)  
**Performance Goals**: 99% of eligible reversals create user-visible notification rows within 5 minutes; nav unread badge/dropdown interactions render without blocking shell navigation and converge to authoritative unread counts  
**Constraints**: No client-side trend-reversal inference; idempotent retry-safe event creation; historical reprocessing defaults to audit-only; recipient scope is explicit subscription only; unread does not auto-expire by age; frontend must use HeroUI + Tailwind and shared components for repeated patterns; coverage >=90% across affected projects  
**Scale/Scope**: All series processed through canonical trend persistence path; notification UI available in shared shell and dataset detail contexts for authenticated users

## Constitution Check

_GATE: Must pass before Phase 0 research. Re-check after Phase 1 design._

- Monorepo cohesion: PASS. Plan includes coherent vertical slice across `libs/db`, `apps/pipeline`, `apps/backend`, and `apps/frontend` with contract-aligned changes.
- Quality gate enforcement: PASS. Lint/format/typecheck/test gates are explicitly required for affected projects and full monorepo gates.
- Full-suite stop rule: PASS. Plan requires `pnpm exec nx run-many -t test --all` before commit and before handoff/stop.
- Coverage stop rule: PASS. Plan requires `pnpm exec nx run-many -t coverage --all` before commit with >=90% thresholds.
- Test and coverage discipline: PASS. Plan includes automated tests for migration, repositories, orchestration, backend contracts/routes, and frontend shell/components/pages.
- Local-first parity: PASS. End-to-end flow remains verifiable with unified Docker Compose + local frontend runtime.
- Data integrity and reliability: PASS. Reversal semantics remain deterministic from persisted canonical descriptors with DB-backed idempotency.
- Configuration integrity: PASS. No new external channel credentials in this branch; existing fail-fast env handling remains in force.
- Frontend UI consistency: PASS. Frontend work uses HeroUI/Tailwind and shared component extraction under `apps/frontend/src/components` for reusable patterns.
- Documentation fidelity: PASS. Plan includes research, data model, contracts, quickstart, and agent-context refresh.

## Project Structure

### Documentation (this feature)

```text
specs/048-trend-change-notifications/
|-- plan.md
|-- research.md
|-- data-model.md
|-- quickstart.md
|-- contracts/
|   `-- trend-notifications.openapi.yaml
`-- tasks.md
```

### Source Code (repository root)

```text
libs/db/
|-- alembic/versions/
|   `-- 0015_trend_notifications.py
|-- src/db/models/
|   `-- trends.py
|-- src/db/repositories/
|   |-- interfaces.py
|   |-- postgres_trend_repository.py
|   `-- notification_repository.py
`-- tests/
    |-- test_trend_notification_migration_contract.py
    `-- test_notification_repository.py

apps/pipeline/
|-- src/orchestration/jobs/
|   |-- trend_runtime_processor.py
|   |-- trend_lifecycle_service.py
|   `-- trend_notification_service.py
|-- src/orchestration/resources/
|   |-- trend_repository.py
|   `-- postgres_trend_repository.py
`-- tests/orchestration/
    |-- test_trend_runtime_processor_notification_events.py
    `-- test_trend_notification_service_idempotency.py

apps/backend/
|-- src/contract/query/
|   `-- trend_notification_query.py
|-- src/query/
|   |-- trend_notification_service.py
|   `-- trend_notification_persisted_repository.py
|-- src/http_api_server.py
`-- tests/contract/
    |-- test_trend_notification_contract_schema.py
    |-- test_trend_notification_service.py
    `-- test_http_trend_notification_endpoints.py

apps/frontend/
|-- src/shell/
|   `-- site-header.tsx
|-- src/components/
|   |-- notifications/
|   |   |-- NotificationBellMenu.tsx
|   |   |-- NotificationDropdownList.tsx
|   |   |-- NotificationListPanel.tsx
|   |   `-- NotificationSubscriptionControl.tsx
|   `-- discovery/
|       `-- DatasetDetailHeader.tsx
|-- src/app/
|   |-- notifications/page.tsx
|   `-- api/notifications/
|       |-- route.ts
|       |-- summary/route.ts
|       |-- mark-all-read/route.ts
|       |-- [notificationId]/mark-read/route.ts
|       |-- [notificationId]/mark-unread/route.ts
|       `-- subscriptions/
|           |-- route.ts
|           `-- [datasetId]/route.ts
|-- src/lib/api/
|   |-- notification-client.ts
|   `-- notification-types.ts
`-- tests/
    |-- navbar-notifications.test.tsx
    |-- notifications-page.test.tsx
    `-- DatasetDetailHeader.notifications.test.tsx
```

**Structure Decision**: Deliver as a full-stack vertical slice where pipeline emits durable reversal events, shared DB repositories enforce idempotent persistence and fan-out boundaries, backend serves authenticated notification/subscription contracts, and frontend integrates shell-level notification entry plus dedicated management and dataset-context subscription controls using shared HeroUI/Tailwind components.

## Phase Plan

### Phase 0: Research and Decision Locking

- Confirm deterministic reversal-detection seam in runtime canonical persistence path.
- Lock event idempotency and notification fan-out dedupe identity boundaries.
- Confirm frontend integration seams:
  - shell notifications control in `SiteHeader`
  - full management route in `app/notifications/page.tsx`
  - dataset subscription control in `DatasetDetailHeader`.
- Lock auth behavior for unauthenticated UI interactions (prompt sign-in; do not leak private data).
- Lock frontend component extraction strategy for reusable notification UI patterns under `apps/frontend/src/components`.
- Output: `research.md` with no unresolved clarifications.

### Phase 1: Design and Contracts

- Define notification-domain data model in `data-model.md` including frontend read-model requirements.
- Define backend API contracts in `contracts/trend-notifications.openapi.yaml` covering list/summary/read-state/subscriptions.
- Define runtime + API + UI verification flow in `quickstart.md`:
  - clean compose restart
  - backend/pipeline validation
  - frontend nav dropdown + notifications page + dataset subscription manual checks.
- Refresh agent context via `.specify/scripts/bash/update-agent-context.sh codex`.

### Phase 2: Implementation Planning

#### Workstream A: Shared DB schema and repository contracts (`libs/db`)

1. Add Alembic migration for notification-domain tables and constraints.
2. Extend ORM models and repository interfaces for event persistence, subscription state, fan-out, unread summary, and read/unread transitions.
3. Implement Postgres repository methods with deterministic ordering.
4. Add migration/repository tests including idempotency and forward-only re-subscribe behavior.

#### Workstream B: Pipeline reversal detection and event persistence (`apps/pipeline`)

1. Integrate reversal detection after canonical descriptor upsert.
2. Emit events only for `up <-> down` transitions; suppress non-event cases.
3. Classify historical reprocessing as audit-only by default.
4. Fan-out user-visible events to active subscriptions idempotently.
5. Add orchestration tests for flips, no-ops, idempotency, and historical suppression.

#### Workstream C: Backend authenticated notification APIs (`apps/backend`)

1. Add contracts, service, and repository adapters for notification list/summary/read-state/subscriptions.
2. Add authenticated routes:
   - `GET /api/notifications`
   - `GET /api/notifications/summary`
   - `POST /api/notifications/mark-all-read`
   - `POST /api/notifications/{notification_id}/mark-read`
   - `POST /api/notifications/{notification_id}/mark-unread`
   - `GET /api/notifications/subscriptions`
   - `POST /api/notifications/subscriptions`
   - `DELETE /api/notifications/subscriptions/{dataset_id}`.
3. Enforce self-only ownership and stable pagination.
4. Add backend contract/service/http tests.

#### Workstream D: Frontend shell notifications and management UX (`apps/frontend`)

1. Add typed notification API client and frontend proxy routes under `app/api/notifications/*` following existing auth proxy patterns, including:
   - `GET /api/notifications`
   - `GET /api/notifications/summary`
   - `POST /api/notifications/mark-all-read`
   - `POST /api/notifications/{notification_id}/mark-read`
   - `POST /api/notifications/{notification_id}/mark-unread`
   - `GET /api/notifications/subscriptions`
   - `POST /api/notifications/subscriptions`
   - `DELETE /api/notifications/subscriptions/{dataset_id}`.
2. Add top-nav notification bell in `SiteHeader` with unread badge and recent dropdown.
3. Add dropdown interactions:
   - recent newest-first list
   - mark-read/mark-unread
   - clear-all unread
   - deep link to `/notifications`.
4. Add full notifications management page (`/notifications`) with pagination/filter/read-state actions and resilient empty/loading/error UI.
5. Add dataset alert follow/unfollow controls in `DatasetDetailHeader` and a required subscription management panel on notifications page.
6. Enforce unauthenticated UX guardrails (sign-in prompts, no private payload rendering).
7. Extract repeated UI patterns to shared notification components in `apps/frontend/src/components/notifications`.
8. Add frontend tests for shell behavior, dropdown interactions, management page, and dataset subscription controls.

#### Workstream E: Operational traceability and documentation alignment

1. Ensure event-to-notification traceability remains queryable for support workflows.
2. Document historical replay behavior and audit-only visibility implications.
3. Ensure quickstart includes explicit manual browser checks and API verification.

## Execution Guidance (Mandatory)

- Use red/green TDD per workstream (DB/repositories -> pipeline -> backend -> frontend).
- Keep reversal semantics server-side and deterministic from persisted canonical descriptors.
- Enforce idempotency via database constraints, not in-memory guards alone.
- For frontend, use HeroUI and Tailwind only; extract repeated patterns into shared components.
- Validate end-to-end from clean compose runtime and real frontend interaction paths before final gates.
- Before commit or handoff, run:
  - `pre-commit run --all-files`
  - `pnpm exec nx run-many -t test --all`
  - `pnpm exec nx run-many -t coverage --all`

## Post-Design Constitution Re-Check

- Monorepo cohesion: PASS
- Quality gate enforcement: PASS
- Full-suite stop rule: PASS
- Coverage stop rule: PASS
- Test and coverage discipline: PASS
- Local-first parity: PASS
- Data integrity and reliability: PASS
- Configuration integrity: PASS
- Frontend UI consistency: PASS
- Documentation fidelity: PASS

## Complexity Tracking

No constitution violations requiring justification.
