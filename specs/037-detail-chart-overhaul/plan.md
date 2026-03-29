# Implementation Plan: Dataset Detail Chart Overhaul

**Branch**: `[037-detail-chart-overhaul]` | **Date**: 2026-03-29 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/specs/037-detail-chart-overhaul/spec.md`

**Note**: This template is filled in by the `/speckit.plan` command. See `.specify/templates/plan-template.md` for the execution workflow.

## Summary

Refine the dataset detail trend chart so it uses the available analysis-panel space more effectively, defaults to all-history, exposes only meaningful time filters in longest-to-shortest order, and removes low-value visual clutter. The implementation stays within the existing frontend detail-page architecture, reuses the current dataset detail payload, updates chart-specific derived state and presentation contracts, and expands frontend tests plus manual verification to cover the new range logic, spacing behavior, and fallback states.

## Technical Context

**Language/Version**: TypeScript 5.x + React 19 in Next.js 15 App Router  
**Primary Dependencies**: Existing discovery API client/types, Recharts time-series primitives, HeroUI components, Tailwind utility classes, existing dataset-detail view-model helpers  
**Storage**: N/A for new persistence; existing PostgreSQL-backed dataset detail payload remains source-of-truth  
**Testing**: Vitest component/page tests, Testing Library utilities, TypeScript noEmit, Biome checks  
**Target Platform**: Responsive web experience inside the existing discovery shell on desktop and mobile viewports  
**Project Type**: Frontend web-application enhancement with no new backend or service runtime  
**Performance Goals**: Preserve current detail-page load behavior and keep chart interactions responsive for datasets with long observation histories  
**Constraints**: Preserve `/datasets/[id]` route shape and existing no-data/error/not-found semantics; avoid new bespoke CSS outside allowed shared/global patterns; maintain quality-gate compliance with no suppressions  
**Scale/Scope**: Chart-specific updates in `apps/frontend/src/components/discovery`, related detail-page composition/view-model logic, frontend tests, and feature docs under `specs/037-detail-chart-overhaul`

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
- Frontend UI consistency: For frontend changes, does the plan use HeroUI components,
  Tailwind utilities, and shared abstractions in `apps/frontend/src/components` for
  repeated patterns instead of new ad hoc CSS or duplicated markup?
- Documentation fidelity: Does the plan identify all documentation that MUST be added or
  updated for the proposed code and behavior changes?

Initial gate assessment:

- Monorepo cohesion: PASS. Changes stay within `apps/frontend` plus feature docs in `specs/037-detail-chart-overhaul`.
- Quality gate enforcement: PASS. Plan retains Biome, typecheck, frontend tests, and mandatory monorepo stop gates without suppression.
- Full-suite stop rule: PASS. `pnpm exec nx run-many -t test --all` remains a required completion gate before commit or handoff.
- Coverage stop rule: PASS. `pnpm exec nx run-many -t coverage --all` remains a required completion gate before commit.
- Test and coverage discipline: PASS. Planned updates expand chart, page, and view-model tests for range availability, default state, layout contract markers, and no-data behavior.
- Local-first parity: PASS. Existing local frontend and compose-backed discovery stack are sufficient for manual validation; no compose changes are required.
- Data integrity and reliability: PASS. Existing dataset detail observations remain authoritative, and new filter availability rules derive deterministically from returned history.
- Configuration integrity: PASS. No new services, secrets, or environment variables are introduced.
- Frontend UI consistency: PASS. Changes remain in shared discovery components and use existing HeroUI/Tailwind conventions instead of introducing a parallel chart wrapper pattern.
- Documentation fidelity: PASS. Plan, research, data model, quickstart, and contracts capture the new chart behavior and verification flow.

## Project Structure

### Documentation (this feature)

```text
specs/037-detail-chart-overhaul/
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
│   └── datasets/
│       └── [id]/
│           └── page.tsx
├── components/
│   └── discovery/
│       ├── DatasetDetailAnalysis.tsx
│       ├── DatasetDetailInsights.tsx
│       ├── ObservationsChart.tsx
│       ├── ObservationsTable.tsx
│       └── dataset-detail-view-model.ts
├── lib/
│   └── api/
│       └── discovery-types.ts
└── app/globals.css

apps/frontend/tests/
├── detail-page.test.tsx
├── ObservationsChart.test.tsx
├── dataset-detail-view-model.test.ts
└── fixtures/
    └── dataset-detail-fixtures.ts

specs/037-detail-chart-overhaul/
├── spec.md
├── plan.md
├── research.md
├── data-model.md
├── quickstart.md
└── contracts/
```

**Structure Decision**: Reuse the existing dataset detail route and shared discovery component stack, concentrating logic changes in the chart component, its parent analysis wrapper, and the chart-supporting view-model helpers rather than creating a new page architecture.

## Phase 0: Research and Decisions

- Confirm the rule for when a time filter is "supported" so visible controls represent distinct views instead of duplicate all-history or long-range states.
- Confirm the least disruptive way to make the chart visually fill the trend panel and align with the metadata column without changing route structure or backend contracts.
- Confirm the chart control order, default selection, and empty-state behavior contract for datasets with very short, medium, and long histories.
- Confirm how x-axis label spacing should be improved within the existing charting library behavior without creating a new styling system.

## Phase 1: Design and Contracts

- Define the chart-specific derived-state model for selected range, available ranges, control visibility, and filtered observations.
- Define the trend-panel layout contract covering width fill, vertical alignment, border removal, footnote removal, and pointer cursor expectations.
- Define range-control contract details for default all-history selection, 5-year support, longest-to-shortest ordering, and hidden unsupported filters.
- Capture manual verification guidance for datasets with no data, limited data, exactly five years of data, and long observation histories across desktop and mobile.
- Update agent context to include this feature's planning footprint.

## Phase 2: Implementation Planning

- Step 1: Extend chart derived-state helpers in `dataset-detail-view-model.ts` to compute supported time ranges, filtered observations, and all-history default behavior.
- Step 2: Update `DatasetDetailAnalysis.tsx` so the trend panel layout allows the chart surface to fill the available analysis-column space and remain aligned with the insight/metadata column.
- Step 3: Refine `ObservationsChart.tsx` to remove the border and footnote, add the 5Y range, order controls longest-to-shortest, hide unsupported controls, add pointer cursor affordance, remove line dots, and loosen x-axis label spacing.
- Step 4: Preserve or refine empty-state rendering so no-data datasets do not show dead-end controls or blank trend space.
- Step 5: Expand `ObservationsChart.test.tsx`, `detail-page.test.tsx`, and `dataset-detail-view-model.test.ts` to cover supported-range calculation, default all-history selection, hidden filters, pointer-cursor affordance, and removal of the footnote.
- Step 6: Run focused frontend checks, perform manual browser validation against real dataset detail pages after a clean restart, then complete mandatory monorepo stop gates.

## Post-Design Constitution Check

- Monorepo cohesion: PASS. The design remains confined to frontend detail-page composition, shared chart/view-model logic, and feature documentation.
- Quality gate enforcement: PASS. No suppressions or bypass strategies are introduced.
- Full-suite stop rule: PASS. Full monorepo test execution remains a required final gate.
- Coverage stop rule: PASS. Full monorepo coverage execution remains a required final gate.
- Test and coverage discipline: PASS. Planned automated tests directly cover each new interaction and presentation requirement that could regress.
- Local-first parity: PASS. Manual validation fits the existing local frontend + discovery stack with no new infrastructure.
- Data integrity and reliability: PASS. Observation history stays canonical, and range visibility rules are deterministic from returned chronology.
- Configuration integrity: PASS. No configuration or credential surface changes are introduced.
- Frontend UI consistency: PASS. The plan extends existing discovery components and styling conventions rather than introducing a separate chart UI system.
- Documentation fidelity: PASS. Required feature artifacts are included, and no additional repo-wide documentation updates are currently implied by this scoped UI behavior change.

## Complexity Tracking

No constitution violations requiring justification.
