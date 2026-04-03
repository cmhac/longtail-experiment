import { NextRequest } from "next/server";
import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";

import { POST } from "../src/app/api/account/password/route";

const originalDiscoveryApiBaseUrl = process.env.DISCOVERY_API_BASE_URL;

describe("account password route", () => {
  beforeEach(() => {
    process.env.DISCOVERY_API_BASE_URL = "http://backend:8080";
    vi.restoreAllMocks();
  });

  afterEach(() => {
    process.env.DISCOVERY_API_BASE_URL = originalDiscoveryApiBaseUrl;
  });

  it("proxies password change request and handles 204 passthrough", async () => {
    const fetchSpy = vi
      .spyOn(globalThis, "fetch")
      .mockResolvedValueOnce(new Response(null, { status: 204 }))
      .mockResolvedValueOnce(
        new Response(
          JSON.stringify({
            error: { code: "invalid_request", message: "Validation failure" },
          }),
          {
            status: 400,
            headers: { "content-type": "application/json" },
          },
        ),
      );

    const noContent = await POST(
      new NextRequest("http://localhost/api/account/password", {
        method: "POST",
        body: JSON.stringify({ current_password: "old", new_password: "newpassword123" }),
        headers: { authorization: "Bearer session-1", "content-type": "application/json" },
      }),
    );

    const withPayload = await POST(
      new NextRequest("http://localhost/api/account/password", {
        method: "POST",
        body: JSON.stringify({ current_password: "old", new_password: "short" }),
        headers: { authorization: "Bearer session-1", "content-type": "application/json" },
      }),
    );

    expect(fetchSpy).toHaveBeenNthCalledWith(
      1,
      "http://backend:8080/api/account/password",
      expect.objectContaining({ method: "POST" }),
    );
    expect(fetchSpy).toHaveBeenNthCalledWith(
      2,
      "http://backend:8080/api/account/password",
      expect.objectContaining({ method: "POST" }),
    );
    expect(noContent.status).toBe(204);
    expect(withPayload.status).toBe(400);
  });

  it("returns 502 when configuration is missing or upstream fails", async () => {
    process.env.DISCOVERY_API_BASE_URL = "";
    const missingConfig = await POST(
      new NextRequest("http://localhost/api/account/password", {
        method: "POST",
        body: JSON.stringify({ current_password: "old", new_password: "newpassword123" }),
      }),
    );
    expect(missingConfig.status).toBe(502);

    process.env.DISCOVERY_API_BASE_URL = "http://backend:8080";
    vi.spyOn(globalThis, "fetch").mockRejectedValue(new Error("boom"));
    const upstreamError = await POST(
      new NextRequest("http://localhost/api/account/password", {
        method: "POST",
        body: JSON.stringify({ current_password: "old", new_password: "newpassword123" }),
      }),
    );
    expect(upstreamError.status).toBe(502);
  });
});
