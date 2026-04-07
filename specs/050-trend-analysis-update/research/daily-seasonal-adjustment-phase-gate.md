# Daily Seasonal-Adjustment Phase Gate: Spec 050

## Purpose

Define explicit entry criteria for enabling daily seasonal adjustment in a
future phase beyond the current Spec 050 scope.

## Current Phase Position

- Daily cadence remains eligible for non-seasonally-adjusted scoring.
- Full daily seasonal adjustment is deferred.

## Gate Criteria (Must All Pass)

1. Canonical divergence threshold:
   - Daily replay canonical-direction divergence <= 5% versus
     non-seasonally-adjusted baseline on approved benchmark sets.
2. Notification/event stability threshold:
   - False-positive reversal-event increase <= 10% on incremental simulations.
3. Contract compatibility threshold:
   - No endpoint contract incompatibilities across discovery payload validation.

## Benchmark Inputs

- Use scenario matrix in `specs/050-trend-analysis-update/research/benchmark_scenarios.md`.
- Include representative daily series with regular and mildly irregular histories.

## Required Validation Outputs

- Replay divergence report with per-series and aggregate percentages.
- Event delta report comparing baseline vs candidate seasonal-adjusted path.
- Contract parity report across search/recent/detail/as-of surfaces.

## Approval

- Gate is considered open only when all thresholds pass in CI and are reviewed
  by feature owners for backend, pipeline, and frontend contracts.
