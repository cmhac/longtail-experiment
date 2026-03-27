# Implementation Plan: Discovery Pagination Rollout

**Branch**: `[034-api-pagination-rollout]` | **Date**: 2026-03-25 | **Spec**: [/Users/hackerc/Projects/longtail-experiment/specs/034-api-pagination-rollout/spec.md](/Users/hackerc/Projects/longtail-experiment/specs/034-api-pagination-rollout/spec.md)
**Input**: Feature specification from `/specs/034-api-pagination-rollout/spec.md`

**Note**: This template is filled in by the `/speckit.plan` command. See `.specify/templates/plan-template.md` for the execution workflow.

## Summary

Implement consistent page-based pagination for all discovery list routes across backend and frontend, replacing oversized single-page fetch behavior and unpaginated detail-list responses. The approach standardizes route query parameters and response metadata, updates repository/service/query layers to honor pagination with stable ordering, adds frontend page-state controls synchronized with URL/query state, and extends contracts/tests to enforce validation and cross-layer consistency.

## Technical Context

<!--
  ACTION REQUIRED: Replace the content in this section with the technical details
  for the project. The structure here is presented in advisory capacity to guide
  the iteration process.
-->

**Language/Version**: Python 3.12 (backend), TypeScript 5.x + React 19 (frontend)  
**Primary Dependencies**: SQLAlchemy query repository and service orchestration in backend; Next.js App Router discovery client/pages/components in frontend  
**Storage**: PostgreSQL 16 discovery metadata tables and observations  
**Testing**: pytest (backend contract/runtime), Vitest (frontend page/client/component), Nx run-many quality gates  
**Target Platform**: Local Docker Compose stack and Next.js server-rendered web UI
**Project Type**: Nx monorepo web application (backend service + frontend application)  
**Performance Goals**: Reduce per-request list payload size to configured page-size boundaries and preserve stable user-facing navigation across large result sets  
**Constraints**: No quality-gate bypass; preserve existing filter/sort semantics; maintain >=90% coverage; no contract-breaking undocumented route behavior changes  
**Scale/Scope**: Cross-cutting updates across discovery backend list routes, query contracts, frontend list pages, shared client types, and associated tests

## Constitution Check

_GATE: Must pass before Phase 0 research. Re-check after Phase 1 design._

- Monorepo cohesion: PASS - Plan keeps changes within existing Nx app boundaries (`apps/backend`, `apps/frontend`) and updates contracts/types jointly.
- Quality gate enforcement: PASS - Plan requires existing lint/format/typecheck/test gates with no suppression strategy.
- Full-suite stop rule: PASS - Plan requires `pnpm exec nx run-many -t test --all` before commit and before agent stop.
- Coverage stop rule: PASS - Plan requires `pnpm exec nx run-many -t coverage --all` before commit with >=90% project thresholds.
- Test and coverage discipline: PASS - Plan adds backend contract/runtime and frontend integration assertions for pagination behavior and validation.
- Local-first parity: PASS - Affected flow remains runnable in existing unified Docker Compose stack; no new services expected.
- Data integrity and reliability: PASS - Stable ordering and metadata contract consistency are explicit to prevent duplicate/skip regressions.
- Configuration integrity: PASS - No new credentialed services/components introduced; existing fail-fast credential policy unchanged.
- Documentation fidelity: PASS - Plan includes updates for feature docs/contracts and AGENTS-aligned workflow references if command surfaces change.

## Project Structure

### Documentation (this feature)

```text
specs/034-api-pagination-rollout/
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
│   │   ├── contract/query/
│   │   ├── query/
│   │   └── http_api_server.py
│   └── tests/contract/
└── frontend/
    ├── src/
    │   ├── app/
    │   │   ├── datasets/
    │   │   ├── search/
    │   │   ├── sources/
    │   │   ├── topics/
    │   │   └── geographies/
    │   ├── components/discovery/
    │   └── lib/api/
    └── tests/
```

**Structure Decision**: Use existing backend/frontend Nx application boundaries and discovery module locations to deliver one vertical-slice pagination rollout with synchronized contract and UI behavior updates.

## Phase Plan

### Phase 0: Research and Scope Lock

- Confirm complete inventory of in-scope list routes and any explicit exclusions.
- Finalize pagination contract invariants and validation policy.
- Lock deterministic ordering expectations per route.

### Phase 1: Design and Contract Finalization

- Finalize request/response pagination model and route coverage matrix.
- Finalize frontend pagination state transitions for navigation, filter/query changes, and out-of-range handling.
- Complete artifacts: `research.md`, `data-model.md`, `contracts/`, `quickstart.md`.

### Phase 2: Implementation Planning

- Backend workstreams:
  - Extend/align list-route contracts and query entrypoints.
  - Apply validated page/page-size handling on currently unpaginated list routes.
  - Preserve stable ordering and aggregate metadata behavior.
- Frontend workstreams:
  - Replace oversized one-page fetch behavior with explicit page-based requests.
  - Add pagination controls/state synchronization in list views.
  - Preserve existing empty/error states.
- Testing workstreams:
  - Backend contract/runtime tests for pagination metadata and bounds.
  - Frontend integration/client tests for page navigation and parameter wiring.
- Documentation workstreams:
  - Update affected discovery contract docs and workflow docs for any route exclusions.

## Implementation Notes and Sequencing Checkpoints

- Complete shared pagination primitives first: validator bounds, metadata mapping helper, and query param parsing helper.
- Land backend route pagination contract updates before frontend type updates that depend on new response shapes.
- Land frontend page-state serialization helpers before page-level pagination control wiring.
- Keep route ordering deterministic before enabling page transitions in UI to avoid duplicate/skip regressions.

### Checkpoint A - Foundation Ready

- Shared pagination helpers exist in backend validators/service and frontend client.
- Foundational validator/client tests pass.

### Checkpoint B - Backend Route Coverage

- In-scope backend list routes emit consistent pagination metadata.
- Backend contract/runtime tests for route pagination pass.

### Checkpoint C - Frontend Route Alignment

- In-scope frontend list pages request explicit page/page_size values.
- Page controls and URL/query state remain synchronized.

### Checkpoint D - Regression Hardening

- Filter/sort/empty/error scenarios remain stable under pagination.
- Full monorepo tests and coverage gates pass.

## Post-Design Constitution Re-Check

- Monorepo cohesion: PASS - Design keeps vertical-slice updates inside existing backend/frontend modules with shared contract coverage.
- Quality gates and stop rules: PASS - Design explicitly preserves full-suite test and coverage stop gates before commit/handoff.
- Coverage discipline: PASS - Design includes backend and frontend automated coverage for new pagination behavior.
- Local-first parity: PASS - No new runtime surfaces beyond existing compose-managed stack.
- Data integrity/reliability: PASS - Stable ordering and scoped totals are modeled as explicit invariants.
- Configuration integrity: PASS - No new credentialed components introduced.
- Documentation fidelity: PASS - Contracts and quickstart artifacts captured in plan outputs.

## Complexity Tracking

No constitution violations requiring justification.

## Implementation Status Notes

- Completed US1 backend pagination rollout for all in-scope list routes.
- Completed US2 frontend pagination state alignment:
  - Added reusable pagination controls component.
  - Added explicit page query handling and pagination wiring for datasets, search, source detail, topic detail, and geography detail routes.
  - Updated discovery client and shared response types to consume paginated detail envelopes.
- Completed US3 regression hardening:
  - Added backend ordering/default behavior regression tests under pagination.
  - Added frontend page reset and empty/error regression coverage.
  - Implemented service-level out-of-range page reconciliation for list routes.
- Validation complete:
  - Full monorepo tests passed.
  - Full monorepo coverage passed with >=90% thresholds.
  - Required all-files quality gate (`pre-commit run --all-files`) passed.
  - Manual API and browser runtime checks passed after clean compose restart.
