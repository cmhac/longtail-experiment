# Findings: Statistical and Signal-Processing Methods

## Scope

Trend extraction and segmentation methods that can support noisy economic time series and potentially multiple horizons.

## Key Findings

- STL/LOESS decomposition is a strong baseline for noisy, seasonal data because it separates trend/seasonality/remainder and supports robust fitting options.
- Change-point detection is the most direct way to segment regimes. Offline methods are typically more accurate for historical segmentation; online methods trade accuracy for low-latency detection.
- CUSUM-type methods are useful for small sustained shifts, with explicit trade-offs among false alarms, misses, and delay.
- Kalman/state-space methods are useful when you want recursively updated latent trend estimates rather than fixed segmentation boundaries.
- HP filter remains common in economics but has known limitations depending on use case and can over-smooth or introduce artifacts in some settings.

## Practical Implications For Your Problem

- A single global trend definition will always underfit some horizons and overfit others.
- Best practice is often to separate objectives:
  - segmentation objective (change points)
  - local trend estimation objective (state-space/smoothing)
- Multi-horizon trend products generally use multiple detectors or windows, then expose each horizon explicitly instead of collapsing everything into one canonical periodization.

## Method Strengths and Limits

- STL/LOESS:
  - Strengths: robust decomposition, intuitive diagnostics.
  - Limits: not itself a regime boundary detector; usually paired with thresholding/change-point logic.
- Offline change-point detection:
  - Strengths: cleaner boundaries for historical data and backfills.
  - Limits: not streaming-first.
- Online change detection:
  - Strengths: operational for fresh data.
  - Limits: detection delay vs false positives is unavoidable.
- Kalman/state-space:
  - Strengths: smooth latent trend for noisy updates.
  - Limits: model specification and tuning complexity.
- HP filter:
  - Strengths: familiar macro workflow tool.
  - Limits: endpoint behavior and interpretation caveats.

## Sources

- Forecasting: Principles and Practice (FPP3): https://otexts.com/fpp3/
- Change detection overview (online vs offline framing): https://en.wikipedia.org/wiki/Change_detection
- Bayesian ensemble change-point/trend/seasonality example referenced in change-detection literature: https://go.osu.edu/beast2019
- CUSUM origins (Page): https://doi.org/10.1093/biomet/44.1-2.248
- Basseville & Nikiforov (classic reference): http://www.irisa.fr/sisthem/kniga/
