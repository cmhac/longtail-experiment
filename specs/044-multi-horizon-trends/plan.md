# Implementation Plan: Multi-Horizon Trends

**Branch**: `044-multi-horizon-trends` | **Date**: 2026-04-01 | **Spec**: [/specs/044-multi-horizon-trends/spec.md](/specs/044-multi-horizon-trends/spec.md)
**Input**: Feature specification from `/specs/044-multi-horizon-trends/spec.md`

**Note**: This template is filled in by the `/speckit.plan` command. See `.specify/templates/plan-template.md` for the execution workflow.

## Summary

Introduce multi-horizon trend snapshots computed by the pipeline, exposed through the backend API as a canonical trend descriptor, and rendered in the frontend as a compact `DatasetTrendChip`. The implementation is a full-stack vertical slice: a new `libs/trend_analysis` library encapsulates classification logic; Alembic migrations and SQLAlchemy models add the persistence layer; the pipeline backfill service writes snapshots after each ingest cycle; the backend API embeds the canonical trend payload in the existing dataset detail response; the frontend removes the ad-hoc `TrendOverlayLayer`/`TrendTooltipController` and replaces them with `DatasetTrendChip` reading from the backend payload. Execution is incremental by phase: pipeline → backend → frontend.

## Technical Context

**Language/Version**: Python 3.12 (backend/pipeline), TypeScript 5.x + React 19 in Next.js 15 App Router
**Primary Dependencies**: SQLAlchemy 2.x, Alembic, Pydantic 2.x, Dagster 1.x, existing pipeline source discovery/registration utilities, existing backend discovery service/repository contracts, HeroUI 3, Tailwind, existing frontend discovery client/types
**Storage**: PostgreSQL 16 — new `lookback_trend_snapshots` and `canonical_trend_descriptors` tables in `libs/db`; no new datastore
**Testing**: pytest backend/pipeline/db, Vitest frontend, `pre-commit run --all-files`, Nx full-suite test/coverage gates
**Target Platform**: Local Docker Compose stack, Next.js-rendered web UI on desktop/mobile browsers
**Project Type**: Nx monorepo web application — Python backend + pipeline + shared DB lib + TypeScript frontend
**Performance Goals**: Canonical trend reads are served from pre-computed rows with no additional latency; chip render is synchronous with existing dataset detail fetch
**Constraints**: Preserve existing discovery API contract shape except for the new optional `trend` field; maintain >=90% coverage; no gate bypasses; regular commits after each stable phase; red/green TDD for classification/weighting logic; mandatory manual local/browser verification before each checkpoint commit
**Scale/Scope**: Full vertical slice across pipeline classification lib, DB schema, pipeline backfill service, backend contract/repository, and frontend detail component

## Constitution Check

_GATE: Must pass before Phase 0 research. Re-check after Phase 1 design._

- Monorepo cohesion: PASS — New `libs/trend_analysis` library follows existing `libs/db` boundary pattern; all layers (pipeline, backend, frontend) updated as a coherent vertical slice with shared contracts and tests.
- Quality gate enforcement: PASS — Plan requires canonical lint/format/typecheck/test/duplication gates via pre-commit and Nx with no suppression strategy.
- Full-suite stop rule: PASS — `pnpm exec nx run-many -t test --all` required before every implementation commit and before agent handoff/stop.
- Coverage stop rule: PASS — `pnpm exec nx run-many -t coverage --all` required before every implementation commit, preserving >=90% per project.
- Test and coverage discipline: PASS — Plan includes unit tests for classification determinism, weighting version metadata, pipeline applicability/no-signal cases, backend contract response validation, and frontend chip rendering.
- Local-first parity: PASS — New tables integrated into existing Docker Compose stack via Alembic migration; backfill service runnable via existing Dagster local runtime.
- Data integrity and reliability: PASS — Snapshot writes are idempotent; weighting algorithm is versioned; `insufficient_data` snapshots are excluded from canonical computation.
- Configuration integrity: PASS — No new credentialed component or env var contract introduced.
- Frontend UI consistency: PASS — `DatasetTrendChip` follows HeroUI/Tailwind conventions and reuses existing discovery component patterns.
- Documentation fidelity: PASS — Plan delivers `research.md`, `contracts/discovery-lookback-trends.openapi.yaml`, `quickstart.md`, and `checklists/requirements.md` artifacts in this feature directory; AGENTS.md updated for canonical descriptor behavior.

## Project Structure

### Documentation (this feature)

```text
specs/044-multi-horizon-trends/
├── spec.md
├── plan.md
├── research.md
├── quickstart.md
├── checklists/
│   └── requirements.md
└── contracts/
    └── discovery-lookback-trends.openapi.yaml
```

### Source Code (repository root)

```text
libs/
├── db/
│   ├── alembic/versions/
│   │   └── 0012_lookback_trend_snapshots.py   (new migration)
│   └── src/db/models/
│       └── trend.py                            (new SQLAlchemy model definitions)
└── trend_analysis/                             (new library)
    ├── pyproject.toml
    ├── src/trend_analysis/
    │   ├── __init__.py
    │   ├── classifier.py
    │   ├── models.py
    │   └── version.py
    └── tests/
        ├── test_canonical_descriptor_weighting.py
        └── test_classifier.py

apps/
├── pipeline/
│   ├── src/orchestration/
│   │   ├── resources/
│   │   │   ├── trend_repository.py             (new protocol/interface definitions)
│   │   │   └── postgres_trend_repository.py    (new PostgreSQL implementation)
│   │   └── jobs/
│   │       └── trend_backfill_service.py        (new backfill service)
│   └── tests/orchestration/
│       └── test_trend_runtime_processor_lookbacks.py
└── backend/
    ├── src/
    │   ├── contract/
    │   │   ├── discovery_trends.py              (replace trend span contracts)
    │   │   └── query/
    │   │       └── dataset_detail_query.py      (add trend field to response)
    │   └── query/
    │       └── dataset_discovery_persisted_repository.py  (add trend reads)
    └── tests/contract/
        └── test_dataset_detail_lookback_snapshot_contract.py

apps/frontend/
├── src/components/
│   ├── discovery/
│   │   ├── DatasetTrendChip.tsx                 (new chip component)
│   │   ├── DatasetDetailAnalysis.tsx            (updated to use chip)
│   │   └── ObservationsChart.tsx               (remove overlay controller)
│   └── trends/
│       ├── TrendOverlayLayer.tsx                (removed)
│       └── TrendTooltipController.tsx          (removed)
└── tests/
    └── components/
        └── DatasetTrendChip.test.tsx
```

**Structure Decision**: Introduce `libs/trend_analysis` as an isolated, independently testable classification library following the `libs/db` pattern. The pipeline depends on it to compute and write snapshots. The backend reads pre-computed rows from PostgreSQL; no runtime classification occurs in the API layer.

## Implementation Phases

### Phase 1: Setup (Shared Infrastructure)

Verify artifact alignment, capture pre-change schema seam notes, and establish tracking checklist before any code is written.

- Validate artifacts alignment: spec.md ↔ plan.md ↔ contracts/discovery-lookback-trends.openapi.yaml
- Capture pre-change schema seam notes in research.md
- Add implementation tracking checklist in checklists/requirements.md

### Phase 2: Foundational (Blocking Prerequisites)

Create the persistence layer and shared protocol scaffolding that all subsequent phases depend on. No user story work begins until this phase completes.

- **DB migration**: `0012_lookback_trend_snapshots.py` — creates `lookback_trend_snapshots` and `canonical_trend_descriptors` tables
- **SQLAlchemy models**: `libs/db/src/db/models/trend.py` — ORM definitions for the two new tables
- **Pipeline protocol types**: `apps/pipeline/src/orchestration/resources/trend_repository.py` — `TrendRepository` Protocol definition (interface only; PostgreSQL implementation follows in Phase 3)
- **Backend scaffolding**: `apps/backend/src/contract/query/dataset_detail_query.py` — stub `TrendPayload` models (empty, typed correctly)

### Phase 3: User Story 1 — Pipeline Computes Multi-Lookback Trend Snapshots

Implement the `trend_analysis` library, the pipeline backfill service, and their unit/integration tests. Canonical weighting must be deterministic and versioned.

- `libs/trend_analysis/src/trend_analysis/models.py` — `LookbackSnapshot`, `CanonicalDescriptor` domain models
- `libs/trend_analysis/src/trend_analysis/classifier.py` — fixed-window trend classification logic
- `libs/trend_analysis/src/trend_analysis/version.py` — weighting version string and metadata
- `libs/trend_analysis/src/trend_analysis/__init__.py` — public entrypoint: `evaluate_lookbacks`, model exports
- `apps/pipeline/src/orchestration/resources/postgres_trend_repository.py` — PostgreSQL implementation of the `TrendRepository` protocol (see `trend_repository.py` for protocol definitions added in Phase 2)
- `apps/pipeline/src/orchestration/jobs/trend_backfill_service.py` — reclassification runtime for lookback snapshots
- Tests: `test_canonical_descriptor_weighting.py`, `test_classifier.py`, `test_trend_runtime_processor_lookbacks.py`

**Checkpoint**: Pipeline computes and persists snapshots; canonical descriptor weighting is deterministic and versioned.

### Phase 4: User Story 2 — Backend Serves Canonical Trend Descriptor

Replace the existing trend span contracts with canonical descriptor and lookback snapshot contracts, implement repository reads from the pre-computed tables, and wire into the dataset detail response.

- `apps/backend/src/contract/discovery_trends.py` — replace trend span contracts with `LookbackSnapshotPayload`, `CanonicalTrendDescriptorPayload`, `TrendPayload`
- `apps/backend/src/contract/query/dataset_detail_query.py` — add `trend: TrendPayload | None` to `DatasetDetailResponse`
- `apps/backend/src/query/dataset_discovery_persisted_repository.py` — reads for canonical descriptor + lookback snapshots
- Tests: `test_dataset_detail_lookback_snapshot_contract.py`

**Checkpoint**: Dataset detail API returns `trend` payload; contract tests pass.

### Phase 5: User Story 3 — Frontend Renders Canonical Trend Chip

Add `DatasetTrendChip`, update `DatasetDetailAnalysis` to use it, remove the obsolete overlay components, and scrub their usages from `ObservationsChart`.

- `apps/frontend/src/components/discovery/DatasetTrendChip.tsx` — new chip; reads `TrendPayload` from discovery-types
- `apps/frontend/src/components/discovery/DatasetDetailAnalysis.tsx` — replace overlay section with `DatasetTrendChip`
- `apps/frontend/src/components/discovery/ObservationsChart.tsx` — remove `TrendTooltipController` usage
- Remove `apps/frontend/src/components/trends/TrendOverlayLayer.tsx`
- Remove `apps/frontend/src/components/trends/TrendTooltipController.tsx`
- Tests: `apps/frontend/tests/components/DatasetTrendChip.test.tsx`

**Checkpoint**: Chip renders correctly; no import errors for removed files; all frontend tests pass.

### Phase 6: Polish

Update documentation, AGENTS.md guidance, and run full monorepo stop gates.

- Update `specs/044-multi-horizon-trends/quickstart.md` and `research.md` with final execution notes
- Update `AGENTS.md` for canonical descriptor behavior guidance
- Run focused frontend checks: typecheck + biome
- Run full monorepo test stop gate: `pnpm exec nx run-many -t test --all`
- Run full monorepo coverage gate: `pnpm exec nx run-many -t coverage --all`
- Run end-to-end manual verification from clean stack

## Data Model

See `data-model.md` for entity definitions.

### New Tables

#### `lookback_trend_snapshots`

| Column | Type | Notes |
|---|---|---|
| `id` | `BIGINT PK` | auto-increment |
| `series_id` | `TEXT NOT NULL` | FK to `data_series.series_id` |
| `window` | `TEXT NOT NULL` | `1M` \| `6M` \| `1Y` \| `5Y` |
| `direction` | `TEXT NOT NULL` | `rising` \| `falling` \| `stable` \| `insufficient_data` |
| `confidence` | `FLOAT NULL` | null when `insufficient_data` |
| `computed_at` | `TIMESTAMPTZ NOT NULL` | pipeline run timestamp |

Unique constraint: `(series_id, window)` — one snapshot per series per window; upserted on each backfill run.

#### `canonical_trend_descriptors`

| Column | Type | Notes |
|---|---|---|
| `id` | `BIGINT PK` | auto-increment |
| `series_id` | `TEXT NOT NULL UNIQUE` | FK to `data_series.series_id` |
| `direction` | `TEXT NULL` | null when no qualifying snapshots |
| `confidence` | `FLOAT NULL` | weighted confidence; null when no qualifying snapshots |
| `weighting_version` | `TEXT NOT NULL` | identifies the weighting algorithm version |
| `computed_at` | `TIMESTAMPTZ NOT NULL` | pipeline run timestamp |

## API Contract

See `contracts/discovery-lookback-trends.openapi.yaml` for the full schema.

### Payload Extension

The existing `DatasetDetailResponse` gains an optional `trend` field:

```json
{
  "dataset_id": "...",
  "trend": {
    "canonical": {
      "direction": "rising",
      "confidence": 0.82,
      "weighting_version": "v1",
      "computed_at": "2026-04-01T00:00:00Z"
    },
    "lookbacks": [
      { "window": "1M", "direction": "rising", "confidence": 0.91, "computed_at": "..." },
      { "window": "6M", "direction": "rising", "confidence": 0.85, "computed_at": "..." },
      { "window": "1Y", "direction": "stable", "confidence": 0.60, "computed_at": "..." },
      { "window": "5Y", "direction": "insufficient_data", "confidence": null, "computed_at": "..." }
    ]
  }
}
```
