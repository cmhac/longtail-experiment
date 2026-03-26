# Implementation Plan: Source Discovery Pages

**Branch**: `[032-source-pages]` | **Date**: 2026-03-25 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/specs/032-source-pages/spec.md`

**Note**: This template is filled in by the `/speckit.plan` command. See `.specify/templates/plan-template.md` for the execution workflow.

## Summary

Add first-class source browsing to discovery with a dedicated sources directory and a source detail page that lists datasets for the selected source. The plan introduces backend source-list and source-detail contracts over the existing persisted discovery metadata, keeps pipeline persistence semantics grounded in current `source_name` attribution, and extends the frontend shell and discovery pages to support source-first navigation without changing existing dataset detail flows.

## Technical Context

**Language/Version**: TypeScript 5.x + React 19 (Next.js 15 App Router), Python 3.12 backend query layer, existing pipeline contracts/persistence semantics  
**Primary Dependencies**: Existing discovery API client/types, Next.js routing primitives, existing shell/layout tokens, backend dataset discovery service/repository surfaces  
**Storage**: Existing PostgreSQL 16 discovery metadata in `source_profiles`, `data_series`, `topic_tags`, and `observations`; no new datastore expected  
**Testing**: Vitest + Testing Library for frontend page/component contracts, pytest contract/integration tests for backend query and HTTP surfaces, existing Nx/Biome/TypeScript/Python quality gates  
**Target Platform**: Responsive web experience in the existing discovery shell, backed by the local compose-backed backend runtime  
**Project Type**: Web application vertical slice spanning frontend and backend discovery layers, with pipeline/persistence behavior verified for compatibility  
**Performance Goals**: Source list and source detail pages preserve current catalog-scale responsiveness for dozens of sources and thousands of datasets without introducing noticeably slower browsing than existing dataset catalog flows  
**Constraints**: Preserve existing dataset routes and detail behavior; keep source identity stable across list/detail navigation; avoid schema churn unless proven necessary; no quality-gate bypasses  
**Scale/Scope**: `apps/frontend` source routes and UI, `apps/backend` source query/HTTP contracts, discovery repository projections over existing persisted metadata, and feature docs under `specs/032-source-pages`

## Constitution Check

_GATE: Must pass before Phase 0 research. Re-check after Phase 1 design._

- Monorepo cohesion: Does the plan preserve clear Nx project boundaries and include
  cross-layer contract updates for vertical-slice changes?
- Quality gate enforcement: Are lint, format, type-check, and test gates defined with no
  suppression, bypass, or workaround strategy?
- Full-suite stop rule: Does the plan require `pnpm exec nx run-many -t test --all` to
  pass before any commit and before any AI agent ends work, with no exceptions?
- Coverage stop rule: Does the plan require `pnpm exec nx run-many -t coverage --all`
  to pass before any commit with >= 90% thresholds for every project?
- Test and coverage discipline: Does the plan include automated tests needed to maintain
  > = 90% coverage across affected backend/frontend projects?
- Local-first parity: Can the complete impacted flow run locally via unified Docker
  Compose, and are compose/healthcheck updates identified?
- Data integrity and reliability: Are data provenance, schema/contract versioning, and
  trend/alert regression protections explicitly designed?
- Configuration integrity: Do all new services/pipeline components fail hard on missing
  env vars/credentials (no soft outcomes), and is `docker/compose/local.secrets.env`
  declared as an `env_file` source for any service that requires secrets?
- Documentation fidelity: Does the plan identify all documentation that MUST be added or
  updated for the proposed code and behavior changes?

Initial gate assessment:

- Monorepo cohesion: PASS. The feature stays within existing frontend/backend/persistence boundaries and adds explicit source contracts for the vertical slice.
- Quality gate enforcement: PASS. Plan retains frontend and backend lint/format/typecheck/test gates with no suppressions.
- Full-suite stop rule: PASS. `pnpm exec nx run-many -t test --all` remains a mandatory completion gate before commit and handoff.
- Coverage stop rule: PASS. `pnpm exec nx run-many -t coverage --all` remains a mandatory completion gate before commit.
- Test and coverage discipline: PASS. Plan includes frontend page/component tests plus backend contract and repository coverage for new source query surfaces.
- Local-first parity: PASS. Feature runs on the existing local compose-backed stack and can be manually validated through frontend routes and backend HTTP endpoints.
- Data integrity and reliability: PASS. Source membership is derived from persisted discovery metadata, and source identifiers are explicitly defined to prevent route/list-detail drift.
- Configuration integrity: PASS. No new credentials, secrets, or service env vars are introduced.
- Documentation fidelity: PASS. Spec, plan, research, data model, contracts, quickstart, and follow-on tasks capture feature behavior and documentation touchpoints.

## Project Structure

### Documentation (this feature)

```text
specs/032-source-pages/
├── plan.md              # This file (/speckit.plan command output)
├── research.md          # Phase 0 output (/speckit.plan command)
├── data-model.md        # Phase 1 output (/speckit.plan command)
├── quickstart.md        # Phase 1 output (/speckit.plan command)
├── contracts/           # Phase 1 output (/speckit.plan command)
└── tasks.md             # Phase 2 output (/speckit.tasks command - NOT created by /speckit.plan)
```

### Source Code (repository root)

```text
apps/frontend/src/
├── app/
│   ├── sources/
│   │   ├── page.tsx
│   │   └── [sourceId]/
│   │       ├── page.tsx
│   │       └── not-found.tsx
│   ├── datasets/
│   └── globals.css
├── components/
│   └── discovery/
│       ├── DatasetCatalogList.tsx
│       ├── UnifiedDatasetRow.tsx
│       ├── EmptyState.tsx
│       ├── ErrorState.tsx
│       └── new source-list/detail presentation components
├── lib/
│   └── api/
│       ├── discovery-client.ts
│       └── discovery-types.ts
└── shell/
    ├── navbar-config.ts
    └── site-header.tsx

apps/frontend/tests/
├── source-list-page.test.tsx
├── source-detail-page.test.tsx
├── source-discovery-client.test.ts
└── shell-structure-contract.test.tsx

apps/backend/src/
├── http_api_server.py
├── contract/
│   └── query/
│       └── new source discovery contract models
└── query/
    ├── dataset_discovery_service.py
    ├── dataset_discovery_persisted_repository.py
    └── new source query entrypoints

apps/backend/tests/
└── contract/
    ├── new source-list/detail query contract tests
    └── new HTTP runtime source endpoint tests

specs/032-source-pages/
├── spec.md
├── plan.md
├── research.md
├── data-model.md
├── quickstart.md
└── contracts/
```

**Structure Decision**: Reuse the current discovery architecture and add first-class source routes/contracts on top of the existing persisted metadata model, rather than introducing a separate service or persistence boundary.

## Phase 0: Research and Decisions

- Confirm the canonical source navigation identifier strategy and whether current slugified `source_name` identifiers are sufficient for first-class routes.
- Confirm backend source-list and source-detail contracts that can be composed from the existing persisted discovery repository without schema changes.
- Confirm frontend navigation and presentation patterns that keep source browsing visually aligned with current dataset catalog/detail flows.
- Confirm whether pipeline changes are required or whether current `source_name`/`source_type` persistence guarantees are adequate for this feature.

## Phase 1: Design and Contracts

- Define source-list and source-detail data entities, including route-safe identifier semantics and source-to-dataset membership rules.
- Define HTTP and UI contracts for `/sources` and `/sources/{sourceId}` loaded, empty, error, and not-found states.
- Define manual verification flow covering source list rendering, source detail filtering, dataset navigation, and fallback states in the local stack.
- Update agent context to reflect the added source-discovery planning footprint.

## Phase 2: Implementation Planning

- Extend backend discovery contracts, service methods, repository projections, and HTTP routing to expose source list and source detail payloads.
- Extend frontend discovery types/client methods and add source list/detail routes plus presentation components.
- Integrate source browsing into shell navigation and reuse existing dataset row patterns for source-owned dataset listings.
- Add backend and frontend automated tests for new source contracts, page behavior, and route fallbacks.
- Validate with focused frontend/backend checks, manual local verification, and mandatory full-suite monorepo test and coverage gates.

## Post-Design Constitution Check

- Monorepo cohesion: PASS. Changes remain within existing frontend/backend/persistence boundaries and are delivered as one vertical slice.
- Quality gate enforcement: PASS. Planned work keeps required lint/format/typecheck/test checks intact across both stacks.
- Full-suite stop rule: PASS. Full monorepo test command remains mandatory before commit and handoff.
- Coverage stop rule: PASS. Full monorepo coverage command remains mandatory before commit.
- Test and coverage discipline: PASS. Story coverage includes repository/service/HTTP/backend tests plus frontend page/component/client tests.
- Local-first parity: PASS. The complete flow remains runnable on the existing local stack with no new service additions.
- Data integrity and reliability: PASS. Source browsing is defined over current persisted source attribution and explicitly documents identifier and membership semantics.
- Configuration integrity: PASS. No new credentialed integrations or env vars are introduced.
- Documentation fidelity: PASS. Plan includes full spec-kit artifact coverage and leaves room for AGENTS review if workflow/tooling references change.

## Complexity Tracking

No constitution violations requiring justification.
