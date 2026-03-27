# Implementation Plan: Filter UI Improvements

**Branch**: `[035-filter-ui-improvements]` | **Date**: 2026-03-26 | **Spec**: [/Users/hackerc/Projects/longtail-experiment/specs/035-filter-ui-improvements/spec.md](/Users/hackerc/Projects/longtail-experiment/specs/035-filter-ui-improvements/spec.md)
**Input**: Feature specification from `/specs/035-filter-ui-improvements/spec.md`

**Note**: This template is filled in by the `/speckit.plan` command. See `.specify/templates/plan-template.md` for the execution workflow.

## Summary

Deliver a three-step refinement of dataset-list filter controls: unify filter panel background styling, modernize selectors to combo-box controls, and align spacing/layout so two filters are grouped on the left while sort is separated on the right with capped widths. The technical approach updates the existing frontend discovery filter controls and associated styles while preserving current filter/sort semantics, accessibility expectations, and responsive behavior.

## Technical Context

**Language/Version**: TypeScript 5.x + React 19 in Next.js 15 App Router  
**Primary Dependencies**: Existing discovery UI components, HeroUI component primitives, shell theme tokens and global CSS  
**Storage**: N/A (presentation and client interaction behavior only)  
**Testing**: Vitest frontend tests, existing discovery page/component tests, Nx quality gates  
**Target Platform**: Next.js-rendered web UI in desktop and mobile browser viewports
**Project Type**: Nx monorepo web application (frontend-focused vertical slice)  
**Performance Goals**: Preserve perceived responsiveness of filter interactions while improving visual scan-ability of controls  
**Constraints**: No filtering-behavior regression; maintain keyboard-operable selector flows; preserve >=90% coverage and all stop-gate commands  
**Scale/Scope**: Dataset list filter row and related discovery filter components/styles in `apps/frontend`

## Constitution Check

_GATE: Must pass before Phase 0 research. Re-check after Phase 1 design._

- Monorepo cohesion: Does the plan preserve clear Nx project boundaries and include
  cross-layer contract updates for vertical-slice changes?
- Monorepo cohesion: PASS - Scope is isolated to existing frontend discovery and style modules within current Nx boundaries.
- Quality gate enforcement: PASS - Plan preserves lint/format/typecheck/test requirements with no suppression strategy.
- Full-suite stop rule: PASS - Plan requires `pnpm exec nx run-many -t test --all` before commit and before agent handoff/stop.
- Coverage stop rule: PASS - Plan requires `pnpm exec nx run-many -t coverage --all` before commit with >=90% project thresholds.
- Test and coverage discipline: PASS - Plan includes frontend test updates for control rendering, behavior continuity, and layout-state expectations.
- Local-first parity: PASS - Feature remains fully verifiable via existing local frontend/runtime stack; no compose service changes required.
- Data integrity and reliability: PASS - No schema/provenance change; plan protects filter/sort semantics from UI-level regressions.
- Configuration integrity: PASS - No new service or credential requirement introduced.
- Documentation fidelity: PASS - Plan includes spec artifacts and contract/quickstart updates for changed UI behavior.

## Project Structure

### Documentation (this feature)

```text
specs/035-filter-ui-improvements/
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
└── frontend/
    ├── src/
    │   ├── app/globals.css
    │   ├── components/discovery/
    │   │   ├── DatasetListControls.tsx
    │   │   ├── InfiniteCatalogList.tsx
    │   │   └── UnifiedSearchSurface.tsx
    │   └── theme/
    └── tests/
        ├── components/
        └── app/
```

**Structure Decision**: Keep implementation within existing frontend discovery component/style boundaries and related frontend tests; no new project/module boundaries are introduced.

## Phase Plan

### Phase 0: Research and Decisions

- Finalize visual consistency strategy for filter-panel background token usage.
- Finalize combo-box migration behavior requirements that preserve current filtering semantics.
- Finalize layout rules for left-group filters, right-group sort control, spacing gap, and capped widths.
- Capture accessibility and responsive behavior expectations as explicit design invariants.

### Phase 1: Design and Contracts

- Define filter-control interaction model with explicit control roles and state invariants.
- Define layout contract for grouped alignment, spacing separation, and responsive reflow behavior.
- Define validation strategy for style consistency and non-regression in filter/sort behavior.
- Complete artifacts: `research.md`, `data-model.md`, `contracts/`, `quickstart.md`.

### Phase 2: Implementation Planning

- UI surface workstreams:
  - Align filter container background with shared filter/shell surface style token usage.
  - Replace dropdown selector UI with combo-box controls while preserving option mapping and selected-state behavior.
  - Rework filter row layout for two left-grouped filter controls, separated right sort control, and capped widths.
- Validation workstreams:
  - Add/adjust frontend tests covering rendering, filter/sort behavior continuity, and layout group semantics.
  - Perform viewport and appearance-mode manual checks.
- Documentation workstreams:
  - Maintain spec artifacts and capture interaction/layout contract updates.

## Implementation Notes and Sequencing Checkpoints

- Implement visual token/background alignment first to establish baseline panel parity.
- Migrate controls to combo-box components second while preserving existing filter value wiring.
- Apply spacing/grouping/capped-width layout adjustments third to avoid coupling layout work with control migration uncertainty.
- Add regression tests after each step to isolate failures.

### Checkpoint A - Visual Baseline

- Filter container background uses designated shared surface style.
- Existing filter behavior remains unchanged.

### Checkpoint B - Control Modernization

- In-scope filter selectors render as combo-box controls.
- Filter and sort result semantics match pre-change behavior.

### Checkpoint C - Layout and Responsiveness

- Two filter controls render as left group; sort control is visually separated on right where width allows.
- Control widths are capped and do not fill the entire row.
- Reflow behavior remains understandable and usable on narrow screens.

### Checkpoint D - Quality Gates

- Targeted frontend tests pass.
- Full monorepo test and coverage stop-gate commands pass.

## Post-Design Constitution Re-Check

- Monorepo cohesion: PASS - Design remains within existing frontend discovery paths and associated tests.
- Quality gates and stop rules: PASS - Design explicitly preserves lint/type/test/coverage stop gates.
- Coverage discipline: PASS - Frontend tests are included to maintain coverage floors.
- Local-first parity: PASS - No runtime surface expansion; existing local stack remains sufficient.
- Data integrity/reliability: PASS - No data contract mutation; behavior-preservation checks prevent filtering regressions.
- Configuration integrity: PASS - No new credential usage or service configuration introduced.
- Documentation fidelity: PASS - Planning artifacts, contracts, and quickstart updated for changed UI behavior.

## Implementation Status Notes

- Completed control-surface baseline update in dataset list controls and global styles.
- Completed selector modernization from native dropdown controls to HeroUI combo-box style controls.
- Completed control-row grouping and capped-width layout update (left filters / right sort) with responsive fallback.
- Added and updated frontend regression coverage in `apps/frontend/tests/DatasetListControls.test.tsx` and `apps/frontend/tests/datasets-page.test.tsx`.
- Focused verification command completed successfully:
  - `pnpm exec vitest run tests/DatasetListControls.test.tsx tests/datasets-page.test.tsx`

## Complexity Tracking

No constitution violations requiring justification.
