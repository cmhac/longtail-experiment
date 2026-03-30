# Implementation Plan: Relative Change Visualizations

**Branch**: `[041-relative-change-visualization]` | **Date**: 2026-03-30 | **Spec**: [/Users/hackerc/Projects/longtail-experiment/specs/041-relative-change-visualization/spec.md](/Users/hackerc/Projects/longtail-experiment/specs/041-relative-change-visualization/spec.md)
**Input**: Feature specification from `/specs/041-relative-change-visualization/spec.md`

**Note**: This template is filled in by the `/speckit.plan` command. See `.specify/templates/plan-template.md` for the execution workflow.

## Summary

Add a dual-mode relative-change experience on the dataset detail chart so users can analyze percentage movement versus either rolling historical offsets or a fixed baseline reference. The implementation extends existing dataset detail view-model/chart behavior and preserves contract compatibility while adding explicit rules for formula semantics, non-computable points, baseline persistence, and exact available-date baseline selection. Execution is incremental by design: agents must use red/green TDD, commit regularly after each stable slice, and manually verify behavior in the local environment, including frontend browser-tool validation.

## Technical Context

**Language/Version**: Python 3.12 (backend), TypeScript 5.x + React 19 in Next.js 15 App Router  
**Primary Dependencies**: Existing discovery API contracts/service/repository layers, frontend discovery client/types, dataset detail view-model helpers, Recharts chart primitives, HeroUI 3 components, Tailwind utility styling  
**Storage**: Existing PostgreSQL 16 discovery metadata and observations tables (no new datastore)  
**Testing**: pytest backend contract/runtime tests, Vitest frontend component/page tests, manual browser verification, `pre-commit run --all-files`, Nx full-suite test/coverage gates  
**Target Platform**: Local Docker Compose stack and Next.js-rendered web UI on desktop/mobile browsers
**Project Type**: Nx monorepo web application (backend + frontend vertical slice)  
**Performance Goals**: Relative-change mode switches and baseline updates should feel immediate in interactive chart usage and avoid noticeable lag under existing dataset-detail workloads  
**Constraints**: Preserve existing dataset detail route/API shape unless explicitly versioned; maintain >=90% coverage; no gate bypasses; HeroUI/Tailwind/shared-component conventions; regular commits during implementation; red/green TDD for behavior changes; mandatory manual local/browser verification before each checkpoint commit  
**Scale/Scope**: Dataset-detail visualization flow across frontend chart/view-model logic with potential backend contract supplementation for clarity, plus associated tests and docs

## Constitution Check

_GATE: Must pass before Phase 0 research. Re-check after Phase 1 design._

- Monorepo cohesion: PASS - Work remains within existing `apps/frontend` dataset-detail flow and optional contract-level clarifications in `apps/backend` without introducing boundary drift.
- Quality gate enforcement: PASS - Plan requires canonical lint/format/typecheck/test/duplication gates via pre-commit and Nx, with no suppression strategy.
- Full-suite stop rule: PASS - Plan requires `pnpm exec nx run-many -t test --all` before every implementation commit and before agent handoff/stop.
- Coverage stop rule: PASS - Plan requires `pnpm exec nx run-many -t coverage --all` before every implementation commit, preserving >=90% per project.
- Test and coverage discipline: PASS - Plan includes backend/frontend automated tests for formula correctness, baseline selection, non-computable handling, and persistence behavior.
- Local-first parity: PASS - Feature verifies via existing compose-backed stack and frontend runtime; no new services needed.
- Data integrity and reliability: PASS - Plan codifies deterministic formula semantics, exact baseline-date rules, and non-computable safeguards.
- Configuration integrity: PASS - No new credentialed component or env var contract is introduced.
- Frontend UI consistency: PASS - Plan extends existing dataset-detail components using HeroUI/Tailwind and shared discovery abstractions.
- Documentation fidelity: PASS - Plan delivers `research.md`, `data-model.md`, `contracts/`, `quickstart.md`, and execution guidance updates in this feature scope.

## Project Structure

### Documentation (this feature)

```text
specs/041-relative-change-visualization/
├── plan.md
├── research.md
├── data-model.md
├── quickstart.md
├── contracts/
│   └── relative-change-visualization-contract.md
└── tasks.md
```

### Source Code (repository root)

```text
apps/
├── frontend/
│   ├── src/
│   │   ├── app/datasets/[id]/page.tsx
│   │   ├── components/discovery/
│   │   │   ├── DatasetDetailAnalysis.tsx
│   │   │   ├── DatasetDetailInsights.tsx
│   │   │   ├── ObservationsChart.tsx
│   │   │   └── dataset-detail-view-model.ts
│   │   └── lib/api/discovery-types.ts
│   └── tests/
│       ├── ObservationsChart.test.tsx
│       ├── detail-page.test.tsx
│       └── dataset-detail-view-model.test.ts
└── backend/
    ├── src/
    │   ├── contract/query/
    │   ├── query/
    │   └── http_api_server.py
    └── tests/contract/
```

**Structure Decision**: Implement as a frontend-first vertical slice in existing dataset-detail modules, with backend contract/service adjustments only if required to keep the relative-change semantics explicit and tested.

## Phase Plan

### Phase 0: Research and Decision Locking

- Confirm canonical relative-change formula semantics and sign behavior for all baseline modes.
- Confirm exact rules for non-computable points and timeline continuity.
- Confirm fixed-baseline date behavior (available-date-only, exact match).
- Confirm baseline-setting persistence behavior across chart range/filter scope changes.
- Confirm incremental execution discipline for agents:
  - use red/green TDD for each behavioral slice
  - commit regularly (one stable slice per commit)
  - perform manual local verification after each slice
  - for frontend slices, use browser tools to validate interactions visually and functionally

### Phase 1: Design and Contracts

- Define data model for chart modes, baseline selectors, computation outputs, and computability status.
- Define contract notes for frontend/backend expectations around observations chronology and relative-change rendering assumptions.
- Define quickstart verification playbook covering unit/integration tests plus browser-based manual checks.
- Deliver artifacts: `research.md`, `data-model.md`, `contracts/relative-change-visualization-contract.md`, `quickstart.md`.

### Phase 2: Implementation Planning

- Workstream A: Relative-change mode foundation
  - Add mode switching between observed-value and relative-change views.
  - Add formula-driven transformation pipeline with chronological guarantees.
  - Add red/green tests for formula correctness and sign behavior.
  - Commit after tests pass and manual verification confirms mode switching.
- Workstream B: Rolling baseline support
  - Add rolling offset controls and computation behavior for 1/2/3/n offsets.
  - Implement non-computable gap handling without fallback numeric coercion.
  - Add tests for insufficient-history cases.
  - Commit after local/browser validation of rolling controls and chart gaps.
- Workstream C: Fixed baseline support
  - Add fixed-baseline selection by exact available date and by index/offset.
  - Ensure date picker/list exposes only available observation dates in active scope.
  - Add tests for exact-match-only selection behavior.
  - Commit after browser validation of date/index baseline workflows.
- Workstream D: Scope-change persistence and hardening
  - Preserve baseline settings across scope changes when valid.
  - Keep invalid preserved settings visible and show explicit unavailable state.
  - Add tests for persistence/non-silent-fallback behavior.
  - Commit after end-to-end manual checks and full quality gates.

## Execution Guidance (Mandatory)

- Agents MUST commit regularly throughout implementation. Do not aggregate all changes into one large commit.
- Agents MUST follow red/green TDD for each behavior slice:
  - write or update failing tests first (red)
  - implement minimal change to pass (green)
  - refactor only with tests still passing
- Agents MUST manually verify functionality in the local dev environment before each slice commit.
- For frontend changes, agents MUST manually test with browser tools (interactive chart controls, baseline selectors, no-data/unavailable states, and visual correctness).
- Before every commit and before ending work, agents MUST run:
  - `pre-commit run --all-files`
  - `pnpm exec nx run-many -t test --all`
  - `pnpm exec nx run-many -t coverage --all`

## Post-Design Constitution Re-Check

- Monorepo cohesion: PASS - Design stays inside existing discovery modules and contracts.
- Quality gates and stop rules: PASS - Explicitly required before every commit and handoff.
- Coverage discipline: PASS - Regression tests are specified across transformed-value logic and interaction behavior.
- Local-first parity: PASS - Verification is local-stack and browser-tool based.
- Data integrity/reliability: PASS - Formula, chronology, and non-computable semantics are explicit and test-protected.
- Configuration integrity: PASS - No new secrets/config surface introduced.
- Frontend UI consistency: PASS - HeroUI/Tailwind/shared-component patterns preserved.
- Documentation fidelity: PASS - Planning artifacts and execution guidance added in feature docs.

## Complexity Tracking

No constitution violations requiring justification.
