import { NextRequest } from "next/server";
import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";

import { GET as getDatasets } from "../src/app/api/discovery/datasets/route";
import { GET as getSearch } from "../src/app/api/discovery/datasets/search/route";
import { GET as getGeography } from "../src/app/api/discovery/geographies/[geographyId]/route";
import { GET as getSource } from "../src/app/api/discovery/sources/[sourceId]/route";
import { GET as getTopic } from "../src/app/api/discovery/topics/[topicId]/route";

const originalDiscoveryApiBaseUrl = process.env.DISCOVERY_API_BASE_URL;

const makeResponseWithoutContentType = (): Response =>
  ({
    status: 200,
    headers: {
      get: vi.fn(() => null),
    },
    text: vi.fn(async () => '{"items":[]}'),
  }) as unknown as Response;

describe("discovery proxy routes", () => {
  beforeEach(() => {
    process.env.DISCOVERY_API_BASE_URL = "http://backend:8080";
    vi.restoreAllMocks();
  });

  afterEach(() => {
    process.env.DISCOVERY_API_BASE_URL = originalDiscoveryApiBaseUrl;
  });

  it("proxies datasets route query params", async () => {
    const fetchSpy = vi.spyOn(globalThis, "fetch").mockResolvedValue(
      new Response(JSON.stringify({ items: [], page: 1, total_pages: 1 }), {
        status: 200,
        headers: { "content-type": "application/json" },
      }),
    );

    const response = await getDatasets(
      new NextRequest("http://localhost/api/discovery/datasets?sort=recency&page=2"),
    );

    expect(fetchSpy).toHaveBeenCalledWith(
      "http://backend:8080/api/datasets?sort=recency&page=2",
      expect.objectContaining({ method: "GET", cache: "no-store" }),
    );
    expect(response.status).toBe(200);
  });

  it("returns 502 for datasets route when config missing", async () => {
    process.env.DISCOVERY_API_BASE_URL = "";

    const response = await getDatasets(
      new NextRequest("http://localhost/api/discovery/datasets?page=1"),
    );

    expect(response.status).toBe(502);
    await expect(response.json()).resolves.toMatchObject({
      error: { code: "http_error", message: "Unable to fetch datasets" },
    });
  });

  it("defaults datasets content type when upstream header is missing", async () => {
    vi.spyOn(globalThis, "fetch").mockResolvedValue(makeResponseWithoutContentType());

    const response = await getDatasets(new NextRequest("http://localhost/api/discovery/datasets"));

    expect(response.status).toBe(200);
    expect(response.headers.get("content-type")).toBe("application/json");
  });

  it("proxies dataset search route query params", async () => {
    const fetchSpy = vi.spyOn(globalThis, "fetch").mockResolvedValue(
      new Response(JSON.stringify({ items: [], page: 1, total_pages: 1 }), {
        status: 200,
        headers: { "content-type": "application/json" },
      }),
    );

    const response = await getSearch(
      new NextRequest("http://localhost/api/discovery/datasets/search?q=inflation&page=2"),
    );

    expect(fetchSpy).toHaveBeenCalledWith(
      "http://backend:8080/api/datasets/search?q=inflation&page=2",
      expect.objectContaining({ method: "GET", cache: "no-store" }),
    );
    expect(response.status).toBe(200);
  });

  it("returns 502 for search route when config missing", async () => {
    process.env.DISCOVERY_API_BASE_URL = "";

    const response = await getSearch(
      new NextRequest("http://localhost/api/discovery/datasets/search?q=inflation"),
    );

    expect(response.status).toBe(502);
    await expect(response.json()).resolves.toMatchObject({
      error: { code: "http_error", message: "Unable to fetch search results" },
    });
  });

  it("defaults search content type when upstream header is missing", async () => {
    vi.spyOn(globalThis, "fetch").mockResolvedValue(makeResponseWithoutContentType());

    const response = await getSearch(
      new NextRequest("http://localhost/api/discovery/datasets/search"),
    );

    expect(response.status).toBe(200);
    expect(response.headers.get("content-type")).toBe("application/json");
  });

  it("proxies source detail route query params", async () => {
    const fetchSpy = vi.spyOn(globalThis, "fetch").mockResolvedValue(
      new Response(JSON.stringify({ items: [], page: 1, total_pages: 1 }), {
        status: 200,
        headers: { "content-type": "application/json" },
      }),
    );

    const response = await getSource(
      new NextRequest("http://localhost/api/discovery/sources/fred?page=2"),
      { params: Promise.resolve({ sourceId: "fred" }) },
    );

    expect(fetchSpy).toHaveBeenCalledWith(
      "http://backend:8080/api/sources/fred?page=2",
      expect.objectContaining({ method: "GET", cache: "no-store" }),
    );
    expect(response.status).toBe(200);
  });

  it("returns 502 for source route when config missing", async () => {
    process.env.DISCOVERY_API_BASE_URL = "";

    const response = await getSource(
      new NextRequest("http://localhost/api/discovery/sources/fred"),
      { params: Promise.resolve({ sourceId: "fred" }) },
    );

    expect(response.status).toBe(502);
    await expect(response.json()).resolves.toMatchObject({
      error: { code: "http_error", message: "Unable to fetch source details" },
    });
  });

  it("defaults source content type when upstream header is missing", async () => {
    vi.spyOn(globalThis, "fetch").mockResolvedValue(makeResponseWithoutContentType());

    const response = await getSource(
      new NextRequest("http://localhost/api/discovery/sources/fred"),
      { params: Promise.resolve({ sourceId: "fred" }) },
    );

    expect(response.status).toBe(200);
    expect(response.headers.get("content-type")).toBe("application/json");
  });

  it("proxies topic detail route query params", async () => {
    const fetchSpy = vi.spyOn(globalThis, "fetch").mockResolvedValue(
      new Response(JSON.stringify({ items: [], page: 1, total_pages: 1 }), {
        status: 200,
        headers: { "content-type": "application/json" },
      }),
    );

    const response = await getTopic(
      new NextRequest("http://localhost/api/discovery/topics/inflation?page=2"),
      { params: Promise.resolve({ topicId: "inflation" }) },
    );

    expect(fetchSpy).toHaveBeenCalledWith(
      "http://backend:8080/api/topics/inflation?page=2",
      expect.objectContaining({ method: "GET", cache: "no-store" }),
    );
    expect(response.status).toBe(200);
  });

  it("returns 502 for topic route when config missing", async () => {
    process.env.DISCOVERY_API_BASE_URL = "";

    const response = await getTopic(
      new NextRequest("http://localhost/api/discovery/topics/inflation"),
      { params: Promise.resolve({ topicId: "inflation" }) },
    );

    expect(response.status).toBe(502);
    await expect(response.json()).resolves.toMatchObject({
      error: { code: "http_error", message: "Unable to fetch topic details" },
    });
  });

  it("defaults topic content type when upstream header is missing", async () => {
    vi.spyOn(globalThis, "fetch").mockResolvedValue(makeResponseWithoutContentType());

    const response = await getTopic(
      new NextRequest("http://localhost/api/discovery/topics/inflation"),
      { params: Promise.resolve({ topicId: "inflation" }) },
    );

    expect(response.status).toBe(200);
    expect(response.headers.get("content-type")).toBe("application/json");
  });

  it("proxies geography detail route query params", async () => {
    const fetchSpy = vi.spyOn(globalThis, "fetch").mockResolvedValue(
      new Response(JSON.stringify({ items: [], page: 1, total_pages: 1 }), {
        status: 200,
        headers: { "content-type": "application/json" },
      }),
    );

    const response = await getGeography(
      new NextRequest("http://localhost/api/discovery/geographies/us?page=2"),
      { params: Promise.resolve({ geographyId: "us" }) },
    );

    expect(fetchSpy).toHaveBeenCalledWith(
      "http://backend:8080/api/geographies/us?page=2",
      expect.objectContaining({ method: "GET", cache: "no-store" }),
    );
    expect(response.status).toBe(200);
  });

  it("returns 502 for geography route when config missing", async () => {
    process.env.DISCOVERY_API_BASE_URL = "";

    const response = await getGeography(
      new NextRequest("http://localhost/api/discovery/geographies/us"),
      { params: Promise.resolve({ geographyId: "us" }) },
    );

    expect(response.status).toBe(502);
    await expect(response.json()).resolves.toMatchObject({
      error: { code: "http_error", message: "Unable to fetch geography details" },
    });
  });

  it("defaults geography content type when upstream header is missing", async () => {
    vi.spyOn(globalThis, "fetch").mockResolvedValue(makeResponseWithoutContentType());

    const response = await getGeography(
      new NextRequest("http://localhost/api/discovery/geographies/us"),
      { params: Promise.resolve({ geographyId: "us" }) },
    );

    expect(response.status).toBe(200);
    expect(response.headers.get("content-type")).toBe("application/json");
  });
});
