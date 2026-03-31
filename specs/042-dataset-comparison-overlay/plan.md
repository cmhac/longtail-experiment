# Implementation Plan: Dataset Comparison Overlay

**Branch**: `042-dataset-comparison-overlay` | **Date**: 2026-03-31 | **Spec**: [/Users/hackerc/Projects/longtail-experiment/specs/042-dataset-comparison-overlay/spec.md](/Users/hackerc/Projects/longtail-experiment/specs/042-dataset-comparison-overlay/spec.md)
**Input**: Feature specification from `/specs/042-dataset-comparison-overlay/spec.md`

**Note**: This template is filled in by the `/speckit.plan` command. See `.specify/templates/plan-template.md` for the execution workflow.

## Summary

Introduce a comparison-set workflow for dataset charts: users add datasets from detail pages, manage selections from a top-nav count indicator, and analyze overlays on a dedicated full-width comparison page. The implementation is frontend-primary, reuses existing discovery detail/chart primitives, and enforces compatibility behavior defined in spec clarifications: absolute mode only for unit-compatible selections, automatic relative-mode fallback for incompatible selections, shared relative baseline configuration, union-date alignment with gaps, and fixed-baseline fallback rules. Browser-local state persistence, max-selection enforcement, and explicit fail-hard behavior for corrupted local state are included from day one.

## Technical Context

**Language/Version**: TypeScript 5.x + React 19 (Next.js 15 App Router), Python 3.12 contracts/runtime context unchanged  
**Primary Dependencies**: HeroUI 3 components (`@heroui/react`), Recharts charting, existing discovery client/types/view-model utilities, Next.js routing primitives  
**Storage**: Browser-local storage for comparison state; existing PostgreSQL 16 discovery data remains source of truth for dataset details  
**Testing**: Vitest + Testing Library (frontend), existing backend contract/runtime tests unaffected unless optional guardrails are added, `pre-commit run --all-files`, Nx full-suite test/coverage gates  
**Target Platform**: Next.js web UI (desktop/mobile browsers) with local Docker Compose parity for full stack
**Project Type**: Nx monorepo web application (frontend route/component work with existing backend contracts)  
**Performance Goals**: Comparison page interactions (mode switch, baseline changes, add/remove actions) remain responsive under current dataset-detail payload sizes and avoid perceptible chart lag in normal usage  
**Constraints**: Maintain existing discovery API contract compatibility; no gate bypasses; >=90% coverage thresholds; HeroUI/Tailwind/shared-component patterns; single centralized max-selection constant; fail-hard handling for corrupted persisted state  
**Scale/Scope**: New comparison UX across detail and dedicated comparison page, with up to 5 selected datasets and multi-series chart projection logic

## Constitution Check

_GATE: Must pass before Phase 0 research. Re-check after Phase 1 design._

- Monorepo cohesion: PASS - Changes remain in existing `apps/frontend` discovery route/component boundaries and reuse existing API client contracts.
- Quality gate enforcement: PASS - Plan requires canonical quality gates with no suppression/bypass strategy.
- Full-suite stop rule: PASS - `pnpm exec nx run-many -t test --all` required before each commit and before handoff/stop.
- Coverage stop rule: PASS - `pnpm exec nx run-many -t coverage --all` required before each commit with configured thresholds.
- Test and coverage discipline: PASS - Plan includes explicit component/view-model/page test updates for selection, compatibility, and baseline rules.
- Local-first parity: PASS - No new service required; behavior validated via existing frontend runtime and compose-backed API.
- Data integrity and reliability: PASS - Compatibility gating, deterministic baseline fallback, and timeline gap rules are explicitly designed and testable.
- Configuration integrity: PASS - No new credentialed component or environment variable requirement introduced.
- Frontend UI consistency: PASS - HeroUI components and shared discovery abstractions are extended rather than introducing isolated CSS patterns.
- Documentation fidelity: PASS - Plan produces `research.md`, `data-model.md`, `contracts/`, and `quickstart.md` artifacts in this feature directory.

## Project Structure

### Documentation (this feature)

```text
specs/042-dataset-comparison-overlay/
├── plan.md
├── research.md
├── data-model.md
├── quickstart.md
├── contracts/
│   └── comparison-overlay-contract.md
└── tasks.md
```

### Source Code (repository root)

```text
apps/
├── frontend/
│   ├── src/
│   │   ├── app/
│   │   │   ├── datasets/[id]/page.tsx
│   │   │   └── comparison/page.tsx
│   │   ├── components/discovery/
│   │   │   ├── DatasetDetailAnalysis.tsx
│   │   │   ├── ObservationsChart.tsx
│   │   │   ├── dataset-detail-view-model.ts
│   │   │   └── [new comparison selection/chart helpers]
│   │   ├── components/shell/
│   │   │   └── [top-nav integration for comparison count indicator]
│   │   └── lib/api/
│   │       ├── discovery-client.ts
│   │       └── discovery-types.ts
│   └── tests/
│       ├── ObservationsChart.test.tsx
│       ├── detail-page.test.tsx
│       ├── dataset-detail-view-model.test.ts
│       └── [new comparison page and selection-state tests]
└── backend/
    ├── src/query/
    │   ├── dataset_discovery_service.py
    │   └── dataset_discovery_persisted_repository.py
    └── tests/contract/
        └── [existing discovery contract coverage retained unless changed]
```

**Structure Decision**: Implement as a frontend-focused vertical slice that extends existing dataset-detail and chart abstractions, adds a new dedicated comparison page route, and keeps backend contracts unchanged unless optional guardrail adjustments become necessary during implementation.

## Phase Plan

### Phase 0: Research and Decision Consolidation

- Confirm repository patterns for discovery detail route composition, chart state flow, and persisted UI state handling.
- Confirm multi-series chart rendering approach using existing Recharts usage and test doubles.
- Confirm compatibility gating semantics and deterministic baseline fallback strategy from clarified spec decisions.
- Confirm local-state corruption handling expectations and message UX patterns in current discovery surfaces.
- Consolidate decisions and alternatives in `research.md` with explicit rationale.

### Phase 1: Design, Data Model, and Contracts

- Define comparison domain entities and lifecycle transitions in `data-model.md`.
- Define external behavior contracts (selection rules, mode gating, timeline alignment, corrupted state fail-hard behavior) in `contracts/comparison-overlay-contract.md`.
- Draft execution and verification steps in `quickstart.md` for local/browser validation and test commands.
- Run `.specify/scripts/bash/update-agent-context.sh codex` and capture resulting context update.

### Phase 2: Implementation Planning Breakdown

- Workstream A: Comparison selection foundation
  - Replace detail page CSV action with add/remove comparison action.
  - Add top-nav comparison indicator and count synchronization.
  - Add single-source-of-truth max-selection constant (default 5).
  - Add persistence and fail-hard reset flow for corrupted local state.
- Workstream B: Dedicated comparison page and chart composition
  - Add chart-first comparison route with no metadata rail and no observation table.
  - Add minimum-selection eligibility flow (<2 selected datasets).
  - Add in-page removal controls and selection management parity with detail pages.
- Workstream C: Comparison math and compatibility behavior
  - Extend projections to support multi-series union timeline with gaps.
  - Enforce absolute-mode unit compatibility, auto-switch to relative mode for incompatibility, and disable absolute toggle while incompatible.
  - Apply shared relative baseline settings across all series and fixed-baseline fallback (nearest prior, else nearest available).
  - Keep line-color mapping stable within current selection only.
- Workstream D: Verification and hardening
  - Update Vitest suites for page behavior, selection lifecycle, chart semantics, compatibility gating, and persistence corruption handling.
  - Execute manual browser validation against local stack.
  - Run full quality gates before commit/handoff.

## Execution Guidance (Mandatory)

- Use red/green TDD for each workstream slice.
- Commit incrementally at stable checkpoints rather than one aggregate implementation commit.
- Manually validate in local runtime after each major slice, including browser interaction checks for add/remove, indicator updates, mode gating, and comparison rendering.
- Before every commit and before ending work, run:
  - `pre-commit run --all-files`
  - `pnpm exec nx run-many -t test --all`
  - `pnpm exec nx run-many -t coverage --all`

## Post-Design Constitution Re-Check

- Monorepo cohesion: PASS - No new project boundaries introduced; existing discovery vertical slice maintained.
- Quality gates and stop rules: PASS - Explicitly required in implementation guidance.
- Coverage discipline: PASS - Automated test updates planned for affected frontend modules.
- Local-first parity: PASS - Flow can be exercised via existing compose-backed local stack and frontend dev runtime.
- Data integrity/reliability: PASS - Compatibility and baseline semantics are deterministic and contract-documented.
- Configuration integrity: PASS - No new secrets/env dependencies introduced.
- Frontend UI consistency: PASS - HeroUI/Tailwind/shared-component expectations preserved.
- Documentation fidelity: PASS - Required planning artifacts generated in feature docs.

## Complexity Tracking

No constitution violations requiring justification.
