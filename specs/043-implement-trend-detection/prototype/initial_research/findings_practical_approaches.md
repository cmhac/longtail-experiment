# Practical Trend Detection for Financial & Economic Data Platforms

**Research date:** 2026-03-31  
**Scope:** How real-world platforms detect and surface trends to non-expert users of monthly economic/financial data series

---

## 1. How Major Platforms Signal Trends to Users

### FRED (Federal Reserve Economic Data)

FRED does not apply automated trend labels or scoring. It surfaces trends through **standardized change metrics** that users choose from a dropdown:

- **Change** — absolute difference from the previous period
- **Change from Year Ago** — absolute YoY difference
- **Percent Change** — MoM % change (e.g. `+0.4%`)
- **Percent Change from Year Ago** — YoY % change (the most commonly cited "trend" signal)
- **Compounded Annual Rate of Change** — annualizes a period percentage
- **Continuously Compounded Rate of Change** — log-based annualized

The **year-over-year (YoY) % change** is FRED's canonical method for surfacing trend direction on monthly series—it eliminates seasonality by comparing the same month across years. FRED also surfaces **percent change from 1 year ago** prominently via its default chart annotation (e.g. "Inflation: +2.9% from a year ago").

Sources:

- https://fred.stlouisfed.org/docs/api/fred/
- https://fred.stlouisfed.org/ (series observation transform documentation)

### BLS (Bureau of Labor Statistics)

The BLS CPI release press kit always leads with:

- **1-month % change** (short-term signal, seasonally adjusted)
- **12-month % change** (trend signal, unadjusted—"inflation over the past year")
- **6-month change** used in shelter estimates as the workhorse rolling window

The BLS X-13ARIMA-SEATS seasonal adjustment removes known seasonal patterns first; the resulting trend/cycle component is what's treated as indicative of actual trend direction.

Sources:

- https://www.bls.gov/opub/hom/cpi/calculation.htm

### Conference Board Leading Economic Indicators (LEI)

The Conference Board LEI system signals trend changes through **streak rules**: if the 6-month smoothed rate of change crosses a threshold and a set number of components turn in the same direction, a "turning point" is signaled. The widely cited heuristic: **3 consecutive monthly declines or increases** in the composite index is treated as an early signal. This "runs" or "consecutive direction" approach is a common practical shorthand.

### Bloomberg Terminal

Bloomberg surfaces trend labels in several ways:

- Color-coded arrows on screener views (↑↓→)
- "52-week high/low" proximity as a proxy for trend strength
- Moving average crossovers (50-day vs. 200-day, i.e., "golden cross" / "death cross")
- Custom signals via BQL (Bloomberg Query Language) where users compare `LAST_PRICE()` to rolling moving averages

For non-expert economic data, Bloomberg Briefs and Bloomberg Economics contextually label series as "accelerating," "decelerating," "contracting," or "stabilizing" using plain language derived from comparing recent to prior periods.

### Financial Data Journalism (NYT Upshot, Reuters Graphics, FT Data)

These outlets use **interpreted sentence templates**:

- "Unemployment has fallen for 6 consecutive months"
- "Inflation is rising at its fastest pace in 4 decades" — framing magnitude vs. history
- "Growth has slowed for the third consecutive quarter"

The patterns: consecutive direction count, magnitude vs. historical range (percentile in history), and acceleration/deceleration vs. prior window.

---

## 2. Simple, Interpretable Trend Scoring Approaches

### Approach A: Percent Change Over a Rolling Window (Most Common)

The simplest and most universally understood method for non-expert users:

```python
import pandas as pd

def pct_change_window(series: pd.Series, window_months: int) -> float:
    """Compute % change from window_months ago to most recent observation."""
    if len(series) < window_months + 1:
        return None
    latest = series.iloc[-1]
    prior = series.iloc[-(window_months + 1)]
    if prior == 0:
        return None
    return (latest - prior) / prior * 100
```

Typical windows for monthly economic data:

- **3-month (1 quarter)**: short-term momentum
- **6-month (semi-annual)**: medium-term direction, eliminates most seasonal noise
- **12-month (YoY)**: gold standard—fully seasonal, compares like-for-like

### Approach B: Consecutive Directional Observations ("Runs Count")

Count how many consecutive periods the series has moved in the same direction. This is interpretable ("rising for N consecutive months") and used by the Conference Board LEI:

```python
def consecutive_direction(series: pd.Series) -> tuple[str, int]:
    """
    Returns (direction, count) where direction is 'up', 'down', or 'flat'.
    count is the number of consecutive periods in that direction.
    """
    diffs = series.diff().dropna()
    if len(diffs) == 0:
        return 'flat', 0

    last_sign = None
    count = 0
    for d in reversed(diffs.values):
        sign = 'up' if d > 0 else ('down' if d < 0 else 'flat')
        if last_sign is None:
            last_sign = sign
            count = 1
        elif sign == last_sign:
            count += 1
        else:
            break
    return last_sign, count
```

Signal threshold: **3+ consecutive months** in the same direction is typically treated as a confirmed trend signal in monthly series context (by analogy with the Conference Board LEI heuristic).

### Approach C: Linear Regression Slope Over a Window

Fit a regression to a rolling window and use the slope (normalized to units per period or annualized %) as a continuous trend score. This is slightly more robust to outliers than raw % change:

```python
import numpy as np
from scipy import stats

def rolling_slope_score(series: pd.Series, window_months: int) -> dict:
    """
    Fit OLS on the last window_months of observations.
    Returns slope, r_squared, and a normalized slope (slope / mean * 100 for comparability).
    """
    if len(series) < window_months:
        return None

    y = series.iloc[-window_months:].values
    x = np.arange(len(y))
    slope, intercept, r_value, p_value, _ = stats.linregress(x, y)
    mean_val = np.mean(y)
    normalized_slope = (slope / mean_val) * 100 if mean_val != 0 else 0

    return {
        'slope': slope,
        'r_squared': r_value ** 2,
        'normalized_slope_pct_per_month': normalized_slope,
        'p_value': p_value,
    }
```

The `r_squared` value indicates how "clean" or consistent the trend is—useful for filtering "noisy" uptrends from clean ones.

### Approach D: Exponentially Weighted Moving Average (EWMA) Direction

Compare the short-term EWMA to the long-term EWMA. When short > long, series is trending up. Used in technical analysis as EMA crossoveras:

```python
def ewma_trend_direction(series: pd.Series, short_span: int = 3, long_span: int = 12) -> str:
    short_ema = series.ewm(span=short_span, adjust=False).mean().iloc[-1]
    long_ema = series.ewm(span=long_span, adjust=False).mean().iloc[-1]

    ratio = (short_ema - long_ema) / long_ema * 100 if long_ema != 0 else 0
    return short_ema, long_ema, ratio
```

---

## 3. Trend Classification vs. Trend Detection

### Trend Detection (Binary)

"Is there a trend?" — requires detecting a structural directional change against noise. Statistical tests (Mann-Kendall, Cox-Stuart, runs test) answer this question with p-values. These are appropriate for deciding whether to compute or display a trend label at all.

**Mann-Kendall test** (via `pymannkendall` library):

- Nonparametric test for monotonic trend
- Returns `trend` ('increasing' / 'decreasing' / 'no trend'), p-value, slope (Sen's slope)
- Does not assume normality—appropriate for economic series

```python
import pymannkendall as mk

result = mk.original_test(series.values)
# result.trend: 'increasing', 'decreasing', 'no trend'
# result.p: p-value
# result.slope: Sen's slope (robust median-based slope estimate)
```

### Trend Classification (5-label or 3-label)

Once a trend is detected (or regardless of significance), you can classify its **strength and direction** into a user-facing label.

#### 5-label classification (recommended for non-expert users):

| Label                | Criteria (using 12-month YoY % change as `pct_yoy`) |
| -------------------- | --------------------------------------------------- |
| **Strong uptrend**   | `pct_yoy > +5%` OR slope is positive AND `r² > 0.7` |
| **Mild uptrend**     | `+1% < pct_yoy ≤ +5%`                               |
| **Flat / Stable**    | `-1% ≤ pct_yoy ≤ +1%`                               |
| **Mild downtrend**   | `-5% ≤ pct_yoy < -1%`                               |
| **Strong downtrend** | `pct_yoy < -5%`                                     |

These thresholds should be domain-calibrated: a 5% YoY change is notable for CPI but unremarkable for equity markets. For monthly economic series reporting rates like unemployment (measured in percentage points), use absolute-change thresholds (e.g. ±0.5pp = mild, ±1.5pp = strong).

#### Simpler 3-label scheme (for general non-expert contexts):

```python
def classify_trend(pct_yoy: float, flat_band: float = 1.0) -> str:
    """
    Classify trend based on year-over-year percent change.
    flat_band: percentage points within which the series is considered flat.
    """
    if pct_yoy is None:
        return 'unknown'
    if pct_yoy > flat_band:
        return 'rising'
    elif pct_yoy < -flat_band:
        return 'falling'
    else:
        return 'stable'
```

#### Combined scoring approach (recommended):

Combine _direction_ (YoY % change sign) with _strength_ (magnitude) and _consistency_ (R² or consecutive-period count):

```python
def trend_score(series: pd.Series, window: int = 12) -> dict:
    """
    Returns a composite trend assessment combining:
    - direction and magnitude (YoY pct change)
    - consistency (rolling slope R²)
    - momentum (consecutive directional periods)
    """
    pct_12m = pct_change_window(series, 12)
    pct_3m = pct_change_window(series, 3)
    slope_info = rolling_slope_score(series, window)
    direction, consecutive = consecutive_direction(series)

    # Classify magnitude
    if pct_12m is None:
        label = 'insufficient_data'
    elif abs(pct_12m) < 1.0:
        label = 'stable'
    elif pct_12m > 0:
        label = 'strong_uptrend' if pct_12m > 5 else 'mild_uptrend'
    else:
        label = 'strong_downtrend' if pct_12m < -5 else 'mild_downtrend'

    return {
        'label': label,
        'pct_change_12m': pct_12m,
        'pct_change_3m': pct_3m,
        'consecutive_periods': consecutive,
        'consecutive_direction': direction,
        'r_squared': slope_info['r_squared'] if slope_info else None,
        'slope_pct_per_month': slope_info['normalized_slope_pct_per_month'] if slope_info else None,
    }
```

---

## 4. Minimum Window Before Calling a Trend (Monthly Series)

| Source / Convention             | Minimum Window                        | Rationale                                               |
| ------------------------------- | ------------------------------------- | ------------------------------------------------------- |
| Conference Board LEI            | **3 consecutive months**              | Streak of 3 same-direction changes = early trend signal |
| NBER recession criteria (GDP)   | **2 consecutive quarters = 6 months** | Strong floor for "contraction" label                    |
| BLS CPI trend references        | **12 months (YoY)**                   | Eliminates seasonal variation entirely                  |
| BLS shelter components          | **6 months**                          | 6-month rolling window for rent/OER estimates           |
| Financial journalism convention | **6–12 months**                       | "6-month high" or "12-month trend" phrases are common   |
| Mann-Kendall minimum            | **~10–12 observations**               | Below ~10 the test has very low power                   |

**Practical recommendation for monthly economic series:**

- **3-month window**: sufficient for short-term momentum signal ("accelerating / decelerating")
- **6-month window**: minimum for a directional trend claim in public-facing copy
- **12-month (YoY)**: the gold standard—fully accounts for seasonality, appropriate for annual KPI-style labels

> **Rule of thumb:** Do not classify a series as "in a trend" using fewer than **6 monthly observations**. Display "insufficient data" or no label for series with fewer than 6 periods. Prefer YoY when seasonality may exist.

---

## 5. Python Libraries and Recipes

### 5a. For Interpretable Trend Scoring

| Library                      | Use Case                                                  | Notes                                                                                                      |
| ---------------------------- | --------------------------------------------------------- | ---------------------------------------------------------------------------------------------------------- |
| **`pandas`**                 | Rolling window stats, EWMAs, consecutive runs             | Zero extra deps; sufficient for most use cases                                                             |
| **`scipy.stats.linregress`** | OLS slope + R² over a window                              | Built into scientific Python stack                                                                         |
| **`statsmodels` STL**        | Seasonal decomposition (trend + seasonal + residual)      | Strong approach for separating true trend from seasonal effects; `STL(series, period=12).fit()`            |
| **`pymannkendall`**          | Statistical trend detection with p-values and Sen's slope | Nonparametric; appropriate for non-normal economic data                                                    |
| **`statsforecast`** (Nixtla) | AutoARIMA/ETS forecasting at scale                        | Useful if deriving trend from a fitted model's trend component; not built for classification labels        |
| **`tsfresh`**                | Feature extraction from time series (bulk)                | Extracts 700+ features including trend slope; more appropriate for ML pipelines than interpretable scoring |

### 5b. Simplest Production-Ready Recipe (Pure pandas + scipy)

```python
import pandas as pd
import numpy as np
from scipy import stats

def compute_trend_metrics(
    observations: list[tuple],  # [(date, value), ...]
    flat_band_pct: float = 1.0,
    min_observations: int = 6,
) -> dict:
    """
    Given a list of (date, value) observations sorted ascending,
    compute interpretable trend metrics.
    """
    series = pd.Series(
        [v for _, v in observations],
        index=pd.to_datetime([d for d, _ in observations]),
    ).sort_index()

    if len(series) < min_observations:
        return {'label': 'insufficient_data', 'pct_change_12m': None}

    # YoY % change
    pct_12m = None
    if len(series) >= 13:
        pct_12m = (series.iloc[-1] - series.iloc[-13]) / series.iloc[-13] * 100

    # 6-month % change (fallback)
    pct_6m = None
    if len(series) >= 7:
        pct_6m = (series.iloc[-1] - series.iloc[-7]) / series.iloc[-7] * 100

    primary_pct = pct_12m if pct_12m is not None else pct_6m

    # Linear slope over last 12 months (or available)
    window = min(12, len(series))
    y = series.iloc[-window:].values
    x = np.arange(len(y))
    slope, _, r_value, p_value, _ = stats.linregress(x, y)
    mean_val = np.mean(y)
    normalized_slope = (slope / mean_val) * 100 if mean_val != 0 else 0

    # Consecutive direction
    diffs = series.diff().dropna()
    direction, consec = 'stable', 0
    if len(diffs) > 0:
        last_sign = None
        for d in reversed(diffs.values):
            s = 'up' if d > 0 else ('down' if d < 0 else 'flat')
            if last_sign is None:
                last_sign, consec = s, 1
            elif s == last_sign:
                consec += 1
            else:
                break
        direction = last_sign or 'stable'

    # Classify
    if primary_pct is None:
        label = 'insufficient_data'
    elif abs(primary_pct) < flat_band_pct:
        label = 'stable'
    elif primary_pct > 0:
        label = 'strong_uptrend' if primary_pct > 5 else 'mild_uptrend'
    else:
        label = 'strong_downtrend' if primary_pct < -5 else 'mild_downtrend'

    return {
        'label': label,                              # e.g. 'mild_uptrend'
        'pct_change_12m': round(pct_12m, 2) if pct_12m else None,
        'pct_change_6m': round(pct_6m, 2) if pct_6m else None,
        'slope_pct_per_month': round(normalized_slope, 3),
        'r_squared': round(r_value ** 2, 3),
        'consecutive_direction': direction,          # 'up' | 'down' | 'flat'
        'consecutive_count': consec,
    }
```

### 5c. Seasonal Adjustment Before Trend Classification

For monthly series with clear seasonality (retail, energy, housing), strip the seasonal component before computing the trend:

```python
from statsmodels.tsa.seasonal import STL

def extract_trend_component(series: pd.Series, period: int = 12) -> pd.Series:
    """Extract the trend component from a monthly series using STL decomposition."""
    result = STL(series, period=period, robust=True).fit()
    return result.trend  # Use this series for trend scoring
```

---

## 6. Scheduling and Storage Patterns for Trend Results

### When to Recalculate

| Pattern                               | Appropriate When                                                                            | Used By                                                     |
| ------------------------------------- | ------------------------------------------------------------------------------------------- | ----------------------------------------------------------- |
| **After every ingest** (event-driven) | Monthly data where each new observation materially extends the window                       | Recommended for datasets updated monthly or less frequently |
| **Nightly batch**                     | Daily-resolution data or high-frequency updates; recalculating after every tick is wasteful | Market data platforms                                       |
| **Weekly batch**                      | Weekly or coarser update cadence                                                            | Government statistical releases                             |
| **On demand (no precalculation)**     | Small dataset, fast query                                                                   | Acceptable for prototypes; not for production API serving   |

For monthly economic data (like what this project ingests), **after-ingest recalculation** is the appropriate pattern: each new observation arrives at most once per month, the window is meaningful (12 months = 12 events), and recalculating after every new observation ensures trend labels are always fresh.

### Storage Schema (Recommended Pattern)

Materialize trend results into a dedicated table:

```sql
CREATE TABLE dataset_trend_scores (
    series_id         TEXT        NOT NULL,
    as_of_date        DATE        NOT NULL,       -- date of the most recent observation used
    calculated_at     TIMESTAMPTZ NOT NULL DEFAULT NOW(),

    -- Window identifiers
    window_months     INT         NOT NULL,       -- 6 or 12

    -- Scores
    label             TEXT        NOT NULL,       -- 'strong_uptrend' | 'mild_uptrend' | 'stable' | etc.
    pct_change        NUMERIC(10,4),              -- e.g. +3.21 (percent)
    slope_pct_per_month NUMERIC(10,4),            -- normalized slope
    r_squared         NUMERIC(5,4),
    consecutive_direction TEXT,                   -- 'up' | 'down' | 'flat'
    consecutive_count INT,

    PRIMARY KEY (series_id, as_of_date, window_months)
);

CREATE INDEX ON dataset_trend_scores (series_id, as_of_date DESC);
```

**API serving**: Join `dataset_trend_scores` to the series metadata on `series_id`, filtering for the latest `as_of_date` per series. This keeps query latency flat regardless of how many observations exist.

### Dagster / Batch Pipeline Integration

Trigger trend recalculation as a downstream Dagster asset after the ingest asset materializes:

```python
@asset(deps=["source_observations"])
def dataset_trend_scores(context, database: DatabaseResource) -> None:
    """Recalculate trend scores for all series that received new observations."""
    # Query series updated in this run
    updated_series = database.execute(
        "SELECT DISTINCT series_id FROM ingestion_runs WHERE run_id = ?",
        [context.run_id]
    ).fetchall()

    for series_id in updated_series:
        obs = database.execute(
            "SELECT observation_date, value FROM observations WHERE series_id = ? ORDER BY observation_date",
            [series_id]
        ).fetchall()

        scores_6m = compute_trend_metrics(obs, window=6)
        scores_12m = compute_trend_metrics(obs, window=12)

        database.upsert("dataset_trend_scores", [
            {**scores_6m, 'series_id': series_id, 'window_months': 6, 'as_of_date': obs[-1][0]},
            {**scores_12m, 'series_id': series_id, 'window_months': 12, 'as_of_date': obs[-1][0]},
        ])
```

### API Response Shape

Embed trend data directly in the dataset detail API response:

```json
{
  "series_id": "PRICE.US.CPI",
  "name": "US Consumer Price Index",
  "trend": {
    "label": "mild_uptrend",
    "pct_change_12m": 2.87,
    "pct_change_6m": 1.44,
    "slope_pct_per_month": 0.23,
    "r_squared": 0.81,
    "consecutive_direction": "up",
    "consecutive_count": 4,
    "window_months": 12,
    "as_of_date": "2026-02-01"
  }
}
```

**For list/catalog views**, compute a single summary reading (`label`, `pct_change_12m`) to display inline badges ("↑ +2.9% past year").

---

## Summary: Recommended Approach for This Project

1. **Use YoY % change (12-month window)** as the primary trend signal for monthly series—it eliminates seasonality and is the most universally understood metric.

2. **Use 6-month % change** as a secondary/momentum signal for series with fewer than 13 observations.

3. **Apply a 5-label classification** using domain-calibrated thresholds: strong_uptrend / mild_uptrend / stable / mild_downtrend / strong_downtrend.

4. **Minimum 6 observations** before calculating any trend; display "N/A" or omit the trend badge below this threshold.

5. **Compute after every ingest** for monthly series — the event-driven trigger ensures labels are always current at a low recalculation cost.

6. **Store pre-computed scores** in a `dataset_trend_scores` table (one row per series × window), joined at query time. Do not recalculate on every API request.

7. **For interpretable summaries**: prefer human-readable phrases like "rising for 4 consecutive months" or "up +2.9% over the past year" over numeric scores alone.

---

## Sources

- FRED API documentation: https://fred.stlouisfed.org/docs/api/fred/
- BLS Handbook of Methods — CPI Calculation: https://www.bls.gov/opub/hom/cpi/calculation.htm
- Minneapolis Fed CPI table (Annual % Change convention): https://www.minneapolisfed.org/about-us/monetary-policy/inflation-calculator/consumer-price-index-1913-
- Investopedia — Trend definition and classification: https://www.investopedia.com/terms/t/trend.asp
- Nixtla StatsForecast — time series modeling: https://pypi.org/project/statsforecast/
- pymannkendall Python library (Mann-Kendall trend test): https://pypi.org/project/pymannkendall/
- Conference Board LEI methodology: https://www.conference-board.org/research/indicators/leading-economic-indicators (composite index methodology guide)
- statsmodels STL documentation: https://www.statsmodels.org/stable/generated/statsmodels.tsa.seasonal.STL.html
