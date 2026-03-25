import { NextRequest } from "next/server";
import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";

import { GET } from "../src/app/api/datasets/search/suggestions/route";

const originalDiscoveryApiBaseUrl = process.env.DISCOVERY_API_BASE_URL;

describe("search suggestions route", () => {
  beforeEach(() => {
    process.env.DISCOVERY_API_BASE_URL = "http://backend:8080";
    vi.restoreAllMocks();
  });

  afterEach(() => {
    process.env.DISCOVERY_API_BASE_URL = originalDiscoveryApiBaseUrl;
  });

  it("proxies query and limit parameters to backend", async () => {
    const fetchSpy = vi.spyOn(globalThis, "fetch").mockResolvedValue(
      new Response(
        JSON.stringify({
          query: "gas",
          limit: 10,
          items: [],
        }),
        {
          status: 200,
          headers: {
            "content-type": "application/json",
          },
        },
      ),
    );

    const request = new NextRequest(
      "http://localhost/api/datasets/search/suggestions?q=gas&limit=10",
    );

    const response = await GET(request);
    const payload = await response.json();

    expect(fetchSpy).toHaveBeenCalledWith(
      "http://backend:8080/api/datasets/search/suggestions?q=gas&limit=10",
      expect.objectContaining({
        method: "GET",
        cache: "no-store",
        headers: {
          accept: "application/json",
        },
      }),
    );
    expect(response.status).toBe(200);
    expect(payload.query).toBe("gas");
  });

  it("returns a 502 envelope when backend base URL is missing", async () => {
    process.env.DISCOVERY_API_BASE_URL = "";

    const request = new NextRequest("http://localhost/api/datasets/search/suggestions?q=gas");

    const response = await GET(request);

    expect(response.status).toBe(502);
    await expect(response.json()).resolves.toMatchObject({
      error: {
        code: "http_error",
        message: "Unable to fetch suggestions",
      },
    });
  });

  it("returns a 502 envelope when backend fetch throws", async () => {
    vi.spyOn(globalThis, "fetch").mockRejectedValue(new Error("network"));

    const request = new NextRequest("http://localhost/api/datasets/search/suggestions?q=gas");

    const response = await GET(request);

    expect(response.status).toBe(502);
  });
});
