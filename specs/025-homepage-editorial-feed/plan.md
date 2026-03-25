# Implementation Plan: Home Page Editorial Feed

**Branch**: `025-homepage-editorial-feed` | **Date**: 2026-03-25 | **Spec**: [/Users/hackerc/Projects/longtail-experiment/specs/025-homepage-editorial-feed/spec.md](/Users/hackerc/Projects/longtail-experiment/specs/025-homepage-editorial-feed/spec.md)
**Input**: Feature specification from `/Users/hackerc/Projects/longtail-experiment/specs/025-homepage-editorial-feed/spec.md`

**Note**: This template is filled in by the `/speckit.plan` command. See `.specify/templates/plan-template.md` for the execution workflow.

## Summary

Implement the first production-quality home page recent updates feed as an editorial list surface with strong hierarchy, recency cue, structured row metadata, and consistent row actions.

The delivery will preserve current search behavior while replacing the current card-style recent section presentation with an editorial layout. Existing recent-updates data contracts and frontend types will be extended where needed so each row can render source/date, title, concise body copy, and action destinations without breaking existing discovery flows.

## Technical Context

**Language/Version**: TypeScript 5.x + React 19 + Next.js 15 (frontend), Python 3.12 (backend discovery contract/repository surfaces)  
**Primary Dependencies**: Existing homepage shell components, discovery API client/types, persisted discovery repository/service, HeroUI-aligned theme tokens  
**Storage**: PostgreSQL 16 discovery metadata tables (existing recent-updates source)  
**Testing**: Vitest component/page tests (frontend), pytest contract/runtime tests (backend), monorepo stop-gate suites via Nx  
**Target Platform**: Local-first monorepo runtime (Docker Compose backend + Next.js frontend)  
**Project Type**: Cross-layer web application feature (UI presentation + API contract refinement)  
**Performance Goals**: Preserve current homepage render responsiveness while displaying up to five editorial rows and action links without visible jank  
**Constraints**: Keep existing search hero behavior unchanged, maintain recency-first ordering semantics, avoid regressions in current dataset detail and catalog flows  
**Scale/Scope**: One homepage section redesign with supporting contract/type updates and validation tests

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

- Monorepo cohesion: PASS - scope is a vertical slice across existing frontend and backend discovery boundaries.
- Quality gate enforcement: PASS - lint/format/typecheck/test/coverage gates remain mandatory with no suppression plan.
- Full-suite stop rule: PASS - `pnpm exec nx run-many -t test --all` required before commit/handoff.
- Coverage stop rule: PASS - `pnpm exec nx run-many -t coverage --all` required before commit.
- Test and coverage discipline: PASS - includes frontend and backend contract/runtime tests to preserve >=90% thresholds.
- Local-first parity: PASS - feature runs in existing local stack with no new services.
- Data integrity and reliability: PASS - recency ordering and feed payload semantics remain explicit and tested.
- Configuration integrity: PASS - no new secret-dependent services introduced.
- Documentation fidelity: PASS - plan defines spec artifacts, contract documentation, quickstart, and agent context update.

Post-design re-check: PASS on all constitution gates.

## Phase 0 Research Outcomes

See /Users/hackerc/Projects/longtail-experiment/specs/025-homepage-editorial-feed/research.md.

- Selected editorial row information hierarchy and recency label behavior for homepage readability.
- Selected contract-shape alignment approach so recent feed rows can include summary copy and action targets.
- Selected responsive layout and fallback behavior for empty/partial data states.

## Phase 1 Design Artifacts

- Data model: /Users/hackerc/Projects/longtail-experiment/specs/025-homepage-editorial-feed/data-model.md
- Interface contract: /Users/hackerc/Projects/longtail-experiment/specs/025-homepage-editorial-feed/contracts/homepage-editorial-feed-contract.md
- Quickstart: /Users/hackerc/Projects/longtail-experiment/specs/025-homepage-editorial-feed/quickstart.md
- Agent context update executed via .specify/scripts/bash/update-agent-context.sh codex

## Project Structure

### Documentation (this feature)

```text
specs/025-homepage-editorial-feed/
├── plan.md
├── research.md
├── data-model.md
├── quickstart.md
├── contracts/
│   └── homepage-editorial-feed-contract.md
└── tasks.md
```

### Source Code (repository root)

```text
apps/
├── frontend/
│   ├── src/
│   │   ├── app/page.tsx
│   │   ├── app/globals.css
│   │   ├── components/discovery/RecentUpdatesFeed.tsx
│   │   ├── components/discovery/DatasetCard.tsx
│   │   └── lib/api/
│   │       ├── discovery-types.ts
│   │       └── discovery-client.ts
│   └── tests/
│       ├── RecentUpdatesFeed.test.tsx
│       ├── DatasetCard.test.tsx
│       └── home-page.test.tsx
└── backend/
    ├── src/
    │   ├── contract/query/
    │   ├── query/dataset_discovery_service.py
    │   ├── query/dataset_discovery_persisted_repository.py
    │   └── http_api_server.py
    └── tests/
        └── contract/
```

**Structure Decision**: [Document the selected structure and reference the real
directories captured above]

**Structure Decision**: Reuse existing homepage and discovery query surfaces to implement the editorial feed as a focused vertical enhancement without adding new projects or service boundaries.

## Implementation Phases

### Phase 2 Delivery Plan

1. Define the editorial feed row presentation contract for homepage consumption, including recency cue and row action semantics.
2. Refine recent-updates backend payload shape as needed to include all feed row fields required by the specification.
3. Update frontend discovery types/client mapping for editorial row fields while preserving compatibility with existing search flows.
4. Replace current card-based recent section rendering with editorial row layout and hierarchy.
5. Implement row-level action link rendering and destination wiring for View Table and Download CSV.
6. Add responsive and theme-safe styling for editorial rows, including recency label treatment.
7. Add/extend frontend and backend tests for populated, empty, and partial-data feed states.
8. Execute required quality gates and monorepo stop rules before handoff or commit.

## Verification Plan

- Focused checks during development:
  - Frontend component tests for feed structure, row metadata, and action labels.
  - Homepage render tests for editorial section presence and search coexistence.
  - Backend contract/runtime tests for recent endpoint ordering and payload completeness.
- Required final gates before commit/handoff:
  - `pnpm exec nx run-many -t test --all`
  - `pnpm exec nx run-many -t coverage --all`

## Complexity Tracking

No constitution violations or exceptional complexity justifications are required for this plan.
