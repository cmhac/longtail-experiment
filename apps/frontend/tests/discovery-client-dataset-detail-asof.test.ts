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

describe("discovery client dataset detail as-of descriptor mapping", () => {
  beforeEach(() => {
    process.env.DISCOVERY_API_BASE_URL = "http://localhost:8080";
    vi.restoreAllMocks();
  });

  afterEach(() => {
    process.env.DISCOVERY_API_BASE_URL = originalEnv;
  });

  it("normalizes missing observation as-of descriptor to explicit unavailable state", async () => {
    vi.spyOn(globalThis, "fetch").mockResolvedValue(
      mockJsonResponse({
        dataset_id: "UNRATE",
        source: { id: "fred", name: "FRED" },
        title: "Unemployment Rate",
        description: null,
        geographic_scope: null,
        topic_tags: [],
        metadata: {},
        observations: [
          {
            observed_on: "2026-03-01",
            value: 4.2,
            reported_at: "2026-03-02T00:00:00Z",
            attributes: {},
          },
        ],
        observation_sort: "observed_on_asc,reported_at_asc",
      }),
    );

    const detail = await fetchDatasetDetail("UNRATE");

    expect(detail.observations[0]?.as_of_trend_descriptor?.descriptor_state).toBe("unavailable");
    expect(detail.observations[0]?.as_of_trend_descriptor?.reason_code).toBe(
      "missing_observation_asof_descriptor",
    );
  });

  it("preserves valid observation as-of descriptor fields", async () => {
    vi.spyOn(globalThis, "fetch").mockResolvedValue(
      mockJsonResponse({
        dataset_id: "UNRATE",
        source: { id: "fred", name: "FRED" },
        title: "Unemployment Rate",
        description: null,
        geographic_scope: null,
        topic_tags: [],
        metadata: {},
        observations: [
          {
            observed_on: "2026-03-08",
            value: 4.1,
            reported_at: "2026-03-09T00:00:00Z",
            attributes: {},
            as_of_trend_descriptor: {
              descriptor_state: "available",
              trend_label: "moderate_sustained_downtrend",
              direction: "down",
              strength: "moderate",
              selected_lookback_points: 50,
              observed_on: "2026-03-08",
              reason_code: null,
            },
          },
        ],
        observation_sort: "observed_on_asc,reported_at_asc",
      }),
    );

    const detail = await fetchDatasetDetail("UNRATE");

    expect(detail.observations[0]?.as_of_trend_descriptor).toEqual({
      descriptor_version: "v2",
      descriptor_state: "available",
      trend_label: "moderate_sustained_downtrend",
      direction: "down",
      strength: "moderate",
      confidence_score: null,
      dominant_measure_family: "none",
      selected_lookback_points: 50,
      observed_on: "2026-03-08",
      reason_code: null,
    });
  });

  it("normalizes malformed observation as-of descriptor fields", async () => {
    vi.spyOn(globalThis, "fetch").mockResolvedValue(
      mockJsonResponse({
        dataset_id: "UNRATE",
        source: { id: "fred", name: "FRED" },
        title: "Unemployment Rate",
        description: null,
        geographic_scope: null,
        topic_tags: [],
        metadata: {},
        observations: [
          {
            observed_on: "2026-03-15",
            value: 4,
            reported_at: "2026-03-16T00:00:00Z",
            attributes: {},
            as_of_trend_descriptor: {
              descriptor_state: "not-a-state",
              trend_label: 12,
              direction: "sideways",
              strength: 4,
              selected_lookback_points: 999,
              observed_on: 3,
              reason_code: 7,
            },
          },
        ],
        observation_sort: "observed_on_asc,reported_at_asc",
      }),
    );

    const detail = await fetchDatasetDetail("UNRATE");

    expect(detail.observations[0]?.as_of_trend_descriptor).toEqual({
      descriptor_version: "v2",
      descriptor_state: "unavailable",
      trend_label: null,
      direction: null,
      strength: null,
      confidence_score: null,
      dominant_measure_family: "none",
      selected_lookback_points: null,
      observed_on: null,
      reason_code: null,
    });
  });

  it("keeps explicit unavailable descriptor payloads", async () => {
    vi.spyOn(globalThis, "fetch").mockResolvedValue(
      mockJsonResponse({
        dataset_id: "UNRATE",
        source: { id: "fred", name: "FRED" },
        title: "Unemployment Rate",
        description: null,
        geographic_scope: null,
        topic_tags: [],
        metadata: {},
        observations: [
          {
            observed_on: "2026-03-22",
            value: 3.9,
            reported_at: "2026-03-23T00:00:00Z",
            attributes: {},
            as_of_trend_descriptor: {
              descriptor_state: "unavailable",
              trend_label: null,
              direction: null,
              strength: null,
              selected_lookback_points: null,
              observed_on: null,
              reason_code: "no_historical_candidate",
            },
          },
        ],
        observation_sort: "observed_on_asc,reported_at_asc",
      }),
    );

    const detail = await fetchDatasetDetail("UNRATE");

    expect(detail.observations[0]?.as_of_trend_descriptor?.descriptor_state).toBe("unavailable");
    expect(detail.observations[0]?.as_of_trend_descriptor?.reason_code).toBe(
      "no_historical_candidate",
    );
  });
});
