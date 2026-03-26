import { NextRequest } from "next/server";
import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";

import { GET } from "../src/app/api/datasets/[datasetId].csv/route";

const originalDiscoveryApiBaseUrl = process.env.DISCOVERY_API_BASE_URL;

describe("dataset csv route", () => {
  beforeEach(() => {
    process.env.DISCOVERY_API_BASE_URL = "http://backend:8080";
    vi.restoreAllMocks();
  });

  afterEach(() => {
    process.env.DISCOVERY_API_BASE_URL = originalDiscoveryApiBaseUrl;
  });

  it("proxies CSV requests to backend and preserves content headers", async () => {
    const fetchSpy = vi.spyOn(globalThis, "fetch").mockResolvedValue(
      new Response("observed_on,value\n2026-01-01,4.33\n", {
        status: 200,
        headers: {
          "content-type": "text/csv; charset=utf-8",
          "content-disposition": 'attachment; filename="FEDFUNDS.csv"',
        },
      }),
    );

    const request = new NextRequest(
      "http://localhost/api/datasets/FEDFUNDS.csv?from_date=2026-01-01",
    );

    const response = await GET(request, {
      params: Promise.resolve({ datasetId: "FEDFUNDS" }),
    });

    expect(fetchSpy).toHaveBeenCalledWith(
      "http://backend:8080/api/datasets/FEDFUNDS.csv?from_date=2026-01-01",
      expect.objectContaining({
        method: "GET",
        cache: "no-store",
        headers: {
          accept: "text/csv",
        },
      }),
    );
    expect(response.status).toBe(200);
    await expect(response.text()).resolves.toContain("observed_on,value");
    expect(response.headers.get("content-type")).toContain("text/csv");
    expect(response.headers.get("content-disposition")).toContain("FEDFUNDS.csv");
  });

  it("supports array route params and applies fallback content-disposition", async () => {
    vi.spyOn(globalThis, "fetch").mockResolvedValue(
      new Response("observed_on,value\n2026-01-01,4.33\n", {
        status: 200,
        headers: {
          "content-type": "text/csv; charset=utf-8",
        },
      }),
    );

    const request = new NextRequest("http://localhost/api/datasets/FEDFUNDS.csv");

    const response = await GET(request, {
      params: Promise.resolve({ datasetId: ["FEDFUNDS"] }),
    });

    expect(response.status).toBe(200);
    expect(response.headers.get("content-disposition")).toBe('attachment; filename="FEDFUNDS.csv"');
  });

  it("returns a 502 envelope when route params do not include datasetId", async () => {
    const request = new NextRequest("http://localhost/api/datasets/FEDFUNDS.csv");

    const response = await GET(request, {
      params: Promise.resolve({}),
    });

    expect(response.status).toBe(502);
    await expect(response.json()).resolves.toMatchObject({
      error: {
        code: "http_error",
        message: "Unable to fetch dataset CSV",
      },
    });
  });

  it("returns a 502 envelope when backend base URL is missing", async () => {
    process.env.DISCOVERY_API_BASE_URL = "";

    const request = new NextRequest("http://localhost/api/datasets/FEDFUNDS.csv");

    const response = await GET(request, {
      params: Promise.resolve({ datasetId: "FEDFUNDS" }),
    });

    expect(response.status).toBe(502);
    await expect(response.json()).resolves.toMatchObject({
      error: {
        code: "http_error",
        message: "Unable to fetch dataset CSV",
      },
    });
  });

  it("returns a 502 envelope when backend fetch throws", async () => {
    vi.spyOn(globalThis, "fetch").mockRejectedValue(new Error("network"));

    const request = new NextRequest("http://localhost/api/datasets/FEDFUNDS.csv");

    const response = await GET(request, {
      params: Promise.resolve({ datasetId: "FEDFUNDS" }),
    });

    expect(response.status).toBe(502);
  });
});
