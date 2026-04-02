# Research: Historical As-Of Trend Tooltips

## Decision 1: Resolve as-of trend per observation in backend service assembly

- Decision: Resolve one canonical descriptor for each observation returned in dataset detail payload assembly, then serialize it directly on each observation.
- Rationale: Tooltip interactions are point-specific and must not infer historical state client-side; backend authority preserves deterministic behavior and keeps frontend simple.
- Alternatives considered:
  - Resolve as-of state in frontend from lookback snapshots: rejected because this reintroduces client-side ranking/weighting logic.
  - Add a dedicated lookup endpoint called on hover: rejected due to latency and interaction complexity.

## Decision 2: Reuse canonical descriptor shape for observation-level as-of payloads

- Decision: Observation-level payload uses the same descriptor semantics as existing dataset-level canonical descriptor (`descriptor_state`, `trend_label`, `direction`, `strength`, `selected_lookback_points`, `observed_on`, `reason_code`).
- Rationale: One consistent descriptor contract reduces mapping drift and lets shared `DatasetTrendIndicator` remain reusable.
- Alternatives considered:
  - Introduce tooltip-only enums: rejected because it duplicates semantics and adds translation layers.
  - Use nullable free-form object: rejected because explicit contract validation is required.

## Decision 3: As-of selection rule uses observation context with deterministic tie-breaks

- Decision: For each detail observation, resolve the canonical descriptor representing that observation context by matching observation date and selecting deterministically when multiple candidates could map:
  1. Prefer descriptors bound to the same `observed_on` date.
  2. If multiple candidates remain, select the most recent candidate by stable ordering rule (latest persisted descriptor for that observation context).
  3. If no candidate exists, emit explicit `descriptor_state=unavailable` with a reason code.
- Rationale: Meets FR-006 determinism and avoids ambiguous tooltip state on dense or revised observation histories.
- Alternatives considered:
  - Nearest-previous date fallback: rejected because it can misstate trend state for same-day multi-report observations.
  - Random/first-hit ordering from SQL result set: rejected as non-deterministic.

## Decision 4: Keep current dataset-level canonical trend fields unchanged

- Decision: Continue returning existing top-level detail fields (`canonical_trend_descriptor`, `lookback_trend_snapshots`) while adding observation-level as-of descriptor fields.
- Rationale: Preserves backward compatibility and existing summary/detail UI behavior while enabling new tooltip behavior.
- Alternatives considered:
  - Replace top-level canonical descriptor with observation-only model: rejected as breaking change.
  - Remove lookback snapshots: rejected because diagnostics and existing contracts rely on them.

## Decision 5: Tooltip chip integration uses shared indicator component

- Decision: Render one `DatasetTrendIndicator` chip at the bottom of each tooltip instance using observation-specific as-of descriptor.
- Rationale: Maintains UI consistency with existing trend indicator semantics and conforms to HeroUI + shared component constitution requirements.
- Alternatives considered:
  - Inline ad hoc arrow markup in tooltip: rejected because it duplicates visual logic.
  - Text-only trend string: rejected because requirement explicitly calls for trend indicator chip.

## Decision 6: No schema migration required for this feature

- Decision: Use existing trend persistence tables and repository capabilities to resolve observation-level descriptors; this slice is contract + query/service + UI wiring.
- Rationale: Persisted trend artifacts already exist and the feature asks for retrieval/wiring, not new persistence semantics.
- Alternatives considered:
  - Add new table for tooltip state cache: rejected as unnecessary complexity.
  - Materialize frontend-specific denormalized trend rows: rejected because current canonical descriptors are sufficient.

## Repository Seams Confirmed

- Backend detail response model: `apps/backend/src/contract/query/dataset_detail_query.py`
- Backend summary descriptor model: `apps/backend/src/contract/query/dataset_search_query.py`
- Backend detail assembly and trend reads: `apps/backend/src/query/dataset_discovery_service.py` and `apps/backend/src/query/dataset_discovery_persisted_repository.py`
- Frontend detail + observation types: `apps/frontend/src/lib/api/discovery-types.ts`
- Frontend tooltip rendering seam: `apps/frontend/src/components/discovery/ObservationsChart.tsx`
- Shared indicator component: `apps/frontend/src/components/discovery/DatasetTrendIndicator.tsx`

## Phase 1 Setup Validation

- Artifact alignment validation completed across:
  - `specs/045-asof-trend-tooltips/spec.md`
  - `specs/045-asof-trend-tooltips/plan.md`
  - `specs/045-asof-trend-tooltips/data-model.md`
  - `specs/045-asof-trend-tooltips/contracts/discovery-asof-trend-tooltips.openapi.yaml`
- Validation result: all four artifacts use the same feature scope (dataset-detail as-of trend descriptors and tooltip chip rendering), contract naming (`as_of_trend_descriptor`), and deterministic as-of selection assumptions.
- Backend implementation seams confirmed for Phase 2+: `apps/backend/src/contract/query/dataset_detail_query.py`, `apps/backend/src/query/dataset_discovery_service.py`, and `apps/backend/src/query/dataset_discovery_persisted_repository.py`.
- Frontend implementation seams confirmed for Phase 2+: `apps/frontend/src/lib/api/discovery-types.ts`, `apps/frontend/src/lib/api/discovery-client.ts`, and `apps/frontend/src/components/discovery/ObservationsChart.tsx`.

## Planning Outcome

- All technical unknowns for this feature are resolved.
- No `NEEDS CLARIFICATION` markers remain.
- Phase 1 artifact generation and Phase 2 task breakdown can proceed without blocking questions.
