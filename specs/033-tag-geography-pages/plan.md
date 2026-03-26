# Implementation Plan: Tag and Geography Discovery Pages

**Branch**: `[033-tag-geography-pages]` | **Date**: 2026-03-25 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/specs/033-tag-geography-pages/spec.md`

**Note**: This template is filled in by the `/speckit.plan` command. See `.specify/templates/plan-template.md` for the execution workflow.

## Summary

Add first-class topic-tag and geography browsing to discovery by turning existing metadata pills into navigable links and introducing dedicated metadata detail pages that list the datasets associated with the selected topic or geography. The plan extends the current persisted discovery repository, query service, HTTP routes, frontend discovery client/types, and Next.js routes using the same vertical-slice pattern already used for source discovery.

## Technical Context

**Language/Version**: TypeScript 5.x + React 19 (Next.js 15 App Router), Python 3.12 backend query layer, existing pipeline contracts/persistence semantics  
**Primary Dependencies**: Existing discovery API client/types, Next.js routing primitives, existing dataset list/detail components, backend dataset discovery service/repository surfaces  
**Storage**: Existing PostgreSQL 16 discovery metadata in `data_series`, `topic_tags`, `data_series_topic_tags`, `source_profiles`, and `observations`; no new datastore expected  
**Testing**: Vitest + Testing Library for frontend page/component/client coverage, pytest contract/integration coverage for backend query and HTTP surfaces, existing Nx/Biome/TypeScript/Python quality gates  
**Target Platform**: Responsive web discovery experience in the existing shell, backed by the local compose-backed backend runtime  
**Project Type**: Web application vertical slice spanning frontend and backend discovery layers, with pipeline/persistence compatibility validation  
**Performance Goals**: Topic and geography detail pages preserve current catalog-scale responsiveness for dozens of sources and hundreds to low thousands of datasets without noticeably slower browsing than existing catalog and source pages  
**Constraints**: Preserve existing dataset/source routes and behavior; keep metadata navigation stable across list/detail contexts; avoid schema churn unless implementation proves current persisted metadata is insufficient; no quality-gate bypasses  
**Scale/Scope**: `apps/frontend` metadata detail routes and pill-link rendering, `apps/backend` metadata query/HTTP contracts, discovery repository projections over existing persisted metadata, and feature docs under `specs/033-tag-geography-pages`

## Constitution Check

_GATE: Must pass before Phase 0 research. Re-check after Phase 1 design._

- Monorepo cohesion: Does the plan preserve clear Nx project boundaries and include cross-layer contract updates for vertical-slice changes?
- Quality gate enforcement: Are lint, format, type-check, and test gates defined with no suppression, bypass, or workaround strategy?
- Full-suite stop rule: Does the plan require `pnpm exec nx run-many -t test --all` to pass before any commit and before any AI agent ends work, with no exceptions?
- Coverage stop rule: Does the plan require `pnpm exec nx run-many -t coverage --all` to pass before any commit with >= 90% thresholds for every project?
- Test and coverage discipline: Does the plan include automated tests needed to maintain >= 90% coverage across affected backend/frontend projects?
- Local-first parity: Can the complete impacted flow run locally via unified Docker Compose, and are compose/healthcheck updates identified?
- Data integrity and reliability: Are data provenance, schema/contract versioning, and trend/alert regression protections explicitly designed?
- Configuration integrity: Do all new services/pipeline components fail hard on missing env vars/credentials (no soft outcomes), and is `docker/compose/local.secrets.env` declared as an `env_file` source for any service that requires secrets?
- Documentation fidelity: Does the plan identify all documentation that MUST be added or updated for the proposed code and behavior changes?

Initial gate assessment:

- Monorepo cohesion: PASS. The feature stays within existing frontend/backend/persistence boundaries and extends current discovery contracts as one vertical slice.
- Quality gate enforcement: PASS. The plan retains frontend and backend lint/format/typecheck/test gates with no suppressions.
- Full-suite stop rule: PASS. `pnpm exec nx run-many -t test --all` remains a mandatory completion gate before commit and handoff.
- Coverage stop rule: PASS. `pnpm exec nx run-many -t coverage --all` remains a mandatory completion gate before commit.
- Test and coverage discipline: PASS. The plan includes frontend page/component/client coverage plus backend contract/repository/service/HTTP coverage for the new metadata routes.
- Local-first parity: PASS. The flow runs on the existing local compose-backed stack with no new service additions.
- Data integrity and reliability: PASS. Topic membership remains grounded in persisted normalized tags, and geography membership remains grounded in persisted discovery-facing geography labels with explicit route-identity rules.
- Configuration integrity: PASS. No new credentialed integrations or env vars are introduced.
- Documentation fidelity: PASS. Plan includes spec-kit artifacts and expects AGENTS review only if canonical workflow or tool references change.

## Project Structure

### Documentation (this feature)

```text
specs/033-tag-geography-pages/
├── plan.md
├── research.md
├── data-model.md
├── quickstart.md
├── contracts/
│   └── metadata-discovery-contract.md
└── tasks.md
```

### Source Code (repository root)

```text
apps/frontend/src/
├── app/
│   ├── datasets/
│   │   └── [id]/
│   │       └── page.tsx
│   ├── sources/
│   ├── topics/
│   │   └── [topicId]/
│   │       ├── page.tsx
│   │       └── not-found.tsx
│   ├── geographies/
│   │   └── [geographyId]/
│   │       ├── page.tsx
│   │       └── not-found.tsx
│   └── globals.css
├── components/
│   └── discovery/
│       ├── DatasetCatalogList.tsx
│       ├── DatasetDetailHeader.tsx
│       ├── UnifiedDatasetRow.tsx
│       ├── DiscoveryListPageHeader.tsx
│       └── new metadata detail header/pill-link helpers if needed
├── lib/
│   └── api/
│       ├── discovery-client.ts
│       └── discovery-types.ts
└── tests/

apps/backend/src/
├── contract/
│   └── query/
│       └── new metadata discovery query contracts
├── query/
│   ├── dataset_discovery_service.py
│   ├── dataset_discovery_persisted_repository.py
│   └── new topic/geography query entrypoints
└── http_api_server.py

apps/backend/tests/
└── contract/
    ├── new topic/geography query contract tests
    └── new HTTP runtime metadata endpoint tests

apps/pipeline/src/
└── existing metadata persistence paths verified for compatibility
```

**Structure Decision**: Reuse the current discovery architecture and source-detail implementation pattern, adding metadata-specific detail routes and contracts on top of the existing persisted metadata model rather than creating a new service or persistence boundary.

## Phase 0: Research and Decisions

- Confirm route and endpoint naming for metadata-driven browsing with dedicated detail pages but no index pages.
- Confirm topic identity and geography identity strategies using route-safe slugs derived from visible labels.
- Confirm that current topic-tag persistence and current discovery-facing geography labels are sufficient without immediate schema additions.
- Confirm UI and contract reuse patterns from existing source detail and dataset list implementations.

## Phase 1: Design and Contracts

- Define topic detail and geography detail entities, including label, slug, dataset count, and dataset membership rules.
- Define HTTP and UI contracts for `/topics/{topicId}` and `/geographies/{geographyId}` including loaded, empty, error, and not-found states.
- Define manual verification covering pill navigation, metadata detail rendering, dataset onward navigation, and fallback states in the local stack.
- Update agent context to reflect the added metadata-discovery planning footprint.

## Phase 2: Implementation Planning

- Extend backend discovery contracts, service methods, repository projections, and HTTP routing to expose topic detail and geography detail payloads.
- Extend frontend discovery types/client methods and add topic/geography routes plus any shared metadata detail presentation components.
- Update dataset list rows and dataset detail header pills to render stable metadata links.
- Add backend and frontend automated tests for metadata contracts, page behavior, pill navigation, and route fallbacks.
- Validate with focused frontend/backend checks, manual local verification, and mandatory full-suite monorepo test and coverage gates.

## Post-Design Constitution Check

- Monorepo cohesion: PASS. Changes remain within existing frontend/backend/persistence boundaries and are delivered as one vertical slice.
- Quality gate enforcement: PASS. Planned work keeps required lint/format/typecheck/test checks intact across both stacks.
- Full-suite stop rule: PASS. Full monorepo test command remains mandatory before commit and handoff.
- Coverage stop rule: PASS. Full monorepo coverage command remains mandatory before commit.
- Test and coverage discipline: PASS. Story coverage includes repository/service/query/HTTP/backend tests plus frontend page/component/client tests.
- Local-first parity: PASS. The complete flow remains runnable on the existing local stack with no new services.
- Data integrity and reliability: PASS. Topic and geography browsing are defined over persisted discovery metadata with explicit route-identity semantics and no hidden membership rules.
- Configuration integrity: PASS. No new credentialed integrations or env vars are introduced.
- Documentation fidelity: PASS. Plan includes full spec-kit artifact coverage and leaves room for AGENTS review if canonical workflow or commands change.

## Complexity Tracking

No constitution violations requiring justification.
