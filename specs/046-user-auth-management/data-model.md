# Data Model: User Auth And Management

## Entity: UserAccount

- Purpose: Represents an end-user identity and lifecycle state.
- Core fields:
  - user_id (string/uuid, unique, immutable)
  - email (string, unique, normalized)
  - display_name (string, nullable)
  - account_status (enum: active, deactivated, deletion_pending, deleted)
  - is_admin (boolean)
  - failed_sign_in_count (integer)
  - lockout_until (timestamp, nullable)
  - created_at (timestamp)
  - updated_at (timestamp)
  - deactivated_at (timestamp, nullable)
  - deletion_requested_at (timestamp, nullable)
  - deletion_due_at (timestamp, nullable)
  - deleted_at (timestamp, nullable)
- Validation rules:
  - email uniqueness is case-insensitive.
  - deleted accounts cannot transition back to active.
  - deletion_due_at is required when account_status is deletion_pending.

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
  - one active credential set per active user for this release.
  - password updates require current credential validation.

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
  - multiple active sessions per user are allowed.
  - deactivation revokes all active sessions immediately.
  - password change revokes all active sessions immediately.

## Entity: RoleAssignment

- Purpose: Captures privileged authorization scope for account actions.
- Core fields:
  - assignment_id (string/uuid, unique)
  - user_id (foreign key -> UserAccount)
  - role (enum: admin)
  - created_at (timestamp)
  - revoked_at (timestamp, nullable)
- Validation rules:
  - user-management admin actions require active admin role assignment.
  - at least one active admin account must remain (guardrail requirement).

## Entity: AccountAuditEvent

- Purpose: Immutable audit trail for security-sensitive account and session actions.
- Core fields:
  - event_id (string/uuid, unique)
  - user_id (nullable foreign key -> UserAccount, nullable for unknown principal)
  - actor_user_id (nullable foreign key -> UserAccount)
  - event_type (enum: register, sign_in_success, sign_in_failure, lockout_applied, sign_out, password_changed, session_revoked, account_deactivated, account_reactivated, deletion_requested, account_hard_deleted)
  - event_context (object)
  - occurred_at (timestamp)
- Validation rules:
  - audit rows are append-only.
  - security-sensitive actions must emit corresponding events.

## Relationships

- UserAccount 1:1 CredentialRecord (active credential set for this release).
- UserAccount 1:N AuthSession.
- UserAccount 1:N RoleAssignment.
- UserAccount 1:N AccountAuditEvent (as subject and/or actor).

## State Transitions

- UserAccount:
  - active -> deactivated (admin action or deletion request)
  - deactivated -> active (admin reactivation)
  - active/deactivated -> deletion_pending (user deletion request)
  - deletion_pending -> deleted (retention window elapsed and hard deletion executed)
- AuthSession:
  - active -> revoked (manual revoke, deactivation, password change)
  - active -> expired (ttl reached)
- Lockout:
  - failed sign-in threshold reached -> lockout_until set
  - lockout window elapsed -> sign-in allowed with valid credentials

## Concurrency and Conflict Rules

- Concurrent profile updates use last-write-wins with updated_at checks for conflict detection in API responses.
- Session revocation operations are idempotent; repeated revoke calls on already revoked sessions return stable success semantics.
- Deletion-request flow must be idempotent; repeated deletion requests do not create duplicate lifecycle transitions.
