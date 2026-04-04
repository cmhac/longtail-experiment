# Research: User Auth And Management (Spec 046 Revision)

## Decision 1: Keep Spec 046 as in-place revision

- Decision: Update planning/design artifacts under existing `046-user-auth-management` instead of creating a new spec/branch.
- Rationale: Stakeholder explicitly requested revision of in-flight spec and branch to preserve delivery continuity.
- Alternatives considered:
  - Create new spec for admin UX expansion: rejected because it fragments scope already under active implementation.

## Decision 2: Admin landing page is a dedicated admin index surface

- Decision: Introduce an admin landing page that lists currently available admin-only destinations, with user management as the initial listed entry.
- Rationale: Provides explicit wayfinding and scalable navigation for future admin pages without coupling directly to one screen.
- Alternatives considered:
  - Direct-link only to admin users page from dropdown/account: rejected because it does not satisfy explicit landing-page requirement.
  - Empty placeholder landing with no links: rejected because it provides no operational value.

## Decision 3: Owner privilege is immutable through administrator workflows

- Decision: Treat `owner` as a protected privilege level that administrators cannot grant, revoke, or downgrade through application UI/API operations.
- Rationale: Matches governance requirement that owner assignment is manual DB-only and resistant to admin override.
- Alternatives considered:
  - Allow admins to demote owners with confirmation: rejected due to explicit non-overridable owner requirement.
  - Hide owner entirely from admin lists: rejected because visibility is needed for safe governance and clear denial messaging.

## Decision 4: Admin role management extends existing admin users flow

- Decision: Add grant/revoke admin controls to existing admin users management experience rather than creating a separate role-management tool.
- Rationale: Keeps operational actions centralized and aligned with existing admin account-status workflows.
- Alternatives considered:
  - Separate role-management page: rejected as unnecessary scope expansion and extra navigation overhead.
  - Backend-only role management without UI: rejected because stakeholder explicitly requested admin UI controls.

## Decision 5: Shared page-header component is mandatory for three target pages

- Decision: Enforce shared page-header usage on account details, admin landing, and admin users pages via existing components-folder abstractions.
- Rationale: Ensures visual consistency and compliance with constitution principle for reusable frontend patterns.
- Alternatives considered:
  - Route-local bespoke headers: rejected due to consistency drift and duplicate markup.

## Decision 6: Role indicators surfaced in both dropdown and account page

- Decision: Display role chips/indicators where specified (profile dropdown and account details page), including admin visibility and owner-aware account context.
- Rationale: Reduces ambiguity about effective privileges and explains why admin navigation/actions are present.
- Alternatives considered:
  - Show role only on account page: rejected because dropdown was explicitly requested.
  - Text-only labels without chip treatment: rejected because stakeholder requested chip presentation.

## Decision 7: Preserve prior auth/session security controls while adding role-governance

- Decision: Keep lockout, multi-session revocation, deactivation behavior, and deletion lifecycle unchanged while extending role governance.
- Rationale: New UX and privilege controls are additive and should not regress previously clarified security/lifecycle rules.
- Alternatives considered:
  - Rework auth lifecycle simultaneously: rejected as high-risk scope expansion.

## Planning Readiness

- All revised-spec planning unknowns are resolved.
- No `NEEDS CLARIFICATION` markers remain for this plan cycle.
- Phase 1 artifacts (data model, contract, quickstart) are ready for updated design alignment.
