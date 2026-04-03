import { NextRequest } from "next/server";
import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";

import { GET } from "../src/app/api/admin/navigation/route";

const originalDiscoveryApiBaseUrl = process.env.DISCOVERY_API_BASE_URL;

describe("admin navigation route", () => {
  beforeEach(() => {
    process.env.DISCOVERY_API_BASE_URL = "http://backend:8080";
    vi.restoreAllMocks();
  });

  afterEach(() => {
    process.env.DISCOVERY_API_BASE_URL = originalDiscoveryApiBaseUrl;
  });

  it("proxies GET navigation requests", async () => {
    const fetchSpy = vi.spyOn(globalThis, "fetch").mockResolvedValue(
      new Response(JSON.stringify({ items: [] }), {
        status: 200,
        headers: { "content-type": "application/json" },
      }),
    );

    const response = await GET(
      new NextRequest("http://localhost/api/admin/navigation", {
        headers: { authorization: "Bearer admin-session" },
      }),
    );

    expect(fetchSpy).toHaveBeenCalledWith(
      "http://backend:8080/api/admin/navigation",
      expect.objectContaining({ method: "GET" }),
    );
    expect(response.status).toBe(200);
  });

  it("returns 502 when configuration is missing", async () => {
    process.env.DISCOVERY_API_BASE_URL = "";
    const response = await GET(new NextRequest("http://localhost/api/admin/navigation"));
    expect(response.status).toBe(502);
  });

  it("forwards without auth header and falls back content type", async () => {
    const fetchSpy = vi.spyOn(globalThis, "fetch").mockResolvedValue(
      new Response(null, {
        status: 200,
      }),
    );

    const response = await GET(new NextRequest("http://localhost/api/admin/navigation"));

    expect(fetchSpy).toHaveBeenCalledWith(
      "http://backend:8080/api/admin/navigation",
      expect.objectContaining({
        headers: { accept: "application/json" },
      }),
    );
    expect(response.headers.get("content-type")).toBe("application/json");
  });
});
