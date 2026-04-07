# Library and Tool Decisions (Spec 050)

## Decision 1 - Primary robust slope estimator

- Date: 2026-04-07
- Choice area: Primary robust slope estimator for per-lookback scoring
- Options presented:
  1. `scipy.stats.theilslopes`
  2. `sklearn.linear_model.TheilSenRegressor`
  3. Hybrid (`theilslopes` primary, sklearn for special multivariate cases)
- Recommended option: 1
- User selection: **1**
- Final decision: Use `scipy.stats.theilslopes` as the primary robust slope estimator.

## Decision 2 - Monotonic evidence implementation path

- Date: 2026-04-07
- Choice area: Monotonic evidence as confidence modifier
- Options presented:
  1. SciPy-first (`scipy.stats.kendalltau` + optional `weightedtau`)
  2. Custom in-house corrected/seasonal Mann-Kendall implementation
  3. Deferred advanced path (start SciPy-only, add corrected MK later)
- Recommended option: 3
- User selection: **1**
- Final decision: Use SciPy-first monotonic evidence with `scipy.stats.kendalltau` (and optional `weightedtau`) as modifier inputs.

## Decision 3 - Default smoothing method strategy

- Date: 2026-04-07
- Choice area: Default preprocessing smoothing method
- Options presented:
  1. EWMA-only default (`pandas.Series.ewm`)
  2. Rolling-median-only default (`pandas.Series.rolling(...).median()`)
  3. Two-step default (rolling median then EWMA)
  4. Adaptive default by series noise profile
- Recommended option: 1
- User selection: **1**
- Final decision: Use EWMA-only as the default smoothing method.

## Decision 4 - Seasonal adjustment tool by cadence

- Date: 2026-04-07
- Choice area: Seasonal adjustment decomposition tooling
- Options presented:
  1. `STL` only for all eligible cadences
  2. `MSTL` only for all eligible cadences
  3. Cadence-aware split (`STL` for monthly/weekly single-season cases; `MSTL` for regular sub-daily multi-season cases)
- Recommended option: 3
- User selection: **3**
- Final decision: Use cadence-aware split: `STL` for monthly/weekly single-season cases and `MSTL` for regular sub-daily multi-season cases.

## Decision 5 - Change-point metadata detector strategy

- Date: 2026-04-07
- Choice area: Additive change-point/regime metadata detector
- Options presented:
  1. `ruptures` only (offline batch metadata)
  2. `river` ADWIN only (streaming metadata)
  3. `statsmodels` Markov switching only (regime context)
  4. Dual-path (`ruptures` + `river` ADWIN)
- Recommended option: 4
- User selection: **1**
- Final decision: Use `ruptures` only for change-point metadata in this phase.

## Decision 6 - OLS diagnostics implementation source

- Date: 2026-04-07
- Choice area: Supplementary OLS diagnostics computation for detail/as-of payloads
- Options presented:
  1. `statsmodels` OLS for diagnostics
  2. NumPy/SciPy linear fit + custom diagnostics
  3. Hybrid (NumPy/SciPy primary, `statsmodels` for selected diagnostics)
- Recommended option: 1
- User selection: **1**
- Final decision: Use `statsmodels` OLS for diagnostic field computation.

## Decision 7 - EWMA implementation engine

- Date: 2026-04-07
- Choice area: Concrete implementation for EWMA default smoothing
- Options presented:
  1. `pandas.Series.ewm`
  2. `statsmodels.tsa.holtwinters.SimpleExpSmoothing`
  3. Hybrid (pandas runtime, statsmodels offline calibration)
- Recommended option: 1
- User selection: **1**
- Final decision: Use `pandas.Series.ewm` for EWMA smoothing in production trend preprocessing.
