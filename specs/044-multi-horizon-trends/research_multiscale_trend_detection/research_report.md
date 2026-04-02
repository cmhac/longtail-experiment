# Research Report: Architectural Options for Multi-Timescale Trend Detection

## Question

Is single canonical trend segmentation fundamentally mismatched to noisy time series where users need different levels of detail, and should we move to parallel multi-horizon trend layers?

## Short Answer

Yes, your framing is correct. In practice, trend periods are horizon-dependent. A single segmentation can be made better, but it will usually remain a compromise that is too broad for some users and too twitchy for others.

## Why This Happens

- Trend detection has unavoidable tradeoffs between responsiveness and stability.
- Change detection has unavoidable tradeoffs between false alarms, misses, and detection delay.
- Different use cases legitimately require different smoothing windows and change thresholds.

## Option Set

### Option A: Improve Single Canonical Segmentation

- Approach:
  - Keep one trend layer.
  - Improve detector quality (for example stronger change-point logic, better noise handling).
- Pros:
  - Lowest complexity in storage/API/UI.
  - Easiest to explain.
- Cons:
  - Intrinsically compromises across user intents.
  - You will keep seeing “too broad” vs “too noisy” complaints from different users.
- Best for:
  - Simpler product goals where one narrative is acceptable.

### Option B: Parallel Multi-Horizon Layers (Recommended for your concern)

- Approach:
  - Run independent detectors for explicit horizons (for example 2w, 1m, 3m, 1y, 3y).
  - Persist and serve each horizon separately.
- Pros:
  - Matches real-world user intent and avoids forcing one answer.
  - Lets UI expose short/medium/long perspectives clearly.
- Cons:
  - More operational complexity, governance, and UX design needed.
- Best for:
  - Analytical products where users care about tactical + strategic context.

### Option C: Hybrid (Macro canonical + Micro overlays)

- Approach:
  - Keep one long-horizon canonical regime layer.
  - Add optional shorter-horizon overlays for detail.
- Pros:
  - Balanced complexity.
  - Gives stable headline plus detail on demand.
- Cons:
  - Needs careful conflict messaging between layers.
- Best for:
  - Teams wanting incremental migration from Option A toward Option B.

## Suggested Horizon Design Principles

- Keep horizon taxonomy explicit and small at first (for example 1m, 6m, 3y).
- Define deterministic conflict rules:
  - aligned -> high confidence
  - mixed -> medium confidence
  - contradictory -> mixed-signal state
- Version each horizon detector independently.
- Measure quality per horizon, not globally.

## Recommended First Iteration

- Start with Option C (hybrid), then graduate to Option B if adoption supports it:
  1. Add one macro horizon (for stable long periods) and one tactical horizon (for recent shifts).
  2. Keep current UI default on macro; add horizon switch for tactical.
  3. Track user interactions and disagreement rates.
  4. Expand horizon set only after quality and UX are stable.

## Key Sources

- Forecasting: Principles and Practice (decomposition and trend/seasonality concepts): https://otexts.com/fpp3/
- Change detection framing and tradeoffs: https://en.wikipedia.org/wiki/Change_detection
- Bayesian Online Changepoint Detection (online probabilistic run-length): https://arxiv.org/abs/0710.3742
- Hidden Markov Models (state-based regime modeling): https://en.wikipedia.org/wiki/Hidden_Markov_model
- Distributed architecture patterns (versioning/idempotency thinking): https://martinfowler.com/articles/patterns-of-distributed-systems/
