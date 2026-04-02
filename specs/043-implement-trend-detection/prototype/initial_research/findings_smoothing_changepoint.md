# Smoothing Techniques & Change-Point Detection for Economic Time Series

> Research date: 2026-03-31  
> Focus: batch pipelines, weekly/monthly observations, economic indicators

---

## 1. Moving Averages

### Simple Moving Average (SMA)

**How it works:** Replace each value with the arithmetic mean of the surrounding _m_ values (centred):

$$\hat{T}_t = \frac{1}{m} \sum_{j=-k}^{k} y_{t+j}, \quad m = 2k+1$$

For mean-shift detection or trend extraction you almost always want a **centered** (symmetric) window so the smoothed point aligns with the time index.

**Window size guidance:**
| Data frequency | Recommended window | Notes |
|---|---|---|
| Monthly, no seasonality | 3 or 5 | Removes month-to-month noise |
| Monthly, annual seasonality | 2×12-MA | Averages each calendar month equally; eliminates seasonality |
| Weekly | 4 or 13 | 4-week = monthly; 13-week = quarterly |

A 2×12-MA is computed as a 12-point MA followed by a 2-point MA. This is the canonical way to extract the trend-cycle from monthly series with annual seasonality (e.g. CPI, employment).

**Using the smoothed series for trend direction:**

- Compute first difference of the smoothed series: `d[t] = smooth[t] - smooth[t-1]`
- Positive d → upward trend at t; negative d → downward
- To determine the _current_ direction, look at the sign of the last 2-3 consecutive differences of the smoothed series

**Python:**

```python
import pandas as pd

# SMA (centred) via pandas rolling
series = pd.Series(data)
sma5 = series.rolling(window=5, center=True, min_periods=3).mean()

# 2×12-MA for monthly seasonal data
ma12 = series.rolling(window=12, center=False, min_periods=12).mean()
sma_2x12 = ma12.rolling(window=2, min_periods=2).mean()  # centred by offset if needed

# Trend direction (sign of consecutive differences)
trend_direction = sma5.diff().apply(lambda x: 1 if x > 0 else (-1 if x < 0 else 0))
```

**Pros:**

- Dead-simple, interpretable, no hyperparameter search
- 2×12-MA perfectly eliminates annual seasonality from monthly data
- Centred window avoids phase lag in trend estimation

**Cons:**

- Loses `(m-1)/2` points at each end (no values at endpoints of the series)
- Equal weights → abrupt entry/exit of old observations (can cause artificial "steps")
- Lagging: for a trailing (non-centered) window, the smoothed value is always behind the actual data

---

### EWMA (Exponential Weighted Moving Average)

**How it works:** Weight recent observations more heavily, with weights decaying geometrically:

$$S_t = \alpha \cdot y_t + (1 - \alpha) \cdot S_{t-1}$$

α ∈ (0, 1) is the smoothing factor. Equivalent `span`: $\alpha = 2 / (\text{span} + 1)$.

**Parameter guidance:**
| α value | Equivalent span | Behaviour |
|---|---|---|
| 0.10–0.15 | 12–18 | High smoothing; lag ~6-9 months |
| 0.20–0.30 | 5–9 | Moderate; common for monthly economic data |
| 0.50+ | 1–3 | Responsive; tracks noise more closely |

For identifying slow-moving structural trends in monthly data: **α = 0.1–0.2 (span ≈ 10–20)**.

**Trend direction from EWMA:** same as SMA — compute sign of EWMA first difference. A "Golden cross" (short-span EWMA crossing above long-span EWMA) is often used as a trend-start signal.

**Python:**

```python
import pandas as pd

ewma_short = series.ewm(span=3, adjust=False).mean()   # fast — reacts quickly
ewma_long  = series.ewm(span=12, adjust=False).mean()  # slow — structural trend

# Signal: short crosses above long = upward trend started
crossover = (ewma_short > ewma_long).astype(int).diff()
# crossover == 1 → upward trend start; crossover == -1 → downward

# Alternatively, via statsmodels (also fits alpha by MLE)
from statsmodels.tsa.holtwinters import SimpleExpSmoothing
fit = SimpleExpSmoothing(series, initialization_method="estimated").fit(optimized=True)
alpha_mle = fit.params["smoothing_level"]
smoothed = fit.fittedvalues
```

**Pros:**

- No missing values at either end (runs from the first observation)
- Naturally causal (no future data); suitable for real-time/streaming pipelines
- Holt extension adds trend damping; Holt-Winters adds seasonality

**Cons:**

- Introduces phase lag proportional to 1/α
- Less interpretable than SMA when communicating to non-statisticians
- Does not remove seasonality; use STL decomposition or 2×12-MA for seasonal data first

---

## 2. Savitzky-Golay Filter

### How it works

Fits a **local polynomial** (degree _p_) to each window of _m_ equally-spaced points using least-squares, then evaluates the polynomial at the window centre. The result is equivalent to a weighted moving average where the weights are optimal for the chosen polynomial degree.

The filter is a low-pass filter that preserves peak heights and curvature better than a simple moving average of the same width.

**Python (scipy):**

```python
from scipy.signal import savgol_filter

# window_length must be odd and >= polyorder + 2
smoothed = savgol_filter(series_array, window_length=7, polyorder=2)

# Also computes 1st derivative (slope):
first_deriv = savgol_filter(series_array, window_length=7, polyorder=2, deriv=1, delta=1)
# Sign of first_deriv gives instantaneous trend direction at each point
```

**Signature:**

```
scipy.signal.savgol_filter(x, window_length, polyorder, deriv=0, delta=1.0, axis=-1, mode='interp')
```

- `window_length`: odd integer, >= polyorder+2. Must be < len(x).
- `polyorder`: 2 or 3 is typical (2/3 give identical smoothing coefficients).
- `deriv=1`: returns slope of the smoothed curve at each point.

### Parameter guidance for economic data

| Series length | window_length   | polyorder | Notes                             |
| ------------- | --------------- | --------- | --------------------------------- |
| 24–36 months  | 5               | 2         | Minimum useful smoothing          |
| 36–60 months  | 7–9             | 2         | Good noise reduction              |
| 60+ months    | 9–13            | 3         | Can handle more complex curvature |
| < 20 points   | Not recommended | —         | Use SMA instead                   |

**Applicability to short/irregular economic series:**

- **Suitable** for regularly spaced series (monthly, quarterly) with at least 15–20 points.
- **Not suitable** for irregular timestamps (gaps due to missing months, irregular release schedules). SG requires equally spaced data.
- **Endpoint artifact:** the `mode='interp'` (scipy default) fits asymmetric polynomials at the edges, which can introduce distortion in the first and last `(window_length-1)/2` points. Inspect endpoints carefully.

**Pros:**

- Better peak/level preservation than SMA (doesn't flatten peaks)
- Can directly output the first derivative (trend slope) at every point
- Reduces noise without lagging as severely as EWMA at low α

**Cons:**

- Requires equally spaced data
- Endpoint distortion in the first/last `(m-1)/2` points
- Not causal — uses future values; appropriate only for batch analysis, not real-time
- For series shorter than ~20 points, the polynomial fit becomes numerically unreliable

---

## 3. Change-Point Detection

### 3a. PELT Algorithm (`ruptures` library)

**How it works:** PELT (Pruned Exact Linear Time) finds the globally optimal segmentation of a signal into piecewise-constant (or piecewise-parametric) segments by minimising a penalised cost:

$$\min_{k, t_1,\ldots,t_k} \sum_{i=0}^{k} c(y_{t_i+1:t_{i+1}}) + k \cdot \beta$$

where c(·) is a cost function on a segment and β is the penalty per additional segment. The pruning rule achieves O(Kn) average complexity.

**Install:**

```bash
pip install ruptures
```

**Basic usage:**

```python
import numpy as np
import ruptures as rpt

# signal must be a 1D or 2D numpy array, shape (n,) or (n, d)
signal = np.array(series_values)

# PELT with l2 cost (mean-shift detection)
algo = rpt.Pelt(model="l2", min_size=6, jump=1).fit(signal)
breakpoints = algo.predict(pen=3 * np.log(len(signal)))
# Returns: [cp1, cp2, ..., n]  (n = len(signal) is always the last element)
```

**Interpreting output:** If breakpoints = [18, 42, 60], then:

- Segment 1: observations 0–17 (first regime)
- Segment 2: observations 18–41 (second regime — "trend started here" = index 18)
- Segment 3: observations 42–59 (third regime)

The change point index is the **first observation of the new segment**.

### Cost functions (`model` parameter)

| model      | Detects                                        | Best for                                           | Speed    |
| ---------- | ---------------------------------------------- | -------------------------------------------------- | -------- |
| `"l2"`     | Sudden mean-shift                              | Level breaks (e.g., recession onset, policy shock) | Fastest  |
| `"l1"`     | Median shifts (robust)                         | Outlier-contaminated data                          | Fast     |
| `"rbf"`    | Distribution changes (non-parametric)          | Gradual trend changes, volatility changes          | Slower   |
| `"normal"` | Mean AND variance shifts                       | Both level and volatility changes simultaneously   | Moderate |
| `"linear"` | Slope/trend changes in piecewise-linear signal | Long-term directional trend shifts                 | Moderate |

**For batch economic pipelines:**

- Use `"l2"` for sudden structural breaks (e.g., policy changes, financial crises).
- Use `"rbf"` for gradual trend changes (e.g., slow inflation build-up, demographic shift). The RBF kernel uses median heuristics for bandwidth — fully automatic, no tuning.
- Use `"linear"` when you expect the trend to be a changing slope (piecewise linear growth).

### Key parameters

**`min_size`** (most important for false positive control):

- Minimum number of observations between change points
- For monthly data: `min_size = 6` (6 months) to `min_size = 12` (1 year)
- Prevents detecting spurious breaks caused by single outlier months

**`pen`** (penalty per changepoint):

- Higher penalty → fewer breakpoints (more conservative)
- Lower penalty → more breakpoints (more sensitive)
- Starting points for monthly economic data (n ≈ 60):
  - Conservative: `pen = 3 * np.log(n)` → typically 1–3 breakpoints
  - Moderate: `pen = np.log(n)` → BIC criterion; 3–6 breakpoints
  - Aggressive: `pen = 0.5 * np.log(n)` → may overfit

**`jump`**: step size for candidate change point locations; `jump=1` considers every observation (slowest but most precise); `jump=5` is faster but coarser.

### Quick-start pattern for monthly economic indicators

```python
import numpy as np
import ruptures as rpt

def detect_trends(monthly_values: list[float], min_months: int = 6) -> list[int]:
    """Returns list of change point indices (first observation of each new segment)."""
    signal = np.array(monthly_values, dtype=float)
    n = len(signal)
    if n < 2 * min_months:
        return []  # too short

    algo = rpt.Pelt(model="rbf", min_size=min_months, jump=1).fit(signal)
    # pen = 3*log(n): conservative starting point; tune as needed
    bkps = algo.predict(pen=3 * np.log(n))
    # Strip the trailing n, prepend 0 to get segment starts
    segment_starts = [0] + bkps[:-1]
    return segment_starts  # e.g. [0, 14, 33] for 3 segments

# Interpret: each segment_start marks where a new trend regime began
```

---

### 3b. CUSUM (Cumulative Sum)

**How it works:** Accumulates standardised deviations from a target mean μ₀:

$$S_n^+ = \max(0,\; S_{n-1}^+ + (x_n - \mu_0) - k)$$
$$S_n^- = \min(0,\; S_{n-1}^- + (x_n - \mu_0) + k)$$

Alert when $S_n^+ > h$ (positive drift) or $S_n^- < -h$ (negative drift).

- **k** = reference value (often 0.5σ); insensitivity parameter — deviations < k are ignored.
- **h** = threshold (often 4σ–5σ for batch; lower for real-time monitoring).

**Python (from scratch):**

```python
def cusum_detect(series, k_sigma_multiplier=0.5, h_sigma_multiplier=4.0):
    """Simple CUSUM on a series. Returns list of alert indices."""
    mu = np.mean(series)
    sigma = np.std(series, ddof=1)
    k = k_sigma_multiplier * sigma
    h = h_sigma_multiplier * sigma

    S_pos, S_neg = 0.0, 0.0
    alerts = []
    for i, x in enumerate(series):
        S_pos = max(0, S_pos + (x - mu) - k)
        S_neg = min(0, S_neg + (x - mu) + k)
        if S_pos > h or S_neg < -h:
            alerts.append(i)
            S_pos, S_neg = 0.0, 0.0  # reset after alert
    return alerts
```

**Alternative via `ruptures`** (offline CUSUM-like using `Window` method):

```python
algo = rpt.Window(width=4, model="l2").fit(signal)
bkps = algo.predict(n_bkps=3)  # specify expected number of breaks
```

**Pros vs PELT:**

- CUSUM is better for **online/streaming** detection (one-pass, computes incrementally)
- More intuitive threshold interpretation (multiples of σ)
- Lower computational overhead for simple level detection

**Cons:**

- Requires a stable reference distribution (μ₀, σ: estimated from "in-control" period)
- Only detects deviations from a fixed baseline — not suitable for detecting slope changes
- False positives if σ is underestimated from a small baseline window

---

### 3c. Bayesian Change-Point Detection

**How it works:** Maintains a posterior distribution over possible change-point locations. At each time step, it computes $P(\text{change at } t \mid \text{data up to } t)$. Peaks in this posterior indicate likely change points.

**Libraries:**

```python
# Option 1: bayesian_changepoint_detection (pure Python, minimal deps)
pip install bayesian_changepoint_detection

import bayesian_changepoint_detection.offline_changepoint_detection as bcd
from functools import partial

Q, P, Pcp = bcd.offline_changepoint_detection(
    data=np.array(series),
    prior_function=partial(bcd.const_prior, p=1/(len(series)+1)),
    observation_log_likelihood_function=bcd.gaussian_obs_log_likelihood,
    truncate=-50
)
# Pcp: posterior probability of change at each index
probable_cps = np.where(np.exp(Pcp).max(0) > 0.5)[0]  # indices where prob > 50%

# Option 2: Use ruptures with Dynp (exact Bayesian-style via penalised cost)
algo = rpt.Dynp(model="normal", min_size=6).fit(signal)
bkps = algo.predict(n_bkps=2)  # if you know expected number of breaks
```

**Interpreting Bayesian output as "trend started here":**

- A peak in the posterior at index t means: "the data is most consistent with a structural break starting at observation t"
- For economic interpretation: combine with the direction of change (compare means of the two segments around the break)

**Pros:**

- Produces uncertainty estimates — you know _how confident_ the model is about each break
- Works well when the number of breaks is uncertain
- Can incorporate prior domain knowledge (e.g., "breaks are rare — expected ~1 per year")

**Cons:**

- Slower than PELT for large series
- More complex to configure and explain to stakeholders
- `bayesian_changepoint_detection` package has limited maintenance; consider `ruptures` + prior specification via `Dynp` instead

---

## 4. Reducing False Positives

### Primary lever: `min_size`

The single most effective way to suppress false positives in `ruptures` PELT:

```python
# Monthly: require at least 6 months in each segment
algo = rpt.Pelt(model="l2", min_size=6).fit(signal)
```

For weekly data: `min_size=4` (4 weeks ≈ 1 month).

### Penalty tuning

| Scenario                                | Suggested `pen` | Effect                                        |
| --------------------------------------- | --------------- | --------------------------------------------- |
| Very conservative (1–2 breaks expected) | `5 * log(n)`    | Almost never fires                            |
| Moderate (structural analysis)          | `3 * log(n)`    | Good starting point for monthly economic data |
| BIC (balanced)                          | `log(n)`        | Standard information criterion                |
| Sensitive (exploratory)                 | `0.5 * log(n)`  | Many small segments; often overfits noise     |

**Cross-validation approach:** run PELT with a range of penalties, plot the "elbow" in number of breakpoints vs. penalty, and choose the penalty at the inflection point.

```python
penalties = np.linspace(0.5, 10, 20) * np.log(len(signal))
n_bkps = []
for pen in penalties:
    bkps = rpt.Pelt(model="l2", min_size=6).fit(signal).predict(pen=pen)
    n_bkps.append(len(bkps) - 1)  # subtract 1 because last element is always n

# Choose pen where the elbow occurs (diminishing returns in new breakpoints)
```

### Post-detection filters

After running PELT, validate each detected segment with:

1. **Directional consistency:** within a segment, require that > 60% of month-over-month changes point in the same direction before labelling it a "trend".
2. **Minimal slope magnitude:** fit OLS on each segment; signal if `|slope| > 2 × std_error_of_slope`.
3. **Persistence:** require the segment to contain at least N observations before surfacing as a confirmed trend (N = min_size).

```python
import numpy as np
from scipy.stats import linregress

def validate_segment(values: np.ndarray, min_observations: int = 6) -> dict:
    """Returns trend direction and whether it's statistically significant."""
    if len(values) < min_observations:
        return {"trend": None, "confident": False}

    x = np.arange(len(values))
    slope, intercept, r_val, p_val, stderr = linregress(x, values)
    significant = abs(slope) > 2 * stderr and p_val < 0.05
    direction = "up" if slope > 0 else "down"
    return {"trend": direction, "slope": slope, "p_value": p_val, "confident": significant}
```

---

## 5. `ruptures` Library Summary

**Install:** `pip install ruptures` (no heavy deps; just numpy/scipy)

**Key detection algorithms:**

| Class           | Algorithm                     | When to use                                                   |
| --------------- | ----------------------------- | ------------------------------------------------------------- |
| `rpt.Pelt`      | PELT (optimal, linear-cost)   | General purpose; best for moderate-length series (n < 10,000) |
| `rpt.Dynp`      | Dynamic programming (exact)   | Small series (n < 500); when you know exact number of breaks  |
| `rpt.Binseg`    | Binary segmentation (greedy)  | Very long series; approximate but fast                        |
| `rpt.BottomUp`  | Bottom-up merging             | Useful when n_bkps is unknown and coarse                      |
| `rpt.Window`    | Sliding window                | Simple, streaming-compatible                                  |
| `rpt.KernelCPD` | Kernel CPD (fast PELT w/ rbf) | Efficient version of rbf for larger n                         |

**Workflow:**

```python
import ruptures as rpt
import numpy as np

signal = np.array(your_series)        # shape (n,) or (n, d)

# 1. Choose algorithm and cost
algo = rpt.Pelt(model="rbf", min_size=6, jump=1)

# 2. Fit
algo.fit(signal)

# 3. Predict (with penalty — unknown number of breaks)
bkps = algo.predict(pen=3 * np.log(len(signal)))

# OR predict with known number of breaks
bkps = algo.predict(n_bkps=2)

# 4. Visualise
import matplotlib.pyplot as plt
fig, ax_arr = rpt.display(signal, bkps)
plt.show()
```

**Model selection guide (gradual vs sudden):**

- **Sudden breaks** (instantaneous level shift): `model="l2"` or `model="l1"`
- **Gradual trend shift** (distribution slowly drifting): `model="rbf"`
- **Slope change** (trend accelerates/decelerates): `model="linear"`
- **Volatility change** (variance increases/decreases): `model="normal"`

---

## 6. Noise vs Real Directional Trend: Recommended Approach

### Key principle

A single anomalous observation or a 2-month reversal is noise. A **directional trend** requires:

1. A statistically significant change-point (via PELT/CUSUM)
2. Persistence across multiple periods (≥ min_size observations)
3. Consistent direction within the segment

### Recommended pipeline for monthly economic indicators

```python
import numpy as np
import pandas as pd
import ruptures as rpt
from statsmodels.tsa.seasonal import STL

def detect_economic_trend(monthly_series: pd.Series,
                           min_months: int = 6,
                           pen_multiplier: float = 3.0) -> dict:
    """
    Full trend detection pipeline for monthly economic data.
    Returns detected regime boundaries and their directions.
    """
    series = monthly_series.dropna()
    n = len(series)
    values = series.values.astype(float)

    # Step 1: Remove seasonality if series is long enough (>= 2 full years)
    if n >= 24:
        stl = STL(series, period=12, robust=True).fit()
        deseasonalised = stl.trend + stl.resid  # remove seasonal component
    else:
        deseasonalised = values  # too short — skip STL

    # Step 2: Light smoothing (3-point SMA to suppress single-month noise)
    ds = pd.Series(deseasonalised)
    smoothed = ds.rolling(3, center=True, min_periods=2).mean().values

    # Step 3: PELT change-point detection on smoothed series
    if n < 2 * min_months:
        return {"breakpoints": [], "segments": []}

    algo = rpt.Pelt(model="rbf", min_size=min_months, jump=1)
    bkps = algo.fit(smoothed).predict(pen=pen_multiplier * np.log(n))

    # Step 4: Characterise each segment
    segments = []
    starts = [0] + bkps[:-1]
    ends = bkps

    for start, end in zip(starts, ends):
        seg_values = values[start:end]
        if len(seg_values) < 3:
            continue
        x = np.arange(len(seg_values))
        from scipy.stats import linregress
        slope, _, r, p, se = linregress(x, seg_values)
        segments.append({
            "start_index": start,
            "end_index": end,
            "length_months": end - start,
            "mean": float(np.mean(seg_values)),
            "slope_per_month": float(slope),
            "direction": "up" if slope > 0 else "down",
            "significant": abs(slope) > 2 * se and p < 0.1,
        })

    return {"breakpoints": bkps[:-1], "segments": segments}
```

### Rule-of-thumb thresholds (monthly economic data)

| Parameter                 | Value                                               | Rationale                                      |
| ------------------------- | --------------------------------------------------- | ---------------------------------------------- | --------- | ----------------------------------- |
| SMA pre-smoothing window  | 3                                                   | Removes extreme single-month noise without lag |
| PELT `min_size`           | 6 months                                            | < 6 consecutive months is not a "trend"        |
| PELT `pen`                | 3 × log(n)                                          | Conservative; reduces false positives          |
| Slope significance        | `                                                   | slope                                          | > 2 × SE` | Equivalent to 95% CI excluding zero |
| Directional consistency   | ≥ 60% observations moving same direction in segment | Pragmatic noise filter                         |
| Min series length for STL | 24 months                                           | Needs at least 2 full seasonal cycles          |

---

## Sources

1. **ruptures documentation** — PELT, cost functions (l2, rbf), usage:  
   https://centre-borelli.github.io/ruptures-docs/user-guide/detection/pelt/  
   https://centre-borelli.github.io/ruptures-docs/user-guide/costs/costrbf/  
   https://centre-borelli.github.io/ruptures-docs/user-guide/costs/costl2/

2. **Forecasting: Principles and Practice (FPP3)** — Moving averages, 2×12-MA, trend estimation:  
   https://otexts.com/fpp3/moving-averages.html

3. **statsmodels TSA documentation** — ExponentialSmoothing, STL, ETSModel, seasonal_decompose:  
   https://www.statsmodels.org/stable/tsa.html

4. **Wikipedia: CUSUM** — Method, threshold tuning, average run length:  
   https://en.wikipedia.org/wiki/CUSUM

5. **Wikipedia: Savitzky–Golay filter** — Polynomial smoothing, endpoint handling, comparison with other filters:  
   https://en.wikipedia.org/wiki/Savitzky%E2%80%93Golay_filter  
   Python implementation: `scipy.signal.savgol_filter`

6. **Killick et al. (2012)** — Original PELT paper: "Optimal detection of changepoints with a linear computational cost", _JASA_ 107(500).  
   Referenced in ruptures docs.

7. **Garreau & Arlot (2018)** — Kernel change-point detection (rbf cost theoretical basis):  
   _Electronic Journal of Statistics_, 12(2).
