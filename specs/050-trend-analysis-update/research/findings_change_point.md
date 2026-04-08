# Change-Point / Regime-Shift Detection for Trend-Pipeline Metadata

## Scope and intent

This research focuses on practical Python options for detecting structural shifts in time series that can be attached as **additive metadata** (tie-break/context), not as primary trend classification logic.

## Shortlist of practical libraries

### 1) `ruptures` (offline segmentation)

**Why it is practical**
- Mature, focused package for offline change-point segmentation.
- Modular: multiple search methods and cost models (good fit for experimentation per data family).

**Key facts**
- Supports exact/approximate methods and multiple parametric/non-parametric models.
- PELT implementation includes a documented average-complexity claim under assumptions.
- Offers tunable runtime controls (`min_size`, `jump`) to reduce compute.

**Runtime/complexity concerns**
- From docs: average complexity for PELT under conditions is \(\mathcal{O}(CKn)\), where:
  - `C` = cost-function evaluation complexity,
  - `K` = number of detected change points,
  - `n` = sample count.
- Cost model materially changes speed; docs explicitly note piecewise constant (`model="l2"`) is faster than linear/AR costs.

**Output usable for metadata scores**
- Breakpoint indices (`predict(...)`) and segment boundaries.
- Derivable metadata examples:
  - `cp_count_recent_window`
  - `distance_since_last_cp`
  - `segment_stability` (segment length / window length)
  - `cp_density` (cp count per N observations)

**Relevant quotes**
- "`ruptures` is a Python library for off-line change point detection."  
  Source: https://centre-borelli.github.io/ruptures-docs/
- "... under certain conditions on the change point repartition, the avarage computational complexity is of the order of \(\mathcal{O}(CKn)\)..."  
  Source: https://centre-borelli.github.io/ruptures-docs/user-guide/detection/pelt/
- "... piecewise constant models (`model=l2`) are significantly faster than linear or autoregressive models."  
  Source: https://centre-borelli.github.io/ruptures-docs/user-guide/detection/pelt/

---

### 2) `river` ADWIN (streaming drift/change detector)

**Why it is practical**
- Very practical for streaming/incremental pipelines.
- Explicitly designed for concept-drift detection with adaptive windows.

**Key facts**
- Maintains variable-length adaptive window and compares subwindows.
- Exposes `drift_detected`, adaptive `width`, and summary statistics.
- Tuning knobs (`clock`, `min_window_length`, `delta`) directly affect delay/false positives and throughput.

**Runtime/operational concerns**
- Faster checks with higher `clock`, but more detection delay.
- Lower `min_window_length` can reduce detection latency but increase false positives.
- Good candidate for low-latency metadata stream where exact offline breakpoint placement is less important.

**Output usable for metadata scores**
- Boolean drift events + window statistics (`n_detections`, `width`, `estimation`, `variance`).
- Derivable metadata examples:
  - `drift_event_recent` (0/1)
  - `drift_rate_recent` (detections per N points)
  - `window_contraction_ratio` (post-drift width / pre-drift width)
  - `instability_index` (weighted drift rate + variance change)

**Relevant quotes**
- "ADWIN (ADaptive WINdowing) is a popular drift detection method with mathematical guarantees."  
  Source: https://riverml.xyz/dev/api/drift/ADWIN/
- "How often ADWIN should check for changes... Higher values speed up processing, but may also lead to increased delay in change detection."  
  Source: https://riverml.xyz/dev/api/drift/ADWIN/
- "Lower values may decrease delay in change detection but may also lead to more false positives."  
  Source: https://riverml.xyz/dev/api/drift/ADWIN/

---

### 3) `statsmodels` Markov switching (`MarkovRegression`) for regime context

**Why it is practical**
- Useful when "regime" context (low/high state, switching variance, persistence) is more valuable than discrete breakpoints.
- Produces regime probabilities and expected duration signals suited to context metadata.

**Key facts**
- Dynamic regression with coefficients and optional variance switching across regimes.
- Fits via Hamilton filter / maximum likelihood.
- Supports time-varying transition probabilities (`exog_tvtp`) for richer contextual signals.

**Runtime/complexity concerns**
- Computationally heavier than threshold methods due to MLE optimization and latent-state filtering/smoothing.
- Estimation can be difficult; examples use multiple random search starts for stability.

**Output usable for metadata scores**
- Smoothed regime probabilities, transition matrix, expected regime durations.
- Derivable metadata examples:
  - `regime_prob_current_max`
  - `regime_entropy` (uncertainty across regimes)
  - `expected_duration_current_regime`
  - `transition_instability` (1 - self-transition probability)

**Relevant quotes**
- "...dynamic regression models with changes in regime."  
  Source: https://www.statsmodels.org/dev/examples/notebooks/generated/markov_regression.html
- "Fits the model by maximum likelihood via Hamilton filter."  
  Source: https://www.statsmodels.org/stable/generated/statsmodels.tsa.regime_switching.markov_regression.MarkovRegression.html
- "Because the models can be often difficult to estimate, for the 3-regime model we employ a search over starting parameters..."  
  Source: https://www.statsmodels.org/dev/examples/notebooks/generated/markov_regression.html

---

## Recommended patterns for additive metadata (tie-break/context only)

1. **Dual-path pattern (offline + online)**
   - Offline (`ruptures`) on completed windows for stable segmentation features.
   - Online (`river` ADWIN) for near-real-time instability context.

2. **Regime-overlay pattern**
   - Add `statsmodels` Markov regime probabilities as contextual tags (e.g., high-volatility regime) while preserving existing trend classifier as primary source of truth.

3. **Consensus metadata pattern**
   - Combine detector outputs into a bounded context score, e.g.:
   - `context_score = 0.4 * norm(cp_prob_latest) + 0.3 * norm(cp_density) + 0.3 * norm(transition_instability)`
   - Keep this score non-blocking and use only for ranking/tie-breaking/explanatory UI.

## Tradeoff summary

- **Best offline segmentation quality/control**: `ruptures` (especially when historical batch windows are available).
- **Best streaming practicality**: `river` ADWIN (simple, incremental, operationally lightweight).
- **Best latent regime context**: `statsmodels` Markov switching.

## Sources used

1. https://centre-borelli.github.io/ruptures-docs/
2. https://centre-borelli.github.io/ruptures-docs/user-guide/detection/pelt/
3. https://riverml.xyz/dev/api/drift/ADWIN/
4. https://www.statsmodels.org/dev/examples/notebooks/generated/markov_regression.html
5. https://www.statsmodels.org/stable/generated/statsmodels.tsa.regime_switching.markov_regression.MarkovRegression.html
