# Tasks: In-App Trend Change Notifications (Full-Stack)

**Input**: Design documents from `/specs/048-trend-change-notifications/`
**Prerequisites**: plan.md (required), spec.md (required for user stories), research.md, data-model.md, contracts/

**Tests**: Test tasks are REQUIRED. Every user story and foundational component MUST include automated coverage sufficient to preserve >=90% thresholds in affected projects. Before any commit and before AI handoff/end, run `pnpm exec nx run-many -t test --all`. Before any commit, run `pnpm exec nx run-many -t coverage --all`.

**Organization**: Tasks are grouped by user story so each story remains independently implementable and testable.

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Align artifacts and verification paths across backend, pipeline, libs, and frontend.

- [ ] T001 Verify and cross-link feature artifacts in `/root/snap/longtail-experiment/specs/048-trend-change-notifications/plan.md`
- [ ] T002 Capture manual API + browser verification flow in `/root/snap/longtail-experiment/specs/048-trend-change-notifications/quickstart.md`
- [ ] T003 [P] Validate endpoint list and payload semantics in `/root/snap/longtail-experiment/specs/048-trend-change-notifications/contracts/trend-notifications.openapi.yaml`

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Introduce notification-domain persistence and shared contracts used by all stories.

**CRITICAL**: No user story implementation starts until this phase is complete.

- [ ] T004 Add notification-domain Alembic migration in `/root/snap/longtail-experiment/libs/db/alembic/versions/0015_trend_notifications.py`
- [ ] T005 Extend DB models and exports for event/subscription/notification entities in `/root/snap/longtail-experiment/libs/db/src/db/models/trends.py`
- [ ] T006 [P] Add repository interfaces for trend notifications and subscriptions in `/root/snap/longtail-experiment/libs/db/src/db/repositories/interfaces.py`
- [ ] T007 [P] Implement Postgres repository SQL for event idempotency, fan-out, and read/unread mutations in `/root/snap/longtail-experiment/libs/db/src/db/repositories/postgres_trend_repository.py`
- [ ] T008 [P] Add notification repository helper module in `/root/snap/longtail-experiment/libs/db/src/db/repositories/notification_repository.py`
- [ ] T009 Add migration and repository tests in `/root/snap/longtail-experiment/libs/db/tests/test_trend_notification_migration_contract.py`
- [ ] T010 [P] Add repository behavior tests in `/root/snap/longtail-experiment/libs/db/tests/test_notification_repository.py`

**Checkpoint**: Shared schema/repository contracts are implemented and test-covered.

---

## Phase 3: User Story 1 - Detect and Persist Reversal Events (Priority: P1) 🎯 MVP

**Goal**: Detect `up <-> down` canonical flips and persist idempotent trend-change events with processing context.

**Independent Test**: Process controlled canonical transitions and confirm one event per qualifying flip, no events for first-available/unchanged/unavailable, and no duplicates on retry.

### Tests for User Story 1 (REQUIRED)

- [ ] T011 [P] [US1] Add orchestration test for qualifying `up -> down` event creation in `/root/snap/longtail-experiment/apps/pipeline/tests/orchestration/test_trend_runtime_processor_notification_events.py`
- [ ] T012 [P] [US1] Add orchestration test for qualifying `down -> up` event creation in `/root/snap/longtail-experiment/apps/pipeline/tests/orchestration/test_trend_runtime_processor_notification_events.py`
- [ ] T013 [P] [US1] Add orchestration test for non-event cases in `/root/snap/longtail-experiment/apps/pipeline/tests/orchestration/test_trend_runtime_processor_notification_events.py`
- [ ] T014 [P] [US1] Add retry idempotency test for event dedupe in `/root/snap/longtail-experiment/apps/pipeline/tests/orchestration/test_trend_notification_service_idempotency.py`

### Implementation for User Story 1

- [ ] T015 [US1] Add trend notification service orchestration in `/root/snap/longtail-experiment/apps/pipeline/src/orchestration/jobs/trend_notification_service.py`
- [ ] T016 [US1] Integrate reversal detection into canonical persistence flow in `/root/snap/longtail-experiment/apps/pipeline/src/orchestration/jobs/trend_runtime_processor.py`
- [ ] T017 [US1] Tag events with processing context and visibility classification in `/root/snap/longtail-experiment/apps/pipeline/src/orchestration/jobs/trend_lifecycle_service.py`
- [ ] T018 [US1] Extend pipeline trend repository protocol for notification seams in `/root/snap/longtail-experiment/apps/pipeline/src/orchestration/resources/trend_repository.py`
- [ ] T019 [US1] Implement pipeline Postgres adapter calls for event write/read context in `/root/snap/longtail-experiment/apps/pipeline/src/orchestration/resources/postgres_trend_repository.py`

**Checkpoint**: US1 independently delivers deterministic reversal-event persistence.

---

## Phase 4: User Story 2 - Backend Notification and Subscription APIs (Priority: P2)

**Goal**: Expose authenticated APIs for list/summary/read-state/subscriptions with ownership constraints.

**Independent Test**: Generate user-visible reversal events and verify list, unread summary, mark-read/mark-unread/mark-all-read, and self-only subscription management.

### Tests for User Story 2 (REQUIRED)

- [ ] T020 [P] [US2] Add backend contract schema tests for notification payloads in `/root/snap/longtail-experiment/apps/backend/tests/contract/test_trend_notification_contract_schema.py`
- [ ] T021 [P] [US2] Add backend service tests for unread summary and pagination ordering in `/root/snap/longtail-experiment/apps/backend/tests/contract/test_trend_notification_service.py`
- [ ] T022 [P] [US2] Add HTTP endpoint tests for auth guards and self-only ownership in `/root/snap/longtail-experiment/apps/backend/tests/contract/test_http_trend_notification_endpoints.py`
- [ ] T023 [P] [US2] Add pipeline test for subscription-based fan-out eligibility in `/root/snap/longtail-experiment/apps/pipeline/tests/orchestration/test_trend_runtime_processor_notification_events.py`
- [ ] T024 [P] [US2] Add pipeline test for re-subscribe forward-only behavior in `/root/snap/longtail-experiment/apps/pipeline/tests/orchestration/test_trend_notification_service_idempotency.py`

### Implementation for User Story 2

- [ ] T025 [US2] Add backend notification contracts in `/root/snap/longtail-experiment/apps/backend/src/contract/query/trend_notification_query.py`
- [ ] T026 [US2] Implement backend persisted repository adapter in `/root/snap/longtail-experiment/apps/backend/src/query/trend_notification_persisted_repository.py`
- [ ] T027 [US2] Implement backend notification service in `/root/snap/longtail-experiment/apps/backend/src/query/trend_notification_service.py`
- [ ] T028 [US2] Register notification routes in `/root/snap/longtail-experiment/apps/backend/src/http_api_server.py`
- [ ] T029 [US2] Implement subscription list/create/delete repository methods in `/root/snap/longtail-experiment/libs/db/src/db/repositories/notification_repository.py`
- [ ] T030 [US2] Implement unread summary + read/unread mutation repository methods in `/root/snap/longtail-experiment/libs/db/src/db/repositories/notification_repository.py`

**Checkpoint**: US2 independently delivers backend contracts required by frontend notification UX.

---

## Phase 5: User Story 3 - Frontend Top-Nav Notifications and Management UX (Priority: P2)

**Goal**: Implement notification bell icon, dropdown recents, and full management UI with read/unread/clear-all flows.

**Independent Test**: With authenticated session and seeded notifications, verify shell badge/dropdown behavior and `/notifications` page actions update state consistently.

### Tests for User Story 3 (REQUIRED)

- [ ] T031 [P] [US3] Add navbar notification bell/dropdown interaction tests in `/root/snap/longtail-experiment/apps/frontend/tests/navbar-notifications.test.tsx`
- [ ] T032 [P] [US3] Add notifications management page tests in `/root/snap/longtail-experiment/apps/frontend/tests/notifications-page.test.tsx`
- [ ] T033 [P] [US3] Add frontend notification client tests for list/summary/read-state calls in `/root/snap/longtail-experiment/apps/frontend/tests/notification-client.test.ts`
- [ ] T034 [P] [US3] Extend shell structure contract test for notification control presence in `/root/snap/longtail-experiment/apps/frontend/tests/shell-structure-contract.test.tsx`

### Implementation for User Story 3 (maps to Spec Story 2)

- [ ] T035 [US3] Add notification API types in `/root/snap/longtail-experiment/apps/frontend/src/lib/api/notification-types.ts`
- [ ] T036 [US3] Add notification API client in `/root/snap/longtail-experiment/apps/frontend/src/lib/api/notification-client.ts`
- [ ] T037 [US3] Add frontend proxy route for notification list in `/root/snap/longtail-experiment/apps/frontend/src/app/api/notifications/route.ts`
- [ ] T038 [US3] Add frontend proxy route for unread summary in `/root/snap/longtail-experiment/apps/frontend/src/app/api/notifications/summary/route.ts`
- [ ] T039 [US3] Add frontend proxy route for mark-all-read in `/root/snap/longtail-experiment/apps/frontend/src/app/api/notifications/mark-all-read/route.ts`
- [ ] T040 [US3] Add frontend proxy route for mark-read in `/root/snap/longtail-experiment/apps/frontend/src/app/api/notifications/[notificationId]/mark-read/route.ts`
- [ ] T041 [US3] Add frontend proxy route for mark-unread in `/root/snap/longtail-experiment/apps/frontend/src/app/api/notifications/[notificationId]/mark-unread/route.ts`
- [ ] T042 [US3] Add frontend proxy route for subscriptions list/create in `/root/snap/longtail-experiment/apps/frontend/src/app/api/notifications/subscriptions/route.ts`
- [ ] T043 [US3] Add frontend proxy route for subscription delete in `/root/snap/longtail-experiment/apps/frontend/src/app/api/notifications/subscriptions/[datasetId]/route.ts`
- [ ] T044 [US3] Add shared notifications components in `/root/snap/longtail-experiment/apps/frontend/src/components/notifications/`
- [ ] T045 [US3] Integrate top-nav bell/unread badge/dropdown in `/root/snap/longtail-experiment/apps/frontend/src/shell/site-header.tsx`
- [ ] T046 [US3] Add full notifications page in `/root/snap/longtail-experiment/apps/frontend/src/app/notifications/page.tsx`

**Checkpoint**: US3 independently delivers authenticated shell/page notification UX.

---

## Phase 6: User Story 4 - Dataset Alert Subscription Controls in UI (Priority: P2)

**Goal**: Enable follow/unfollow alert controls in dataset-facing UI and subscription management list behavior.

**Independent Test**: Toggle follow/unfollow in dataset detail and verify backend subscription state changes and forward-only notification eligibility.

### Tests for User Story 4 (REQUIRED)

- [ ] T047 [P] [US4] Add dataset detail subscription control tests in `/root/snap/longtail-experiment/apps/frontend/tests/DatasetDetailHeader.notifications.test.tsx`
- [ ] T048 [P] [US4] Add notification subscription management UI tests in `/root/snap/longtail-experiment/apps/frontend/tests/notifications-page.test.tsx`
- [ ] T049 [P] [US4] Add new-user default-empty-subscriptions test in `/root/snap/longtail-experiment/apps/backend/tests/contract/test_trend_notification_service.py`

### Implementation for User Story 4 (maps to Spec Story 3)

- [ ] T050 [US4] Add reusable dataset subscription control in `/root/snap/longtail-experiment/apps/frontend/src/components/notifications/NotificationSubscriptionControl.tsx`
- [ ] T051 [US4] Integrate follow/unfollow alert action into dataset detail header in `/root/snap/longtail-experiment/apps/frontend/src/components/discovery/DatasetDetailHeader.tsx`
- [ ] T052 [US4] Add subscription-management section to notifications page in `/root/snap/longtail-experiment/apps/frontend/src/app/notifications/page.tsx`
- [ ] T053 [US4] Add unauthenticated guard handling for frontend subscription actions in `/root/snap/longtail-experiment/apps/frontend/src/lib/api/notification-client.ts`

**Checkpoint**: US4 independently delivers user-managed dataset alert subscriptions via UI.

---

## Phase 7: User Story 5 - Channel-Ready Auditability and Cross-Surface Consistency (Priority: P3)

**Goal**: Preserve channel-ready metadata and ensure support traceability plus cross-surface consistency between dropdown and page.

**Independent Test**: Verify delivery/process metadata visibility and consistency of unread totals after mixed dropdown/page interactions.

### Tests for User Story 5 (REQUIRED)

- [ ] T054 [P] [US5] Add repository tests for processing-context and visibility metadata persistence in `/root/snap/longtail-experiment/libs/db/tests/test_notification_repository.py`
- [ ] T055 [P] [US5] Add backend tests for metadata exposure in notification responses in `/root/snap/longtail-experiment/apps/backend/tests/contract/test_trend_notification_service.py`
- [ ] T056 [P] [US5] Add pipeline test for historical reprocessing audit-only suppression in `/root/snap/longtail-experiment/apps/pipeline/tests/orchestration/test_trend_runtime_processor_notification_events.py`
- [ ] T057 [P] [US5] Add frontend consistency test for dropdown/page unread reconciliation in `/root/snap/longtail-experiment/apps/frontend/tests/navbar-notifications.test.tsx`
- [ ] T058 [P] [US5] Add repository/service test asserting no age-based unread auto-expiry in `/root/snap/longtail-experiment/libs/db/tests/test_notification_repository.py`
- [ ] T059 [P] [US5] Add backend/frontend tests for deactivated-user access and delivery behavior in `/root/snap/longtail-experiment/apps/backend/tests/contract/test_http_trend_notification_endpoints.py`
- [ ] T060 [P] [US5] Add frontend tests for unauthenticated notification dropdown/page actions routing to sign-in in `/root/snap/longtail-experiment/apps/frontend/tests/navbar-notifications.test.tsx`

### Implementation for User Story 5

- [ ] T061 [US5] Add delivery/process metadata mapping in `/root/snap/longtail-experiment/libs/db/src/db/models/trends.py`
- [ ] T062 [US5] Ensure backend contracts expose required metadata in `/root/snap/longtail-experiment/apps/backend/src/contract/query/trend_notification_query.py`
- [ ] T063 [US5] Implement and verify 365-day retention policy handling in `/root/snap/longtail-experiment/libs/db/src/db/repositories/notification_repository.py`
- [ ] T064 [US5] Document traceability/replay guidance in `/root/snap/longtail-experiment/specs/048-trend-change-notifications/quickstart.md`

**Checkpoint**: US5 independently confirms auditable and channel-ready foundation with consistent UX state.

---

## Phase 8: Polish & Cross-Cutting Concerns

**Purpose**: Final hardening, documentation sync, and mandatory stop gates.

- [ ] T065 [P] Sync final design intent in `/root/snap/longtail-experiment/specs/048-trend-change-notifications/research.md`
- [ ] T066 [P] Verify plan/spec/data-model/contracts/quickstart/tasks consistency in `/root/snap/longtail-experiment/specs/048-trend-change-notifications/`
- [ ] T067 [P] Run focused libs/pipeline/backend/frontend suites for notification feature paths
- [ ] T068 Run mandatory pre-commit gate with `pre-commit run --all-files` from `/root/snap/longtail-experiment`
- [ ] T069 Run mandatory full-suite tests with `pnpm exec nx run-many -t test --all` from `/root/snap/longtail-experiment`
- [ ] T070 Run mandatory full-suite coverage with `pnpm exec nx run-many -t coverage --all` from `/root/snap/longtail-experiment`

---

## Dependencies & Execution Order

### Phase Dependencies

- Setup (Phase 1): no dependencies.
- Foundational (Phase 2): depends on Setup.
- US1-US2 (Phases 3-4): depend on Foundational completion.
- US3-US4 (Phases 5-6): depend on backend API seams from US2.
- US5 (Phase 7): depends on prior stories.
- Polish (Phase 8): depends on selected stories complete.

### User Story Dependencies

- **US1 (P1)**: starts after Phase 2; no dependency on other stories.
- **US2 (P2)**: starts after US1 event creation seams are ready.
- **US3 (P2)**: starts after US2 APIs are available.
- **US4 (P2)**: starts after US2 APIs and can run parallel with late US3 tasks.
- **US5 (P3)**: starts after US1-US4 are stable.

### Within Each User Story

- Write tests first and confirm failure.
- Implement minimal behavior to pass tests.
- Re-run story-scoped suites.
- Confirm independent acceptance before moving on.

### Parallel Opportunities

- Phase 2: T006-T008 parallel after T004-T005.
- US1 tests: T011-T014 parallel.
- US2 tests: T020-T024 parallel.
- US3 tests: T031-T034 parallel.
- US4 tests: T047-T049 parallel.
- US5 tests: T054-T060 parallel.

---

## Parallel Example: User Story 3

```bash
# Launch US3 tests in parallel:
Task: "Add navbar notifications interaction tests in apps/frontend/tests/navbar-notifications.test.tsx"
Task: "Add notifications page tests in apps/frontend/tests/notifications-page.test.tsx"
Task: "Add notification client tests in apps/frontend/tests/notification-client.test.ts"
```

---

## Implementation Strategy

### MVP First (US1 + US2)

1. Complete Phase 1 and Phase 2.
2. Deliver US1 reversal event persistence.
3. Deliver US2 backend notification/subscription APIs.
4. Validate API behavior before frontend integration.

### Incremental Delivery

1. Deliver shell and page UX in US3.
2. Deliver dataset subscription controls in US4.
3. Deliver auditability and cross-surface consistency in US5.
4. Execute Phase 8 mandatory gates.

### Parallel Team Strategy

1. One engineer handles libs/db + pipeline core.
2. One engineer handles backend API contracts/routes/tests.
3. One engineer handles frontend shell/page/subscription UI and tests.

---

## Notes

- Tasks follow required checklist format with explicit file paths.
- Scope is full-stack in this branch, including frontend implementation.
- Frontend must use HeroUI + Tailwind and shared components for repeated notification patterns.
- Re-subscribe remains forward-only and unread does not auto-expire by age.
- Historical reprocessing remains audit-only by default.
