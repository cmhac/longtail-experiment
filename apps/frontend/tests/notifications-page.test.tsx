/** @vitest-environment jsdom */

import { fireEvent, render, screen, waitFor } from "@testing-library/react";
import React from "react";
import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";
import { NotificationsPageClient } from "../src/components/notifications/NotificationsPageClient";

vi.mock("../src/lib/auth/session-state", () => ({
  loadAuthSessionState: vi.fn(() => ({ sessionToken: "session-1" })),
}));

vi.mock("../src/lib/api/notification-client", () => ({
  requireNotificationSessionToken: vi.fn(async (token?: string) => token ?? "session-1"),
  fetchNotificationSummary: vi.fn(),
  fetchNotificationList: vi.fn(),
  markAllNotificationsRead: vi.fn(),
  markNotificationRead: vi.fn(),
  markNotificationUnread: vi.fn(),
}));

import {
  fetchNotificationList,
  fetchNotificationSummary,
  markAllNotificationsRead,
  markNotificationRead,
  markNotificationUnread,
} from "../src/lib/api/notification-client";

const asMock = <T extends (...args: never[]) => unknown>(value: T) => {
  return vi.mocked(value);
};

beforeEach(() => {
  vi.restoreAllMocks();
});

afterEach(() => {
  document.body.innerHTML = "";
});

describe("notifications page", () => {
  it("renders notification list and toggles read/unread state", async () => {
    const state = {
      items: [
        {
          notification_id: "notification-1",
          event_id: "event-1",
          dataset_id: "PRICE.US.CPI",
          title: "Trend reversed",
          body: "CPI switched from up to down",
          previous_direction: "up" as const,
          current_direction: "down" as const,
          confidence_score: 0.74,
          effective_observed_on: "2026-04-05",
          destination_path: "/datasets/PRICE.US.CPI",
          unread: true,
          read_at: null,
          delivered_at: "2026-04-05T00:00:00+00:00",
          channel: "in_app" as const,
          delivery_status: "delivered" as const,
          processing_context: "incremental" as const,
          visibility_classification: "user_visible" as const,
        },
      ],
    };

    asMock(fetchNotificationSummary).mockImplementation(async () => ({
      unread_count: state.items.filter((item) => item.unread).length,
      last_notification_at: "2026-04-05T00:00:00+00:00",
      generated_at: "2026-04-05T00:00:00+00:00",
    }));
    asMock(fetchNotificationList).mockImplementation(async () => ({
      items: state.items,
      pagination: { page_size: 50, has_more: false, next_cursor: null },
    }));
    asMock(markAllNotificationsRead).mockImplementation(async () => {
      state.items = state.items.map((item) => ({ ...item, unread: false }));
      return { updated_count: 1, unread_count: 0 };
    });
    asMock(markNotificationRead).mockImplementation(
      async (_token: string, notificationId: string) => {
        state.items = state.items.map((item) =>
          item.notification_id === notificationId ? { ...item, unread: false } : item,
        );
        return { notification_id: notificationId, updated: true, unread_count: 0 };
      },
    );
    asMock(markNotificationUnread).mockImplementation(
      async (_token: string, notificationId: string) => {
        state.items = state.items.map((item) =>
          item.notification_id === notificationId ? { ...item, unread: true } : item,
        );
        return { notification_id: notificationId, updated: true, unread_count: 1 };
      },
    );

    render(<NotificationsPageClient />);

    await waitFor(() => {
      expect(screen.getByTestId("notifications-unread-count").textContent).toContain("Unread: 1");
    });

    fireEvent.click(screen.getByTestId("notifications-page-mark-read-notification-1"));

    await waitFor(() => {
      expect(screen.getByTestId("notifications-unread-count").textContent).toContain("Unread: 0");
    });

    fireEvent.click(screen.getByTestId("notifications-page-mark-unread-notification-1"));

    await waitFor(() => {
      expect(screen.getByTestId("notifications-unread-count").textContent).toContain("Unread: 1");
    });
  });

  it("supports unread-only filtering and mark-all-read action", async () => {
    const state = {
      items: [
        {
          notification_id: "notification-1",
          event_id: "event-1",
          dataset_id: "PRICE.US.CPI",
          title: "Unread item",
          body: "Unread body",
          previous_direction: "up" as const,
          current_direction: "down" as const,
          confidence_score: 0.74,
          effective_observed_on: "2026-04-05",
          destination_path: "/datasets/PRICE.US.CPI",
          unread: true,
          read_at: null,
          delivered_at: "2026-04-05T00:00:00+00:00",
          channel: "in_app" as const,
          delivery_status: "delivered" as const,
          processing_context: "incremental" as const,
          visibility_classification: "user_visible" as const,
        },
        {
          notification_id: "notification-2",
          event_id: "event-2",
          dataset_id: "PRICE.US.PPI",
          title: "Read item",
          body: "Read body",
          previous_direction: "down" as const,
          current_direction: "up" as const,
          confidence_score: 0.52,
          effective_observed_on: "2026-04-05",
          destination_path: "/datasets/PRICE.US.PPI",
          unread: false,
          read_at: "2026-04-05T01:00:00+00:00",
          delivered_at: "2026-04-05T00:00:00+00:00",
          channel: "in_app" as const,
          delivery_status: "delivered" as const,
          processing_context: "incremental" as const,
          visibility_classification: "user_visible" as const,
        },
      ],
    };

    asMock(fetchNotificationSummary).mockImplementation(async () => ({
      unread_count: state.items.filter((item) => item.unread).length,
      last_notification_at: "2026-04-05T00:00:00+00:00",
      generated_at: "2026-04-05T00:00:00+00:00",
    }));
    asMock(fetchNotificationList).mockImplementation(async () => ({
      items: state.items,
      pagination: { page_size: 50, has_more: false, next_cursor: null },
    }));
    asMock(markAllNotificationsRead).mockImplementation(async () => {
      state.items = state.items.map((item) => ({ ...item, unread: false }));
      return { updated_count: 1, unread_count: 0 };
    });
    asMock(markNotificationRead).mockResolvedValue({
      notification_id: "notification-1",
      updated: true,
      unread_count: 0,
    });
    asMock(markNotificationUnread).mockResolvedValue({
      notification_id: "notification-1",
      updated: true,
      unread_count: 1,
    });

    render(<NotificationsPageClient />);

    await waitFor(() => {
      expect(screen.getByTestId("notifications-page-item-notification-1")).not.toBeNull();
      expect(screen.getByTestId("notifications-page-item-notification-2")).not.toBeNull();
    });

    fireEvent.click(screen.getByTestId("notifications-toggle-unread-only"));

    await waitFor(() => {
      expect(screen.getByTestId("notifications-page-item-notification-1")).not.toBeNull();
      expect(screen.queryByTestId("notifications-page-item-notification-2")).toBeNull();
    });

    fireEvent.click(screen.getByTestId("notifications-mark-all-read"));

    await waitFor(() => {
      expect(screen.getByTestId("notifications-unread-count").textContent).toContain("Unread: 0");
    });
  });
});
