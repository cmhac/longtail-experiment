# Data Model: User Auth And Management (Spec 046 Revision)

## Entity: UserAccount

- Purpose: Represents a person identity, lifecycle status, and effective privilege classification.
- Core fields:
  - user_id (string/uuid, unique, immutable)
  - email (string, unique, normalized)
  - display_name (string, nullable)
  - account_status (enum: active, deactivated, deletion_pending, deleted)
  - privilege_level (enum: user, admin, owner)
  - failed_sign_in_count (integer)
  - lockout_until (timestamp, nullable)
  - created_at (timestamp)
  - updated_at (timestamp)
  - deactivated_at (timestamp, nullable)
  - deletion_requested_at (timestamp, nullable)
  - deletion_due_at (timestamp, nullable)
  - deleted_at (timestamp, nullable)
- Validation rules:
  - Email uniqueness is case-insensitive.
  - `deleted` accounts cannot transition back to active.
  - `deletion_due_at` is required when account_status is `deletion_pending`.
  - `owner` privilege assignments are immutable through administrator-facing workflows.

## Entity: CredentialRecord

- Purpose: Stores authentication secret material and credential lifecycle metadata.
- Core fields:
  - credential_id (string/uuid, unique)
  - user_id (foreign key -> UserAccount)
  - password_hash (string)
  - password_changed_at (timestamp)
  - credential_status (enum: active, rotated, revoked)
  - created_at (timestamp)
  - updated_at (timestamp)
- Validation rules:
  - One active credential set per active user for this release.
  - Password updates require current credential validation.

## Entity: AuthSession

- Purpose: Represents an authenticated session bound to a user and client context.
- Core fields:
  - session_id (string/uuid, unique)
  - user_id (foreign key -> UserAccount)
  - session_status (enum: active, revoked, expired)
  - created_at (timestamp)
  - expires_at (timestamp)
  - revoked_at (timestamp, nullable)
  - revoked_reason (string, nullable)
  - client_metadata (object: device/browser/ip summary)
- Validation rules:
  - Multiple active sessions per user are allowed.
  - Deactivation revokes all active sessions immediately.
  - Password change revokes all active sessions immediately.

## Entity: AdminNavigationItem

- Purpose: Represents an admin-only destination shown on admin landing.
- Core fields:
  - item_key (string, unique)
  - label (string)
  - route (string)
  - description (string)
  - is_enabled (boolean)
  - display_order (integer)
- Validation rules:
  - Only admin-visible destinations are listed.
  - User-management destination is present in initial release.

## Entity: RoleChangeAction

- Purpose: Represents requested role-governance operations from admin user management.
- Core fields:
  - action_id (string/uuid, unique)
  - actor_user_id (foreign key -> UserAccount)
  - target_user_id (foreign key -> UserAccount)
  - requested_role (enum: admin_grant, admin_revoke)
  - action_result (enum: applied, denied)
  - denial_reason (enum: owner_protected, unauthorized, invalid_state, nullable)
  - occurred_at (timestamp)
- Validation rules:
  - Actor must have `admin` or `owner` privilege level.
  - Target with `owner` privilege always resolves as `denied` with owner-protected reason.
  - Action is idempotent for already-in-desired-state targets.

## Entity: AccountAuditEvent

- Purpose: Immutable audit trail for security-sensitive account, session, and role-governance actions.
- Core fields:
  - event_id (string/uuid, unique)
  - user_id (nullable foreign key -> UserAccount, nullable for unknown principal)
  - actor_user_id (nullable foreign key -> UserAccount)
  - event_type (enum: register, sign_in_success, sign_in_failure, lockout_applied, sign_out, password_changed, session_revoked, account_deactivated, account_reactivated, deletion_requested, account_hard_deleted, admin_granted, admin_revoked, owner_role_change_denied)
  - event_context (object)
  - occurred_at (timestamp)
- Validation rules:
  - Audit rows are append-only.
  - Denied owner-targeted role-change attempts must emit explicit audit events.

## Relationships

- UserAccount 1:1 CredentialRecord (active credential set for this release).
- UserAccount 1:N AuthSession.
- UserAccount 1:N AccountAuditEvent (as subject and/or actor).
- UserAccount 1:N RoleChangeAction (as actor and as target).
- AdminNavigationItem is a catalog consumed by admin-authorized clients.

## State Transitions

- UserAccount:
  - active -> deactivated (admin action or deletion request)
  - deactivated -> active (admin reactivation)
  - active/deactivated -> deletion_pending (user deletion request)
  - deletion_pending -> deleted (retention window elapsed and hard deletion executed)
  - privilege_level transitions:
    - user <-> admin (admin governance actions)
    - owner -> no UI/API transition allowed
- AuthSession:
  - active -> revoked (manual revoke, deactivation, password change)
  - active -> expired (ttl reached)
- Lockout:
  - failed sign-in threshold reached -> lockout_until set
  - lockout window elapsed -> sign-in allowed with valid credentials

## Concurrency and Conflict Rules

- Concurrent profile updates use last-write-wins with `updated_at` checks for conflict-aware responses.
- Session revocation operations are idempotent; repeated revoke calls on revoked sessions return stable success semantics.
- Deletion-request flow is idempotent; repeated requests do not duplicate lifecycle transitions.
- Admin grant/revoke actions are idempotent and must not mutate owner records.
- Owner-targeted role-change attempts always return deterministic denial semantics with corresponding audit records.
