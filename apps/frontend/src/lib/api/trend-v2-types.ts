export interface TrendV2OlsDiagnostics {
  slope: number | null;
  intercept: number | null;
  r_squared: number | null;
  p_value: number | null;
}

export interface TrendV2Preprocessing {
  smoothing_method: "ewma" | "none";
  smoothing_parameters: Record<string, unknown>;
  seasonal_adjustment_method: "stl" | "mstl" | "none";
  seasonal_periods: number[];
  seasonal_reliability_state: "reliable" | "fallback_non_adjusted" | "not_applicable";
  preprocess_version: string;
}

export interface TrendV2CanonicalDescriptor {
  descriptor_version: "v2";
  descriptor_state: "available" | "unavailable";
  trend_label: string | null;
  direction: "up" | "down" | "flat" | null;
  confidence_score: number | null;
  selected_lookback_points: 1 | 2 | 3 | 4 | 5 | 10 | 25 | 50 | 100 | 250 | 500 | 1000 | null;
  observed_on: string | null;
  dominant_measure_family: "theil_sen" | "mixed" | "none";
  reason_code: string | null;
}

export interface TrendV2LookbackEvidence {
  lookback_points: 1 | 2 | 3 | 4 | 5 | 10 | 25 | 50 | 100 | 250 | 500 | 1000;
  applicability_state: "applicable" | "inapplicable";
  descriptor_state: "available" | "unavailable";
  trend_label: string | null;
  direction: "up" | "down" | "flat" | null;
  confidence_score: number | null;
  dominant_measure_family: "theil_sen" | "mixed" | "none" | null;
  theil_sen_slope: number | null;
  theil_sen_low_slope: number | null;
  theil_sen_high_slope: number | null;
  kendall_tau: number | null;
  kendall_p_value: number | null;
  preprocessing: TrendV2Preprocessing;
  ols_diagnostics: TrendV2OlsDiagnostics;
  reason_code: string | null;
}
