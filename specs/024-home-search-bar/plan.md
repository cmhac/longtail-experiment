# Implementation Plan: Homepage Search Bar Experience

**Branch**: `024-home-search-bar` | **Date**: 2026-03-24 | **Spec**: [/Users/hackerc/Projects/longtail-experiment/specs/024-home-search-bar/spec.md](/Users/hackerc/Projects/longtail-experiment/specs/024-home-search-bar/spec.md)
**Input**: Feature specification from `/Users/hackerc/Projects/longtail-experiment/specs/024-home-search-bar/spec.md`

**Note**: This template is filled in by the `/speckit.plan` command. See `.specify/templates/plan-template.md` for the execution workflow.

## Summary

Deliver a centered, prominent homepage search surface with two integrated data experiences: a runtime aggregate scope line showing active dataset/source counts, and a typing-time likely-match dropdown for fast discovery.

The implementation spans frontend presentation and interaction updates plus backend aggregation/suggestion contract extensions. Existing discovery APIs and homepage search wiring will be extended to provide summary totals and suggestion payloads while preserving current search and recent updates behavior.

## Technical Context

<!--
  ACTION REQUIRED: Replace the content in this section with the technical details
  for the project. The structure here is presented in advisory capacity to guide
  the iteration process.
-->

**Language/Version**: Python 3.12 (backend query/runtime), TypeScript 5.x + React 19 + Next.js 15 (frontend)  
**Primary Dependencies**: existing backend discovery service/repository surfaces, PostgreSQL 16 dataset metadata store, frontend discovery client, HeroUI-aligned shell styling  
**Storage**: PostgreSQL 16 canonical/discovery tables with trigram-enabled text matching support for likely suggestions  
**Testing**: pytest contract/query tests (backend), Vitest component/page/client tests (frontend), required monorepo stop-gate suites  
**Target Platform**: Local-first monorepo runtime (Docker Compose + Next.js app + backend API server)
**Project Type**: Cross-layer web application feature spanning backend query contracts and frontend homepage UX  
**Performance Goals**: Suggestion updates return quickly enough to support interactive typing and maintain discovery usability targets  
**Constraints**: Preserve existing dataset search route compatibility, keep graceful fallback when summary/suggestions are unavailable, maintain constitution quality and coverage gates  
**Scale/Scope**: Single feature slice across homepage discovery UX, backend aggregation endpoint(s), and API client contract extensions

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

- Monorepo cohesion: PASS - scope is a coherent backend+frontend vertical slice with explicit contract updates.
- Quality gate enforcement: PASS - lint/format/typecheck/test/coverage are required with no suppression strategy.
- Full-suite stop rule: PASS - `pnpm exec nx run-many -t test --all` required before commit/handoff.
- Coverage stop rule: PASS - `pnpm exec nx run-many -t coverage --all` required before commit.
- Test and coverage discipline: PASS - includes new backend and frontend tests for summary counts and suggestion behavior.
- Local-first parity: PASS - feature runs in existing local compose stack and frontend runtime.
- Data integrity and reliability: PASS - aggregate counts and suggestion contracts are explicit and validated.
- Configuration integrity: PASS - no new credential-dependent service introduced.
- Documentation fidelity: PASS - plan includes contract and quickstart updates for new homepage search behavior.

Post-design re-check: PASS on all gates. No constitution violations identified.

## Phase 0 Research Outcomes

See `/Users/hackerc/Projects/longtail-experiment/specs/024-home-search-bar/research.md`.

- Selected backend response-shape extension strategy for summary counts and likely-match suggestions.
- Selected suggestion query behavior grounded in trigram similarity and current discovery semantics.
- Selected frontend interaction model for centered search surface and dynamic dropdown updates.

## Phase 1 Design Artifacts

- Data model: `/Users/hackerc/Projects/longtail-experiment/specs/024-home-search-bar/data-model.md`
- Interface contract: `/Users/hackerc/Projects/longtail-experiment/specs/024-home-search-bar/contracts/homepage-search-contract.md`
- Quickstart: `/Users/hackerc/Projects/longtail-experiment/specs/024-home-search-bar/quickstart.md`
- Agent context update executed via `.specify/scripts/bash/update-agent-context.sh codex`

## Project Structure

### Documentation (this feature)

```text
specs/024-home-search-bar/
├── plan.md
├── research.md
├── data-model.md
├── quickstart.md
├── contracts/
│   └── homepage-search-contract.md
└── tasks.md
```

### Source Code (repository root)

<!--
  ACTION REQUIRED: Replace the placeholder tree below with the concrete layout
  for this feature. Delete unused options and expand the chosen structure with
  real paths (e.g., apps/admin, packages/something). The delivered plan must
  not include Option labels.
-->

```text
apps/
├── backend/
│   ├── src/
│   │   ├── contract/query/
│   │   ├── query/
│   │   └── http_api_server.py
│   └── tests/
│       ├── contract/
│       └── query/
└── frontend/
    ├── src/
    │   ├── app/page.tsx
    │   ├── components/discovery/
    │   └── lib/api/
    └── tests/
        ├── home-page.test.tsx
        ├── DatasetSearchBox*.test.tsx
        └── discovery-client.test.ts
```

**Structure Decision**: Use existing discovery query/API/client surfaces and homepage component composition. This avoids adding new services while preserving current discovery architecture boundaries.

## Implementation Phases

### Phase 2 Delivery Plan

1. Extend backend discovery contract(s) to expose homepage summary counts and likely-match suggestions.
2. Implement repository/service query paths for active dataset/source aggregation and likely-match generation.
3. Wire new backend route behavior into the API handler with error-safe fallback semantics.
4. Extend frontend discovery client/types for summary and suggestion payloads.
5. Redesign homepage search section to centered prominent layout with minimal scope text and dynamic values.
6. Add typing-time suggestion dropdown behavior and stale-result prevention in search interactions.
7. Add backend and frontend tests validating aggregates, suggestions, rendering, and graceful fallbacks.
8. Run required quality gates and full monorepo stop-gate commands.

## Verification Plan

- Focused checks while developing:
  - backend query/contract tests for summary + suggestion responses
  - frontend unit/integration tests for search bar layout and dropdown behavior
  - local API/manual query checks for aggregate numbers and likely-match ordering
- Required final gates before commit/handoff:
  - `pnpm exec nx run-many -t test --all`
  - `pnpm exec nx run-many -t coverage --all`

## Complexity Tracking

No constitution violations or exceptional complexity justifications are required for this plan.
