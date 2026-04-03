# Research: User Auth And Management

## Decision 1: Session model supports multiple concurrent sessions with revocation

- Decision: Allow multiple active sessions per user and provide explicit user-level and admin-level session revocation controls.
- Rationale: Matches clarified product behavior, supports multi-device usage, and allows targeted risk response without unnecessary sign-outs.
- Alternatives considered:
  - Single-session-only model: rejected due to poor multi-device UX and higher support friction.
  - Multi-session with no revocation controls: rejected because it weakens incident response.

## Decision 2: Failed sign-in protection uses bounded temporary lockout

- Decision: Enforce temporary lockout after a bounded number of consecutive failed sign-in attempts.
- Rationale: Reduces credential-stuffing and brute-force risk while keeping user recovery manageable.
- Alternatives considered:
  - No lockout: rejected for insufficient security posture.
  - Immediate long lockout: rejected for high support burden and account abuse risk.

## Decision 3: Account deactivation immediately revokes active sessions

- Decision: On account deactivation, immediately revoke all existing sessions and block new session creation.
- Rationale: Provides deterministic access cut-off and aligns with clarified admin expectations.
- Alternatives considered:
  - Block only new sessions: rejected because active sessions could retain access.
  - Grace-period revocation: rejected because it introduces avoidable security ambiguity.

## Decision 4: Initial release excludes MFA

- Decision: Multi-factor authentication is explicitly out of scope for this release.
- Rationale: Keeps first release focused on foundational identity/session capabilities and reduces delivery risk.
- Alternatives considered:
  - MFA for all users now: rejected as too broad for initial slice.
  - MFA only for admins now: rejected as additional complexity better handled in follow-up.

## Decision 5: Deletion lifecycle is deactivation-first with delayed hard deletion

- Decision: Handle deletion requests by immediate deactivation + session revocation, then hard deletion after retention period.
- Rationale: Supports safety, reversibility window, and clean eventual data lifecycle handling.
- Alternatives considered:
  - Immediate hard deletion: rejected due to operational recovery risk.
  - Soft-delete forever: rejected because it does not satisfy irreversible deletion requirement.

## Decision 6: Use shared libs/db migration authority for account schema changes

- Decision: Add account, credential, session, role, and audit-event persistence via libs/db models and Alembic versions.
- Rationale: Repository conventions designate libs/db as sole migration authority and shared persistence boundary.
- Alternatives considered:
  - Backend-local ad hoc tables: rejected due to architecture boundary violations.
  - External identity store now: rejected for unnecessary initial complexity.

## Decision 7: Preserve backend contract-first pattern with explicit error envelopes

- Decision: Add auth/account/admin backend contracts and standardized error envelopes following existing contract/query style.
- Rationale: Maintains consistent API behavior, validation, and testability across backend surfaces.
- Alternatives considered:
  - Implicit response shapes from handlers: rejected due to brittle client behavior.
  - Frontend-only validation assumptions: rejected because backend must enforce authority.

## Decision 8: Frontend flow implemented with shared HeroUI/Tailwind components

- Decision: Build auth and account-management UI with HeroUI primitives and reusable shared components under apps/frontend/src/components.
- Rationale: Aligns with constitution requirements and existing frontend architecture.
- Alternatives considered:
  - Route-local one-off components: rejected for duplication and consistency drift.
  - Custom CSS-heavy bespoke patterns: rejected by UI system constraints.

## Planning Readiness

- All high-impact clarification items from the spec are resolved.
- No remaining NEEDS CLARIFICATION markers are required for planning.
- Phase 1 design artifacts can proceed without blocking decisions.
