# Research Plan: Multiscale Trend Detection For Noisy Time Series

## Main Research Question

What are best-practice architectures for identifying trend periods in noisy time series when trend granularity depends on analysis horizon, and is a multi-timescale approach (short/medium/long trend layers) preferable to a single canonical segmentation?

## Subtopics

1. Statistical signal-processing baselines for trend extraction

- Scope: smoothing/decomposition and change-point methods (for example LOESS/STL, HP filter, Kalman/state-space, CUSUM, offline change-point detection)
- Expected info: what each method assumes, how robust each is to noise/regime shifts, and whether each yields one segmentation or can support multiple horizons

2. Financial/economic analytics best practices for multi-horizon trend systems

- Scope: short/intermediate/long horizon frameworks in practice (for example moving average families, trend-strength indicators, regime labeling)
- Expected info: how production systems define horizons, avoid overfitting, and present conflicting signals across horizons

3. Machine learning and representation-learning approaches

- Scope: HMM/MSM regime models, Bayesian online change-point detection, hierarchical and multiresolution models, forecasting-model-derived trend states
- Expected info: accuracy/interpretability tradeoffs, data requirements, retraining concerns, and operational complexity

4. Product architecture patterns for multi-scale trend products

- Scope: storage model, API contract design, UX patterns for layered trends, validation/monitoring and governance
- Expected info: how to structure a robust system where one series can have concurrent short/medium/long trend labels without confusion

## Synthesis Plan

- Compare approaches on: interpretability, stability, responsiveness, computational cost, and operational complexity.
- Produce an options matrix with 3 practical architecture options:
  - Single canonical segmentation with improved algorithm
  - Explicit multi-horizon parallel trend layers
  - Hybrid (canonical macro-regime + optional micro-trend overlays)
- Provide recommendation criteria and a phased rollout path appropriate for our existing pipeline/API/UI stack.
