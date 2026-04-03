import { NextRequest } from "next/server";
import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";

import { GET, PATCH } from "../src/app/api/account/profile/route";

const originalDiscoveryApiBaseUrl = process.env.DISCOVERY_API_BASE_URL;

describe("account profile route", () => {
  beforeEach(() => {
    process.env.DISCOVERY_API_BASE_URL = "http://backend:8080";
    vi.restoreAllMocks();
  });

  afterEach(() => {
    process.env.DISCOVERY_API_BASE_URL = originalDiscoveryApiBaseUrl;
  });

  it("proxies GET and PATCH profile requests", async () => {
    const fetchSpy = vi
      .spyOn(globalThis, "fetch")
      .mockResolvedValueOnce(
        new Response(JSON.stringify({ user_id: "user-1" }), {
          status: 200,
          headers: { "content-type": "application/json" },
        }),
      )
      .mockResolvedValueOnce(
        new Response(JSON.stringify({ user_id: "user-1", display_name: "Updated" }), {
          status: 200,
          headers: { "content-type": "application/json" },
        }),
      );

    const getResponse = await GET(
      new NextRequest("http://localhost/api/account/profile", {
        headers: { authorization: "Bearer session-1" },
      }),
    );
    const patchResponse = await PATCH(
      new NextRequest("http://localhost/api/account/profile", {
        method: "PATCH",
        body: JSON.stringify({ display_name: "Updated" }),
        headers: { authorization: "Bearer session-1", "content-type": "application/json" },
      }),
    );

    expect(fetchSpy).toHaveBeenNthCalledWith(
      1,
      "http://backend:8080/api/account/profile",
      expect.objectContaining({ method: "GET" }),
    );
    expect(fetchSpy).toHaveBeenNthCalledWith(
      2,
      "http://backend:8080/api/account/profile",
      expect.objectContaining({ method: "PATCH" }),
    );
    expect(getResponse.status).toBe(200);
    expect(patchResponse.status).toBe(200);
  });

  it("returns 502 when configuration is missing or upstream fails", async () => {
    process.env.DISCOVERY_API_BASE_URL = "";
    const missingConfig = await GET(new NextRequest("http://localhost/api/account/profile"));
    expect(missingConfig.status).toBe(502);

    process.env.DISCOVERY_API_BASE_URL = "http://backend:8080";
    vi.spyOn(globalThis, "fetch").mockRejectedValue(new Error("boom"));
    const upstreamError = await PATCH(
      new NextRequest("http://localhost/api/account/profile", {
        method: "PATCH",
        body: JSON.stringify({ display_name: "Updated" }),
      }),
    );
    expect(upstreamError.status).toBe(502);
  });
});
