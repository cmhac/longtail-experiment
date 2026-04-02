import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";
import {
  DiscoveryApiError,
  fetchDatasetCatalog,
  fetchDatasetDetail,
  fetchDatasetSearch,
  fetchRecentDatasets,
  fetchSearchSuggestions,
  fetchSearchSummary,
} from "../src/lib/api/discovery-client";

const originalEnv = process.env.DISCOVERY_API_BASE_URL;

const mockJsonResponse = (payload: unknown, status = 200): Response => {
  return {
    ok: status >= 200 && status < 300,
    status,
    json: async () => payload,
  } as Response;
};

describe("discovery client", () => {
  beforeEach(() => {
    process.env.DISCOVERY_API_BASE_URL = "http://localhost:8080";
    vi.restoreAllMocks();
  });

  afterEach(() => {
    process.env.DISCOVERY_API_BASE_URL = originalEnv;
  });

  it("constructs encoded search URL and returns typed payload", async () => {
    const fetchSpy = vi.spyOn(globalThis, "fetch").mockResolvedValue(
      mockJsonResponse({
        items: [],
        page: 1,
        page_size: 20,
        total_items: 0,
        total_pages: 0,
        sort: "latest_update_at_desc",
      }),
    );

    const response = await fetchDatasetSearch({ q: "federal funds", page: 2, pageSize: 10 });

    expect(fetchSpy).toHaveBeenCalledTimes(1);
    const calledUrl = String(fetchSpy.mock.calls[0]?.[0]);
    expect(calledUrl).toContain("/api/datasets/search");
    expect(calledUrl).toContain("q=federal+funds");
    expect(calledUrl).toContain("page=2");
    expect(calledUrl).toContain("page_size=10");
    expect(response.page).toBe(1);
  });

  it("serializes explicit pagination values even when zero", async () => {
    const fetchSpy = vi.spyOn(globalThis, "fetch").mockResolvedValue(
      mockJsonResponse({
        items: [],
        page: 1,
        page_size: 20,
        total_items: 0,
        total_pages: 0,
        sort: "latest_update_at_desc",
      }),
    );

    await fetchDatasetCatalog({ page: 0, pageSize: 0 });

    const calledUrl = String(fetchSpy.mock.calls[0]?.[0]);
    expect(calledUrl).toContain("page=0");
    expect(calledUrl).toContain("page_size=0");
  });

  it("sends recent limit query parameter", async () => {
    const fetchSpy = vi.spyOn(globalThis, "fetch").mockResolvedValue(
      mockJsonResponse({
        items: [
          {
            dataset_id: "ENERGY.US.GASREGW",
            source: { id: "eia", name: "EIA" },
            title: "Regular Retail Gasoline Prices",
            description: "Weekly gasoline price update",
            geographic_scope: "US",
            topic_tags: ["energy", "gasoline"],
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
              view_table_href: "/datasets/ENERGY.US.GASREGW",
              download_csv_href: "/api/datasets/ENERGY.US.GASREGW.csv",
            },
          },
        ],
        limit: 5,
        sort: "latest_update_at_desc",
      }),
    );

    const response = await fetchRecentDatasets({ limit: 5 });

    const calledUrl = String(fetchSpy.mock.calls[0]?.[0]);
    expect(calledUrl).toContain("/api/datasets/recent");
    expect(calledUrl).toContain("limit=5");
    expect(response.items[0]?.action_links.download_csv_href).toContain(".csv");
    const datasetItem = response.items[0];
    if (datasetItem?.item_type !== "trend_event") {
      expect(datasetItem?.canonical_trend_descriptor?.descriptor_state).toBe("available");
    }
  });

  it("calls recent endpoint without limit when params are omitted", async () => {
    const fetchSpy = vi
      .spyOn(globalThis, "fetch")
      .mockResolvedValue(mockJsonResponse({ items: [], limit: 5, sort: "latest_update_at_desc" }));

    await fetchRecentDatasets();

    const calledUrl = String(fetchSpy.mock.calls[0]?.[0]);
    expect(calledUrl).toContain("/api/datasets/recent");
    expect(calledUrl).not.toContain("limit=");
  });

  it("fills missing editorial optional fields and action links for recent payloads", async () => {
    vi.spyOn(globalThis, "fetch").mockResolvedValue(
      mockJsonResponse({
        items: [
          {
            dataset_id: "ID WITH SPACE",
            source: { id: "fred", name: "FRED" },
            title: "Dataset With Space",
            latest_update_at: "2026-03-24T00:00:00Z",
          },
        ],
        limit: 5,
        sort: "latest_update_at_desc",
      }),
    );

    const response = await fetchRecentDatasets({ limit: 5 });
    const item = response.items[0];
    if (!item || item.item_type === "trend_event") {
      throw new Error("Expected dataset_update item");
    }

    expect(item.description).toBeNull();
    expect(item.geographic_scope).toBeNull();
    expect(item.topic_tags).toEqual([]);
    expect(item.canonical_trend_descriptor?.descriptor_state).toBe("unavailable");
    expect(item.canonical_trend_descriptor?.reason_code).toBe("missing_canonical_descriptor");
    expect(item.action_links.view_table_href).toBe("/datasets/ID%20WITH%20SPACE");
    expect(item.action_links.download_csv_href).toBe("/api/datasets/ID%20WITH%20SPACE.csv");
  });

  it("normalizes canonical trend descriptor on catalog items", async () => {
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

    const response = await fetchDatasetCatalog({});
    expect(response.items[0]?.canonical_trend_descriptor?.descriptor_state).toBe("unavailable");
    expect(response.items[0]?.canonical_trend_descriptor?.reason_code).toBe(
      "missing_canonical_descriptor",
    );
  });

  it("sends catalog group_by_source parameter when enabled", async () => {
    const fetchSpy = vi.spyOn(globalThis, "fetch").mockResolvedValue(
      mockJsonResponse({
        items: [],
        groups: [],
        aggregations: {
          total_dataset_count: 0,
          sources: [],
          categories: [],
        },
        page: 1,
        page_size: 20,
        total_items: 0,
        total_pages: 0,
        sort: "source_name_asc",
      }),
    );

    await fetchDatasetCatalog({ q: "rate", groupBySource: true });

    const calledUrl = String(fetchSpy.mock.calls[0]?.[0]);
    expect(calledUrl).toContain("/api/datasets?");
    expect(calledUrl).toContain("q=rate");
    expect(calledUrl).toContain("group_by_source=true");
  });

  it("sends optional source/category/sort parameters for catalog requests", async () => {
    const fetchSpy = vi.spyOn(globalThis, "fetch").mockResolvedValue(
      mockJsonResponse({
        items: [],
        groups: [],
        aggregations: {
          total_dataset_count: 0,
          sources: [],
          categories: [],
        },
        page: 1,
        page_size: 20,
        total_items: 0,
        total_pages: 0,
        sort: "latest_update_at_desc",
      }),
    );

    await fetchDatasetCatalog({ source: "eia", category: "energy", sort: "title_asc" });

    const calledUrl = String(fetchSpy.mock.calls[0]?.[0]);
    expect(calledUrl).toContain("source=eia");
    expect(calledUrl).toContain("category=energy");
    expect(calledUrl).toContain("sort=title_asc");
  });

  it("encodes dataset id on detail endpoint", async () => {
    const fetchSpy = vi.spyOn(globalThis, "fetch").mockResolvedValue(
      mockJsonResponse({
        dataset_id: "ID WITH SPACE",
        source: { id: "fred", name: "FRED" },
        title: "Title",
        description: null,
        geographic_scope: null,
        topic_tags: [],
        metadata: {},
        observations: [],
        observation_sort: "observed_on_asc",
      }),
    );

    await fetchDatasetDetail("ID WITH SPACE");

    const calledUrl = String(fetchSpy.mock.calls[0]?.[0]);
    expect(calledUrl).toContain("/api/datasets/ID%20WITH%20SPACE");
  });

  it("throws DiscoveryApiError with code and status on non-200 responses", async () => {
    vi.spyOn(globalThis, "fetch").mockResolvedValue(
      mockJsonResponse(
        {
          error: {
            code: "invalid_request",
            message: "page_size must be between 1 and 100",
          },
        },
        400,
      ),
    );

    await expect(fetchDatasetSearch({ q: "x" })).rejects.toMatchObject({
      name: "DiscoveryApiError",
      code: "invalid_request",
      status: 400,
    });
  });

  it("throws when base URL is missing", async () => {
    process.env.DISCOVERY_API_BASE_URL = "";

    await expect(fetchDatasetSearch({ q: "x" })).rejects.toThrow("Missing DISCOVERY_API_BASE_URL");
  });

  it("falls back to default http_error code when error payload is not JSON", async () => {
    vi.spyOn(globalThis, "fetch").mockResolvedValue({
      ok: false,
      status: 502,
      json: async () => {
        throw new Error("invalid json");
      },
    } as unknown as Response);

    await expect(fetchDatasetSearch({ q: "x" })).rejects.toMatchObject({
      code: "http_error",
      status: 502,
    });
  });

  it("fetches search summary payload", async () => {
    const fetchSpy = vi.spyOn(globalThis, "fetch").mockResolvedValue(
      mockJsonResponse({
        active_dataset_count: 48,
        active_source_count: 3,
        generated_at: "2026-03-24T00:00:00Z",
      }),
    );

    const response = await fetchSearchSummary();

    const calledUrl = String(fetchSpy.mock.calls[0]?.[0]);
    expect(calledUrl).toContain("/api/datasets/search/summary");
    expect(response.active_dataset_count).toBe(48);
  });

  it("throws DiscoveryApiError when summary endpoint fails", async () => {
    vi.spyOn(globalThis, "fetch").mockResolvedValue(
      mockJsonResponse(
        {
          error: {
            code: "http_error",
            message: "down",
          },
        },
        503,
      ),
    );

    await expect(fetchSearchSummary()).rejects.toBeInstanceOf(DiscoveryApiError);
  });

  it("fetches likely suggestions with query and limit", async () => {
    const fetchSpy = vi.spyOn(globalThis, "fetch").mockResolvedValue(
      mockJsonResponse({
        query: "fund",
        limit: 5,
        items: [
          {
            dataset_id: "FEDFUNDS",
            source: { id: "fred", name: "FRED" },
            title: "Federal Funds Effective Rate",
            rank_score: 0.91,
          },
        ],
      }),
    );

    const response = await fetchSearchSuggestions({ q: "fund", limit: 5 });

    const calledUrl = String(fetchSpy.mock.calls[0]?.[0]);
    expect(calledUrl).toContain("/api/datasets/search/suggestions");
    expect(calledUrl).toContain("q=fund");
    expect(calledUrl).toContain("limit=5");
    expect(response.items[0]?.dataset_id).toBe("FEDFUNDS");
  });
});
