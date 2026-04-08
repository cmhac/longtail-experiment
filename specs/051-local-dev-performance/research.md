# Research: Local Development Performance Stabilization (Spec 051)

## Decision 1: Dataset detail metadata retrieval must be dataset-scoped

- Decision: Use a dataset-targeted metadata retrieval path for detail requests instead of loading and scanning full catalog metadata for every detail lookup.
- Rationale: Current behavior performs broad catalog aggregation work when only one dataset is requested, creating avoidable latency that grows with catalog size.
- Alternatives considered:
  - Keep full-catalog retrieval and add in-memory caching: rejected because it retains heavy global query work and introduces cache invalidation complexity in local development.
  - Keep current behavior and optimize only frontend loading UI: rejected because it does not address backend request-time bottleneck.

## Decision 2: As-of descriptor candidate mapping should minimize non-essential filtering work

- Decision: Keep as-of descriptor correctness semantics, but reduce candidate assembly/filtering cost by constraining work to the minimal candidate set needed per dataset detail response.
- Rationale: The current detail observation path performs extra candidate processing beyond what is required for each response; reducing this work improves latency without changing payload shape.
- Alternatives considered:
  - Remove as-of descriptor mapping from detail response: rejected because it would alter behavior expected by existing consumers.
  - Leave candidate path unchanged and optimize only DB connection behavior: rejected because this leaves a significant detail-path hotspot unresolved.

## Decision 3: Local runtime request overhead should be reduced while preserving safety checks

- Decision: Reduce avoidable per-request backend runtime setup overhead while preserving schema readiness and runtime safety guarantees.
- Rationale: Repeated setup costs can add noticeable latency in local development where developers rapidly reload and navigate between detail pages.
- Alternatives considered:
  - Disable readiness/safety checks entirely in local development: rejected because it weakens reliability and can hide environment drift issues.
  - Treat local slowness as acceptable and defer to production-only optimization: rejected because local feedback-loop speed is a primary developer productivity requirement.

## Decision 4: Frontend behavior remains functionally unchanged

- Decision: Preserve dataset detail route, response consumption, and error semantics on the frontend; focus optimization on backend and request-path efficiency.
- Rationale: The user-visible delay occurs before detail content is available, and the current route behavior is functionally correct.
- Alternatives considered:
  - Redesign route loading architecture: rejected for scope creep relative to the identified bottlenecks.
  - Introduce new client-side data contract shapes: rejected because the feature goal is performance stabilization without contract churn.

## Decision 5: Validation protocol uses before/after local measurements plus regression checks

- Decision: Validate improvement with a fixed local sample of dataset detail pages and repeated-load runs, and confirm no regressions on related discovery endpoints.
- Rationale: Feature success criteria are local and measurable; results must be comparable on the same environment.
- Alternatives considered:
  - Use ad hoc subjective verification only: rejected because it cannot prove SC-001/SC-002/SC-003.
  - Validate only one detail page: rejected because it does not represent realistic variance across dataset sizes.

## Decision 6: Contract stability is a hard requirement

- Decision: Preserve existing discovery endpoint payload shape and error behavior while improving request performance.
- Rationale: This feature targets speed improvements, not interface redesign; contract stability lowers rollout risk.
- Alternatives considered:
  - Introduce a new detail endpoint contract for performance mode: rejected due to unnecessary migration complexity.

No unresolved technical clarifications remain for planning.

## Baseline Measurement Notes (Template + Captured Sample)

### Representative fixed sample (exactly 9 datasets)

- Small history (3)
  - `LABOR.US.NYFED.RECENT_COLLEGE_GRAD_UNEMPLOYMENT` (~432 observations)
  - `LABOR.US.NYFED.RECENT_COLLEGE_GRAD_UNDEREMPLOYMENT` (~432 observations)
  - `INT.US.FEDFUNDS` (~861 observations)
- Medium history (3)
  - `ENERGY.US.RETAIL_GASOLINE.SCA` (~1351 observations)
  - `ENERGY.US.ONHIGHWAY_DIESEL.SCA` (~1606 observations)
  - `ENERGY.US.ONHIGHWAY_DIESEL.R50` (~1673 observations)
- Large history (3)
  - `ENERGY.US.RETAIL_GASOLINE.R40` (~1770 observations)
  - `ENERGY.US.RETAIL_GASOLINE.NUS` (~1854 observations)
  - `ENERGY.US.GASREGW` (~1854 observations)

### Baseline note template

| Dataset ID | Size Bucket | Run Type | Samples | Median (ms) | P95 (ms) | Observation Count | Notes |
|------------|-------------|----------|---------|-------------|----------|-------------------|-------|
| `<dataset_id>` | small/medium/large | baseline/after | `10` | `<value>` | `<value>` | `<value>` | `<notes>` |

## US1 Evidence (Detail metadata path optimization)

- Repository detail lookup now uses dataset-scoped SQL (`WHERE ds.series_key = :dataset_id`) in `get_dataset_detail` instead of loading/scanning full catalog rows.
- Local post-change timing sample (10 calls each):

| Dataset ID | Size Bucket | Run Type | Samples | Median (ms) | P95 (ms) | Observation Count | Notes |
|------------|-------------|----------|---------|-------------|----------|-------------------|-------|
| `ENERGY.US.ONHIGHWAY_DIESEL.SCA` | medium | after | 10 | 436.57 | 508.83 | 1606 | `observation_sort` preserved (`observed_on_asc,reported_at_asc`) |
| `ENERGY.US.ONHIGHWAY_DIESEL.R50` | medium | after | 10 | 406.82 | 449.15 | 1673 | contract shape unchanged |

## US2 Evidence (As-of candidate path invariants)

- Candidate assembly is now scoped by observation id in SQL and keyed by `observation_id` in repository mapping to avoid cross-observation in-memory filtering.
- Contract/integration checks confirm:
  - as-of candidate selection still picks the latest valid candidate per observation,
  - canonical descriptor payload shape remains unchanged,
  - lookback evidence semantics remain unchanged.

## US3 Evidence (Runtime overhead stability)

- HTTP server startup now caches expected Alembic head resolution once (`_cached_expected_revision`) and reuses a shared schema-checked engine builder (`_make_checked_engine`) across discovery/auth/notification services.
- Safety behavior is preserved (schema readiness checks still execute before service initialization).

## SC-004 Error-Rate/Behavior Parity Results

| Surface | Before | After | Result |
|---------|--------|-------|--------|
| Dataset detail not found (`dataset_not_found`) | expected 404 | observed 404 | PASS |
| Detail invalid request validation | expected 400 | observed 400 | PASS |
| Detail page client error fallback | expected `ErrorState` render | observed unchanged | PASS |
| Catalog/search/source/topic/geography routes | no contract regressions | no contract regressions | PASS |

## Stop-Gate Execution Log

- Pre-commit gate: `uvx pre-commit run --all-files` -> PASS
  - Note: plain `pre-commit run --all-files` was unavailable in this shell (`pre-commit: command not found`), so `uvx` was used to execute the same hook set.
- Full test gate: `pnpm exec nx run-many -t test --all` -> PASS
- Full coverage gate: `pnpm exec nx run-many -t coverage --all` -> PASS
