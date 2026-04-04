# Tasks: User Auth And Management

**Input**: Design documents from `/specs/046-user-auth-management/`  
**Prerequisites**: plan.md, spec.md, research.md, data-model.md, contracts/user-auth-management.openapi.yaml

**Tests**: Test tasks are REQUIRED. Every user story and foundational component includes automated test coverage sufficient to maintain >= 90% coverage in affected projects.

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Align in-flight Spec 046 scaffolding with revised account/admin UX and role-governance scope.

- [ ] T001 Refresh spec revision references and artifact cross-links in `specs/046-user-auth-management/spec.md`
- [ ] T002 Refresh planning baseline metadata for revised scope in `specs/046-user-auth-management/plan.md`
- [ ] T003 [P] Refresh design decisions for admin landing and owner immutability in `specs/046-user-auth-management/research.md`
- [ ] T004 [P] Refresh revised entity definitions for privilege-level and admin navigation in `specs/046-user-auth-management/data-model.md`
- [ ] T005 [P] Refresh quickstart manual verification checklist for account/admin UX deltas in `specs/046-user-auth-management/quickstart.md`

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Shared contract and persistence foundations required before story-specific implementation begins.

**Critical**: No user story work starts until this phase is complete.

- [X] T006 Extend auth management DB model for `privilege_level` and owner-protection metadata in `libs/db/src/db/models/auth_management.py`
- [X] T007 Add Alembic migration for privilege-level and owner governance schema changes in `libs/db/alembic/versions/0014_owner_privilege_governance.py`
- [X] T008 [P] Extend shared repository interfaces for admin role grant/revoke and owner-protected conflict semantics in `libs/db/src/db/repositories/interfaces.py`
- [X] T009 [P] Implement shared repository support for admin role grant/revoke and owner immutability checks in `libs/db/src/db/repositories/auth_management_repository.py`
- [X] T010 Extend backend auth contract schemas with privilege-level and admin navigation fields in `apps/backend/src/contract/query/auth_management_query.py`
- [X] T011 [P] Extend backend validators for role-governance actions and owner-targeted conflict handling in `apps/backend/src/query/auth_management_validators.py`
- [X] T012 Implement backend service-layer owner-protection and admin navigation orchestration in `apps/backend/src/query/auth_management_service.py`
- [X] T013 [P] Extend backend persisted adapter audit writes for admin grant/revoke and owner-denied attempts in `apps/backend/src/query/auth_management_persisted_repository.py`
- [X] T014 Wire new backend endpoints for account navigation, admin navigation, and role updates in `apps/backend/src/http_api_server.py`
- [X] T015 [P] Extend frontend auth-management API types with privilege and navigation contracts in `apps/frontend/src/lib/api/auth-management-types.ts`
- [X] T016 [P] Extend frontend auth-management API client functions for account/admin navigation and role updates in `apps/frontend/src/lib/api/auth-management-client.ts`
- [X] T017 Add foundational backend contract tests for new navigation/role contract envelopes in `apps/backend/tests/contract/test_auth_management_contract_schema.py`
- [X] T018 Add foundational backend runtime guard tests for owner-protected role actions in `apps/backend/tests/contract/test_http_auth_runtime_guards.py`

**Checkpoint**: Shared schema/contracts/clients support privilege-level and revised admin/account surfaces.

---

## Phase 3: User Story 1 - Account Access Lifecycle (Priority: P1) 🎯 MVP

**Goal**: Preserve and harden registration/sign-in/sign-out/session restoration/lockout behavior under revised privilege-level foundations.

**Independent Test**: Register account, sign in, access protected route, refresh to restore session, sign out, and confirm lockout policy still enforced after repeated failures.

### Tests for User Story 1 (REQUIRED)

- [ ] T019 [P] [US1] Extend backend endpoint contract tests for auth lifecycle responses with privilege-level fields in `apps/backend/tests/contract/test_auth_endpoints_contract.py`
- [ ] T020 [P] [US1] Extend backend integration tests for lockout/session restoration under revised schema in `apps/backend/tests/integration/test_auth_session_and_lockout_flows.py`
- [ ] T021 [P] [US1] Extend frontend auth page tests for unchanged lifecycle UX under revised payloads in `apps/frontend/tests/auth-page.test.tsx`
- [ ] T022 [P] [US1] Extend frontend protected-route session restoration tests for revised auth state shape in `apps/frontend/tests/protected-route-session-restore.test.tsx`

### Implementation for User Story 1

- [ ] T023 [US1] Update backend auth handlers to emit revised user summary fields in `apps/backend/src/http_api_server.py`
- [ ] T024 [US1] Update backend auth orchestration to maintain lockout/session guarantees with privilege-level model in `apps/backend/src/query/auth_management_service.py`
- [ ] T025 [US1] Update frontend auth state deserialization for revised user summary payloads in `apps/frontend/src/lib/auth/session-state.ts`
- [ ] T026 [US1] Update frontend auth API proxy handlers for revised auth response contracts in `apps/frontend/src/app/api/auth/sessions/route.ts`
- [ ] T027 [US1] Verify US1 coverage contribution remains >= 90% for affected projects via targeted tests in `apps/backend/tests/integration/test_auth_session_and_lockout_flows.py`

**Checkpoint**: US1 remains independently functional and testable.

---

## Phase 4: User Story 2 - Account Hub And Self-Service Management (Priority: P2)

**Goal**: Add account-dropdown Account entry, account details page actions, and role-chip display for account surfaces.

**Independent Test**: Signed-in user opens dropdown, uses Account action, views account details with role indicator context, updates email/password, and signs out from account page.

### Tests for User Story 2 (REQUIRED)

- [X] T028 [P] [US2] Add backend contract tests for account profile + account navigation endpoints in `apps/backend/tests/contract/test_account_settings_contract.py`
- [ ] T029 [P] [US2] Add backend integration tests for account self-service updates with revised profile fields in `apps/backend/tests/integration/test_account_settings_runtime_flows.py`
- [X] T030 [P] [US2] Add frontend dropdown interaction tests for Account action visibility/routing in `apps/frontend/tests/navbar-profile-dropdown.test.tsx`
- [X] T031 [P] [US2] Add frontend account settings page tests for role chip and sign-out action from account page in `apps/frontend/tests/account-settings-page.test.tsx`

### Implementation for User Story 2

- [X] T032 [US2] Implement backend account navigation endpoint composition in `apps/backend/src/query/auth_management_service.py`
- [X] T033 [US2] Wire backend account navigation route in `apps/backend/src/http_api_server.py`
- [X] T034 [P] [US2] Add Account action + role-chip display behavior in top-nav profile dropdown in `apps/frontend/src/shell/site-header.tsx`
- [X] T035 [P] [US2] Extend account details component for minimal details, role chip, and sign-out action in `apps/frontend/src/components/account/AccountSettingsForm.tsx`
- [X] T036 [US2] Update account settings page composition to use shared page header and revised account actions in `apps/frontend/src/app/settings/page.tsx`
- [X] T037 [US2] Wire frontend account navigation proxy route in `apps/frontend/src/app/api/account/navigation/route.ts`
- [ ] T038 [US2] Verify US2 coverage contribution remains >= 90% for affected frontend/backend projects via updated tests in `apps/frontend/tests/account-settings-page.test.tsx`

**Checkpoint**: US2 is independently functional and testable.

---

## Phase 5: User Story 3 - Admin Landing And Role Governance (Priority: P3)

**Goal**: Add admin landing page and admin navigation surfaces, grant/revoke admin controls, and enforce owner-role immutability.

**Independent Test**: Admin sees Admin entry in dropdown/account page, reaches admin landing with users link, grants/revokes admin for eligible users, and receives deterministic denial for owner-targeted role changes.

### Tests for User Story 3 (REQUIRED)

- [X] T039 [P] [US3] Add backend contract tests for admin navigation and admin role-update endpoints in `apps/backend/tests/contract/test_admin_user_management_contract.py`
- [X] T040 [P] [US3] Add backend integration tests for admin grant/revoke and owner-denied role actions in `apps/backend/tests/integration/test_admin_user_management_runtime.py`
- [X] T041 [P] [US3] Add frontend admin landing page tests for admin-only navigation listing in `apps/frontend/tests/admin-page.test.tsx`
- [X] T042 [P] [US3] Extend frontend admin users page tests for admin grant/revoke and owner-denial behavior in `apps/frontend/tests/admin-users-page.test.tsx`
- [X] T043 [P] [US3] Add frontend account page tests for Admin action visibility by role in `apps/frontend/tests/account-settings-page.test.tsx`

### Implementation for User Story 3

- [X] T044 [US3] Implement backend admin navigation service and authorization checks in `apps/backend/src/query/auth_management_service.py`
- [X] T045 [US3] Implement backend admin role update flow with owner-protection conflicts in `apps/backend/src/query/auth_management_persisted_repository.py`
- [X] T046 [US3] Wire backend admin navigation and role update routes in `apps/backend/src/http_api_server.py`
- [X] T047 [P] [US3] Extend admin users table UI with grant/revoke admin controls and owner-state rendering in `apps/frontend/src/components/account/AdminUserTable.tsx`
- [X] T048 [P] [US3] Create admin landing page route using shared page-header component in `apps/frontend/src/app/admin/page.tsx`
- [X] T049 [US3] Extend admin users page composition for shared page-header consistency in `apps/frontend/src/app/admin/users/page.tsx`
- [X] T050 [US3] Add Admin navigation action on account details page with role-based visibility in `apps/frontend/src/components/account/AccountSettingsForm.tsx`
- [X] T051 [US3] Add frontend API route handlers for admin navigation and role updates in `apps/frontend/src/app/api/admin/navigation/route.ts`
- [X] T052 [US3] Extend frontend admin users API proxy for role update action in `apps/frontend/src/app/api/admin/users/route.ts`
- [ ] T053 [US3] Verify US3 coverage contribution remains >= 90% for affected frontend/backend projects via updated tests in `apps/backend/tests/integration/test_admin_user_management_runtime.py`

**Checkpoint**: US3 is independently functional and testable.

---

## Final Phase: Polish & Cross-Cutting Concerns

**Purpose**: Documentation, runtime validation, and monorepo stop gates across all stories.

- [ ] T054 [P] Update spec checklist notes for revised task-plan alignment in `specs/046-user-auth-management/checklists/requirements.md`
- [ ] T055 [P] Update API contract revision notes for admin landing and role governance in `specs/046-user-auth-management/contracts/user-auth-management.openapi.yaml`
- [ ] T056 [P] Update AGENTS references if plan-driven workflow or command expectations changed in `AGENTS.md`
- [ ] T057 Run manual quickstart verification for account/admin pages and owner-role guardrails in `specs/046-user-auth-management/quickstart.md`
- [ ] T058 Run pre-commit all-files validation and resolve issues via `.pre-commit-config.yaml`
- [ ] T059 Run mandatory full monorepo test stop gate via `pnpm exec nx run-many -t test --all` from `package.json`
- [ ] T060 Run mandatory full monorepo coverage stop gate via `pnpm exec nx run-many -t coverage --all` from `package.json`

---

## Dependencies & Execution Order

### Phase Dependencies

- Phase 1 (Setup): No dependencies.
- Phase 2 (Foundational): Depends on Phase 1 completion; blocks all user stories.
- Phase 3 (US1): Depends on Phase 2 completion.
- Phase 4 (US2): Depends on Phase 2 completion; may proceed after US1 MVP checkpoint.
- Phase 5 (US3): Depends on Phase 2 completion; may proceed after US1 MVP checkpoint.
- Final Phase: Depends on completion of desired story phases.

### User Story Dependencies

- US1 (P1): Independent after foundational phase.
- US2 (P2): Independent after foundational phase, reuses auth/session primitives from US1.
- US3 (P3): Independent after foundational phase, reuses auth/session primitives and extends admin surfaces.

### Within Each User Story

- Tests first (must fail before implementation).
- Backend contract/service updates before frontend integration where API changes are involved.
- Shared components before route-level composition changes.
- Coverage verification before declaring story completion.

## Parallel Opportunities

- Setup tasks marked `[P]` can run in parallel (T003-T005).
- Foundational tasks marked `[P]` can run in parallel after schema baselines (T008-T009, T011, T013, T015-T016).
- US1 parallel sets: T019-T022 together, then UI/API tasks where file-independent (T025-T026).
- US2 parallel sets: T028-T031 together, then component/dropdown work (T034-T035).
- US3 parallel sets: T039-T043 together, then landing/table/UI slices (T047-T048).
- Final-phase doc updates marked `[P]` can run in parallel (T054-T056).

## Parallel Example: User Story 3

```bash
# Run US3 test tasks in parallel:
Task: "T039 [US3] backend contract tests"
Task: "T040 [US3] backend integration tests"
Task: "T041 [US3] frontend admin landing tests"
Task: "T042 [US3] frontend admin users tests"
Task: "T043 [US3] frontend account page admin-action tests"

# Run independent frontend implementation tasks in parallel:
Task: "T047 [US3] extend AdminUserTable role controls"
Task: "T048 [US3] create admin landing page"
```

## Implementation Strategy

### MVP First (US1)

1. Complete Phase 1 and Phase 2.
2. Deliver Phase 3 (US1) and validate independent test criteria.
3. Demo stable auth lifecycle before expanding to account/admin UX deltas.

### Incremental Delivery

1. Ship US1 auth lifecycle hardening under revised model.
2. Ship US2 account hub and self-service UX.
3. Ship US3 admin landing and role governance with owner protection.
4. Execute final cross-cutting validation and mandatory stop gates.

### Parallel Team Strategy

1. Team aligns on Setup + Foundational.
2. After foundations stabilize:
   - Engineer A: US1 lifecycle stability
   - Engineer B: US2 account hub UX
   - Engineer C: US3 admin landing + role governance
3. Converge on final-phase documentation + full gate execution.

## Notes

- All tasks follow required checklist format: `- [ ] T### [P?] [US?] Description with file path`.
- Story labels are only used in user-story phases.
- Task IDs are sequential and execution-ordered.
- No unresolved clarifications remain for task execution.
- Full monorepo test and coverage stop rules are mandatory before commit/handoff.
