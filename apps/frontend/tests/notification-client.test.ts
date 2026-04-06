import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";
import {
  createNotificationSubscription,
  deleteNotificationSubscription,
  fetchNotificationList,
  fetchNotificationSubscriptions,
  fetchNotificationSummary,
  markAllNotificationsRead,
  markNotificationRead,
  markNotificationUnread,
  requireNotificationSessionToken,
} from "../src/lib/api/notification-client";
import type { NotificationApiError } from "../src/lib/api/notification-client";

const originalEnv = process.env.DISCOVERY_API_BASE_URL;

describe("notification client", () => {
  beforeEach(() => {
    process.env.DISCOVERY_API_BASE_URL = "http://localhost:8080";
    vi.restoreAllMocks();
  });

  afterEach(() => {
    process.env.DISCOVERY_API_BASE_URL = originalEnv;
  });

  it("fetches list and summary payloads", async () => {
    const fetchSpy = vi
      .spyOn(globalThis, "fetch")
      .mockResolvedValueOnce(
        new Response(
          JSON.stringify({
            items: [],
            pagination: { page_size: 25, has_more: false, next_cursor: null },
          }),
          { status: 200 },
        ),
      )
      .mockResolvedValueOnce(
        new Response(
          JSON.stringify({
            unread_count: 0,
            last_notification_at: null,
            generated_at: "2026-04-06T00:00:00+00:00",
          }),
          { status: 200 },
        ),
      );

    const listing = await fetchNotificationList("session-1", {
      pageSize: 25,
      unreadOnly: false,
    });
    const summary = await fetchNotificationSummary("session-1");

    expect(fetchSpy).toHaveBeenNthCalledWith(
      1,
      "http://localhost:8080/api/notifications?page_size=25&unread_only=false",
      expect.objectContaining({ method: "GET" }),
    );
    expect(fetchSpy).toHaveBeenNthCalledWith(
      2,
      "http://localhost:8080/api/notifications/summary",
      expect.objectContaining({ method: "GET" }),
    );
    expect(listing.pagination.page_size).toBe(25);
    expect(summary.unread_count).toBe(0);
  });

  it("calls mutation and subscription endpoints", async () => {
    const fetchSpy = vi
      .spyOn(globalThis, "fetch")
      .mockResolvedValueOnce(
        new Response(JSON.stringify({ updated_count: 2, unread_count: 0 }), { status: 200 }),
      )
      .mockResolvedValueOnce(
        new Response(
          JSON.stringify({
            notification_id: "notification-1",
            updated: true,
            unread_count: 1,
          }),
          { status: 200 },
        ),
      )
      .mockResolvedValueOnce(
        new Response(
          JSON.stringify({
            notification_id: "notification-1",
            updated: true,
            unread_count: 2,
          }),
          { status: 200 },
        ),
      )
      .mockResolvedValueOnce(new Response(JSON.stringify({ items: [] }), { status: 200 }))
      .mockResolvedValueOnce(
        new Response(
          JSON.stringify({
            dataset_id: "PRICE.US.CPI",
            subscribed_at: "2026-04-06T00:00:00+00:00",
            created: true,
          }),
          { status: 200 },
        ),
      )
      .mockResolvedValueOnce(
        new Response(JSON.stringify({ dataset_id: "PRICE.US.CPI", removed: true }), {
          status: 200,
        }),
      );

    const markAll = await markAllNotificationsRead("session-1");
    const markRead = await markNotificationRead("session-1", "notification-1");
    const markUnread = await markNotificationUnread("session-1", "notification-1");
    const subscriptions = await fetchNotificationSubscriptions("session-1");
    const created = await createNotificationSubscription("session-1", {
      dataset_id: "PRICE.US.CPI",
    });
    const removed = await deleteNotificationSubscription("session-1", "PRICE.US.CPI");

    expect(fetchSpy).toHaveBeenNthCalledWith(
      1,
      "http://localhost:8080/api/notifications/mark-all-read",
      expect.objectContaining({ method: "POST" }),
    );
    expect(fetchSpy).toHaveBeenNthCalledWith(
      2,
      "http://localhost:8080/api/notifications/notification-1/mark-read",
      expect.objectContaining({ method: "POST" }),
    );
    expect(fetchSpy).toHaveBeenNthCalledWith(
      3,
      "http://localhost:8080/api/notifications/notification-1/mark-unread",
      expect.objectContaining({ method: "POST" }),
    );
    expect(subscriptions.items).toEqual([]);
    expect(markAll.updated_count).toBe(2);
    expect(markRead.updated).toBe(true);
    expect(markUnread.updated).toBe(true);
    expect(created.dataset_id).toBe("PRICE.US.CPI");
    expect(removed.removed).toBe(true);
  });

  it("throws NotificationApiError on non-OK responses", async () => {
    vi.spyOn(globalThis, "fetch").mockResolvedValue(
      new Response(
        JSON.stringify({
          error: {
            code: "invalid_request",
            message: "bad page size",
          },
        }),
        { status: 400 },
      ),
    );

    await expect(fetchNotificationList("session-1", { pageSize: 0 })).rejects.toMatchObject({
      name: "NotificationApiError",
      code: "invalid_request",
      status: 400,
    } satisfies Partial<NotificationApiError>);
  });

  it("handles cursor query and 204 mutation payloads", async () => {
    const fetchSpy = vi
      .spyOn(globalThis, "fetch")
      .mockResolvedValueOnce(
        new Response(
          JSON.stringify({
            items: [],
            pagination: {
              page_size: 10,
              has_more: false,
              next_cursor: null,
            },
          }),
          { status: 200 },
        ),
      )
      .mockResolvedValueOnce(new Response(null, { status: 204 }))
      .mockResolvedValueOnce(new Response(null, { status: 205 }));

    const listing = await fetchNotificationList("session-1", {
      pageSize: 10,
      cursor: "2026-04-06T00:00:00+00:00|notification-1",
      unreadOnly: true,
    });
    const readResult = await markNotificationRead("session-1", "notification-1");
    const unreadResult = await markNotificationUnread("session-1", "notification-1");

    expect(fetchSpy).toHaveBeenNthCalledWith(
      1,
      "http://localhost:8080/api/notifications?page_size=10&cursor=2026-04-06T00%3A00%3A00%2B00%3A00%7Cnotification-1&unread_only=true",
      expect.objectContaining({ method: "GET" }),
    );
    expect(listing.pagination.page_size).toBe(10);
    expect(readResult).toBeUndefined();
    expect(unreadResult).toBeUndefined();
  });

  it("rejects when session token is missing", async () => {
    await expect(requireNotificationSessionToken(undefined)).rejects.toMatchObject({
      name: "AuthManagementApiError",
      status: 401,
      code: "unauthorized",
    });
  });
});
