# Findings: Product and System Architecture for Multi-Timescale Trends

## Scope

API/data-model/storage/UX/governance patterns for delivering short/medium/long trend signals without forcing one canonical answer.

## Key Findings

- Treat trend outputs as versioned analytical artifacts, not mutable facts.
- Store per-horizon trend segments independently with model metadata (model/version/params/confidence/source window).
- Keep writes idempotent and append transition events for auditability.
- Expose horizon as a first-class API parameter and include conflict metadata in responses.

## Recommended Data Model Pattern

- `trend_records` keyed by:
  - series_id
  - horizon_key (e.g. 2w, 3m, 1y)
  - trend_label/direction/strength
  - start_period/end_period/is_ongoing
  - analysis_version + config_hash
- `trend_transition_events` for lifecycle provenance.
- Keep one ongoing record per (series_id, horizon_key), not one per series globally.

## API Contract Pattern

- `GET /datasets/{id}?trend_horizons=2w,3m,1y`
- Response includes:
  - `trend_spans_by_horizon`
  - horizon-local confidence
  - optional `horizon_conflict_summary`
- Do not collapse horizons server-side into one span set by default.

## UX Pattern

- Layered display:
  - default one selected horizon
  - easy horizon switcher
  - optional compare mode (stacked or small multiples)
- If horizons conflict, show an explicit mixed-signal state rather than silent averaging.

## Governance and Reliability

- Version every detector/horizon and make model/version visible in diagnostics.
- Run horizon-specific backtests and drift monitors.
- Track quality metrics per horizon: stability, flip-rate, latency-to-detect, and user-facing disagreement frequency.

## Sources

- Martin Fowler distributed-systems pattern catalog (versioned value, WAL, idempotency-aligned thinking): https://martinfowler.com/articles/patterns-of-distributed-systems/
- Time-series decomposition and representation context: https://en.wikipedia.org/wiki/Time_series
- Change-detection model selection framing: https://en.wikipedia.org/wiki/Change_detection
- SRE reliability measurement framing: https://sre.google/sre-book/service-level-objectives/
