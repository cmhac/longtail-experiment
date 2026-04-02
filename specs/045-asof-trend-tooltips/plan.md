# Implementation Plan: Historical As-Of Trend Tooltips

**Branch**: `045-asof-trend-tooltips` | **Date**: 2026-04-02 | **Spec**: `/Users/hackerc/Projects/longtail-experiment/specs/045-asof-trend-tooltips/spec.md`
**Input**: Feature specification from `/specs/045-asof-trend-tooltips/spec.md`

## Summary

Add observation-level as-of canonical trend descriptors to dataset-detail responses and wire them through frontend observation chart tooltip rendering. The backend remains authoritative for as-of resolution, returning an explicit available/unavailable descriptor for every observation in the detail payload. The frontend extends the existing tooltip composition to render one shared `DatasetTrendIndicator` chip at the bottom of each tooltip for the hovered observation, without introducing client-side trend inference or extra API requests.

## Technical Context

**Language/Version**: Python 3.12 (backend/query), TypeScript 5.x + React 19 + Next.js 15 App Router (frontend)  
**Primary Dependencies**: SQLAlchemy 2.x repository/query layer, Pydantic 2.x contracts, existing discovery service orchestration, HeroUI 3 (`@heroui/react`), Recharts, Vitest, pytest, Ruff, Ty, Biome  
**Storage**: PostgreSQL 16 persisted discovery + trend tables (`observations`, `trend_canonical_descriptors`, `trend_lookback_snapshots`)  
**Testing**: Backend contract/query pytest suites, frontend Vitest tooltip/component tests, browser manual verification, `pre-commit run --all-files`, Nx full-suite tests + coverage gates  
**Target Platform**: Local Docker Compose backend plus Next.js dataset-detail UI in desktop/mobile browsers
**Project Type**: Nx monorepo vertical slice across backend contracts/service/repository and frontend shared discovery components  
**Performance Goals**: No additional network round trips for tooltip trend state; maintain existing dataset-detail render responsiveness while resolving as-of trend in the detail payload assembly path  
**Constraints**: Preserve current dataset-level canonical descriptor behavior; explicit unavailable state required per observation; deterministic as-of selection; no client-side as-of ranking/weighting; maintain >=90% coverage and full-suite/coverage stop rules  
**Scale/Scope**: Dataset-detail endpoint and dataset-detail chart tooltip only; all returned observations in detail payload receive as-of trend envelope

## Constitution Check

_GATE: Must pass before Phase 0 research. Re-check after Phase 1 design._

- Monorepo cohesion: PASS. Scope spans existing backend query contracts/repository/service and frontend discovery components with one coherent detail-page vertical slice.
- Quality gate enforcement: PASS. Plan requires standard Ruff/Ty/Biome/typecheck/test gates with no suppressions.
- Full-suite stop rule: PASS. Plan requires `pnpm exec nx run-many -t test --all` before commit and before agent handoff/stop.
- Coverage stop rule: PASS. Plan requires `pnpm exec nx run-many -t coverage --all` with >=90% thresholds before commit.
- Test and coverage discipline: PASS. Plan adds backend contract/query tests and frontend tooltip rendering tests for as-of state coverage.
- Local-first parity: PASS. Flow is verifiable using existing Docker Compose services and local frontend runtime.
- Data integrity and reliability: PASS. As-of selection rules are deterministic and contract-validated with explicit unavailable states.
- Configuration integrity: PASS. No new secret-bearing services or env vars are introduced.
- Frontend UI consistency: PASS. Tooltip uses shared `DatasetTrendIndicator` and existing chart tooltip primitives in `apps/frontend/src/components`.
- Documentation fidelity: PASS. Plan includes `research.md`, `data-model.md`, `contracts/`, `quickstart.md`, and agent-context refresh.

## Project Structure

### Documentation (this feature)

```text
specs/045-asof-trend-tooltips/
├── plan.md
├── research.md
├── data-model.md
├── quickstart.md
├── contracts/
│   └── discovery-asof-trend-tooltips.openapi.yaml
└── tasks.md
```

### Source Code (repository root)

<!--
  ACTION REQUIRED: Replace the placeholder tree below with the concrete layout
  for this feature. Delete unused options and expand the chosen structure with
  real paths (e.g., apps/admin, packages/something). The delivered plan must
  not include Option labels.
-->

```text
apps/backend/
├── src/contract/query/
├── src/query/
└── tests/

apps/frontend/
├── src/lib/api/
├── src/components/discovery/
└── tests/

libs/db/
└── src/db/models/
```

**Structure Decision**: Implement as a backend+frontend refinement over existing discovery detail surfaces. Backend defines and validates observation-level as-of trend payloads; frontend consumes those fields in the existing observations tooltip composition.

## Phase Plan

### Phase 0: Research and Decision Locking

- Lock the deterministic as-of selection rule for per-observation trend resolution.
- Confirm existing persistence surfaces are sufficient (no schema migration required).
- Confirm contract shape for observation-level trend payload and explicit unavailable semantics.
- Confirm frontend insertion seam in `ObservationsChart` tooltip and shared indicator reuse.

### Phase 1: Design and Contracts

- Add observation-level as-of trend entities/read models to `data-model.md`.
- Define contract updates in `contracts/discovery-asof-trend-tooltips.openapi.yaml`:
  - observation item includes required `as_of_trend_descriptor`
  - explicit error envelope semantics for malformed payloads
- Produce `quickstart.md` with red/green/manual/full-gate validation flow.
- Refresh agent context via `.specify/scripts/bash/update-agent-context.sh codex`.

### Phase 2: Implementation Planning

#### Workstream A: Backend as-of resolution and detail contract

1. Extend backend detail observation contract model to carry one as-of descriptor per observation.
2. Implement deterministic resolver in discovery service/repository path:

- for each returned observation, resolve canonical descriptor at that observation context
- produce explicit unavailable descriptor when no canonical match exists

3. Preserve existing dataset-level `canonical_trend_descriptor` and `lookback_trend_snapshots` fields unchanged.
4. Add backend tests for:

- per-observation available resolution
- mixed availability resolution
- deterministic tie-breaking for same observed date with differing report times
- malformed as-of payload validation failure behavior

#### Workstream B: Frontend tooltip chip integration

1. Extend frontend API types with observation-level `as_of_trend_descriptor`.
2. Update `ObservationsChart` tooltip point model to carry descriptor for hovered observation.
3. Render one shared `DatasetTrendIndicator` chip at tooltip bottom:

- available state renders direction/strength arrow chip
- unavailable state renders explicit unavailable chip text/state

4. Keep existing tooltip value/change content intact and preserve chart interaction behavior.
5. Add frontend tests for:

- observation-specific chip updates while moving across points
- unavailable state rendering
- no regression in existing tooltip text/value sections

#### Workstream C: End-to-end hardening

1. Validate local API detail payload includes `as_of_trend_descriptor` on each observation.
2. Validate browser tooltip behavior with multiple observations and mixed availability datasets.
3. Run full quality gates before completion:

- `pre-commit run --all-files`
- `pnpm exec nx run-many -t test --all`
- `pnpm exec nx run-many -t coverage --all`

## Execution Guidance (Mandatory)

- Use red/green TDD for each backend and frontend slice.
- Keep as-of trend selection exclusively server-side; frontend only renders provided payloads.
- Prefer extending shared discovery primitives (`DatasetTrendIndicator`, chart tooltip controls) over creating one-off tooltip styling.
- Re-run manual checks after any runtime bug discovered in browser/API validation.

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
