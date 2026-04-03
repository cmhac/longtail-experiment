import { NextRequest } from "next/server";
import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";

import { POST } from "../src/app/api/account/deletion-request/route";

const originalDiscoveryApiBaseUrl = process.env.DISCOVERY_API_BASE_URL;

describe("account deletion request route", () => {
  beforeEach(() => {
    process.env.DISCOVERY_API_BASE_URL = "http://backend:8080";
    vi.restoreAllMocks();
  });

  afterEach(() => {
    process.env.DISCOVERY_API_BASE_URL = originalDiscoveryApiBaseUrl;
  });

  it("proxies POST deletion request", async () => {
    const fetchSpy = vi.spyOn(globalThis, "fetch").mockResolvedValue(
      new Response(
        JSON.stringify({
          user_id: "user-1",
          account_status: "deletion_pending",
          deletion_due_at: "2026-04-10T00:00:00+00:00",
        }),
        {
          status: 202,
          headers: { "content-type": "application/json" },
        },
      ),
    );

    const response = await POST(
      new NextRequest("http://localhost/api/account/deletion-request", {
        method: "POST",
        headers: { authorization: "Bearer session-1" },
      }),
    );

    expect(fetchSpy).toHaveBeenCalledWith(
      "http://backend:8080/api/account/deletion-request",
      expect.objectContaining({
        method: "POST",
        cache: "no-store",
        headers: expect.objectContaining({ authorization: "Bearer session-1" }),
      }),
    );
    expect(response.status).toBe(202);
  });

  it("returns 502 when configuration is missing or upstream fails", async () => {
    process.env.DISCOVERY_API_BASE_URL = "";
    const missingConfig = await POST(
      new NextRequest("http://localhost/api/account/deletion-request", {
        method: "POST",
      }),
    );
    expect(missingConfig.status).toBe(502);

    process.env.DISCOVERY_API_BASE_URL = "http://backend:8080";
    vi.spyOn(globalThis, "fetch").mockRejectedValue(new Error("boom"));
    const upstreamError = await POST(
      new NextRequest("http://localhost/api/account/deletion-request", {
        method: "POST",
      }),
    );
    expect(upstreamError.status).toBe(502);
  });
});
