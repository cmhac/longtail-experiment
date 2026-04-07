import type {
  CanonicalTrendDescriptor,
  LookbackTrendSnapshot,
} from "../../src/lib/api/discovery-types";

export const canonicalUpV2Fixture: CanonicalTrendDescriptor = {
  descriptor_state: "available",
  trend_label: "moderate_uptrend",
  direction: "up",
  strength: null,
  selected_lookback_points: 25,
  observed_on: "2026-03-01",
  reason_code: null,
};

export const canonicalDownV2Fixture: CanonicalTrendDescriptor = {
  descriptor_state: "available",
  trend_label: "moderate_downtrend",
  direction: "down",
  strength: null,
  selected_lookback_points: 25,
  observed_on: "2026-03-01",
  reason_code: null,
};

export const canonicalUnavailableV2Fixture: CanonicalTrendDescriptor = {
  descriptor_state: "unavailable",
  trend_label: null,
  direction: null,
  strength: null,
  selected_lookback_points: null,
  observed_on: "2026-03-01",
  reason_code: "cadence_irregular_rejected",
};

export const lookbackSnapshotsV2Fixture: LookbackTrendSnapshot[] = [
  {
    lookback_points: 25,
    applicability_state: "applicable",
    outcome_state: "significant_trend",
    trend_label: "moderate_uptrend",
    direction: "up",
    strength: null,
    reason_code: null,
  },
  {
    lookback_points: 100,
    applicability_state: "inapplicable",
    outcome_state: null,
    trend_label: null,
    direction: null,
    strength: null,
    reason_code: "insufficient_history",
  },
];
