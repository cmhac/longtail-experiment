import { NextRequest } from "next/server";
import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";

import { GET as getNotifications } from "../src/app/api/notifications/route";
import { POST as postMarkAllRead } from "../src/app/api/notifications/mark-all-read/route";
import { POST as postMarkRead } from "../src/app/api/notifications/[notificationId]/mark-read/route";
import { POST as postMarkUnread } from "../src/app/api/notifications/[notificationId]/mark-unread/route";
import { GET as getSummary } from "../src/app/api/notifications/summary/route";
import {
  DELETE as deleteSubscription,
} from "../src/app/api/notifications/subscriptions/[datasetId]/route";
import {
  GET as getSubscriptions,
  POST as postSubscriptions,
} from "../src/app/api/notifications/subscriptions/route";

const originalDiscoveryApiBaseUrl = process.env.DISCOVERY_API_BASE_URL;

const makeResponseWithoutContentType = (): Response =>
  ({
    status: 200,
    headers: {
      get: vi.fn(() => null),
    },
    text: vi.fn(async () => '{"items":[]}'),
  }) as unknown as Response;

describe("notification proxy routes", () => {
  beforeEach(() => {
    process.env.DISCOVERY_API_BASE_URL = "http://backend:8080";
    vi.restoreAllMocks();
  });

  afterEach(() => {
    process.env.DISCOVERY_API_BASE_URL = originalDiscoveryApiBaseUrl;
  });

  it("proxies list and summary routes with auth header", async () => {
    const fetchSpy = vi
      .spyOn(globalThis, "fetch")
      .mockResolvedValueOnce(
        new Response('{"items":[],"pagination":{"page_size":25,"has_more":false,"next_cursor":null}}', {
          status: 200,
          headers: { "content-type": "application/json" },
        }),
      )
      .mockResolvedValueOnce(
        new Response('{"unread_count":0,"last_notification_at":null,"generated_at":"2026-04-06T00:00:00+00:00"}', {
          status: 200,
          headers: { "content-type": "application/json" },
        }),
      );

    const listResponse = await getNotifications(
      new NextRequest("http://localhost/api/notifications?page_size=25", {
        headers: { authorization: "Bearer session-1" },
      }),
    );
    const summaryResponse = await getSummary(
      new NextRequest("http://localhost/api/notifications/summary", {
        headers: { authorization: "Bearer session-1" },
      }),
    );

    expect(fetchSpy).toHaveBeenNthCalledWith(
      1,
      "http://backend:8080/api/notifications?page_size=25",
      expect.objectContaining({ method: "GET" }),
    );
    expect(fetchSpy).toHaveBeenNthCalledWith(
      2,
      "http://backend:8080/api/notifications/summary",
      expect.objectContaining({ method: "GET" }),
    );
    expect(listResponse.status).toBe(200);
    expect(summaryResponse.status).toBe(200);
  });

  it("proxies mark-read and mark-unread routes", async () => {
    const fetchSpy = vi
      .spyOn(globalThis, "fetch")
      .mockResolvedValueOnce(
        new Response('{"notification_id":"notification-1","updated":true,"unread_count":0}', {
          status: 200,
          headers: { "content-type": "application/json" },
        }),
      )
      .mockResolvedValueOnce(
        new Response('{"notification_id":"notification-1","updated":true,"unread_count":1}', {
          status: 200,
          headers: { "content-type": "application/json" },
        }),
      )
      .mockResolvedValueOnce(
        new Response('{"updated_count":2,"unread_count":0}', {
          status: 200,
          headers: { "content-type": "application/json" },
        }),
      );

    const markReadResponse = await postMarkRead(
      new NextRequest("http://localhost/api/notifications/notification-1/mark-read", {
        method: "POST",
        headers: { authorization: "Bearer session-1" },
      }),
      { params: Promise.resolve({ notificationId: "notification-1" }) },
    );
    const markUnreadResponse = await postMarkUnread(
      new NextRequest("http://localhost/api/notifications/notification-1/mark-unread", {
        method: "POST",
        headers: { authorization: "Bearer session-1" },
      }),
      { params: Promise.resolve({ notificationId: "notification-1" }) },
    );
    const markAllResponse = await postMarkAllRead(
      new NextRequest("http://localhost/api/notifications/mark-all-read", {
        method: "POST",
        headers: { authorization: "Bearer session-1" },
      }),
    );

    expect(fetchSpy).toHaveBeenNthCalledWith(
      1,
      "http://backend:8080/api/notifications/notification-1/mark-read",
      expect.objectContaining({ method: "POST" }),
    );
    expect(fetchSpy).toHaveBeenNthCalledWith(
      2,
      "http://backend:8080/api/notifications/notification-1/mark-unread",
      expect.objectContaining({ method: "POST" }),
    );
    expect(fetchSpy).toHaveBeenNthCalledWith(
      3,
      "http://backend:8080/api/notifications/mark-all-read",
      expect.objectContaining({ method: "POST" }),
    );
    expect(markReadResponse.status).toBe(200);
    expect(markUnreadResponse.status).toBe(200);
    expect(markAllResponse.status).toBe(200);
  });

  it("proxies subscriptions list/create/delete routes", async () => {
    const fetchSpy = vi
      .spyOn(globalThis, "fetch")
      .mockResolvedValueOnce(
        new Response('{"items":[]}', {
          status: 200,
          headers: { "content-type": "application/json" },
        }),
      )
      .mockResolvedValueOnce(
        new Response('{"dataset_id":"PRICE.US.CPI","subscribed_at":"2026-04-06T00:00:00+00:00","created":true}', {
          status: 200,
          headers: { "content-type": "application/json" },
        }),
      )
      .mockResolvedValueOnce(
        new Response('{"dataset_id":"PRICE.US.CPI","removed":true}', {
          status: 200,
          headers: { "content-type": "application/json" },
        }),
      );

    const listResponse = await getSubscriptions(
      new NextRequest("http://localhost/api/notifications/subscriptions", {
        headers: { authorization: "Bearer session-1" },
      }),
    );
    const createResponse = await postSubscriptions(
      new NextRequest("http://localhost/api/notifications/subscriptions", {
        method: "POST",
        headers: { authorization: "Bearer session-1", "content-type": "application/json" },
        body: JSON.stringify({ dataset_id: "PRICE.US.CPI" }),
      }),
    );
    const deleteResponse = await deleteSubscription(
      new NextRequest("http://localhost/api/notifications/subscriptions/PRICE.US.CPI", {
        method: "DELETE",
        headers: { authorization: "Bearer session-1" },
      }),
      { params: Promise.resolve({ datasetId: "PRICE.US.CPI" }) },
    );

    expect(fetchSpy).toHaveBeenNthCalledWith(
      1,
      "http://backend:8080/api/notifications/subscriptions",
      expect.objectContaining({ method: "GET" }),
    );
    expect(fetchSpy).toHaveBeenNthCalledWith(
      2,
      "http://backend:8080/api/notifications/subscriptions",
      expect.objectContaining({ method: "POST" }),
    );
    expect(fetchSpy).toHaveBeenNthCalledWith(
      3,
      "http://backend:8080/api/notifications/subscriptions/PRICE.US.CPI",
      expect.objectContaining({ method: "DELETE" }),
    );
    expect(listResponse.status).toBe(200);
    expect(createResponse.status).toBe(200);
    expect(deleteResponse.status).toBe(200);
  });

  it("returns 502 when config missing and falls back content type", async () => {
    vi.spyOn(globalThis, "fetch").mockResolvedValue(makeResponseWithoutContentType());

    const contentTypeResponse = await getNotifications(
      new NextRequest("http://localhost/api/notifications"),
    );
    expect(contentTypeResponse.headers.get("content-type")).toBe("application/json");

    process.env.DISCOVERY_API_BASE_URL = "";

    const listResponse = await getNotifications(new NextRequest("http://localhost/api/notifications"));
    const summaryResponse = await getSummary(new NextRequest("http://localhost/api/notifications/summary"));
    const markAllResponse = await postMarkAllRead(
      new NextRequest("http://localhost/api/notifications/mark-all-read", { method: "POST" }),
    );
    const markReadResponse = await postMarkRead(
      new NextRequest("http://localhost/api/notifications/notification-1/mark-read", { method: "POST" }),
      { params: Promise.resolve({ notificationId: "notification-1" }) },
    );
    const markUnreadResponse = await postMarkUnread(
      new NextRequest("http://localhost/api/notifications/notification-1/mark-unread", { method: "POST" }),
      { params: Promise.resolve({ notificationId: "notification-1" }) },
    );
    const getSubsResponse = await getSubscriptions(
      new NextRequest("http://localhost/api/notifications/subscriptions"),
    );
    const postSubsResponse = await postSubscriptions(
      new NextRequest("http://localhost/api/notifications/subscriptions", {
        method: "POST",
        body: JSON.stringify({ dataset_id: "PRICE.US.CPI" }),
      }),
    );
    const deleteSubsResponse = await deleteSubscription(
      new NextRequest("http://localhost/api/notifications/subscriptions/PRICE.US.CPI", {
        method: "DELETE",
      }),
      { params: Promise.resolve({ datasetId: "PRICE.US.CPI" }) },
    );

    expect(listResponse.status).toBe(502);
    expect(summaryResponse.status).toBe(502);
    expect(markAllResponse.status).toBe(502);
    expect(markReadResponse.status).toBe(502);
    expect(markUnreadResponse.status).toBe(502);
    expect(getSubsResponse.status).toBe(502);
    expect(postSubsResponse.status).toBe(502);
    expect(deleteSubsResponse.status).toBe(502);
  });

  it("falls back content type across summary/mutation/subscription routes", async () => {
    const responseDouble = makeResponseWithoutContentType();
    const fetchSpy = vi
      .spyOn(globalThis, "fetch")
      .mockResolvedValueOnce(responseDouble)
      .mockResolvedValueOnce(responseDouble)
      .mockResolvedValueOnce(responseDouble)
      .mockResolvedValueOnce(responseDouble)
      .mockResolvedValueOnce(responseDouble)
      .mockResolvedValueOnce(responseDouble)
      .mockResolvedValueOnce(responseDouble);

    const summaryResponse = await getSummary(
      new NextRequest("http://localhost/api/notifications/summary"),
    );
    const markAllResponse = await postMarkAllRead(
      new NextRequest("http://localhost/api/notifications/mark-all-read", { method: "POST" }),
    );
    const markReadResponse = await postMarkRead(
      new NextRequest("http://localhost/api/notifications/notification-1/mark-read", {
        method: "POST",
      }),
      { params: Promise.resolve({ notificationId: "notification-1" }) },
    );
    const markUnreadResponse = await postMarkUnread(
      new NextRequest("http://localhost/api/notifications/notification-1/mark-unread", {
        method: "POST",
      }),
      { params: Promise.resolve({ notificationId: "notification-1" }) },
    );
    const listSubsResponse = await getSubscriptions(
      new NextRequest("http://localhost/api/notifications/subscriptions"),
    );
    const createSubsResponse = await postSubscriptions(
      new NextRequest("http://localhost/api/notifications/subscriptions", {
        method: "POST",
        body: JSON.stringify({ dataset_id: "PRICE.US.CPI" }),
        headers: { "content-type": "application/json" },
      }),
    );
    const deleteSubsResponse = await deleteSubscription(
      new NextRequest("http://localhost/api/notifications/subscriptions/PRICE.US.CPI", {
        method: "DELETE",
      }),
      { params: Promise.resolve({ datasetId: "PRICE.US.CPI" }) },
    );

    expect(fetchSpy).toHaveBeenCalledTimes(7);
    expect(summaryResponse.headers.get("content-type")).toBe("application/json");
    expect(markAllResponse.headers.get("content-type")).toBe("application/json");
    expect(markReadResponse.headers.get("content-type")).toBe("application/json");
    expect(markUnreadResponse.headers.get("content-type")).toBe("application/json");
    expect(listSubsResponse.headers.get("content-type")).toBe("application/json");
    expect(createSubsResponse.headers.get("content-type")).toBe("application/json");
    expect(deleteSubsResponse.headers.get("content-type")).toBe("application/json");
  });
});
