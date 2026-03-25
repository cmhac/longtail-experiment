# Implementation Plan: Dataset Detail Page Overhaul

**Branch**: `[031-dataset-detail-overhaul]` | **Date**: 2026-03-25 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/specs/031-dataset-detail-overhaul/spec.md`

**Note**: This template is filled in by the `/speckit.plan` command. See `.specify/templates/plan-template.md` for the execution workflow.

## Summary

Overhaul the dataset detail page into an editorial, analysis-first layout with a strong hero, quick insight rail, richer trend panel, and observation table that emphasizes directional movement. The plan reuses existing dataset-detail contracts and route entry points, adds derived presentation metrics from already available observation data, and updates frontend component/layout contracts plus tests to preserve fallback, not-found, and responsive usability guarantees.

## Technical Context

**Language/Version**: TypeScript 5.x + React 19 (Next.js 15 App Router), Python 3.12 backend contracts reused unchanged  
**Primary Dependencies**: Existing discovery API client/types, Recharts time-series primitives, shell/theme tokens and layout classes  
**Storage**: N/A for new persistence; existing PostgreSQL-backed dataset detail payload remains source-of-truth  
**Testing**: Vitest component/page contract tests, Testing Library utilities, TypeScript noEmit, Biome checks  
**Target Platform**: Responsive web experience inside existing shell (desktop-first with mobile parity)
**Project Type**: Web application frontend enhancement with no new service runtime  
**Performance Goals**: Preserve current detail-page load behavior while keeping chart/table interactions responsive for datasets with 100+ observations  
**Constraints**: Preserve current not-found/error handling semantics; keep existing route shape and data contracts; avoid quality-gate bypasses  
**Scale/Scope**: Detail-page route and discovery components in `apps/frontend`, with supporting spec contracts and validation docs under `specs/031-dataset-detail-overhaul`

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

- Monorepo cohesion: PASS. Changes remain in `apps/frontend` and feature docs under `specs/031-dataset-detail-overhaul`.
- Quality gate enforcement: PASS. Plan retains lint/format/typecheck/test gates with no suppressions.
- Full-suite stop rule: PASS. `pnpm exec nx run-many -t test --all` is required before commit/handoff.
- Coverage stop rule: PASS. `pnpm exec nx run-many -t coverage --all` is required before commit.
- Test and coverage discipline: PASS. Component and page tests cover hero, insight rail, trend controls, table movement states, and fallbacks.
- Local-first parity: PASS. Existing local stack and frontend runtime support manual validation; no new service required.
- Data integrity and reliability: PASS. Existing detail contract fields remain canonical; derived view metrics are computed from returned observations.
- Configuration integrity: PASS. No new credentials, env vars, or services introduced.
- Documentation fidelity: PASS. This plan, research, data model, quickstart, and contract docs capture the behavior overhaul.

## Project Structure

### Documentation (this feature)

```text
specs/031-dataset-detail-overhaul/
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
│           ├── page.tsx
│           └── not-found.tsx
├── components/
│   └── discovery/
│       ├── DatasetDetailHeader.tsx
│       ├── ObservationsChart.tsx
│       ├── ObservationsTable.tsx
│       └── EmptyState/ErrorState shared renderers
├── lib/
│   └── api/
│       ├── discovery-client.ts
│       └── discovery-types.ts
└── app/globals.css

apps/frontend/tests/
├── detail-page.test.tsx
├── DatasetDetailHeader.test.tsx
├── ObservationsChart.test.tsx
├── ObservationsTable.test.tsx
└── not-found-page.test.tsx

specs/031-dataset-detail-overhaul/
├── spec.md
├── plan.md
├── research.md
├── data-model.md
├── quickstart.md
└── contracts/
```

**Structure Decision**: Reuse the existing discovery detail route/component architecture in `apps/frontend`, expanding detail-specific composition and presentation contracts while leaving backend query interfaces stable.

## Phase 0: Research and Decisions

- Confirm visual-information hierarchy mapping from mockup intent into existing detail route sections (hero, insight rail, trend panel, observed table).
- Confirm how to derive comparison metrics and directional deltas from current observation payload shape without backend contract changes.
- Confirm reusable responsive behavior patterns from existing shell/list surfaces to avoid layout drift.
- Confirm table/archive behavior contract for default visible rows and progressive historical access.

## Phase 1: Design and Contracts

- Define view-level entities and derived-state formulas for latest observation, comparative metrics, and movement status classification.
- Define UI behavior contract for trend-range controls, chart/table empty states, and archive access affordance.
- Define route-level contract preserving not-found/error semantics and safe rendering requirements.
- Capture manual verification flow for desktop and mobile rendering, interaction, and fallback states.
- Update agent context to include this feature's planning footprint.

## Phase 2: Implementation Planning

- Refactor detail page composition to align with hero + insight + trend + observed-values section architecture.
- Enhance chart section to support explicit time-range controls and point inspection behavior.
- Enhance observations table to include value-change and status semantics with archive entry point.
- Apply new page-scoped styling for editorial typography, card layout rhythm, and responsive reflow.
- Update and expand frontend tests for new section contracts and fallback behavior.
- Validate with focused frontend checks, manual UI verification, and mandatory monorepo stop gates.

## Post-Design Constitution Check

- Monorepo cohesion: PASS. Frontend detail page changes and spec artifacts stay within established boundaries.
- Quality gate enforcement: PASS. Plan retains required lint/format/typecheck/test commands.
- Full-suite stop rule: PASS. Full monorepo test command remains mandatory completion gate.
- Coverage stop rule: PASS. Full monorepo coverage command remains mandatory completion gate.
- Test and coverage discipline: PASS. Planned test updates cover all new display/interaction behaviors and fallback paths.
- Local-first parity: PASS. No new runtime services; feature remains verifiable in current local setup.
- Data integrity and reliability: PASS. Existing dataset detail contract remains authoritative; derived metrics are deterministic from observations.
- Configuration integrity: PASS. No secret/config surface changes.
- Documentation fidelity: PASS. Feature docs include plan/research/data-model/quickstart/contracts artifacts.

## Complexity Tracking

No constitution violations requiring justification.
