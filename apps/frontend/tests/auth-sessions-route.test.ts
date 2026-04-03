import { NextRequest } from "next/server";
import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";

import { GET, POST } from "../src/app/api/auth/sessions/route";

const originalDiscoveryApiBaseUrl = process.env.DISCOVERY_API_BASE_URL;

describe("auth sessions route", () => {
  beforeEach(() => {
    process.env.DISCOVERY_API_BASE_URL = "http://backend:8080";
    vi.restoreAllMocks();
  });

  afterEach(() => {
    process.env.DISCOVERY_API_BASE_URL = originalDiscoveryApiBaseUrl;
  });

  it("proxies GET /api/auth/sessions with auth header", async () => {
    const fetchSpy = vi.spyOn(globalThis, "fetch").mockResolvedValue(
      new Response(JSON.stringify({ items: [] }), {
        status: 200,
        headers: { "content-type": "application/json" },
      }),
    );

    const request = new NextRequest("http://localhost/api/auth/sessions", {
      headers: { authorization: "Bearer session-1" },
    });
    const response = await GET(request);

    expect(fetchSpy).toHaveBeenCalledWith(
      "http://backend:8080/api/auth/sessions",
      expect.objectContaining({
        method: "GET",
        cache: "no-store",
        headers: expect.objectContaining({ authorization: "Bearer session-1" }),
      }),
    );
    expect(response.status).toBe(200);
  });

  it("falls back content type for GET when upstream header missing", async () => {
    const responseDouble = {
      status: 200,
      text: async () => JSON.stringify({ items: [] }),
      headers: {
        get: () => null,
      },
    } as unknown as Response;
    vi.spyOn(globalThis, "fetch").mockResolvedValue(responseDouble);

    const response = await GET(new NextRequest("http://localhost/api/auth/sessions"));

    expect(response.headers.get("content-type")).toBe("application/json");
  });

  it("proxies POST /api/auth/sessions with payload and no-content passthrough", async () => {
    const fetchSpy = vi
      .spyOn(globalThis, "fetch")
      .mockResolvedValueOnce(
        new Response(JSON.stringify({ user: {}, session: {} }), {
          status: 201,
          headers: { "content-type": "application/json" },
        }),
      )
      .mockResolvedValueOnce(new Response(null, { status: 204 }));

    const loginResponse = await POST(
      new NextRequest("http://localhost/api/auth/sessions", {
        method: "POST",
        body: JSON.stringify({ action: "login", email: "u@example.com", password: "pw" }),
        headers: { authorization: "Bearer session-1", "content-type": "application/json" },
      }),
    );

    const logoutResponse = await POST(
      new NextRequest("http://localhost/api/auth/sessions", {
        method: "POST",
        body: JSON.stringify({ action: "logout" }),
        headers: { authorization: "Bearer session-1", "content-type": "application/json" },
      }),
    );

    expect(fetchSpy).toHaveBeenNthCalledWith(
      1,
      "http://backend:8080/api/auth/sessions",
      expect.objectContaining({ method: "POST" }),
    );
    expect(fetchSpy).toHaveBeenNthCalledWith(
      2,
      "http://backend:8080/api/auth/sessions",
      expect.objectContaining({ method: "POST" }),
    );
    expect(loginResponse.status).toBe(201);
    expect(logoutResponse.status).toBe(204);
  });

  it("falls back content type for non-204 POST when upstream header missing", async () => {
    const responseDouble = {
      status: 201,
      text: async () => JSON.stringify({ user: {}, session: {} }),
      headers: {
        get: () => null,
      },
    } as unknown as Response;
    vi.spyOn(globalThis, "fetch").mockResolvedValue(responseDouble);

    const response = await POST(
      new NextRequest("http://localhost/api/auth/sessions", {
        method: "POST",
        body: JSON.stringify({ action: "login", email: "u@example.com", password: "pw" }),
        headers: { "content-type": "application/json" },
      }),
    );

    expect(response.status).toBe(201);
    expect(response.headers.get("content-type")).toBe("application/json");
  });

  it("returns 502 on missing config or upstream error", async () => {
    process.env.DISCOVERY_API_BASE_URL = "";
    const missingConfig = await GET(new NextRequest("http://localhost/api/auth/sessions"));
    expect(missingConfig.status).toBe(502);

    process.env.DISCOVERY_API_BASE_URL = "http://backend:8080";
    vi.spyOn(globalThis, "fetch").mockRejectedValue(new Error("boom"));
    const upstreamError = await POST(
      new NextRequest("http://localhost/api/auth/sessions", {
        method: "POST",
        body: JSON.stringify({ action: "login", email: "u@example.com", password: "pw" }),
      }),
    );
    expect(upstreamError.status).toBe(502);
  });
});
