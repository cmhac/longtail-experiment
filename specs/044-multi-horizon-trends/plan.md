# Implementation Plan: Current-State Multi-Lookback Trends

**Branch**: `044-multi-horizon-trends` | **Date**: 2026-04-02 | **Spec**: `/Users/hackerc/Projects/longtail-experiment/specs/044-multi-horizon-trends/spec.md`
**Input**: Feature specification from `/specs/044-multi-horizon-trends/spec.md`

## Summary

Update the existing spec 044 rollout so the already-persisted canonical current-trend descriptor becomes available on every dataset-summary surface, then replace the removed detail-chip behavior with one shared arrow indicator component rendered in two places: at the far right of every dataset row and adjacent to the `Historical Trend` heading on dataset detail pages. Delivery remains a vertical slice across backend contracts/query projections and frontend shared-component rendering, with no client-side trend weighting or ranking logic.

## Technical Context

**Language/Version**: Python 3.12 (backend/pipeline/libs), TypeScript 5.x + React 19 + Next.js 15 App Router (frontend)  
**Primary Dependencies**: SQLAlchemy 2.x, Pydantic 2.x, Dagster 1.x, existing discovery query/service contracts, existing trend-analysis library and canonical descriptor persistence, HeroUI 3, Tailwind utilities, Vitest, pytest, Ruff, Ty, Biome  
**Storage**: PostgreSQL 16 existing trend tables plus already-added `trend_lookback_evaluations`, `trend_lookback_snapshots`, and `trend_canonical_descriptors`  
**Testing**: pytest contract/query tests, Vitest component/rendering tests, browser-based manual validation, `pre-commit run --all-files`, Nx full-suite test/coverage gates  
**Target Platform**: Local Docker Compose stack plus Next.js-rendered discovery UI on desktop and mobile browsers  
**Project Type**: Nx monorepo full-stack feature refinement (pipeline-backed read model + API + web UI)  
**Performance Goals**: Dataset-list and detail pages continue to render without extra per-row network requests; indicator rendering remains visually immediate on existing catalog/feed/detail surfaces  
**Constraints**: Preserve deterministic canonical descriptor ownership in backend/pipeline; no client-side lookback ranking; maintain >=90% coverage; keep frontend changes in shared `apps/frontend/src/components`; preserve responsive list-row layout and detail-chart header layout  
**Scale/Scope**: All dataset-summary responses that feed dataset rows (`catalog`, `search`, topic/geography/source detail, and homepage recent dataset updates) plus dataset-detail trend heading rendering

## Constitution Check

_GATE: Must pass before Phase 0 research. Re-check after Phase 1 design._

- Monorepo cohesion: PASS. Work stays within existing `libs`/`apps/backend`/`apps/frontend` boundaries and updates shared contracts for a vertical slice.
- Quality gate enforcement: PASS. Plan requires normal lint/format/typecheck/test gates with no suppression or bypass strategy.
- Full-suite stop rule: PASS. Plan requires `pnpm exec nx run-many -t test --all` before commit and before agent handoff/stop.
- Coverage stop rule: PASS. Plan requires `pnpm exec nx run-many -t coverage --all` before commit with >=90% thresholds preserved.
- Test and coverage discipline: PASS. Plan includes backend contract/query tests and frontend component/rendering tests for the new summary payload and indicator states.
- Local-first parity: PASS. End-to-end verification remains runnable through the existing Docker Compose stack and frontend runtime.
- Data integrity and reliability: PASS. Canonical descriptor ownership stays server-side, summary/detail payloads remain deterministic, and unavailable-state behavior is explicitly designed.
- Configuration integrity: PASS. No new credentialed services or env-var contracts are introduced.
- Frontend UI consistency: PASS. Plan extends shared discovery components and HeroUI/Tailwind patterns rather than introducing one-off route-local markup.
- Documentation fidelity: PASS. Plan updates `research.md`, `data-model.md`, `contracts/`, `quickstart.md`, and agent context for the revised list/detail indicator scope.

## Project Structure

### Documentation (this feature)

```text
specs/044-multi-horizon-trends/
├── plan.md
├── research.md
├── data-model.md
├── quickstart.md
├── contracts/
│   └── discovery-lookback-trends.openapi.yaml
└── tasks.md
```

### Source Code (repository root)

```text
libs/
├── trend_analysis/
│   ├── src/trend_analysis/
│   └── tests/
└── db/
    ├── alembic/
    └── src/db/models/

apps/backend/
├── src/contract/query/
├── src/contract/discovery_trends.py
├── src/query/
└── tests/

apps/frontend/
├── src/app/
├── src/components/discovery/
├── src/lib/api/
└── tests/
```

**Structure Decision**: Treat this revision as a backend-and-frontend refinement on top of the existing multi-lookback persistence implementation. Pipeline classification/storage stays authoritative; the planned code changes are concentrated in backend discovery summary/detail projections and shared frontend discovery components.

## Phase Plan

### Phase 0: Research and Decision Locking

- Confirm the scope of dataset-summary payloads that must now include a canonical current-trend descriptor.
- Confirm that the existing persisted canonical descriptor shape is sufficient for list and detail rendering without new client-side computation.
- Lock the visual-state mapping from canonical descriptor direction/strength to the four arrow states and explicit unavailable behavior.
- Confirm the shared frontend insertion points:
  - dataset rows via `UnifiedDatasetRow` and related mappers
  - detail heading via `DatasetDetailAnalysis` or the chart-card title surface
- Record current repository seams and any already-implemented behavior that this plan assumes.

### Phase 1: Design and Contracts

- Update the data model to add summary-level current-trend read models and a shared indicator projection.
- Update the OpenAPI/contract artifact so dataset-summary payloads and dataset-detail payloads both expose canonical current-trend descriptors.
- Define quickstart/manual validation steps for:
  - list payload verification
  - detail payload verification
  - list-row indicator rendering
  - detail-heading indicator rendering
- Refresh agent context after artifact updates.

### Phase 2: Implementation Planning

#### Workstream A: Backend summary/detail projection alignment

1. Extend backend discovery summary contracts so `DatasetSummary`-based responses carry the canonical current-trend descriptor.
2. Update persisted-repository query paths to project the latest canonical descriptor alongside dataset-summary rows, without requiring additional per-item fetches.
3. Keep dataset-detail canonical descriptor and lookback snapshot behavior intact while aligning naming and validation with the new shared read model.
4. Add or update backend tests for:
   - dataset catalog/search/source/topic/geography summary payload validation
   - recent dataset update payloads carrying summary-level current trend
   - deterministic unavailable-state behavior when no canonical descriptor exists

#### Workstream B: Shared frontend indicator integration

1. Introduce one shared trend-indicator UI primitive under `apps/frontend/src/components` that renders the four supported directional states plus an unavailable state from API data only.
2. Extend `UnifiedDatasetRow` and its mapper inputs so the indicator renders at the far right of dataset rows across all list surfaces that consume dataset summaries.
3. Add the same indicator next to the `Historical Trend` heading on dataset detail pages, replacing the removed chip behavior without reintroducing overlay logic.
4. Preserve responsive behavior for narrow list rows and detail-page header layouts.
5. Add or update frontend tests for:
   - all four directional indicator states
   - unavailable rendering
   - row placement on shared dataset-list components
   - detail-heading placement next to `Historical Trend`

#### Workstream C: End-to-end hardening

1. Verify list and detail API payloads expose canonical current-trend descriptors consistently.
2. Verify no client-side weighting/ranking logic is reintroduced in list or detail rendering paths.
3. Verify recent updates, catalog/search results, and detail pages all render consistently for datasets with available and unavailable trend states.
4. Update any residual documentation or developer guidance that still references chip-only detail rendering.

## Execution Guidance (Mandatory)

- Use red/green TDD for each backend and frontend slice:
  - write or update failing tests first
  - implement the minimal change to pass
  - refactor only with tests still green
- For backend slices, validate real payloads from the local backend before moving on.
- For frontend slices, validate both desktop and mobile-width layouts with browser tools.
- Before every commit and before ending work, run:
  - `pre-commit run --all-files`
  - `pnpm exec nx run-many -t test --all`
  - `pnpm exec nx run-many -t coverage --all`

## Post-Design Constitution Re-Check

- Monorepo cohesion: PASS
- Quality gate enforcement: PASS
- Full-suite stop rule: PASS
- Coverage stop rule: PASS
- Test and coverage discipline: PASS
- Local-first parity: PASS
- Data integrity and reliability: PASS
- Configuration integrity: PASS
- Frontend UI consistency: PASS
- Documentation fidelity: PASS

## Complexity Tracking

No constitution violations requiring justification.

## Scope Revision Completion Targets

- Dataset-summary contracts expose canonical descriptors across catalog, search, and recent dataset update surfaces for shared row rendering.
- Dataset-detail continues exposing canonical descriptor plus lookback snapshots, with current-trend emphasis at the `Historical Trend` heading indicator.
- Shared frontend indicator mapping covers directional and unavailable states from API fields only.
