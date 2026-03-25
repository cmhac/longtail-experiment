# Implementation Plan: Dataset List Page

**Branch**: `[027-dataset-list-page]` | **Date**: 2026-03-25 | **Spec**: [/Users/hackerc/Projects/longtail-experiment/specs/027-dataset-list-page/spec.md](/Users/hackerc/Projects/longtail-experiment/specs/027-dataset-list-page/spec.md)
**Input**: Feature specification from `/specs/027-dataset-list-page/spec.md`

**Note**: This template is filled in by the `/speckit.plan` command. See `.specify/templates/plan-template.md` for the execution workflow.

## Summary

Deliver a dedicated dataset listing page experience that matches the screenshot direction: a strong page heading, total-series summary, source/category filtering, recency-first sorting, metadata-rich dataset cards, and a request-new-dataset entry point.

Implementation builds on existing discovery frontend surfaces and dataset catalog endpoint, with frontend-led delivery and coordinated backend contract/query updates when needed. No backend schema migration is expected.

## Technical Context

**Language/Version**: Python 3.12 (backend query/runtime), TypeScript 5.x + React 19 in Next.js 15 App Router  
**Primary Dependencies**: Existing backend discovery service/repository surfaces, frontend discovery client/types, dataset catalog components, shell/nav primitives, HeroUI-aligned theme tokens  
**Storage**: PostgreSQL 16 discovery metadata tables consumed through existing backend discovery contracts  
**Testing**: pytest backend contract/query tests, Vitest frontend tests, Biome lint/format checks, TypeScript type checks, Nx monorepo stop-gate suites  
**Target Platform**: Web application (desktop + mobile responsive)
**Project Type**: Cross-layer web application feature spanning frontend listing UX and backend discovery contracts/query composition in Nx monorepo  
**Performance Goals**: Filter and sort interactions update visible list fast enough for interactive browsing (target: under 2 seconds for normal catalog loads)  
**Constraints**: Preserve existing dataset detail navigation behavior, maintain empty/error fallback usability, and keep backend contract changes backward-compatible where feasible  
**Scale/Scope**: One datasets page vertical slice with related discovery component/style/test updates and conditional backend query/contract updates if required by filtering/sorting behavior

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

- Monorepo cohesion: PASS - scope remains a coherent frontend-led vertical slice with backend updates allowed when required.
- Quality gate enforcement: PASS - no suppression or bypass strategy is introduced.
- Full-suite stop rule: PASS - `pnpm exec nx run-many -t test --all` is required before commit/handoff.
- Coverage stop rule: PASS - `pnpm exec nx run-many -t coverage --all` is required before commit.
- Test and coverage discipline: PASS - includes story-level tests for dataset list rendering, controls, and actions.
- Local-first parity: PASS - feature runs through existing frontend runtime and compose-backed local stack.
- Data integrity and reliability: PASS - no schema changes; listing behavior depends on existing discovery data contracts.
- Configuration integrity: PASS - no new credential-requiring service components are introduced.
- Documentation fidelity: PASS - plan/research/data-model/contract/quickstart/tasks are part of this feature scope.

Post-design re-check: PASS on all gates.

## Project Structure

### Documentation (this feature)

```text
specs/027-dataset-list-page/
├── plan.md
├── research.md
├── data-model.md
├── quickstart.md
├── contracts/
│   └── dataset-list-page-contract.md
└── tasks.md
```

### Source Code (repository root)

```text
apps/
├── backend/
│   ├── src/
│   │   ├── http_api_server.py
│   │   ├── contract/query/
│   │   └── query/
│   └── tests/
│       └── contract/
└── frontend/
    ├── src/
    │   ├── app/
    │   │   └── datasets/page.tsx
    │   ├── components/discovery/
    │   │   ├── DatasetCatalogList.tsx
    │   │   ├── DatasetCard.tsx
    │   │   ├── EmptyState.tsx
    │   │   └── DatasetListControls.tsx
    │   ├── lib/api/
    │   │   ├── discovery-client.ts
    │   │   └── discovery-types.ts
    │   └── app/globals.css
    └── tests/
        ├── datasets-page.test.tsx
        ├── discovery-client.test.ts
        └── shell-structure-contract.test.tsx
```

      **Structure Decision**: Reuse the existing datasets route and discovery component surfaces, extending them with list-control orchestration and card metadata guarantees. Backend contract/query surfaces may be updated when necessary to satisfy frontend requirements.

## Phase 0 Research Outcomes

See /Users/hackerc/Projects/longtail-experiment/specs/027-dataset-list-page/research.md.

- Keep discovery behavior list-first and scan-oriented with strong metadata hierarchy.
- Consolidate source/category/sort controls in one stable toolbar contract.
- Preserve graceful empty/error states as non-blocking list outcomes.

## Phase 1 Design Artifacts

- Data model: /Users/hackerc/Projects/longtail-experiment/specs/027-dataset-list-page/data-model.md
- Interface contract: /Users/hackerc/Projects/longtail-experiment/specs/027-dataset-list-page/contracts/dataset-list-page-contract.md
- Quickstart: /Users/hackerc/Projects/longtail-experiment/specs/027-dataset-list-page/quickstart.md
- Agent context update command: `.specify/scripts/bash/update-agent-context.sh codex`

## Implementation Phases

### Phase 2 Delivery Plan

1. Refactor datasets page composition around a clear title/summary/controls/list hierarchy.
2. Extend list control behavior to support source/category filters plus recency-focused sort, including backend query/contract updates if existing payloads are insufficient.
3. Upgrade dataset cards to include source badge, summary text, tags, last-updated context, and action affordances.
4. Implement deterministic empty-results behavior for filter combinations with no matches.
5. Preserve request-new-dataset call-to-action discoverability and routing from the listing page.
6. Add and update frontend tests plus backend contract tests (if backend changes are introduced) for card metadata guarantees and control behavior.
7. Run required monorepo stop-gate commands before commit/handoff.

## Verification Plan

- Focused checks during implementation:
  - `pnpm --dir apps/frontend test -- tests/datasets-page.test.tsx tests/home-page.test.tsx tests/discovery-client.test.ts`
  - `uv run --project apps/backend pytest --no-cov apps/backend/tests/contract`
  - `pnpm --dir apps/frontend typecheck`
  - `pnpm --dir apps/frontend exec biome check .`
- Required final gates before commit/handoff:
  - `pnpm exec nx run-many -t test --all`
  - `pnpm exec nx run-many -t coverage --all`

## Complexity Tracking

No constitution violations or exceptional complexity justifications are required for this plan.
