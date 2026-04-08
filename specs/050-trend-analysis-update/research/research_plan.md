## Main Research Question

Which concrete libraries, tooling choices, and implementation patterns are best suited for implementing the statistical techniques required by `specs/050-trend-analysis-update/spec.md` (Theil-Sen trend estimation, rank-based monotonic evidence, smoothing, STL/MSTL seasonal adjustment, and change-point metadata) in this repository's Python-first trend-analysis stack?

## Subtopics

1. **Robust slope estimation with Theil-Sen**
   - Expected information: production-ready Python library options, API behavior, confidence interval support, computational tradeoffs, and suitability for rolling/as-of lookback evaluation.

2. **Rank-based monotonic evidence (Kendall tau / Mann-Kendall)**
   - Expected information: best libraries for significance testing under time-series conditions (including seasonality/autocorrelation caveats), output semantics, and recommended usage as weighted confidence modifiers.

3. **Default preprocessing with smoothing (EWMA and robust rolling median)**
   - Expected information: reliable Python APIs and patterns for EWMA + rolling median, parameterization guidance, and strategies to preserve interpretability metadata for downstream contracts.

4. **Seasonal adjustment for weekly/monthly and regular sub-daily data (STL/MSTL)**
   - Expected information: mature decomposition tooling, data regularity requirements, period selection guidance, robustness settings, and fallback conditions when decomposition is unreliable.

5. **Change-point/regime-shift detection as tie-break metadata**
   - Expected information: practical Python libraries and patterns for low-latency change-point detection, confidence scoring, and use as additive context rather than primary direction selection.

## Synthesis Plan

I will synthesize findings into implementation recommendations tailored to this monorepo's existing Python pipeline/library architecture, including:
- Preferred primary libraries per technique,
- Secondary/fallback library choices,
- Concrete implementation patterns for lookback-as-of trend computation,
- Risk/limitation notes (complexity, assumptions, irregular cadence behavior), and
- A practical adoption order aligned with the feature's phased rollout requirements.
