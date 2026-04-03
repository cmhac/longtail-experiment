import { NextRequest } from "next/server";
import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";

import { GET, PATCH, POST } from "../src/app/api/admin/users/route";

const originalDiscoveryApiBaseUrl = process.env.DISCOVERY_API_BASE_URL;

describe("admin users route", () => {
  beforeEach(() => {
    process.env.DISCOVERY_API_BASE_URL = "http://backend:8080";
    vi.restoreAllMocks();
  });

  afterEach(() => {
    process.env.DISCOVERY_API_BASE_URL = originalDiscoveryApiBaseUrl;
  });

  it("proxies GET and PATCH admin-user requests", async () => {
    const fetchSpy = vi
      .spyOn(globalThis, "fetch")
      .mockResolvedValueOnce(
        new Response(JSON.stringify({ items: [] }), {
          status: 200,
          headers: { "content-type": "application/json" },
        }),
      )
      .mockResolvedValueOnce(
        new Response(JSON.stringify({ user_id: "user-1", account_status: "deactivated" }), {
          status: 200,
          headers: { "content-type": "application/json" },
        }),
      );

    const getResponse = await GET(
      new NextRequest("http://localhost/api/admin/users", {
        headers: { authorization: "Bearer admin-session" },
      }),
    );
    const patchResponse = await PATCH(
      new NextRequest("http://localhost/api/admin/users", {
        method: "PATCH",
        body: JSON.stringify({ user_id: "user-1", account_status: "deactivated" }),
        headers: { authorization: "Bearer admin-session", "content-type": "application/json" },
      }),
    );

    expect(fetchSpy).toHaveBeenNthCalledWith(
      1,
      "http://backend:8080/api/admin/users",
      expect.objectContaining({ method: "GET" }),
    );
    expect(fetchSpy).toHaveBeenNthCalledWith(
      2,
      "http://backend:8080/api/admin/users/user-1/status",
      expect.objectContaining({ method: "PATCH" }),
    );
    expect(getResponse.status).toBe(200);
    expect(patchResponse.status).toBe(200);
  });

  it("validates PATCH and POST payloads", async () => {
    const missingUserIdPatch = await PATCH(
      new NextRequest("http://localhost/api/admin/users", {
        method: "PATCH",
        body: JSON.stringify({ account_status: "deactivated" }),
        headers: { "content-type": "application/json" },
      }),
    );
    expect(missingUserIdPatch.status).toBe(400);

    const invalidPostAction = await POST(
      new NextRequest("http://localhost/api/admin/users", {
        method: "POST",
        body: JSON.stringify({ action: "noop", user_id: "user-1" }),
        headers: { "content-type": "application/json" },
      }),
    );
    expect(invalidPostAction.status).toBe(400);

    const missingPostFields = await POST(
      new NextRequest("http://localhost/api/admin/users", {
        method: "POST",
        body: JSON.stringify({}),
        headers: { "content-type": "application/json" },
      }),
    );
    expect(missingPostFields.status).toBe(400);
  });

  it("proxies POST session revoke and preserves 204", async () => {
    const fetchSpy = vi
      .spyOn(globalThis, "fetch")
      .mockResolvedValue(new Response(null, { status: 204 }));

    const response = await POST(
      new NextRequest("http://localhost/api/admin/users", {
        method: "POST",
        body: JSON.stringify({ action: "revoke_sessions", user_id: "user-1" }),
        headers: { authorization: "Bearer admin-session", "content-type": "application/json" },
      }),
    );

    expect(fetchSpy).toHaveBeenCalledWith(
      "http://backend:8080/api/admin/users/user-1/sessions/revoke",
      expect.objectContaining({ method: "POST" }),
    );
    expect(response.status).toBe(204);
  });

  it("passes through non-204 POST responses", async () => {
    vi.spyOn(globalThis, "fetch").mockResolvedValue(
      new Response(JSON.stringify({ error: { code: "forbidden", message: "Forbidden" } }), {
        status: 403,
      }),
    );

    const response = await POST(
      new NextRequest("http://localhost/api/admin/users", {
        method: "POST",
        body: JSON.stringify({ action: "revoke_sessions", user_id: "user-1" }),
        headers: { "content-type": "application/json" },
      }),
    );

    expect(response.status).toBe(403);
  });

  it("falls back to application/json content-type when upstream omits header", async () => {
    const responseDouble = {
      status: 403,
      text: async () => JSON.stringify({ error: { code: "forbidden", message: "Forbidden" } }),
      headers: { get: () => null },
    } as unknown as Response;
    vi.spyOn(globalThis, "fetch").mockResolvedValue(responseDouble);

    const response = await GET(new NextRequest("http://localhost/api/admin/users"));

    expect(response.status).toBe(403);
    expect(response.headers.get("content-type")).toBe("application/json");
  });

  it("returns 502 when config is missing or upstream fails", async () => {
    process.env.DISCOVERY_API_BASE_URL = "";
    const missingConfig = await GET(new NextRequest("http://localhost/api/admin/users"));
    expect(missingConfig.status).toBe(502);

    process.env.DISCOVERY_API_BASE_URL = "http://backend:8080";
    vi.spyOn(globalThis, "fetch").mockRejectedValue(new Error("boom"));
    const upstreamError = await POST(
      new NextRequest("http://localhost/api/admin/users", {
        method: "POST",
        body: JSON.stringify({ action: "revoke_sessions", user_id: "user-1" }),
      }),
    );
    expect(upstreamError.status).toBe(502);

    vi.spyOn(globalThis, "fetch").mockRejectedValue(new Error("boom"));
    const patchError = await PATCH(
      new NextRequest("http://localhost/api/admin/users", {
        method: "PATCH",
        body: JSON.stringify({ user_id: "user-1", account_status: "deactivated" }),
        headers: { "content-type": "application/json" },
      }),
    );
    expect(patchError.status).toBe(502);
  });
});
