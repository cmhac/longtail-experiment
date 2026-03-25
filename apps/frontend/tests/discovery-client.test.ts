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

  it("sends recent limit query parameter", async () => {
    const fetchSpy = vi
      .spyOn(globalThis, "fetch")
      .mockResolvedValue(mockJsonResponse({ items: [], limit: 5, sort: "latest_update_at_desc" }));

    await fetchRecentDatasets({ limit: 5 });

    const calledUrl = String(fetchSpy.mock.calls[0]?.[0]);
    expect(calledUrl).toContain("/api/datasets/recent");
    expect(calledUrl).toContain("limit=5");
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

  it("sends catalog group_by_source parameter when enabled", async () => {
    const fetchSpy = vi.spyOn(globalThis, "fetch").mockResolvedValue(
      mockJsonResponse({
        items: [],
        groups: [],
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
