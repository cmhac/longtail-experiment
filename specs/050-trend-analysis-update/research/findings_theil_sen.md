# Theil-Sen Robust Slope Estimation Options for Python Production Pipelines

## Scope and method

- Web searches used: 4 (within requested 3-5).
- Focus: production-suitable Theil-Sen options for univariate time-series lookback trend evaluation, including API behavior, confidence interval support, computational tradeoffs, and rolling/as-of suitability.

## Options reviewed

### 1) SciPy `scipy.stats.theilslopes` (recommended default)

**What it is**
- Univariate Theil-Sen slope on `(x, y)` points; robust to outliers by using the median of all pairwise slopes.

**API behavior**
- Signature includes `alpha`, `method`, `axis`, `nan_policy`, `keepdims`.
- Returns `slope`, `intercept`, `low_slope`, `high_slope` in a result object.
- Intercept mode is explicit: `method='separate'` or `method='joint'`.

**Confidence interval support**
- Native slope CI via `alpha` (returns lower/upper slope bounds).
- No intercept CI.

**Performance/computational tradeoffs**
- Pairwise-slope median implies quadratic work in lookback length (`O(n^2)` pairs).
- Excellent for short/medium windows; can become costly on very large windows across many series/as-of points.

**Rolling/as-of suitability**
- Strong fit for per-lookback, per-as-of evaluation in a pipeline that already computes multiple discrete windows.
- `nan_policy='omit'` is useful for real-world missingness.
- Best when windows are bounded and cadence-gated (which this repo already does).

**Relevant quotes**
- "It computes the slope as the median of all slopes between paired values."
- "Confidence degree between 0 and 1... both 0.1 and 0.9 are interpreted as 'find the 90% confidence interval'."
- "A confidence interval for the intercept is not given..."

**Source URL**
- https://docs.scipy.org/doc/scipy/reference/generated/scipy.stats.theilslopes.html

---

### 2) scikit-learn `sklearn.linear_model.TheilSenRegressor` (multivariate/ML-style option)

**What it is**
- Robust multivariate regression estimator using subsampling + spatial median aggregation.

**API behavior**
- Estimator API (`fit`, `predict`) with controls: `n_subsamples`, `max_subpopulation`, `n_jobs`, `max_iter`, `tol`, `random_state`.
- Produces coefficients/intercept and diagnostics such as `breakdown_`, `n_subpopulation_`.

**Confidence interval support**
- No native confidence intervals for slope/coef in the estimator API.
- CI would require external bootstrapping or resampling logic.

**Performance/computational tradeoffs**
- Explicit combinatorial growth: "n_samples choose n_subsamples"; bounded via stochastic subsampling (`max_subpopulation`).
- More tunable for larger datasets than exact pairwise univariate Theil-Sen, but tuning affects robustness/efficiency tradeoff.

**Rolling/as-of suitability**
- Usually overkill for 1D time-index trend slope snapshots.
- Better when you truly need multivariate robust regression features/covariates.
- For rolling/as-of univariate trend catalogs, added estimator overhead and parameter management often outweigh benefits.

**Relevant quotes**
- "The algorithm calculates least square solutions on subsets with size n_subsamples..."
- "Since the number of least square solutions is 'n_samples choose n_subsamples', it can be extremely large and can therefore be limited with max_subpopulation."
- "A lower number leads to a higher breakdown point and a low efficiency while a high number leads to a low breakdown point and a high efficiency."

**Source URL**
- https://scikit-learn.org/stable/modules/generated/sklearn.linear_model.TheilSenRegressor.html

---

### 3) SciPy `scipy.stats.mstats.sen_seasonal_slopes` (seasonal Theil-Sen companion)

**What it is**
- Seasonal generalization of Sen slope for 2D season-structured arrays.

**API behavior**
- Input is 2D array where columns are seasons; returns per-season Theil-Sen slopes and a pooled seasonal Kendall slope.

**Confidence interval support**
- No CI outputs.

**Performance/computational tradeoffs**
- Computes within-season pairwise slopes; complexity grows with points-per-season and number of seasons.
- Good when regular season structure is explicit and available.

**Rolling/as-of suitability**
- Useful when lookbacks are evaluated on seasonally indexed matrices (e.g., monthly slots across years).
- Less convenient for irregular cadence or sparse/as-of slices without careful reshaping.

**Relevant quotes**
- "Computes seasonal Theil-Sen and Kendall slope estimators."
- "Each column of x contains measurements... within a season."
- "inter_slope... seasonal Kendall slope estimator"

**Source URL**
- https://docs.scipy.org/doc/scipy/reference/generated/scipy.stats.mstats.sen_seasonal_slopes.html

---

### 4) SciPy `scipy.stats.siegelslopes` (fallback robust slope, not Theil-Sen)

**What it is**
- Repeated-medians robust regression; often used when stronger outlier robustness is needed.

**API behavior**
- Returns slope/intercept, with intercept methods (`hierarchical` or `separate`).

**Confidence interval support**
- No CI output.

**Performance/computational tradeoffs**
- Documentation explicitly warns performance can be slow for large vectors.

**Rolling/as-of suitability**
- Good fallback for highly contaminated windows; slower and no CI.
- More of a robustness alternative than a direct Theil-Sen replacement for this feature scope.

**Relevant quotes**
- "...using repeated medians... robust to outliers with an asymptotic breakdown point of 50%."
- "The implementation computes n times the median of a vector of size n which can be slow for large vectors."

**Source URL**
- https://docs.scipy.org/doc/scipy/reference/generated/scipy.stats.siegelslopes.html

## Production recommendation for this trend-analysis pipeline

1. Use **SciPy `theilslopes` as primary estimator** for each applicable lookback and as-of point.
2. Persist `slope`, `intercept`, `low_slope`, `high_slope` (or derived confidence width) as evidence metadata where contract allows.
3. Use **seasonal companion path** with `sen_seasonal_slopes` only when cadence/shape is regular enough to form seasonal matrices.
4. Treat **scikit-learn TheilSenRegressor** as optional for multivariate feature-based trend models, not default univariate lookback scoring.
5. Use **SciPy `siegelslopes`** only as an outlier-heavy fallback when Theil-Sen behavior appears insufficient for a specific series family.

## Rolling/as-of implementation notes

- For lookback catalogs like `1,2,3,4,5,10,25,...`, total cost is dominated by larger windows because each lookback call is quadratic in window size.
- Keep strict applicability gating (`min_points`, cadence support, missingness thresholds) to avoid expensive low-value evaluations.
- Use deterministic `x` (`np.arange(window_len)`) for stable slope semantics across rolling/as-of runs.
- For very long windows at scale, use one or more of: reduced long-horizon frequency, downsampling for context-only windows, or asynchronous batch recomputation for deep-history snapshots.

## Search log (3-5 constraint)

1. SciPy theilslopes confidence interval and intercept method search.
2. scikit-learn TheilSenRegressor complexity/tuning search.
3. SciPy Siegel slopes robust fallback search.
