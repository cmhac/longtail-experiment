import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";

import { fetchDatasetDetail } from "../src/lib/api/discovery-client";

const originalEnv = process.env.DISCOVERY_API_BASE_URL;

const mockJsonResponse = (payload: unknown, status = 200): Response => {
  return {
    ok: status >= 200 && status < 300,
    status,
    json: async () => payload,
  } as Response;
};

describe("discovery client canonical trend mapping", () => {
  beforeEach(() => {
    process.env.DISCOVERY_API_BASE_URL = "http://localhost:8080";
    vi.restoreAllMocks();
  });

  afterEach(() => {
    process.env.DISCOVERY_API_BASE_URL = originalEnv;
  });

  it("preserves canonical descriptor and lookback evidence from dataset detail payload", async () => {
    vi.spyOn(globalThis, "fetch").mockResolvedValue(
      mockJsonResponse({
        dataset_id: "UNRATE",
        source: { id: "fred", name: "FRED" },
        title: "Unemployment Rate",
        description: null,
        geographic_scope: null,
        topic_tags: [],
        metadata: {},
        observations: [],
        canonical_trend_descriptor: {
          descriptor_version: "v2",
          descriptor_state: "available",
          trend_label: "strong_sustained_uptrend",
          direction: "up",
          confidence_score: 0.88,
          dominant_measure_family: "theil_sen",
          selected_lookback_points: 100,
          observed_on: "2026-03-01",
          reason_code: null,
        },
        lookback_trend_evidence: [
          {
            lookback_points: 100,
            applicability_state: "applicable",
            descriptor_state: "available",
            trend_label: "strong_sustained_uptrend",
            direction: "up",
            confidence_score: 0.88,
            dominant_measure_family: "theil_sen",
            theil_sen_slope: 1.2,
            theil_sen_low_slope: 1.0,
            theil_sen_high_slope: 1.4,
            kendall_tau: 0.79,
            kendall_p_value: 0.01,
            preprocessing: {
              smoothing_method: "ewma",
              smoothing_parameters: { halflife: 3 },
              seasonal_adjustment_method: "none",
              seasonal_periods: [],
              seasonal_reliability_state: "not_applicable",
              preprocess_version: "v2",
            },
            ols_diagnostics: {
              slope: 1.1,
              intercept: 99.2,
              r_squared: 0.75,
              p_value: 0.02,
            },
            reason_code: null,
          },
        ],
        observation_sort: "observed_on_asc",
      }),
    );

    const response = await fetchDatasetDetail("UNRATE");

    expect(response.canonical_trend_descriptor?.descriptor_state).toBe("available");
    expect(response.canonical_trend_descriptor?.confidence_score).toBe(0.88);
    expect(response.canonical_trend_descriptor?.selected_lookback_points).toBe(100);
    expect(response.lookback_trend_evidence).toHaveLength(1);
  });

  it("maps missing lookback evidence to an empty array", async () => {
    vi.spyOn(globalThis, "fetch").mockResolvedValue(
      mockJsonResponse({
        dataset_id: "UNRATE",
        source: { id: "fred", name: "FRED" },
        title: "Unemployment Rate",
        description: null,
        geographic_scope: null,
        topic_tags: [],
        metadata: {},
        observations: [],
        canonical_trend_descriptor: {
          descriptor_version: "v2",
          descriptor_state: "unavailable",
          trend_label: null,
          direction: null,
          confidence_score: null,
          dominant_measure_family: "none",
          selected_lookback_points: null,
          observed_on: null,
          reason_code: "no_applicable_lookbacks",
        },
        observation_sort: "observed_on_asc",
      }),
    );

    const response = await fetchDatasetDetail("UNRATE");

    expect(response.lookback_trend_evidence).toEqual([]);
    expect(response.canonical_trend_descriptor?.descriptor_state).toBe("unavailable");
  });
});
