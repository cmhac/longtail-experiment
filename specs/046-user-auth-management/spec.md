# Feature Specification: User Auth And Management

**Feature Branch**: `[046-user-auth-management]`  
**Created**: 2026-04-02  
**Status**: Draft  
**Input**: User description: "Revise Spec 046 to improve account and admin UX: add Account action in nav dropdown, account details page with self-service updates and sign-out, admin status chips and admin navigation surfaces, an admin landing page, admin role grant/revoke controls on admin users page, immutable owner role protections, and shared page header usage across account/admin pages"

## Clarifications

### Session 2026-04-02

- Q: How many concurrent sessions should one user account allow after sign-in? → A: Multiple concurrent sessions are allowed, with explicit revocation controls in account settings and admin workflows.
- Q: What protection should apply after repeated failed sign-in attempts? → A: Apply temporary account lockout after a bounded number of failed attempts.
- Q: What happens to active sessions when an administrator deactivates an account? → A: Deactivation immediately revokes all active sessions and blocks new sessions.
- Q: Is multi-factor authentication required in the initial release? → A: No, multi-factor authentication is deferred to a follow-up feature.
- Q: How should user deletion requests be handled? → A: Deactivate immediately, then hard-delete after a defined retention period.

### Session 2026-04-03

- Q: Should this request create a new spec/branch? → A: No; revise existing Spec 046 in place.
- Q: What initial admin landing scope is required? → A: Provide an admin landing page that lists admin-only destinations, with user management as the initial entry.
- Q: How should owner-level permissions work? → A: Owner role assignment is manual and cannot be granted, revoked, or downgraded through administrator UI actions.

## User Scenarios & Testing _(mandatory)_

<!--
  IMPORTANT: User stories should be PRIORITIZED as user journeys ordered by importance.
  Each user story/journey must be INDEPENDENTLY TESTABLE - meaning if you implement just ONE of them,
  you should still have a viable MVP (Minimum Viable Product) that delivers value.

  Assign priorities (P1, P2, P3, etc.) to each story, where P1 is the most critical.
  Think of each story as a standalone slice of functionality that can be:
  - Developed independently
  - Tested independently
  - Deployed independently
  - Demonstrated to users independently
-->

### User Story 1 - Account Access Lifecycle (Priority: P1)

As a platform user, I need to create an account, sign in, remain signed in securely, and sign out so I can access protected application features with a persistent identity.

**Why this priority**: Without a working account and sign-in lifecycle, there is no trusted identity for permissions, personalization, or account ownership.

**Independent Test**: Can be fully tested by creating a new account, signing in, accessing a protected page, refreshing the browser, and signing out.

**Acceptance Scenarios**:

1. **Given** a visitor without an account, **When** they complete registration with valid credentials, **Then** a new active user account is created and they can proceed to signed-in experience.
2. **Given** a registered user, **When** they sign in with valid credentials, **Then** they receive an authenticated session and can access protected pages.
3. **Given** a signed-in user, **When** they sign out, **Then** their active session is revoked and protected pages require sign-in again.
4. **Given** a signed-in user with an active session, **When** they revisit or refresh the app, **Then** their authenticated state is restored without forcing immediate re-login.
5. **Given** repeated failed sign-in attempts exceed allowed thresholds, **When** additional sign-in attempts are made during lockout, **Then** authentication is denied until lockout expires.

---

### User Story 2 - Account Hub And Self-Service Management (Priority: P2)

As a signed-in user, I need a clear Account entry in the top-nav profile menu and a dedicated account page where I can view key account details, update email/password, and sign out.

**Why this priority**: Core authentication is not sufficient unless users can reliably find and manage their own account information from the primary navigation.

**Independent Test**: Can be tested by signing in, opening the top-nav profile dropdown, navigating to Account, viewing account details, updating email/password, and signing out.

**Acceptance Scenarios**:

1. **Given** a signed-in user, **When** they open the profile dropdown, **Then** an Account action is visible and routes to the account details page.
2. **Given** a signed-in user, **When** they open the account page, **Then** they can see minimal user details and current account role indicators relevant to their access.
3. **Given** a signed-in user, **When** they submit a valid email update, **Then** the email change is persisted and immediately reflected in account details.
4. **Given** a signed-in user, **When** they change their password with valid current and new credentials, **Then** password change succeeds and future sign-ins require the new password.
5. **Given** a signed-in user, **When** they activate sign-out from the account page, **Then** their active session ends and protected pages require sign-in.
6. **Given** invalid account-setting input, **When** the user submits changes, **Then** the system rejects the request with clear actionable validation feedback.

---

### User Story 3 - Admin Landing And Role Governance (Priority: P3)

As an administrator, I need clear admin navigation and role controls so I can access admin tools quickly, grant/revoke admin access safely, and preserve owner-level safeguards.

**Why this priority**: Admin workflows become error-prone without clear wayfinding and explicit role-governance rules, especially when owner-level constraints must be enforced.

**Independent Test**: Can be tested by signing in as an administrator, accessing admin entry points from dropdown/account page, opening admin landing, navigating to users management, changing admin roles for eligible users, and verifying owner protections.

**Acceptance Scenarios**:

1. **Given** an authenticated administrator, **When** they open the profile dropdown or account page, **Then** they see a visible Admin action leading to the admin landing page.
2. **Given** an authenticated administrator, **When** they open the admin landing page, **Then** they can see a list of available admin-only destinations, including user management.
3. **Given** an authenticated administrator, **When** they open user management, **Then** they can view paginated user summaries with role indicators, including administrator and owner visibility.
4. **Given** an authenticated administrator, **When** they grant administrator access to an eligible non-owner account, **Then** that account gains administrator permissions.
5. **Given** an authenticated administrator, **When** they revoke administrator access from an eligible non-owner account, **Then** that account loses administrator permissions while remaining active unless separately deactivated.
6. **Given** an owner account, **When** an administrator attempts to change its role, **Then** the action is denied and owner role remains unchanged.
7. **Given** a non-administrator user, **When** they attempt to access administrative pages or role-management actions, **Then** access is denied.
8. **Given** an authenticated administrator, **When** they deactivate a user account, **Then** all currently active sessions for that account are terminated immediately.

### Edge Cases

- What happens when a user attempts to register with an email that already exists?
- What happens when repeated failed sign-in attempts exceed allowed thresholds?
- What happens when a session expires during an in-progress account settings update?
- What happens when two account settings updates are submitted concurrently for the same user?
- What happens when a signed-in non-admin user tries to access admin landing directly by URL?
- Deactivating a currently signed-in user immediately ends all active sessions and blocks new session creation until reactivation.
- What happens when the final active administrator account would be deactivated?
- What happens when an administrator attempts to promote, demote, or deactivate an owner account?
- What happens when authentication cookies or tokens are missing, expired, or tampered with?
- During retention after deletion request, the account remains deactivated and all account actions are denied until hard deletion completes.

## Requirements _(mandatory)_

### Functional Requirements

- **FR-001**: System MUST allow visitors to create user accounts using unique email identity and password credentials.
- **FR-002**: System MUST validate account registration input and reject invalid, incomplete, or duplicate identity submissions.
- **FR-003**: System MUST authenticate registered users at sign-in and establish an authenticated session on success.
- **FR-004**: System MUST terminate authenticated sessions on explicit sign-out.
- **FR-005**: System MUST enforce authentication on protected backend and frontend user-account routes.
- **FR-006**: System MUST restrict administrative user-management actions to authorized administrator accounts.
- **FR-007**: System MUST provide a user-facing account settings view that includes current profile and security metadata.
- **FR-008**: System MUST allow signed-in users to update permitted profile fields and persist those updates.
- **FR-009**: System MUST allow signed-in users to change their password after validating current credentials.
- **FR-010**: System MUST invalidate all active sessions for a user after a successful password change.
- **FR-011**: System MUST provide administrators a basic user list with account status and key identifiers.
- **FR-012**: System MUST allow administrators to activate and deactivate user accounts.
- **FR-013**: System MUST block session creation for deactivated accounts.
- **FR-014**: System MUST produce consistent error responses for authentication and authorization failures without exposing sensitive internal details.
- **FR-015**: System MUST record auditable events for account lifecycle and security-sensitive actions, including sign-in success/failure, sign-out, password changes, and status changes.
- **FR-016**: System MUST preserve account ownership boundaries so users can only view or mutate their own account settings unless explicitly authorized as administrators.
- **FR-017**: System MUST support deterministic session restoration behavior for valid active sessions across page refresh and revisit flows.
- **FR-018**: System MUST provide user-facing feedback messages for all failed account actions, including validation failures, authentication failures, and permission denials.
- **FR-019**: System MUST allow multiple concurrent active sessions per user account.
- **FR-020**: System MUST provide users explicit controls to view and revoke their active sessions.
- **FR-021**: System MUST provide administrators explicit controls to revoke active sessions for managed user accounts.
- **FR-022**: System MUST enforce temporary account lockout after a bounded number of consecutive failed sign-in attempts.
- **FR-023**: System MUST allow sign-in again after lockout expiration and successful credential validation.
- **FR-024**: System MUST immediately revoke all currently active sessions when an account is deactivated.
- **FR-025**: System MUST not require multi-factor authentication for the initial release account sign-in flow.
- **FR-026**: System MUST support user deletion requests by immediately deactivating the account and revoking active sessions.
- **FR-027**: System MUST perform irreversible hard deletion of requested accounts after a defined retention period.
- **FR-028**: System MUST deny all account access and session creation for accounts in deletion-pending or deactivated states.
- **FR-029**: System MUST expose an Account action in the signed-in top navigation profile dropdown that routes to the account details page.
- **FR-030**: System MUST provide an account details page showing minimal user account information and security/account actions including sign-out, email update, and password change.
- **FR-031**: System MUST display an administrator role indicator in the profile dropdown and account details page for users with administrator privileges.
- **FR-032**: System MUST expose an Admin action in both the profile dropdown and account details page for users with administrator privileges.
- **FR-033**: System MUST provide an admin landing page that lists available admin-only pages and supports navigation to them.
- **FR-034**: System MUST include user management as an available destination on the initial admin landing page.
- **FR-035**: System MUST allow administrators to grant administrator role to eligible non-owner accounts from the admin users management page.
- **FR-036**: System MUST allow administrators to revoke administrator role from eligible non-owner accounts from the admin users management page.
- **FR-037**: System MUST enforce an owner role classification that cannot be granted, revoked, or downgraded through administrator-facing application workflows.
- **FR-038**: System MUST deny and audit any administrator-initiated role change attempt targeting an owner account.
- **FR-039**: System MUST present consistent shared page-header treatment on account details, admin landing, and admin user-management pages.
- **FR-040**: System MUST preserve existing admin user-management controls for account activation/deactivation and session revocation while adding role-governance actions.

### Assumptions and Dependencies

- The initial release supports email-and-password based user accounts as the primary sign-in method.
- Password reset by out-of-band recovery flow is out of scope for this feature and will be addressed separately.
- Multi-factor authentication is out of scope for this initial release and planned for a separate follow-up feature.
- User deletion follows a two-step lifecycle in this release: immediate deactivation, then hard deletion after a defined retention period.
- Existing protected product surfaces can be grouped behind a single authenticated experience boundary for first rollout.
- A minimal administrator role model is sufficient for initial user-management operations.
- Existing local environment, testing gates, and quality requirements remain mandatory for this feature.
- The initial release permits concurrent sessions across multiple devices/browsers for the same user account.
- The initial admin landing page can list only currently available admin destinations and will include user management at minimum.
- Minimal account details include identity and role information sufficient for account verification and self-management tasks.
- Owner role assignment is out of scope for UI/API workflows and is handled manually through controlled operational procedures.

### Key Entities _(include if feature involves data)_

- **User Account**: Represents a person identity with unique login identifier, lifecycle status, role assignment, and profile metadata.
- **Credential Record**: Represents authentication secret material and credential lifecycle metadata required for sign-in validation.
- **Authenticated Session**: Represents an active signed-in context tied to one user, with creation, expiry, and revocation state.
- **User Role Assignment**: Represents granted access scope for a user, including administrative permissions.
- **Privilege Level**: Represents effective account privilege tier (standard user, administrator, owner) with owner constraints that override administrator role-governance actions.
- **Account Audit Event**: Represents immutable security and lifecycle events for account and session actions.

## Success Criteria _(mandatory)_

### Measurable Outcomes

- **SC-001**: At least 95% of new users can complete account registration and first sign-in in under 3 minutes during usability validation.
- **SC-002**: At least 99% of valid sign-in attempts successfully establish authenticated sessions under normal operating conditions.
- **SC-003**: At least 95% of authenticated users can complete profile update and password change tasks on first attempt.
- **SC-004**: 100% of audited protected-route requests without valid authentication are denied.
- **SC-005**: 100% of audited non-administrator attempts to perform administrator-only user-management actions are denied.
- **SC-006**: 100% of account lifecycle and security-sensitive actions in audit samples produce corresponding audit events.
- **SC-007**: 100% of audited sign-in attempts during active lockout windows are denied.
- **SC-008**: 100% of audited requests from sessions belonging to deactivated accounts are denied after deactivation.
- **SC-009**: 100% of deletion-requested accounts in audit samples are deactivated immediately and transition to hard-deleted state after the retention window.
- **SC-010**: At least 95% of signed-in users can navigate from the top-nav dropdown to the account details page and complete a basic self-service update flow in under 2 minutes.
- **SC-011**: 100% of audited administrator sessions can reach admin landing from at least one primary account surface (dropdown or account page), while 100% of audited non-admin sessions cannot.
- **SC-012**: 100% of audited administrator attempts to change owner account privilege are denied and recorded in audit events.
- **SC-013**: 100% of audited renders for account details, admin landing, and admin user-management pages include the shared page-header experience.

## Constitution Alignment _(mandatory)_

- **CA-001 Quality Gates**: Feature can satisfy linting, formatting, type checking, and
  automated test gates without suppressions, bypasses, or workaround-only code, and the
  full-suite stop rule (`pnpm exec nx run-many -t test --all`) can be satisfied before
  commit and before AI agent handoff/end of work. (Yes)
- **CA-002 Coverage**: Feature includes tests to keep backend/frontend coverage at or
  above 90% in affected projects, and can satisfy the commit-time coverage stop rule
  (`pnpm exec nx run-many -t coverage --all`). (Yes)
- **CA-003 Local Stack**: Feature is runnable in the unified local Docker Compose stack,
  or explicitly lists compose updates needed. (Yes)
- **CA-004 Contracts and Data Integrity**: Data/interface contract changes,
  provenance/timestamp impacts, and trend-alert reliability safeguards are defined.
  (Yes)
- **CA-005 Documentation Fidelity**: Relevant documentation is identified and will be
  created or updated in the same change for any impacted behavior, contracts, setup, or
  runbooks, including AGENTS.md when repository structure/workflows/tooling change.
  (Yes)
- **CA-006 Configuration Integrity**: Any new service or pipeline component that requires
  credentials or external API keys will fail hard (exception/non-zero exit/job-level
  failure) when those variables are absent — no soft outcome recording, no silent
  swallowing. `docker/compose/local.secrets.env` is declared as an `env_file` source
  for any Docker Compose service that requires secrets. (Yes)
- **CA-007 Frontend UI System**: For frontend changes, the feature uses HeroUI
  components, Tailwind utilities, and shared abstractions in
  `apps/frontend/src/components` for repeated patterns; it does not introduce duplicate
  one-off component patterns or new local CSS without a documented exception.
  (Yes)
