# Implementation Plan: User Auth And Management

**Branch**: `[046-user-auth-management]` | **Date**: 2026-04-02 | **Spec**: [spec.md](spec.md)
**Input**: Feature specification from `/specs/046-user-auth-management/spec.md`

**Note**: This template is filled in by the `/speckit.plan` command. See `.specify/templates/plan-template.md` for the execution workflow.

## Summary

Deliver real user accounts and authentication across database, backend, and frontend,
including account settings, admin user oversight, session revocation controls,
temporary lockout on repeated failed sign-ins, and deletion lifecycle handling
(immediate deactivation followed by delayed hard deletion). The implementation will add
shared persistence entities and migrations in libs/db, introduce authenticated backend
write/read endpoints and authorization enforcement, and add frontend auth + account
settings + admin user management workflows that consume those backend contracts.

## Technical Context

**Language/Version**: Python 3.12 (backend/libs), TypeScript 5.x + React 19 + Next.js 15 (frontend)  
**Primary Dependencies**: SQLAlchemy 2.x, Alembic, Pydantic 2.x, psycopg 3.x, HeroUI 3, Tailwind utilities, Next.js App Router  
**Storage**: PostgreSQL 16 via shared libs/db migration authority  
**Testing**: pytest, Vitest, Ruff, Ty, Biome, Nx run-many test and coverage gates  
**Target Platform**: Local Docker Compose stack (backend, frontend, db), Linux-based containers
**Project Type**: Nx monorepo web application with backend API and frontend client  
**Performance Goals**: Sign-in and account settings endpoints return within 1s p95 under normal local-stack load; user can complete registration plus first sign-in in under 3 minutes in validation flows  
**Constraints**: No MFA in this release; concurrent sessions allowed with revocation controls; immediate session revocation on deactivation; fail hard on missing credentials/env vars; maintain >= 90% coverage across affected projects  
**Scale/Scope**: Initial production scope targets foundational account system for authenticated product access and basic admin user management for early-stage operations

## Constitution Check

_GATE: Must pass before Phase 0 research. Re-check after Phase 1 design._

- Monorepo cohesion: Does the plan preserve clear Nx project boundaries and include
  cross-layer contract updates for vertical-slice changes?
  - Pass: Yes. Changes are planned in libs/db, apps/backend, and apps/frontend with explicit contract artifacts.
- Quality gate enforcement: Are lint, format, type-check, and test gates defined with no
  suppression, bypass, or workaround strategy?
  - Pass: Yes. Plan requires existing Ruff, Ty, Biome, pytest, and Vitest gates without suppression.
- Full-suite stop rule: Does the plan require `pnpm exec nx run-many -t test --all` to
  pass before any commit and before any AI agent ends work, with no exceptions?
  - Pass: Yes. Included as mandatory stop gate.
- Coverage stop rule: Does the plan require `pnpm exec nx run-many -t coverage --all`
  to pass before any commit with >= 90% thresholds for every project?
  - Pass: Yes. Included as mandatory commit gate.
- Test and coverage discipline: Does the plan include automated tests needed to maintain
  > = 90% coverage across affected backend/frontend projects?
  - Pass: Yes. Contract, integration, and UI/workflow tests are in-scope deliverables.
- Local-first parity: Can the complete impacted flow run locally via unified Docker
  Compose, and are compose/healthcheck updates identified?
  - Pass: Yes. Auth flow verification is planned against compose backend/frontend/db runtime.
- Data integrity and reliability: Are data provenance, schema/contract versioning, and
  trend/alert regression protections explicitly designed?
  - Pass: Yes. User/account schema and API contracts are versioned through migrations and spec artifacts; no trend behavior change is planned.
- Configuration integrity: Do all new services/pipeline components fail hard on missing
  env vars/credentials (no soft outcomes), and is `docker/compose/local.secrets.env`
  declared as an `env_file` source for any service that requires secrets?
  - Pass: Yes. New auth-related secret inputs will be hard-fail and wired through compose env_file where applicable.
- Frontend UI consistency: For frontend changes, does the plan use HeroUI components,
  Tailwind utilities, and shared abstractions in `apps/frontend/src/components` for
  repeated patterns instead of new ad hoc CSS or duplicated markup?
  - Pass: Yes. Account and admin flows will use shared HeroUI/Tailwind component patterns.
- Documentation fidelity: Does the plan identify all documentation that MUST be added or
  updated for the proposed code and behavior changes?
  - Pass: Yes. Plan includes updates to feature docs plus AGENTS.md/runtime docs if commands or setup changes.

## Project Structure

### Documentation (this feature)

```text
specs/046-user-auth-management/
├── plan.md              # This file (/speckit.plan command output)
├── research.md          # Phase 0 output (/speckit.plan command)
├── data-model.md        # Phase 1 output (/speckit.plan command)
├── quickstart.md        # Phase 1 output (/speckit.plan command)
├── contracts/           # Phase 1 output (/speckit.plan command)
└── tasks.md             # Phase 2 output (/speckit.tasks command - NOT created by /speckit.plan)
```

### Source Code (repository root)

```text
apps/
├── backend/
│   ├── src/
│   │   ├── contract/
│   │   │   └── query/
│   │   ├── query/
│   │   └── http_api_server.py
│   └── tests/
│       ├── contract/
│       └── integration/
├── frontend/
│   ├── src/
│   │   ├── app/
│   │   │   ├── api/
│   │   │   ├── settings/
│   │   │   └── admin/
│   │   ├── components/
│   │   ├── lib/api/
│   │   └── shell/
│   └── tests/
└── pipeline/
  └── src/ (no functional auth changes expected)

libs/
└── db/
  ├── alembic/versions/
  └── src/db/
    ├── models/
    └── repositories/

docker-compose.yml
docs/
└── runbooks/
```

**Structure Decision**: Use the existing monorepo web-application structure with shared
persistence in libs/db, API/runtime changes in apps/backend, and authenticated UI flows
in apps/frontend.

## Complexity Tracking

No constitution violations identified.

## Post-Design Constitution Check

- Monorepo cohesion: Pass. Design artifacts span shared db, backend API, and frontend client boundaries.
- Quality gate enforcement: Pass. Plan and quickstart include all lint/type/test gates with no bypass path.
- Full-suite stop rule: Pass. Explicitly required in quickstart and commit gates.
- Coverage stop rule: Pass. Explicitly required in quickstart and commit gates.
- Test and coverage discipline: Pass. Contract, integration, and UI tests are mandatory for each auth/account slice.
- Local-first parity: Pass. Quickstart verifies end-to-end auth behavior on docker compose services.
- Data integrity and reliability: Pass. Data model defines lifecycle and idempotency/concurrency behavior for sessions and deletion.
- Configuration integrity: Pass. Auth secret/env requirements remain fail-hard by policy.
- Frontend UI consistency: Pass. UI plan requires HeroUI/Tailwind and shared component reuse.
- Documentation fidelity: Pass. Plan includes contracts, quickstart, data model, and AGENTS.md context refresh.
