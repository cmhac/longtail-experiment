# Findings: Seasonal Adjustment with STL/MSTL in Python

## Scope

Research focus: Python tooling and implementation patterns for seasonal adjustment using STL (single seasonality) and MSTL (multiple seasonalities), with emphasis on:

- Weekly/monthly series
- Regular sub-daily series (e.g., hourly, 30-minute, 5-minute)
- Data regularity requirements
- Period selection
- Robustness options
- Fallback behavior when decomposition is unreliable

## Key facts

1. `statsmodels` is the primary Python implementation for both STL and MSTL.
2. STL expects a 1D regular series and a valid seasonal period (`period`), with optional robust weighting for outliers.
3. MSTL supports multiple periods and internally iterates STL over each seasonal component.
4. MSTL requires missing-data handling outside the class and can silently drop too-long periods (>= half the sample length) with a warning.
5. Classical `seasonal_decompose` exists but is explicitly described by statsmodels as a naive method and requires at least 2 complete cycles.

## Python tooling and practical use

### Recommended library

- **Library:** `statsmodels.tsa.seasonal`
- **Use STL when:** one dominant seasonal cycle (e.g., monthly with annual cycle `period=12`, weekly with annual-like cycle approximated separately if needed)
- **Use MSTL when:** multiple seasonal cycles are expected (e.g., hourly data with daily + weekly cycles)

### Core APIs

- `statsmodels.tsa.seasonal.STL`
- `statsmodels.tsa.seasonal.MSTL`
- `statsmodels.tsa.seasonal.seasonal_decompose` (baseline/reference only)

## Data regularity requirements

### What must be true before STL/MSTL

- Series must be regularly sampled (fixed interval) and 1D.
- If using numpy arrays, period(s) must be provided explicitly.
- If using pandas time index, period may be inferred from index frequency.
- Missing values should be resolved before MSTL (impute, aggregate, or re-index + fill strategy).

### Evidence

- STL docs: "If `endog` is a ndarray, `period` must be provided."
- MSTL docs/source: "If `endog` is a ndarray, periods must be provided." and source note "Missing data must be handled outside of this class."
- `seasonal_decompose` docs: "x must contain 2 complete cycles."

## Period selection patterns

### Weekly/monthly

- **Monthly data:** use STL with `period=12` for annual seasonality.
- **Weekly data:** annual seasonality is non-integer in weeks (`365.25/7 ≈ 52.179`), so a single integer-period decomposition is approximate.
  - Practical pattern: use STL for dominant integer cycle only, or move to methods that handle complex/non-integer seasonality (e.g., harmonic regression) when annual weekly effects are important.

### Regular sub-daily

- Use MSTL with multiple periods, e.g.:
  - Hourly: `periods=(24, 24*7)`
  - 30-minutely: `periods=(48, 48*7)`
  - 5-minutely business-day-only data: period equals intervals per business day, plus weekly multiple if present.
- FPP3 example supports this structure explicitly (daily + weekly seasonal components for 5-minute call data).

### Window selection

- STL seasonal smoother window must be odd and usually `>= 7`.
- MSTL default windows are increasing odd values by component index: `7 + 4*i` (implementation default).
- Start with defaults, tune only if diagnostics indicate under/over-smoothing.

## Robustness and outlier handling

- STL has `robust=True` to use robust weighting against some outlier forms.
- MSTL passes STL kwargs via `stl_kwargs`, so robust behavior can be enabled in MSTL by passing `{"robust": True}`.
- For scale-variant or positive-only data, MSTL supports Box-Cox transform (`lmbda` or `"auto"`) before decomposition.

## Reliability checks and fallback rules

Use these guardrails before accepting decomposition as reliable:

1. **Cycle sufficiency rule**
   - Require at least 2 full cycles per seasonal period (`n >= 2 * max(periods)`) as a minimum practical threshold (hard requirement for `seasonal_decompose`, good safety threshold for STL/MSTL usage).
2. **Period feasibility rule**
   - Reject/defer any period `>= n/2` (MSTL drops these internally; make this explicit upstream).
3. **Regularity rule**
   - If cadence is irregular or has large gaps, do not run STL/MSTL directly; first regularize (resample/reindex + explicit fill policy).
4. **Residual quality rule**
   - If residual variance remains highly structured (e.g., clear leftover seasonal ACF peaks at target periods), treat decomposition as unreliable.
5. **Amplitude sanity rule**
   - If extracted seasonal component amplitude is near-zero relative to residual noise over multiple cycles, treat seasonal adjustment as low-confidence.

### Fallback strategy when unreliable

- **Fallback A (simplify):** reduce to one dominant period STL.
- **Fallback B (preprocess):** re-regularize data and retry with explicit period(s).
- **Fallback C (transform):** retry MSTL with Box-Cox (`lmbda="auto"`) and robust mode.
- **Fallback D (alternative model):** switch to dynamic harmonic regression/Fourier terms for complex or non-integer seasonality (especially weekly data with annual effects).
- **Fallback E (no adjustment):** if no stable seasonality signal remains, skip seasonal adjustment and operate on trend/smoothed raw series with a low-confidence flag.

## Implementation pattern (Python)

```python
from statsmodels.tsa.seasonal import STL, MSTL

def seasonal_adjust(series, freq_kind):
    # 1) Ensure regular cadence and no missing values (done upstream)
    # 2) Select periods
    if freq_kind == "monthly":
        periods = (12,)
    elif freq_kind == "hourly":
        periods = (24, 24 * 7)
    else:
        periods = infer_periods_somehow(series)

    # 3) Reliability pre-check
    if len(series) < 2 * max(periods):
        return None, "fallback:no_enough_cycles"

    # 4) Decompose
    if len(periods) == 1:
        res = STL(series, period=periods[0], robust=True).fit()
        seasonal = res.seasonal
    else:
        res = MSTL(series, periods=periods, lmbda="auto", stl_kwargs={"robust": True}).fit()
        seasonal = res.seasonal.sum(axis=1) if hasattr(res.seasonal, "sum") else res.seasonal

    adjusted = series - seasonal
    return adjusted, "ok"
```

## Relevant quotes and source URLs

### statsmodels STL API

- Quote: "Season-Trend decomposition using LOESS."
- Quote: "If `endog` is a ndarray, `period` must be provided."
- Quote: "Flag indicating whether to use a weighted version that is robust to some forms of outliers."
- URL: https://www.statsmodels.org/stable/generated/statsmodels.tsa.seasonal.STL.html

### statsmodels MSTL API

- Quote: "Season-Trend decomposition using LOESS for multiple seasonalities."
- Quote: "If `endog` is a ndarray, periods must be provided."
- Quote: "Length of the seasonal smoothers ... Must be an odd integer, and should normally be >= 7 (default)."
- URL: https://www.statsmodels.org/stable/generated/statsmodels.tsa.seasonal.MSTL.html

### statsmodels MSTL source implementation

- Quote: "Missing data must be handled outside of this class."
- Quote: "A period(s) is larger than half the length of time series. Removing these period(s)."
- Quote: default windows: `return tuple(7 + 4 * i for i in range(1, n + 1))`
- URL: https://www.statsmodels.org/stable/_modules/statsmodels/tsa/stl/mstl.html

### statsmodels seasonal_decompose API

- Quote: "This is a naive decomposition. More sophisticated methods should be preferred."
- Quote: "x must contain 2 complete cycles."
- URL: https://www.statsmodels.org/stable/generated/statsmodels.tsa.seasonal.seasonal_decompose.html

### Forecasting: Principles and Practice (FPP3)

- Quote: "Even weekly data can be challenging ... seasonal period of 365.25/7 ≈ 52.179 on average."
- Quote: "The STL() function is designed to deal with multiple seasonality. It will return multiple seasonal components..."
- Quote: Example uses daily and weekly periods for 5-minute data (`season(period = 169)` and `season(period = 5*169)`).
- URL: https://otexts.com/fpp3/complexseasonality.html

## Practical recommendation for this project

- Default to STL for monthly (`period=12`) and simple single-season series.
- Default to MSTL for regular sub-daily series with known multiple cycles.
- Enforce explicit prechecks (regularity, cycle sufficiency, period < n/2) before decomposition.
- Enable robust mode by default for noisy operational data.
- Route to fallback modeling (Fourier/harmonic regression or no seasonal adjustment) when reliability checks fail.
