# Implementation Plan: User Auth And Management

**Branch**: `[046-user-auth-management]` | **Date**: 2026-04-03 | **Spec**: `/Users/hackerc/Projects/longtail-experiment/specs/046-user-auth-management/spec.md`
**Input**: Feature specification from `/Users/hackerc/Projects/longtail-experiment/specs/046-user-auth-management/spec.md`

## Summary

Revise the in-flight auth/account/admin implementation to align with the updated spec by adding clear account/admin navigation surfaces, a dedicated admin landing page, owner-role governance constraints, and consistent shared page headers across account/admin pages while preserving existing authentication, session, and lifecycle guarantees.

## Technical Context

**Language/Version**: Python 3.12 (backend/libs), TypeScript 5.x + React 19 + Next.js 15 App Router (frontend)  
**Primary Dependencies**: SQLAlchemy 2.x, Alembic, Pydantic 2.x, HeroUI 3 (`@heroui/react`), Tailwind utilities, existing auth/discovery client contracts  
**Storage**: PostgreSQL 16 via shared `libs/db` migration authority  
**Testing**: pytest, Vitest, Biome, Ruff, Ty, pre-commit, Nx monorepo gates  
**Target Platform**: Docker Compose local stack (backend/frontend/db), browser clients for frontend  
**Project Type**: Monorepo web application (backend API + frontend App Router UI)  
**Performance Goals**: Meet existing spec success criteria, including account/admin task completion and deterministic authorization outcomes under normal interactive usage  
**Constraints**: No bypass of full-suite stop gates; owner role cannot be modified via admin workflows; frontend must use shared page-header component patterns and HeroUI/Tailwind conventions  
**Scale/Scope**: Incremental revision to existing Spec 046 scope, covering account details page UX, admin landing navigation, admin-role management controls, and owner-protection enforcement

## Constitution Check

_GATE: Must pass before Phase 0 research. Re-check after Phase 1 design._

- Monorepo cohesion: Pass. Changes remain in existing Nx projects (`apps/backend`, `apps/frontend`, `libs/db`) with coordinated contract/model/UI updates.
- Quality gate enforcement: Pass. Plan keeps lint/format/typecheck/test requirements and disallows suppressions/bypasses.
- Full-suite stop rule: Pass. Plan requires `pnpm exec nx run-many -t test --all` before commit/handoff.
- Coverage stop rule: Pass. Plan requires `pnpm exec nx run-many -t coverage --all` with >=90% per project.
- Test and coverage discipline: Pass. Plan includes backend + frontend contract/integration/UI tests for new role/navigation/header behavior.
- Local-first parity: Pass. Flow remains runnable via unified Docker Compose stack.
- Data integrity and reliability: Pass. Role-governance and owner-protection behaviors are explicit, auditable, and contract-tested.
- Configuration integrity: Pass. No new secret-requiring service introduced; existing fail-fast credential policy unchanged.
- Frontend UI consistency: Pass. Plan mandates HeroUI/Tailwind and existing shared page-header components for account/admin pages.
- Documentation fidelity: Pass. Spec, plan, data model, contracts, quickstart, and agent context updates are included.

## Project Structure

### Documentation (this feature)

```text
/Users/hackerc/Projects/longtail-experiment/specs/046-user-auth-management/
├── plan.md
├── research.md
├── data-model.md
├── quickstart.md
├── contracts/
│   └── user-auth-management.openapi.yaml
└── tasks.md
```

### Source Code (repository root)

```text
/Users/hackerc/Projects/longtail-experiment/apps/backend/
├── src/
│   ├── contract/query/
│   ├── query/
│   └── http_api_server.py
└── tests/

/Users/hackerc/Projects/longtail-experiment/libs/db/
├── src/db/models/
├── src/db/repositories/
└── alembic/versions/

/Users/hackerc/Projects/longtail-experiment/apps/frontend/
├── src/app/
│   ├── settings/
│   ├── admin/
│   │   ├── page.tsx
│   │   └── users/
│   └── api/
├── src/components/
│   └── discovery/PageHeader.tsx
├── src/components/account/
└── tests/
```

**Structure Decision**: Continue with the established monorepo web-application structure and revise existing Spec 046 artifacts/codepaths in place, adding no new top-level project boundaries.

## Phase 0: Outline & Research

No unresolved technical clarifications remain after spec revision. Existing research decisions are extended with in-scope updates:

1. Admin landing is a dedicated, authenticated admin-only index page that lists currently available admin destinations.
2. Owner role is treated as a privileged classification with immutable UI/API governance boundaries for administrator actions.
3. Shared page-header usage is a hard UX consistency requirement for account details, admin landing, and admin user-management pages.

Research artifact updated: `/Users/hackerc/Projects/longtail-experiment/specs/046-user-auth-management/research.md`.

## Phase 1: Design & Contracts

### Data Model Revisions

Revise `/Users/hackerc/Projects/longtail-experiment/specs/046-user-auth-management/data-model.md` to reflect:

- `PrivilegeLevel` entity/field semantics (`user`, `admin`, `owner`).
- Owner immutability constraints for admin-originated role changes.
- Audit-event coverage for denied owner-targeted role changes and admin-role grant/revoke actions.

### Contract Revisions

Revise `/Users/hackerc/Projects/longtail-experiment/specs/046-user-auth-management/contracts/user-auth-management.openapi.yaml` to include:

- Account details payloads with role indicator fields needed by dropdown/account surfaces.
- Admin landing metadata endpoint shape (if needed for dynamic listing) or explicit contract notes for static list sourcing.
- Admin role-governance endpoints or extension of existing admin user endpoints for grant/revoke administrator actions.
- Explicit conflict/forbidden error semantics for owner-targeted role modification attempts.

### Quickstart Revisions

Revise `/Users/hackerc/Projects/longtail-experiment/specs/046-user-auth-management/quickstart.md` to include manual verification steps for:

- Account dropdown Account button routing.
- Admin chip visibility rules.
- Admin navigation from dropdown and account page.
- Admin landing rendering and links.
- Admin grant/revoke behavior and owner-protection denial behavior.
- Shared page-header consistency on all three required pages.

### Agent Context Update

Run:

- `.specify/scripts/bash/update-agent-context.sh codex`

Expected output artifact update: `/Users/hackerc/Projects/longtail-experiment/AGENTS.md` (or agent-targeted context file selected by script).

## Phase 2: Implementation Planning Approach

Implementation will be sequenced into vertical slices aligned with revised stories:

1. Navigation + account surface UX (dropdown Account action, account page details/actions, role chips).
2. Admin navigation + landing page.
3. Admin users role-governance controls (grant/revoke admin) with owner-role enforcement.
4. Shared page-header normalization across account/admin pages.
5. Backend contract/repository updates and audit coverage for owner-protected role-change denials.
6. Automated + manual verification and full monorepo quality gates.

## Post-Design Constitution Check

- Monorepo cohesion: Pass (same projects, coordinated contracts and UI/backend updates).
- Quality and stop rules: Pass (explicitly retained in quickstart and plan).
- Coverage discipline: Pass (new tests required for role governance and UI pathways).
- Local-first parity: Pass (manual runtime verification in compose stack remains required).
- Data integrity and reliability: Pass (owner immutability + auditability explicitly modeled).
- Frontend UI consistency: Pass (shared page-header requirement enforced in scope and tests).
- Documentation fidelity: Pass (spec/plan/research/data-model/contracts/quickstart updated together).

## Complexity Tracking

No constitution violations identified; complexity tracking table not required.
