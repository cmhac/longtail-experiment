# Implementation Plan: Unified Search Page Experience

**Branch**: `[030-unified-search-page]` | **Date**: 2026-03-25 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/specs/030-unified-search-page/spec.md`

**Note**: This template is filled in by the `/speckit.plan` command. See `.specify/templates/plan-template.md` for the execution workflow.

## Summary

Deliver a single unified search interaction used by homepage, a new dedicated search route, and an expandable navbar search control. The plan reuses existing discovery search/suggestion contracts, refactors entry-point UI into a shared search surface primitive, and routes all query submission flows to the dedicated search page while preserving current result ranking and summary behavior.

## Technical Context

**Language/Version**: TypeScript 5.x + React 19 (Next.js 15 App Router), Python 3.12 backend contracts unchanged  
**Primary Dependencies**: Next.js routing primitives, existing discovery API client/types, HeroUI-aligned shell/theme tokens  
**Storage**: N/A for new persistence; existing PostgreSQL-backed discovery search source remains unchanged  
**Testing**: Vitest + Testing Library for frontend component/page contracts, TypeScript noEmit, Biome checks  
**Target Platform**: Responsive web (desktop + mobile) within existing frontend shell
**Project Type**: Web application (frontend-first vertical slice over existing backend search endpoints)  
**Performance Goals**: Preserve current search response behavior and avoid adding additional blocking network calls during submit flow  
**Constraints**: Maintain existing result relevance/summary contract; no regressions to shell navigation accessibility; no lint/type/test gate bypasses  
**Scale/Scope**: Frontend discovery and shell navigation surfaces (`/`, new dedicated search route, navbar control) with existing backend contract reuse

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

- Monorepo cohesion: PASS. Changes are contained to `apps/frontend` with contract documentation updates under `specs/030-unified-search-page/contracts`.
- Quality gate enforcement: PASS. Plan includes biome/typecheck/test + full monorepo gate execution before handoff.
- Full-suite stop rule: PASS. `pnpm exec nx run-many -t test --all` is a mandatory completion gate.
- Coverage stop rule: PASS. `pnpm exec nx run-many -t coverage --all` is a mandatory completion gate.
- Test and coverage discipline: PASS. New/updated tests will cover homepage routing behavior, dedicated search route render states, and navbar expansion/submit behavior.
- Local-first parity: PASS. Feature is frontend behavior over existing local stack services; manual browser/API validation remains required.
- Data integrity and reliability: PASS. Existing search result and summary contracts remain source-of-truth; no schema changes.
- Configuration integrity: PASS. No new credentials, services, or env vars introduced.
- Documentation fidelity: PASS. Spec artifacts and quickstart validation steps will capture behavior deltas.

## Project Structure

### Documentation (this feature)

```text
specs/030-unified-search-page/
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
│   ├── page.tsx
│   ├── search/
│   │   └── page.tsx
│   └── api/
│       └── datasets/
│           └── search/
├── components/
│   ├── home/
│   ├── shell/
│   └── search/
├── services/
│   └── discovery/
└── theme/

apps/frontend/tests/
├── home-page.test.tsx
├── shell-structure-contract.test.tsx
├── search-page.test.tsx
└── search-surface-contract.test.tsx

specs/030-unified-search-page/
├── spec.md
├── plan.md
├── research.md
├── data-model.md
├── quickstart.md
└── contracts/
```

**Structure Decision**: Use the existing Next.js frontend project structure and introduce a dedicated `app/search` route plus reusable search UI primitives under `components/search`. Keep backend/repository code untouched and document user-facing behavior via spec contracts.

## Phase 0: Research and Decisions

- Confirm query-state transport strategy for route-based search (URL query parameter as canonical navigation context).
- Confirm reusable search surface boundaries (shared interaction component with entry-point wrappers for homepage and navbar presentation modes).
- Confirm dedicated search page layout parity requirements against existing homepage search/results hierarchy.
- Confirm failure/empty behavior contract for no query, no results, and backend errors.

## Phase 1: Design and Contracts

- Define UI state model for shared search surface, navbar expansion state, and dedicated search page state.
- Define UI-level contract documenting route/query synchronization, submit behavior, and result/suggestion rendering expectations.
- Define manual verification flow covering homepage submit, navbar submit, search refinement, responsive behavior, and error states.
- Update agent context to reflect this feature's technology footprint and contract emphasis.

## Phase 2: Implementation Planning

- Refactor homepage search to submit via route transition and remove inline execution path.
- Add dedicated search route that renders centered search surface and existing results presentation stack.
- Replace navbar icon control with compact-expand search component sharing the same submit/suggestion contract.
- Add/adjust frontend tests for routing behavior, search-page rendering states, and navbar interaction states.
- Validate via focused frontend checks, manual local run, and mandatory full-suite monorepo test and coverage gates.

## Post-Design Constitution Check

- Monorepo cohesion: PASS. Changes remain inside frontend app + spec docs; no boundary drift.
- Quality gate enforcement: PASS. Plan explicitly requires biome/typecheck/tests and full monorepo stop gates.
- Full-suite stop rule: PASS. Required command retained as non-optional completion criterion.
- Coverage stop rule: PASS. Coverage stop gate retained as non-optional completion criterion.
- Test and coverage discipline: PASS. Contract and behavior tests are included for all new interaction pathways.
- Local-first parity: PASS. Feature remains runnable in existing compose-backed local stack with frontend dev server.
- Data integrity and reliability: PASS. Search result contract and summary semantics preserved; no schema/version changes.
- Configuration integrity: PASS. No new secrets or env vars added.
- Documentation fidelity: PASS. Plan includes spec artifacts and quickstart verification updates.

## Complexity Tracking

No constitution violations requiring justification.
