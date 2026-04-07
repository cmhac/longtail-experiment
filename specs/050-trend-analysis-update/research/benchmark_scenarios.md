# Benchmark Scenarios: Spec 050 Trend Analysis Upgrade

## Purpose

Define deterministic scenario sets used to validate success criteria for the v2 trend descriptor rollout.

## Scenario Matrix

| Scenario ID | Series Shape | Cadence | Expected Canonical Behavior |
|-------------|--------------|---------|------------------------------|
| S1 | Smooth positive slope | monthly | `up` with stable confidence |
| S2 | Smooth negative slope | monthly | `down` with stable confidence |
| S3 | Near-flat noisy | monthly | `flat` or low-confidence non-directional |
| S4 | Short noisy reversal | weekly | fewer direction flips than v1 baseline |
| S5 | Regular sub-daily with seasonal cycle | sub-daily | consistent direction with MSTL path |
| S6 | Irregular gap series | mixed | unavailable canonical with cadence rejection reason |

## Replay Inputs

- Use canonical datasets already available in local bootstrap fixtures.
- Include at least one representative series per scenario with >= 120 observations where possible.
- For irregular-cadence validation, include explicit missing interval blocks to trigger rejection precedence.

## Comparison Outputs

- Canonical descriptor direction and confidence by as-of date.
- Count of direction flips over identical replay windows (v1 vs v2).
- Number of emitted reversal notifications (`up <-> down`) over replay window.
- Contract conformance snapshots for list/search/recent/detail/as-of endpoints.

## Acceptance Notes

- SC-001: short-horizon direction-flip churn reduced by >= 30%.
- SC-004: false-positive reversal notifications reduced by >= 25%.
- SC-008/SC-009: endpoint contracts respect canonical-only vs evidence visibility boundaries.
- SC-010: UX consistency preserved for chip-first rendering and detail evidence expansion.
