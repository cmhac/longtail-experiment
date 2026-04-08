import type {
  CanonicalTrendDescriptor,
  LookbackTrendEvidence,
} from "../../src/lib/api/discovery-types";

export const canonicalUpV2Fixture: CanonicalTrendDescriptor = {
  descriptor_version: "v2",
  descriptor_state: "available",
  trend_label: "moderate_uptrend",
  direction: "up",
  confidence_score: 0.64,
  dominant_measure_family: "theil_sen",
  selected_lookback_points: 25,
  observed_on: "2026-03-01",
  reason_code: null,
};

export const canonicalDownV2Fixture: CanonicalTrendDescriptor = {
  descriptor_version: "v2",
  descriptor_state: "available",
  trend_label: "moderate_downtrend",
  direction: "down",
  confidence_score: 0.61,
  dominant_measure_family: "theil_sen",
  selected_lookback_points: 25,
  observed_on: "2026-03-01",
  reason_code: null,
};

export const canonicalUnavailableV2Fixture: CanonicalTrendDescriptor = {
  descriptor_version: "v2",
  descriptor_state: "unavailable",
  trend_label: null,
  direction: null,
  confidence_score: null,
  dominant_measure_family: "none",
  selected_lookback_points: null,
  observed_on: "2026-03-01",
  reason_code: "cadence_irregular_rejected",
};

export const lookbackEvidenceV2Fixture: LookbackTrendEvidence[] = [
  {
    lookback_points: 25,
    applicability_state: "applicable",
    descriptor_state: "available",
    trend_label: "moderate_uptrend",
    direction: "up",
    confidence_score: 0.64,
    dominant_measure_family: "theil_sen",
    theil_sen_slope: 0.24,
    theil_sen_low_slope: 0.18,
    theil_sen_high_slope: 0.31,
    kendall_tau: 0.42,
    kendall_p_value: 0.01,
    preprocessing: {
      smoothing_method: "none",
      smoothing_parameters: {},
      seasonal_adjustment_method: "none",
      seasonal_periods: [],
      seasonal_reliability_state: "not_applicable",
      preprocess_version: "v2",
    },
    ols_diagnostics: {
      slope: 0.2,
      intercept: 1.0,
      r_squared: 0.58,
      p_value: 0.02,
    },
    reason_code: null,
  },
  {
    lookback_points: 100,
    applicability_state: "inapplicable",
    descriptor_state: "unavailable",
    trend_label: null,
    direction: null,
    confidence_score: null,
    dominant_measure_family: "none",
    theil_sen_slope: null,
    theil_sen_low_slope: null,
    theil_sen_high_slope: null,
    kendall_tau: null,
    kendall_p_value: null,
    preprocessing: {
      smoothing_method: "none",
      smoothing_parameters: {},
      seasonal_adjustment_method: "none",
      seasonal_periods: [],
      seasonal_reliability_state: "not_applicable",
      preprocess_version: "v2",
    },
    ols_diagnostics: {
      slope: null,
      intercept: null,
      r_squared: null,
      p_value: null,
    },
    reason_code: "insufficient_history",
  },
];
