import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";

import {
  fetchDatasetCatalog,
  fetchDatasetSearch,
  fetchRecentDatasets,
} from "../src/lib/api/discovery-client";

const originalEnv = process.env.DISCOVERY_API_BASE_URL;

const mockJsonResponse = (payload: unknown, status = 200): Response => {
  return {
    ok: status >= 200 && status < 300,
    status,
    json: async () => payload,
  } as Response;
};

describe("discovery client summary canonical descriptor mapping", () => {
  beforeEach(() => {
    process.env.DISCOVERY_API_BASE_URL = "http://localhost:8080";
    vi.restoreAllMocks();
  });

  afterEach(() => {
    process.env.DISCOVERY_API_BASE_URL = originalEnv;
  });

  it("normalizes missing canonical descriptor to unavailable on search and catalog rows", async () => {
    vi.spyOn(globalThis, "fetch")
      .mockResolvedValueOnce(
        mockJsonResponse({
          items: [
            {
              dataset_id: "UNRATE",
              source: { id: "fred", name: "FRED" },
              title: "Unemployment Rate",
              description: null,
              geographic_scope: "US",
              topic_tags: ["labor"],
              latest_update_at: "2026-03-24T00:00:00Z",
            },
          ],
          page: 1,
          page_size: 20,
          total_items: 1,
          total_pages: 1,
          sort: "latest_update_at_desc,title_asc,dataset_id_asc",
        }),
      )
      .mockResolvedValueOnce(
        mockJsonResponse({
          items: [
            {
              dataset_id: "UNRATE",
              source: { id: "fred", name: "FRED" },
              title: "Unemployment Rate",
              description: null,
              geographic_scope: "US",
              topic_tags: ["labor"],
              latest_update_at: "2026-03-24T00:00:00Z",
            },
          ],
          groups: [],
          aggregations: {
            total_dataset_count: 1,
            sources: [],
            categories: [],
          },
          page: 1,
          page_size: 20,
          total_items: 1,
          total_pages: 1,
          sort: "latest_update_at_desc,title_asc,dataset_id_asc",
        }),
      );

    const search = await fetchDatasetSearch({ q: "rate" });
    const catalog = await fetchDatasetCatalog({});

    expect(search.items[0]?.canonical_trend_descriptor?.descriptor_state).toBe("unavailable");
    expect(catalog.items[0]?.canonical_trend_descriptor?.descriptor_state).toBe("unavailable");
  });

  it("preserves provided canonical descriptor for recent dataset_update items", async () => {
    vi.spyOn(globalThis, "fetch").mockResolvedValue(
      mockJsonResponse({
        items: [
          {
            dataset_id: "UNRATE",
            source: { id: "fred", name: "FRED" },
            title: "Unemployment Rate",
            description: null,
            geographic_scope: "US",
            topic_tags: ["labor"],
            latest_update_at: "2026-03-24T00:00:00Z",
            canonical_trend_descriptor: {
              descriptor_state: "available",
              trend_label: "strong_sustained_uptrend",
              direction: "up",
              strength: "strong",
              selected_lookback_points: 100,
              observed_on: "2026-03-24",
              reason_code: null,
            },
            action_links: {
              view_table_href: "/datasets/UNRATE",
              download_csv_href: "/api/datasets/UNRATE.csv",
            },
          },
        ],
        limit: 5,
        sort: "event_timestamp_desc,title_asc,dataset_id_asc",
      }),
    );

    const recent = await fetchRecentDatasets({ limit: 5 });
    const item = recent.items[0];
    if (!item || item.item_type === "trend_event") {
      throw new Error("Expected dataset_update item");
    }
    expect(item.canonical_trend_descriptor?.descriptor_state).toBe("available");
    expect(item.canonical_trend_descriptor?.direction).toBe("up");
  });
});
