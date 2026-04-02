# Trend Detection Spike — Findings Report

**Date:** 2026-03-31
**Status:** Spike complete, ready for productionization spec
**Artifacts:**

- `research_trend_detection/spike_trend_detection.py` — v1 spike (single-horizon, real DB data)
- `research_trend_detection/spike_multi_horizon.py` — v2 spike (multi-horizon, synthetic data, 14/14 scenarios passing)
- `research_trend_detection/initial_research/` — web research on classical methods, smoothing/changepoint, and practical approaches

---

## 1. What We Did

### Phase 1: Research (web research, 3 parallel tracks)

Surveyed the landscape of trend detection for economic/financial time series:

- **Classical statistical methods**: Mann-Kendall (MK), OLS regression, Holt-Winters. MK was selected as the primary detection algorithm due to its non-parametric nature (no normality assumption), built-in handling of ties, and clean binary significance output.
- **Smoothing & change-point detection**: SMA, EWMA, PELT/CUSUM. These are better suited for signal extraction and structural break detection than for trend labeling. Useful as future enhancements but not the core.
- **Practical approaches from platforms (FRED, BLS, Bloomberg)**: Year-over-year percent change is the practical gold standard. Rolling windows, consecutive direction counts, and EWMA crossovers are common supplementary signals.

Key decision: **Mann-Kendall with Hamed-Rao autocorrelation correction** as the primary trend test, layered with magnitude classification gates for user-facing labels.

### Phase 2: Single-Horizon Spike (real data, 28 series)

Connected to the local PostgreSQL database (`longtail_local`) and tested trend detection on all 28 real series across 3 sources:

- **EIA**: 22 weekly fuel price series (USD)
- **FRED**: 2 series (FEDFUNDS monthly percent, GASREGW weekly USD)
- **NYFED**: 4 monthly college labor market series (percent)

Iterated through 4 versions of a single-horizon classifier using a 24-month lookback with MK + 4 quality gates.

### Phase 3: Multi-Horizon Spike (synthetic data, 14 scenarios)

Redesigned the approach to run MK across multiple calendar-anchored time windows per series cadence. Tested against 14 synthetic scenarios covering every real-world pattern.

---

## 2. What We Found

### Single-horizon limitations (v1 spike)

The initial approach ran MK on a single 24-month window and used `pct_change_window(values, 12)` for magnitude. This had three fundamental problems:

1. **Observation-count windows are cadence-dependent.** "12 observations back" means 12 weeks for weekly data but 12 months for monthly data. For daily data, it would mean 12 days — useless for trend detection. The naming was misleading (originally called `pct_12m`).

2. **Percentage-point vs relative-change confusion.** For rate-type series (FEDFUNDS, unemployment), gate4 was comparing relative % change against pp thresholds. FEDFUNDS dropped 0.69pp (from ~5.33% to ~4.48%), which is a -15.94% relative change. Using relative change against a 1.5pp threshold classified this as "strong" when it should be "mild."

3. **A single long window can't detect emerging trends.** A 24-month MK window will only flag trends that have persisted for most of that period. A rate that started dropping 3 months ago won't reach significance in a 24-month window until weeks or months later.

### The U-shape problem (EIA gasoline data)

All 22 EIA fuel price series exhibited a U-shaped pattern over the 24-month window: prices dipped in the first year then recovered in the second. MK said "decreasing" (the dip dominated the pairwise comparisons), but the 12-observation lookback showed +40% (comparing to 12 weeks ago, during the bottom of the dip). Every gate combination either mislabeled them as trending or required overly strict momentum checks that killed legitimate trends.

**Root cause:** A single-horizon approach fundamentally cannot distinguish "currently declining" from "was declining but now recovering."

**Solution:** The multi-horizon approach resolves this by running MK on multiple overlapping windows. The U-shape check (OLS slope comparison on first vs second half of the data) catches the remaining cases.

### The monthly data problem

Monthly series have only 12–24 observations in a 24-month window. This means:

- Very few observations per sub-window (6-month monthly window = 6 observations)
- Consecutive-direction momentum checks are unreliable (a single monthly tick can break a 3-observation streak)
- Hard momentum gates rejected series like FEDFUNDS (τ=-0.841, very strong signal) because one month ticked the wrong way

**Solution:** The multi-horizon approach relaxes momentum requirements for low-frequency data and uses the "12m not significant" heuristic to detect emerging trends in monthly series.

### Seasonal data false positives

Weekly fuel price data has strong seasonal patterns (summer driving season → higher prices). A 13-week window during the seasonal upswing shows a highly significant MK trend, even though the full year is flat. Without seasonal detection, this produces false "emerging_uptrend" labels.

**Solution:** When significant windows have conflicting directions (e.g., 13w=up, 12m=down), check the longest window's net % change. If it's near zero (<2%), the conflicting signals are seasonal oscillation, not a real trend.

---

## 3. What Worked: The Multi-Horizon Classifier

### Architecture

Run Mann-Kendall on **multiple calendar-anchored windows** per cadence, then combine results:

| Cadence | Windows                                         |
| ------- | ----------------------------------------------- |
| Daily   | 2 weeks, 1 month, 3 months, 6 months, 12 months |
| Weekly  | 4 weeks, 13 weeks, 6 months, 12 months          |
| Monthly | 6 months, 12 months                             |

### Classification Logic (in priority order)

1. **No significant windows → `stable`**: No window passes MK (p < 0.05, |τ| ≥ 0.15)

2. **Conflicting directions among significant windows:**
   - Check for seasonal oscillation first (net change < 2% over longest window → `stable`)
   - If shortest significant window has |τ| ≥ 0.4, it's a **reversal** → `emerging_[up/down]trend`
   - If shortest significant window has weak τ, it's noise → `stable`

3. **U-shape detection:** OLS slope on first vs second half of full data; if slopes contradict → `stable`

4. **Stale move detection:** Short windows exist + all non-significant + their τ direction disagrees with long → `stable`

5. **Emerging vs sustained:**
   - If 12m window is NOT significant but shorter windows are → `emerging_[up/down]trend`
   - If short-window τ is much larger than long-window τ (ratio > 1.8 and |τ*short| > 0.4) → `emerging*[up/down]trend`

6. **Sustained magnitude (from longest significant window):**
   - Rate series (percent type): |pp change| > 1.5 → `strong`, > 0.3 → `mild`, else `stable`
   - Price/number series: |% change| > 10 → `strong`, > 3 → `mild`, else `stable`

### Labels

| Label                        | Meaning                                                         |
| ---------------------------- | --------------------------------------------------------------- |
| `strong_sustained_uptrend`   | Significant in both short and long windows, large magnitude     |
| `mild_sustained_uptrend`     | Significant across windows, moderate magnitude                  |
| `emerging_uptrend`           | Significant in short windows only, trend is recent/accelerating |
| `stable`                     | No consistent directional signal                                |
| `emerging_downtrend`         | Significant in short windows only, recent decline               |
| `mild_sustained_downtrend`   | Significant across windows, moderate decline                    |
| `strong_sustained_downtrend` | Significant in both short and long windows, large decline       |

### Configuration

| Parameter                  | Value                  | Rationale                                                                          |
| -------------------------- | ---------------------- | ---------------------------------------------------------------------------------- |
| MK variant                 | Hamed-Rao modification | Corrects for autocorrelation in economic time series                               |
| MK α                       | 0.05                   | Standard statistical significance                                                  |
| MK τ_min                   | 0.15                   | Minimum effect size to filter near-zero correlations                               |
| MK min obs                 | 6                      | Allows 6-month window on monthly data (low power but sufficient for strong trends) |
| PP "mild" threshold        | 0.3 pp                 | Meaningful rate change for monetary policy / labor metrics                         |
| PP "strong" threshold      | 1.5 pp                 | Large rate change (e.g., full Fed rate-cut cycle)                                  |
| Pct "mild" threshold       | 3%                     | Noticeable price change                                                            |
| Pct "strong" threshold     | 10%                    | Significant price movement                                                         |
| Seasonal net-pct threshold | 2%                     | Net change below this = oscillation, not trend                                     |
| Reversal τ_min             | 0.4                    | Short window must have this τ to call a reversal                                   |

### Validated Scenarios (14/14 passing)

| #   | Scenario                  | Cadence     | Label                      | Detection Mechanism             |
| --- | ------------------------- | ----------- | -------------------------- | ------------------------------- |
| 1   | Steady climb 18mo         | daily/USD   | strong_sustained_uptrend   | 3m–12m all SIG, τ consistent    |
| 2   | Slow climb 2yr            | weekly/USD  | mild_sustained_uptrend     | 12m SIG, short τ agrees         |
| 3   | Rate cut 3pp/24mo         | monthly/pct | strong_sustained_downtrend | 6m+12m SIG, pp=-1.58            |
| 4   | Rate decline 0.8pp/24mo   | monthly/pct | mild_sustained_downtrend   | 6m+12m SIG, pp=-0.43            |
| 5   | Flat → +8% in 6 weeks     | daily/USD   | emerging_uptrend           | τ ratio 3.17 (2w >> 12m)        |
| 6   | Flat → -10% in 8 weeks    | weekly/USD  | emerging_downtrend         | 12m not significant             |
| 7   | Flat → +0.8pp in 6 months | monthly/pct | emerging_uptrend           | 12m not significant             |
| 8   | 20% spike, flat 8 months  | daily/USD   | stable                     | Conflicting dirs, weak recent τ |
| 9   | V-shape drop-then-recover | weekly/USD  | stable                     | U-shape OLS half-check          |
| 10  | Random walk rate          | monthly/pct | stable                     | No significant windows          |
| 11  | Random walk price         | daily/USD   | stable                     | No significant windows          |
| 12  | Seasonal ±$0.30/yr        | weekly/USD  | stable                     | Near-zero net Δ over 12m        |
| 13  | 18mo rise → 2mo reversal  | weekly/USD  | emerging_downtrend         | Short=down, long=up reversal    |
| 14  | Flat → +10% in 2 weeks    | daily/USD   | emerging_uptrend           | 12m not significant, τ=1.0@2w   |

---

## 4. Dependencies

| Package         | Version    | Purpose                              |
| --------------- | ---------- | ------------------------------------ |
| `pymannkendall` | (latest)   | Hamed-Rao modified Mann-Kendall test |
| `numpy`         | (existing) | Array math, OLS slopes               |
| `scipy`         | (existing) | Used by pymannkendall internally     |

No new database tables, API endpoints, or infrastructure required for the spike.

---

## 5. Open Questions for Productionization

### Where does trend computation run?

- **Option A: Batch pipeline job** — compute trends after each ingestion run, store in a `trend_scores` table. Simple, decoupled from API. Trend freshness depends on ingestion cadence.
- **Option B: On-demand in backend** — compute when a dataset detail page is requested. Always fresh, but adds latency and CPU cost per request.
- **Recommendation:** Option A (batch) for the main labels, with cacheable API responses.

### New database table

A `trend_scores` table storing pre-computed results:

- `series_id` (FK → data_series)
- `computed_at` (timestamp)
- `trend_label` (enum: the 7 labels)
- `classification_reason` (text, for debugging)
- `window_results` (JSONB, per-window MK details for transparency)
- `magnitude_pct` / `magnitude_pp` (numeric, for sorting/filtering)

### Cadence inference

In the spike, cadence was inferred from the data frequency. This approach should generalize well and is more robust than relying on source-based assumptions. The cadence inference logic should be implemented as a reusable utility function.

### Threshold calibration

All magnitude thresholds (0.3pp/1.5pp mild/strong for rates, 3%/10% for prices) are reasonable defaults for current data (Fed rates, gas prices, unemployment). As more data sources arrive with different scales, consider:

- Per-source-profile threshold overrides
- Percentile-based adaptive thresholds (e.g., "strong" = top 10% of historical changes for this series)

### What the frontend needs

- A "trending" badge/chip on dataset list items and detail pages
- Optional: a "trending" sort/filter on the dataset catalog
- The classification_reason and window_results should be available for a "why is this trending?" affordance

### Seasonality

The prototype now includes explicit seasonality inference and decomposition:

- Infer seasonality per series cadence (daily=252, weekly=52, monthly=12) using STL strength-of-seasonality (Fs) plus a detrended seasonal-lag autocorrelation gate.
- Apply STL deseasonalization when seasonality is confirmed.
- Preserve emerging breakout sensitivity with a seasonal blend rule: if deseasonalized classification is stable due tiny magnitude but raw windows show a clear emerging trend, keep the raw emerging label.

This resolved false seasonal flags on non-seasonal U-shapes/reversals while still capturing meaningful seasonal trends (including seasonal + emerging behavior) in the synthetic suite.

---

## 6. Lessons Learned

1. **Observation-count windows are a trap.** Always use calendar-anchored windows. "12 observations back" means completely different things for daily vs monthly data.

2. **Relative % change vs absolute pp change is a critical distinction.** For rate-type series (interest rates, unemployment, etc.), a 0.5pp move from 5.0% to 4.5% is a 10% relative change but a modest policy shift. Always use pp for rate-type magnitude classification.

3. **Single-horizon MK cannot detect emerging trends.** By definition, an emerging trend has not yet persisted long enough to dominate a long lookback window. Multi-horizon MK solves this by detecting significance at the shortest available window.

4. **U-shapes and seasonal cycles are the main sources of false positives.** Both produce statistically significant MK results because MK sees the dominant half of the cycle. The multi-horizon approach catches these through conflicting-window directions and OLS half-slope comparison.

5. **Monthly data is inherently hard.** With only 12 observations in a year, statistical power is low. The MK test needs strong effect sizes (high |τ|) to reach significance. Increasing the minimum observation threshold (e.g., requiring 8+ obs) would exclude 6-month monthly windows, which are the only way to detect emerging trends in monthly data. The current MK_MIN_OBS=6 is a deliberate tradeoff.

6. **Noise in the test harness matters.** Synthetic data with realistic noise levels (0.3–1.5% of mean) is essential for validating that thresholds work. Tests with clean data pass trivially but miss real-world edge cases.
