# Implementation Plan: Current-State Multi-Lookback Trends

**Branch**: `044-multi-horizon-trends` | **Date**: 2026-04-01 | **Spec**: `/specs/044-multi-horizon-trends/spec.md`
**Input**: Feature specification from `/specs/044-multi-horizon-trends/spec.md`

## Summary

Replace period-bound trend spans with per-observation multi-lookback trend snapshots across the full stack. For each newly persisted observation, the pipeline will evaluate a fixed lookback catalog in parallel, persist per-lookback current-state outcomes, compute one weighted canonical trend descriptor upstream, and expose that descriptor via backend contracts so frontend dataset detail renders a single chip without client-side trend ranking logic. This plan is grounded in current trend implementation seams observed in git history (`2e2f890`, `65af051`, `6cd2f09`, `da067b7`) and current code paths in `libs/trend_analysis`, pipeline trend runtime/repositories, backend discovery query surfaces, Alembic migration history, and frontend trend overlay components.

## Technical Context

**Language/Version**: Python 3.12 (libs/backend/pipeline), TypeScript 5.x + React 19 + Next.js 15 (frontend)  
**Primary Dependencies**: SQLAlchemy 2.x, Alembic, Pydantic 2.x, Dagster 1.x, pytest, Ruff, Ty, HeroUI 3, Tailwind, Biome, Vitest  
**Storage**: PostgreSQL 16 (`observations`, `data_series`, existing `trend_records`/`trend_transition_events`, plus new lookback snapshot + canonical descriptor persistence)  
**Testing**: pytest + pytest-cov, Vitest + coverage, pre-commit, Nx monorepo test/coverage gates  
**Target Platform**: Local Docker Compose parity and Linux container runtime  
**Project Type**: Nx monorepo vertical slice spanning library + pipeline + db + backend API + frontend app  
**Performance Goals**: Per-observation trend processing remains bounded and parallelized across applicable lookbacks; dataset detail response remains deterministic and lightweight for direct chip render  
**Constraints**: Deterministic outputs, idempotent reprocessing, failure isolation by series/lookback, no client-side trend weighting logic, >=90% coverage in affected projects  
**Scale/Scope**: All trend-enabled discovery series; lookback catalog `{1,2,3,4,5,10,25,50,100,250,500,1000}` with applicability gating by update behavior + history depth

## Constitution Check

_GATE: Must pass before Phase 0 research. Re-check after Phase 1 design._

- Monorepo cohesion: PASS. Changes are explicitly scoped to `libs/trend_analysis`, `libs/db`, `apps/pipeline`, `apps/backend`, and `apps/frontend` with synchronized contracts.
- Quality gate enforcement: PASS. Plan includes lint/format/typecheck/test and pre-commit loops per stage without suppressions.
- Full-suite stop rule: PASS. Plan mandates `pnpm exec nx run-many -t test --all` before commit and handoff.
- Coverage stop rule: PASS. Plan mandates `pnpm exec nx run-many -t coverage --all` before commit.
- Test and coverage discipline: PASS. Each layer includes contract/unit/integration coverage updates.
- Local-first parity: PASS. Manual validation runs on fresh Docker Compose restarts.
- Data integrity and reliability: PASS. Deterministic lookback snapshot + canonical descriptor persistence, auditability, and idempotency are first-class.
- Configuration integrity: PASS. No new credentialed service surface; existing hard-fail env policy remains unchanged.
- Frontend UI consistency: PASS. HeroUI/Tailwind and shared component reuse are maintained; overlay stack is removed.
- Documentation fidelity: PASS. Plan generates and aligns research/data-model/contracts/quickstart for this feature.

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
    ├── alembic/versions/
    └── src/db/

apps/pipeline/
├── src/orchestration/jobs/
├── src/orchestration/resources/
└── tests/orchestration/

apps/backend/
├── src/contract/
├── src/contract/query/
├── src/query/
└── tests/

apps/frontend/
├── src/components/discovery/
├── src/components/trends/
├── src/lib/api/
└── tests/
```

**Structure Decision**: Keep existing vertical-slice boundaries and replace legacy trend-span seams in place instead of introducing parallel trend stacks.

## Phase 0: Research and Design Decisions

1. Confirm weighted canonical descriptor policy from lookback snapshots and define deterministic tie-breaking.
2. Define applicability policy for each lookback depth based on available history and update-frequency characteristics.
3. Decide whether canonical descriptor is stored per latest observation only or historized by observation timestamp; choose historized snapshots with explicit latest projection for deterministic replay/audit.
4. Confirm migration strategy from existing `trend_records` period model to lookback snapshot model without breaking dataset detail contracts during rollout.
5. Record selected approach and rejected alternatives in `research.md`.

## Phase 1: Design Artifacts and Contracts

1. Create `data-model.md` with new entities for:
   - observation lookback snapshot persistence
   - lookback applicability outcomes
   - canonical weighted descriptor
   - compatibility/deprecation relation to existing trend lifecycle tables
2. Create API contract updates in `contracts/discovery-lookback-trends.openapi.yaml` covering dataset detail trend payload replacement for chip use.
3. Create `quickstart.md` with red/green/manual validation commands spanning all impacted layers.
4. Run `.specify/scripts/bash/update-agent-context.sh codex` and retain generated context updates.

## Phase 2: Implementation Plan (Execution-Ready)

### Stage A: Library Model and Deterministic Multi-Lookback Classification

1. Refactor `libs/trend_analysis/src/trend_analysis/classifier.py` to support batch evaluation over fixed lookback depths instead of period-window segmentation.
2. Extend `libs/trend_analysis/src/trend_analysis/models.py` to represent:
   - per-lookback outcomes
   - applicability/inapplicability reasoning
   - canonical weighted descriptor payload
3. Keep cadence/frequency interpretation deterministic and owned by library defaults.
4. Add tests in `libs/trend_analysis/tests/` for:
   - lookback applicability depth boundaries
   - deterministic weighted canonical descriptor output
   - stable results for identical ordered inputs

### Stage B: Database and Persistence Model Migration

1. Add Alembic migration in `libs/db/alembic/versions/` introducing lookback snapshot tables and canonical descriptor persistence structures.
2. Preserve historical auditability and idempotency constraints via unique indexes keyed to series, observation, and lookback depth.
3. Explicitly mark legacy `trend_records` period semantics as deprecated for primary product reads in migration and repository code comments.

### Stage C: Pipeline Runtime and Repository Integration

1. Update `apps/pipeline/src/orchestration/jobs/trend_runtime_processor.py` to run lookback evaluation per new observation in parallel for applicable depths.
2. Replace lifecycle-transition write path in `apps/pipeline/src/orchestration/jobs/trend_lifecycle_service.py` and `apps/pipeline/src/orchestration/resources/postgres_trend_repository.py` with snapshot + canonical descriptor writes.
3. Preserve branch-scoped failure isolation and idempotent reprocessing semantics.
4. Add orchestration tests in `apps/pipeline/tests/orchestration/` for:
   - partial lookback failure isolation
   - no duplicate snapshots on retry
   - canonical descriptor persistence correctness

### Stage D: Backend Contract and Query Layer Migration

1. Replace trend-span contract models in `apps/backend/src/contract/query/dataset_detail_query.py` with canonical descriptor + optional lookback snapshot payload structures.
2. Update query mappings in `apps/backend/src/query/dataset_discovery_persisted_repository.py` and `apps/backend/src/query/dataset_discovery_service.py` to read new snapshot/descriptors from persistence.
3. Decommission span normalization path in `apps/backend/src/query/trend_span_mapper.py` where no longer needed.
4. Add/adjust backend tests for contract validity, response compatibility, and error behavior for missing canonical descriptor data.

### Stage E: Frontend Simplification to API-Driven Chip Rendering

1. Remove overlay-specific consumption paths from:
   - `apps/frontend/src/components/discovery/DatasetDetailAnalysis.tsx`
   - `apps/frontend/src/components/trends/TrendOverlayLayer.tsx`
   - `apps/frontend/src/components/trends/TrendTooltipController.tsx`
2. Update API types/client in:
   - `apps/frontend/src/lib/api/discovery-types.ts`
   - `apps/frontend/src/lib/api/discovery-client.ts`
3. Add a dataset-detail chip component below dataset title using only API-provided canonical descriptor data.
4. Add frontend tests verifying:
   - no overlay rendering
   - chip render + unavailable state
   - no client-side weighting/ranking behavior

### Stage F: End-to-End Hardening and Release Readiness

1. Manual local-stack validation from clean runtime (`docker compose down && docker compose up -d`) for ingest -> pipeline -> API -> UI chip flow.
2. Run repeated `pre-commit run --all-files` during iteration.
3. Run mandatory stop gates:
   - `pnpm exec nx run-many -t test --all`
   - `pnpm exec nx run-many -t coverage --all`
4. Verify docs/spec artifacts and contracts remain aligned with implemented behavior.

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

No constitution violations or exception requests identified.
