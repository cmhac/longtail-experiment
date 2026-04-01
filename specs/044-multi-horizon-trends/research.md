# Research: Current-State Multi-Lookback Trends

## Decision 1: Replace period-bounded lifecycle spans with observation-lookback snapshots

- Decision: Primary persistence model is per-observation, per-lookback current-state snapshots rather than start/end period lifecycle spans.
- Rationale: The product requirement is "what is the trend now" across fixed lookback depths, and this avoids fragile historical segmentation assumptions.
- Alternatives considered:
  - Keep span lifecycle model and derive lookbacks indirectly: rejected because it preserves the same segmentation ambiguity.
  - Compute lookbacks only in API query-time: rejected due to repeatability risk and elevated read-path compute cost.

## Decision 2: Fixed lookback catalog with applicability gating

- Decision: Use fixed lookback depths `{1,2,3,4,5,10,25,50,100,250,500,1000}` and evaluate applicability per series using update behavior + available observation depth.
- Rationale: Catalog consistency simplifies persistence/query contracts while applicability avoids false precision on sparse or short histories.
- Alternatives considered:
  - Dynamic per-series lookback selection: rejected because contracts/UI become unstable across datasets.
  - Depth-only gating with no frequency context: rejected because very low-update series can produce misleading short-lookback descriptors.

## Decision 3: Weighted canonical trend descriptor computed in pipeline and persisted

- Decision: Compute one deterministic weighted canonical descriptor upstream (pipeline) from applicable lookback snapshots, persist it, and serve it via API.
- Rationale: Ensures one canonical answer across clients and keeps frontend purely presentational.
- Alternatives considered:
  - Compute weighted descriptor in frontend: rejected by requirement for cross-client consistency and auditability.
  - Compute weighted descriptor in backend query layer only: rejected because it duplicates runtime logic and weakens replay determinism.

## Decision 4: Keep snapshot history plus latest projection

- Decision: Persist descriptor snapshots at observation granularity and expose latest canonical descriptor in dataset detail response.
- Rationale: Supports replay/audit while keeping read contract simple for the UI chip.
- Alternatives considered:
  - Persist latest descriptor only: rejected because it loses historical traceability for reclassification verification.

## Decision 5: Pipeline failure isolation and idempotency remain mandatory

- Decision: Continue branch-scoped failure handling and state-based idempotency for lookback writes.
- Rationale: Existing trend runtime has proven semantics for failure isolation and retry safety and should be preserved through the model change.
- Alternatives considered:
  - Fail entire run on any lookback failure: rejected due to unacceptable blast radius.
  - Run-id idempotency only: rejected because unchanged data retries can still duplicate writes.

## Decision 6: Dataset detail contract migrates from `trend_spans` to canonical chip payload

- Decision: Replace overlay span payload reliance with API-provided canonical descriptor (plus optional lookback snapshot payload for diagnostics).
- Rationale: Product direction removes overlays and requires render-ready chip data with no client ranking logic.
- Alternatives considered:
  - Continue returning `trend_spans` and infer chip client-side: rejected because it preserves client computation and old abstraction.

## Decision 7: Decommission frontend trend overlay components in this feature

- Decision: Remove overlay rendering paths and introduce a compact dataset detail trend chip under the title.
- Rationale: Simplifies UX and aligns with canonical descriptor ownership in pipeline/backend.
- Alternatives considered:
  - Keep overlay behind feature flag while adding chip: rejected for scope complexity and split UX semantics.

## Decision 8: Grounding from repository history and active seams

- Decision: Use existing trend vertical seams as migration anchors, based on recent commits (`2e2f890`, `65af051`, `6cd2f09`, `da067b7`) and live code in:
  - `libs/trend_analysis/src/trend_analysis/classifier.py`
  - `apps/pipeline/src/orchestration/jobs/trend_runtime_processor.py`
  - `apps/pipeline/src/orchestration/resources/postgres_trend_repository.py`
  - `libs/db/alembic/versions/0011_trend_lifecycle_tables.py`
  - `apps/backend/src/query/dataset_discovery_service.py`
  - `apps/backend/src/query/dataset_discovery_persisted_repository.py`
  - `apps/frontend/src/components/discovery/DatasetDetailAnalysis.tsx`
  - `apps/frontend/src/components/trends/TrendOverlayLayer.tsx`
- Rationale: Reduces migration risk by modifying established paths rather than creating a parallel trend stack.
- Alternatives considered:
  - Introduce new sidecar trend modules in each layer: rejected due to duplication and rollout complexity.
