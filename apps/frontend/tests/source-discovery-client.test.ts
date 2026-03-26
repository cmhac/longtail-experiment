import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";

import { fetchSourceDetail, fetchSourceList } from "../src/lib/api/discovery-client";

const originalEnv = process.env.DISCOVERY_API_BASE_URL;

const mockJsonResponse = (payload: unknown, status = 200): Response =>
  ({
    ok: status >= 200 && status < 300,
    status,
    json: async () => payload,
  }) as Response;

describe("source discovery client", () => {
  beforeEach(() => {
    process.env.DISCOVERY_API_BASE_URL = "http://localhost:8080";
    vi.restoreAllMocks();
  });

  afterEach(() => {
    process.env.DISCOVERY_API_BASE_URL = originalEnv;
  });

  it("fetches source list payload from the source endpoint", async () => {
    const fetchSpy = vi.spyOn(globalThis, "fetch").mockResolvedValue(
      mockJsonResponse({
        items: [{ id: "fred", name: "FRED", dataset_count: 2, source_type: "external" }],
        total_items: 1,
        sort: "source_name_asc,source_id_asc",
      }),
    );

    const response = await fetchSourceList();

    expect(String(fetchSpy.mock.calls[0]?.[0])).toContain("/api/sources");
    expect(response.items[0]?.id).toBe("fred");
  });

  it("encodes source identifiers on source detail requests", async () => {
    const fetchSpy = vi.spyOn(globalThis, "fetch").mockResolvedValue(
      mockJsonResponse({
        source: { id: "fred-economic-data", name: "FRED Economic Data", dataset_count: 1 },
        datasets: [],
        sort: "title_asc,dataset_id_asc",
      }),
    );

    await fetchSourceDetail("FRED Economic Data");

    expect(String(fetchSpy.mock.calls[0]?.[0])).toContain("/api/sources/FRED%20Economic%20Data");
  });
});
