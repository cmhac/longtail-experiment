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

  it("preserves canonical descriptor and lookback snapshots from dataset detail payload", async () => {
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
          descriptor_state: "available",
          trend_label: "strong_sustained_uptrend",
          direction: "up",
          strength: "strong",
          selected_lookback_points: 100,
          observed_on: "2026-03-01",
          reason_code: null,
        },
        lookback_trend_snapshots: [
          {
            lookback_points: 100,
            applicability_state: "applicable",
            outcome_state: "significant_trend",
            trend_label: "strong_sustained_uptrend",
            direction: "up",
            strength: "strong",
            reason_code: null,
          },
        ],
        observation_sort: "observed_on_asc",
      }),
    );

    const response = await fetchDatasetDetail("UNRATE");

    expect(response.canonical_trend_descriptor?.descriptor_state).toBe("available");
    expect(response.canonical_trend_descriptor?.selected_lookback_points).toBe(100);
    expect(response.lookback_trend_snapshots).toHaveLength(1);
  });

  it("maps missing lookback snapshots to an empty array", async () => {
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
          descriptor_state: "unavailable",
          trend_label: null,
          direction: null,
          strength: null,
          selected_lookback_points: null,
          observed_on: null,
          reason_code: "no_applicable_lookbacks",
        },
        observation_sort: "observed_on_asc",
      }),
    );

    const response = await fetchDatasetDetail("UNRATE");

    expect(response.lookback_trend_snapshots).toEqual([]);
    expect(response.canonical_trend_descriptor?.descriptor_state).toBe("unavailable");
  });
});
