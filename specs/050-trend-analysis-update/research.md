# Research: Trend Analysis Upgrade (Spec 050)

## Decision 1: Primary robust per-lookback slope estimator

- Decision: Use `scipy.stats.theilslopes` as the primary per-lookback trend slope estimator.
- Rationale: Robust full-window slope behavior with native slope confidence bounds fits the requirement to reduce endpoint sensitivity while preserving interpretable evidence payloads.
- Alternatives considered:
  - `sklearn.linear_model.TheilSenRegressor`: rejected as default due to heavier estimator semantics and unnecessary multivariate overhead for core univariate lookback scoring.

## Decision 2: Monotonic evidence modifier

- Decision: Use `scipy.stats.kendalltau` as rank-based monotonic evidence input and apply it as a weighted confidence modifier, not an absolute gate.
- Rationale: Meets FR-021 with mature, maintained tooling and clean output semantics (`tau`, `pvalue`) suitable for bounded weighting.
- Alternatives considered:
  - In-house corrected/seasonal Mann-Kendall implementation in phase 1: deferred to later phase if replay data shows need.
  - Outdated packages (`pymannkendall`, `mannkendall`): rejected by recency policy.

## Decision 3: Default smoothing behavior

- Decision: Apply EWMA preprocessing by default using `pandas.Series.ewm`.
- Rationale: Causal, efficient, and easily parameterized smoothing with explicit metadata fields (`halflife`, `adjust`, `ignore_na`, `min_periods`) supports FR-004/FR-022 traceability requirements.
- Alternatives considered:
  - Rolling-median-only default: rejected as sole default due to responsiveness tradeoff.
  - Two-step median->EWMA default: deferred; can be introduced per-series if noise profile warrants.

## Decision 4: Seasonal adjustment by cadence

- Decision: Use cadence-aware split: `statsmodels` STL for monthly/weekly eligible series and MSTL for regular eligible sub-daily series; keep daily on non-seasonally-adjusted path this phase.
- Rationale: Directly aligns with FR-031 and phase scope constraints while allowing explicit fallback conditions when decomposition reliability criteria are not met.
- Alternatives considered:
  - STL-only for all cadences: rejected for multi-season sub-daily limitations.
  - MSTL-only for all cadences: rejected due to unnecessary complexity for single-season cases.

## Decision 5: Change-point/regime context metadata

- Decision: Use `ruptures` only for additive change-point metadata in this phase.
- Rationale: Mature offline segmentation with clear runtime controls supports FR-024 tie-break/context requirements without coupling canonical direction to detector output.
- Alternatives considered:
  - `river` ADWIN dual-path: deferred.
  - `statsmodels` Markov switching as primary context engine: deferred for complexity.
  - Outdated `kats`: rejected by recency policy.

## Decision 6: OLS diagnostics as supplementary evidence

- Decision: Use `statsmodels` OLS diagnostics for canonical/per-lookback supplementary fields in detail/as-of payloads.
- Rationale: Rich diagnostics and clear semantics reduce custom statistical implementation risk while satisfying FR-033/FR-034.
- Alternatives considered:
  - NumPy/SciPy custom diagnostics path: rejected as higher maintenance risk for phase 1.

## Decision 7: Contract and rollout semantics

- Decision: Hard-cutover versioned trend contracts include explicit `flat`, numeric confidence, and unavailable descriptor semantics with local reset posture.
- Rationale: Matches clarified contract strategy and FR-016/FR-019/FR-041 requirements.
- Alternatives considered:
  - Dual-contract overlap period: rejected by explicit hard-cutover decision.

## Decision 8: Evidence exposure boundaries

- Decision: Detail and as-of endpoints expose evidence payload (including OLS diagnostics); summary/list endpoints remain canonical-only.
- Rationale: Keeps primary UX stable and avoids overloading list surfaces while preserving traceability where needed.
- Alternatives considered:
  - Expose full evidence payload on summary/list: rejected by FR-031/FR-036 clarifications.

## Tool Recency Resolution

- Decision: Exclude tools with latest release older than one year.
- Rationale: Reduces maintenance and security risk for core statistical dependencies.
- Alternatives considered:
  - Include stale packages for convenience: rejected.

Excluded by policy:
- `pymannkendall`
- `mannkendall`
- `kats`

No unresolved technical clarifications remain for planning.
