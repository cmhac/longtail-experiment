# Tasks: User Auth And Management

**Input**: Design documents from /specs/046-user-auth-management/
**Prerequisites**: plan.md, spec.md, research.md, data-model.md, contracts/user-auth-management.openapi.yaml

**Tests**: Test tasks are required. Every user story and foundational component includes automated test coverage.

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: [ID] [P?] [Story] Description

- [P] means task can run in parallel
- [Story] maps work to one user story
- Every task includes a concrete file path

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Align auth/account feature scaffolding and baseline tooling before foundational work.

- [x] T001 Create feature module index exports for new auth/account models in libs/db/src/db/models/**init**.py
- [x] T002 Create backend auth/account test package scaffolding in apps/backend/tests/contract/test_auth_contract.py
- [x] T003 [P] Create backend auth integration test scaffolding in apps/backend/tests/integration/test_auth_runtime_flows.py
- [x] T004 [P] Create frontend auth/account test scaffolding in apps/frontend/tests/auth-page.test.tsx
- [x] T005 [P] Create frontend admin-user-management test scaffolding in apps/frontend/tests/admin-users-page.test.tsx

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Shared identity/session persistence and backend enforcement foundations required by all user stories.

**Critical**: No user story tasks start until this phase is complete.

- [ ] T006 Add shared persistence entity definitions for UserAccount, CredentialRecord, AuthSession, RoleAssignment, and AccountAuditEvent in libs/db/src/db/models/auth_management.py
- [ ] T007 Add Alembic migration for auth/account/session/role/audit tables in libs/db/alembic/versions/0013_user_auth_management.py
- [ ] T008 [P] Add shared repository interface contracts for auth/account/session operations in libs/db/src/db/repositories/interfaces.py
- [ ] T009 [P] Implement shared Postgres auth/account repository adapter in libs/db/src/db/repositories/auth_management_repository.py
- [ ] T010 Wire shared repository exports in libs/db/src/db/repositories/**init**.py
- [ ] T011 Add backend auth/account contract models and error envelope types in apps/backend/src/contract/query/auth_management_query.py
- [ ] T012 [P] Add backend auth/account input validation helpers in apps/backend/src/query/auth_management_validators.py
- [ ] T013 Implement backend auth/account orchestration service in apps/backend/src/query/auth_management_service.py
- [ ] T014 [P] Implement backend persisted auth/account repository adapter in apps/backend/src/query/auth_management_persisted_repository.py
- [ ] T015 Extend backend HTTP server route dispatch and auth guard middleware behavior in apps/backend/src/http_api_server.py
- [ ] T016 Add backend foundational contract tests for schema and error envelopes in apps/backend/tests/contract/test_auth_management_contract_schema.py
- [ ] T017 Add backend foundational runtime tests for auth guards and lifecycle constraints in apps/backend/tests/contract/test_http_auth_runtime_guards.py
- [ ] T018 Add frontend shared auth/account API client types in apps/frontend/src/lib/api/auth-management-types.ts
- [ ] T019 [P] Add frontend shared auth/account API client functions in apps/frontend/src/lib/api/auth-management-client.ts
- [ ] T020 Add frontend shared auth state utilities for current session restoration in apps/frontend/src/lib/auth/session-state.ts

**Checkpoint**: Shared schema, contracts, guardrails, and clients exist for all stories.

---

## Phase 3: User Story 1 - Account Access Lifecycle (Priority: P1) MVP

**Goal**: Deliver registration, sign-in, sign-out, lockout, and protected-route session restoration behavior.

**Independent Test**: Register a new account, sign in, access protected page, refresh and remain signed in, sign out, then validate lockout after repeated failed sign-ins.

### Tests for User Story 1

- [ ] T021 [P] [US1] Add backend contract tests for register/login/logout endpoints in apps/backend/tests/contract/test_auth_endpoints_contract.py
- [ ] T022 [P] [US1] Add backend integration tests for multi-session creation and lockout enforcement in apps/backend/tests/integration/test_auth_session_and_lockout_flows.py
- [ ] T023 [P] [US1] Add frontend auth page interaction tests for register/login/logout flows in apps/frontend/tests/auth-page.test.tsx
- [ ] T024 [P] [US1] Add frontend protected-route restoration tests in apps/frontend/tests/protected-route-session-restore.test.tsx

### Implementation for User Story 1

- [ ] T025 [US1] Implement backend register/login/logout/session-list/session-revoke handlers in apps/backend/src/http_api_server.py
- [ ] T026 [US1] Implement lockout threshold and lockout-window policy logic in apps/backend/src/query/auth_management_service.py
- [ ] T027 [US1] Implement auth audit event writes for sign-in and sign-out lifecycle in apps/backend/src/query/auth_management_persisted_repository.py
- [ ] T028 [P] [US1] Create frontend sign-in and registration UI page in apps/frontend/src/app/login/page.tsx
- [ ] T029 [P] [US1] Create frontend registration route UI page in apps/frontend/src/app/register/page.tsx
- [ ] T030 [US1] Create frontend protected-route guard helper and redirect behavior in apps/frontend/src/lib/auth/route-guard.ts
- [ ] T031 [US1] Add header auth actions for signed-in versus signed-out states in apps/frontend/src/shell/site-header.tsx
- [ ] T032 [US1] Add frontend auth API route handlers for register/login/logout/session list/revoke in apps/frontend/src/app/api/auth/sessions/route.ts

**Checkpoint**: US1 is independently functional and testable.

---

## Phase 4: User Story 2 - Account Settings Management (Priority: P2)

**Goal**: Deliver account settings profile updates, password change, and user-driven session revocation.

**Independent Test**: Sign in, open account settings, update profile, change password, verify all sessions revoked, sign in again with new password, and revoke one active session.

### Tests for User Story 2

- [ ] T033 [P] [US2] Add backend contract tests for profile/password/deletion-request endpoints in apps/backend/tests/contract/test_account_settings_contract.py
- [ ] T034 [P] [US2] Add backend integration tests for password-change revocation and deletion-pending behavior in apps/backend/tests/integration/test_account_settings_runtime_flows.py
- [ ] T035 [P] [US2] Add frontend account settings page tests for profile/password/session management in apps/frontend/tests/account-settings-page.test.tsx

### Implementation for User Story 2

- [ ] T036 [US2] Implement backend account profile read/update and password change service methods in apps/backend/src/query/auth_management_service.py
- [ ] T037 [US2] Implement backend deletion-request lifecycle transition logic in apps/backend/src/query/auth_management_service.py
- [ ] T038 [US2] Implement backend password-change all-session revocation flow in apps/backend/src/query/auth_management_persisted_repository.py
- [ ] T039 [P] [US2] Create shared frontend account settings components with HeroUI in apps/frontend/src/components/account/AccountSettingsForm.tsx
- [ ] T040 [P] [US2] Create frontend account settings route page in apps/frontend/src/app/settings/page.tsx
- [ ] T041 [US2] Add frontend account settings API route handlers in apps/frontend/src/app/api/account/profile/route.ts
- [ ] T042 [US2] Add frontend password and deletion-request API route handlers in apps/frontend/src/app/api/account/password/route.ts

**Checkpoint**: US2 is independently functional and testable.

---

## Phase 5: User Story 3 - Administrative User Oversight (Priority: P3)

**Goal**: Deliver admin user listing, activation/deactivation controls, and admin-driven session revocation.

**Independent Test**: Sign in as admin, list users, deactivate user and verify immediate session revocation plus blocked re-login, reactivate user and verify login restored, verify non-admin denial.

### Tests for User Story 3

- [ ] T043 [P] [US3] Add backend contract tests for admin user list/status/session-revoke endpoints in apps/backend/tests/contract/test_admin_user_management_contract.py
- [ ] T044 [P] [US3] Add backend integration tests for deactivation/re-activation and final-active-admin guardrail in apps/backend/tests/integration/test_admin_user_management_runtime.py
- [ ] T045 [P] [US3] Add frontend admin user-management page and authorization tests in apps/frontend/tests/admin-users-page.test.tsx

### Implementation for User Story 3

- [ ] T046 [US3] Implement backend admin user list and status update service logic in apps/backend/src/query/auth_management_service.py
- [ ] T047 [US3] Implement backend admin-driven user session revocation and final-admin protection in apps/backend/src/query/auth_management_persisted_repository.py
- [ ] T048 [P] [US3] Create shared frontend admin user table components with HeroUI in apps/frontend/src/components/account/AdminUserTable.tsx
- [ ] T049 [P] [US3] Create frontend admin users route page in apps/frontend/src/app/admin/users/page.tsx
- [ ] T050 [US3] Add frontend admin API route handlers for user list/status/session revoke in apps/frontend/src/app/api/admin/users/route.ts

**Checkpoint**: US3 is independently functional and testable.

---

## Phase 6: Polish & Cross-Cutting Concerns

**Purpose**: Complete documentation, end-to-end verification, and repository-wide quality gates.

- [ ] T051 [P] Update feature runbook content for auth/account operational flows in docs/runbooks/local-stack-baseline.md
- [ ] T052 [P] Update AGENTS context and command references if auth/account workflow commands changed in AGENTS.md
- [ ] T053 Add frontend accessibility pass for auth/account/admin forms and error states in apps/frontend/src/components/account/AccountSettingsForm.tsx
- [ ] T054 Add backend observability and structured auth audit logging validation tests in apps/backend/tests/contract/test_auth_audit_observability.py
- [ ] T055 Execute full manual quickstart validation scenarios in specs/046-user-auth-management/quickstart.md
- [ ] T056 Run pre-commit all-files gate and resolve failures in .pre-commit-config.yaml
- [ ] T057 Run mandatory full monorepo tests gate in package.json
- [ ] T058 Run mandatory full monorepo coverage gate in package.json

---

## Dependencies & Execution Order

### Phase Dependencies

- Phase 1 depends on no prior work and starts immediately.
- Phase 2 depends on Phase 1 and blocks all user-story implementation.
- Phase 3 depends on Phase 2 and is the MVP slice.
- Phase 4 depends on Phase 2 and can proceed after US1 or in parallel once shared foundations are stable.
- Phase 5 depends on Phase 2 and can proceed after US1 or in parallel once shared foundations are stable.
- Phase 6 depends on completion of targeted user stories.

### User Story Dependencies

- US1 (P1) has no dependency on other user stories after foundational completion.
- US2 (P2) depends on shared auth/session foundations and can reuse US1 auth flow components.
- US3 (P3) depends on shared auth/session foundations and admin role/authorization enforcement.

### Within Each User Story

- Tests are created first and fail before implementation.
- Service and persistence logic precede route-handler wiring.
- Frontend pages are built on shared components and shared API clients.
- Story-level checkpoint validation is required before advancing.

## Parallel Execution Examples

### User Story 1

- Run in parallel:
  - T021 and T022 and T023 and T024
  - T028 and T029

### User Story 2

- Run in parallel:
  - T033 and T034 and T035
  - T039 and T040

### User Story 3

- Run in parallel:
  - T043 and T044 and T045
  - T048 and T049

## Implementation Strategy

### MVP First (US1)

1. Complete Phase 1 and Phase 2.
2. Deliver Phase 3 (US1) fully.
3. Validate US1 independent test criteria before expanding scope.

### Incremental Delivery

1. Ship US1 account access lifecycle.
2. Add US2 account settings and deletion-request flow.
3. Add US3 administrative oversight.
4. Finish with cross-cutting verification and docs updates.

### Parallel Team Strategy

1. Team completes Setup and Foundational phases together.
2. After foundations stabilize, split by story tracks:

- Engineer A: US1 flow hardening
- Engineer B: US2 settings and session tools
- Engineer C: US3 admin management

## Notes

- All tasks use strict checklist format with task ID and concrete file path.
- Story labels are included only in user-story phases.
- Parallel markers are used only where file-level independence is expected.
- Full-suite and coverage stop gates are mandatory before commit and before handoff.
