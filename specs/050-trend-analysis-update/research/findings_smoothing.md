# Findings: EWMA and Robust Rolling Median Smoothing (Python)

## Scope

Research focus: practical Python implementations for EWMA and robust rolling-median smoothing in time-series preprocessing, including library recommendations, parameterization, edge handling, and interpretability metadata patterns for downstream API contracts.

## Recommended Libraries

1. **Primary default: pandas (`Series.ewm`, `Series.rolling`)**
   - Best fit for tabular time-series pipelines and per-series preprocessing.
   - Strong control over decay, missingness behavior, warm-up handling (`min_periods`), and time-aware windows.

2. **Robust median fallback/alternative: SciPy (`scipy.ndimage.median_filter`)**
   - Useful when explicit boundary modes are needed (`reflect`, `nearest`, `constant`, etc.) or multidimensional filtering is relevant.
   - Caveat: docs explicitly warn NaN behavior is undefined.

3. **Model-based EW smoothing option: statsmodels (`SimpleExpSmoothing`)**
   - Useful when treating smoothing as a fitted model (estimated smoothing parameter, initialization method) rather than a fixed preprocessing transform.
   - Heavier than pandas for routine preprocessing, but good for diagnostics and model-governed parameter estimation.

## Practical Implementation Patterns

### A) EWMA via pandas

Use `Series.ewm(...).mean()` for smoothing before trend-evidence calculation.

Typical choices:
- **Regular cadence**: tune with `halflife` (or `span`) in number-of-points terms.
- **Irregular cadence**: use `times=` plus timedelta `halflife` in `mean()` so decay aligns to elapsed time rather than row count.
- **Streaming-like behavior**: prefer `adjust=False` (recursive form) for easy explainability as state update.
- **Batch unbiased early periods**: `adjust=True` (default) if you want normalized weighted averaging at the beginning.

Example:

```python
smoothed = series.ewm(
    halflife="14 days",
    times=series.index,      # must be monotonic datetime64[ns]
    adjust=False,
    ignore_na=True,
    min_periods=3,
).mean()
```

### B) Rolling median via pandas

Use `Series.rolling(window=...).median()` for robust local smoothing against outliers/spikes.

Typical choices:
- **Point-based window** for stable cadence (`window=5`, `window=7`, etc.).
- **Offset/time window** for irregular timestamps (`window="30D"`).
- **Trailing window (`center=False`)** for causal/as-of pipelines.
- **Centered window (`center=True`)** for retrospective analytics, not real-time canonical descriptor generation.

Example:

```python
median_smoothed = series.rolling(
    window=7,
    min_periods=4,
    center=False,
).median()
```

### C) Median filter with explicit edge modes (SciPy)

Use when edge-extension semantics must be explicit and reproducible:

```python
from scipy.ndimage import median_filter

median_smoothed = median_filter(
    series.to_numpy(),
    size=7,
    mode="reflect",   # or nearest/constant/mirror/wrap
)
```

## Parameterization Strategies

1. **EWMA decay should map to cadence intent**
   - Daily: start with `halflife` around 7-30 points depending on responsiveness target.
   - Weekly/monthly: map halflife to meaningful business horizon (e.g., 6 weeks, 3 months).
   - Prefer `halflife` over raw `alpha` for interpretability in API metadata.

2. **Rolling median window should map to expected noise burst length**
   - Use odd windows (3/5/7/9) for stable center/trailing interpretation.
   - Shorter window = faster response, less denoising; longer window = stronger denoising, more lag.

3. **Warm-up policy should be explicit (`min_periods`)**
   - Keep `min_periods` in metadata and contract payloads so consumers understand when smoothing is provisional vs fully populated.

4. **Missingness policy should be explicit for EWMA**
   - `ignore_na=False`: weighting tied to absolute positions.
   - `ignore_na=True`: weighting tied to relative non-missing positions.

## Edge Handling Guidance

1. **Boundary periods**
   - EWMA: choose `adjust` strategy and expose it.
   - Rolling median: decide trailing vs centered and minimum required observations.

2. **Irregular timestamps**
   - Prefer `ewm(..., times=..., halflife=...)` and offset-based rolling windows to avoid misleading equal-step assumptions.

3. **NaNs**
   - Pandas supports explicit missingness handling (`ignore_na` in EWMA, `min_periods` in rolling).
   - SciPy median filter docs caution that NaN behavior is undefined; pre-clean or avoid SciPy median when NaNs are common.

4. **Deterministic edge extension**
   - If edge behavior must be tightly controlled/documented, SciPy `mode` can be advantageous versus implicit window truncation semantics.

## Interpretability Metadata Patterns for Downstream API Contracts

Recommended metadata block per smoothed series (or per lookback evaluation input):

```json
{
  "smoothing": {
    "applied": true,
    "method": "ewma",                       
    "library": "pandas",
    "library_version": "3.x",
    "parameters": {
      "halflife": "14 days",
      "adjust": false,
      "ignore_na": true,
      "min_periods": 3,
      "times_used": true
    },
    "windowing": {
      "orientation": "trailing",
      "causal": true
    },
    "input_points": 180,
    "output_non_null_points": 178,
    "warmup_points": 2,
    "missing_input_points": 5,
    "edge_policy": "ewma_recursive",
    "lineage": {
      "input_field": "value",
      "output_field": "value_smoothed",
      "preprocess_version": "smoothing_v1"
    }
  }
}
```

For rolling median, use analogous fields with `method: "rolling_median"`, `window`, `center`, and explicit boundary policy. If SciPy is used, include `mode` and `cval` (when constant mode applies).

Contract pattern suggestions:
- Include **method + parameters + version** so downstream services can reproduce/compare outputs.
- Include **causality marker** (`causal=true/false`) to prevent accidental use of centered windows in as-of/canonical computations.
- Include **data-quality counters** (missing points, warm-up points) so confidence and applicability logic can down-weight weakly-supported smoothed outputs.
- Include **lineage identifiers** (`preprocess_version`, optional hash/fingerprint of config) to support auditability and backfill comparisons.

## Key Quotes and Source Facts

### pandas EWMA

> "Exactly one of `com`, `span`, `halflife`, or `alpha` must be provided if `times` is not provided."  
Source: https://pandas.pydata.org/docs/reference/api/pandas.Series.ewm.html

> "When `adjust=False`, the exponentially weighted function is calculated recursively."  
Source: https://pandas.pydata.org/docs/reference/api/pandas.Series.ewm.html

> "Only applicable to `mean()`. Times corresponding to the observations. Must be monotonically increasing and `datetime64[ns]` dtype."  
Source: https://pandas.pydata.org/docs/reference/api/pandas.Series.ewm.html

### pandas rolling windows

> "If an integer, the delta between the start and end of each window." / "If a timedelta, str, or offset, the time period of each window."  
Source: https://pandas.pydata.org/docs/reference/api/pandas.Series.rolling.html

> "Minimum number of observations in window required to have a value; otherwise, result is `np.nan`."  
Source: https://pandas.pydata.org/docs/reference/api/pandas.Series.rolling.html

### SciPy median filter

> "mode {'reflect', 'constant', 'nearest', 'mirror', 'wrap'}"  
Source: https://docs.scipy.org/doc/scipy/reference/generated/scipy.ndimage.median_filter.html

> "behavior in the presence of NaNs is undefined"  
Source: https://docs.scipy.org/doc/scipy/reference/generated/scipy.ndimage.median_filter.html

### statsmodels SimpleExpSmoothing

> "Simple Exponential Smoothing" / "fit ... [smoothing_level, optimized, ...]"  
Source: https://www.statsmodels.org/stable/generated/statsmodels.tsa.holtwinters.SimpleExpSmoothing.html

> "Method for initialize the recursions. One of: None, 'estimated', 'heuristic', 'legacy-heuristic', 'known'"  
Source: https://www.statsmodels.org/stable/generated/statsmodels.tsa.holtwinters.SimpleExpSmoothing.html

## Source URLs

1. https://pandas.pydata.org/docs/reference/api/pandas.Series.ewm.html  
2. https://pandas.pydata.org/docs/reference/api/pandas.Series.rolling.html  
3. https://docs.scipy.org/doc/scipy/reference/generated/scipy.ndimage.median_filter.html  
4. https://www.statsmodels.org/stable/generated/statsmodels.tsa.holtwinters.SimpleExpSmoothing.html
