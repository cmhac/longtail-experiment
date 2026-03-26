import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";

import { fetchGeographyDetail, fetchTopicDetail } from "../src/lib/api/discovery-client";

const originalEnv = process.env.DISCOVERY_API_BASE_URL;

const mockJsonResponse = (payload: unknown, status = 200): Response =>
  ({
    ok: status >= 200 && status < 300,
    status,
    json: async () => payload,
  }) as Response;

describe("metadata discovery client", () => {
  beforeEach(() => {
    process.env.DISCOVERY_API_BASE_URL = "http://localhost:8080";
    vi.restoreAllMocks();
  });

  afterEach(() => {
    process.env.DISCOVERY_API_BASE_URL = originalEnv;
  });

  it("encodes topic identifiers on topic detail requests", async () => {
    const fetchSpy = vi.spyOn(globalThis, "fetch").mockResolvedValue(
      mockJsonResponse({
        topic: { id: "interest-rates", label: "Interest Rates", dataset_count: 1 },
        datasets: [],
        sort: "title_asc,dataset_id_asc",
      }),
    );

    await fetchTopicDetail("Interest Rates");

    expect(String(fetchSpy.mock.calls[0]?.[0])).toContain("/api/topics/Interest%20Rates");
  });

  it("encodes geography identifiers on geography detail requests", async () => {
    const fetchSpy = vi.spyOn(globalThis, "fetch").mockResolvedValue(
      mockJsonResponse({
        geography: { id: "united-states", label: "United States", dataset_count: 2 },
        datasets: [],
        sort: "title_asc,dataset_id_asc",
      }),
    );

    await fetchGeographyDetail("United States");

    expect(String(fetchSpy.mock.calls[0]?.[0])).toContain("/api/geographies/United%20States");
  });
});
