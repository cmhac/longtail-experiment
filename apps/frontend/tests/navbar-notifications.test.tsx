/** @vitest-environment jsdom */

import { fireEvent, render, screen, waitFor } from "@testing-library/react";
import React from "react";
import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";
import { AuthManagementApiError } from "../src/lib/api/auth-management-client";
import { NotificationsPageClient } from "../src/components/notifications/NotificationsPageClient";
import { SiteHeader } from "../src/shell/site-header";

vi.mock("next/navigation", () => ({
  usePathname: () => "/",
  useRouter: () => ({ push: () => undefined }),
  useSearchParams: () => new URLSearchParams("q="),
}));

vi.mock("../src/lib/auth/session-state", () => ({
  loadAuthSessionState: vi.fn(() => ({ sessionToken: "session-1" })),
  clearAuthSessionState: vi.fn(),
}));

vi.mock("../src/lib/api/notification-client", () => ({
  requireNotificationSessionToken: vi.fn(async (token?: string) => token ?? "session-1"),
  fetchNotificationSummary: vi.fn(),
  fetchNotificationList: vi.fn(),
  markNotificationRead: vi.fn(),
  fetchNotificationSubscriptions: vi.fn(),
  markAllNotificationsRead: vi.fn(),
  markNotificationUnread: vi.fn(),
}));

import {
  fetchNotificationList,
  fetchNotificationSubscriptions,
  fetchNotificationSummary,
  markAllNotificationsRead,
  markNotificationRead,
  markNotificationUnread,
  requireNotificationSessionToken,
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

describe("navbar notifications", () => {
  it("loads dropdown notifications and allows marking a notification read", async () => {
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
      pagination: { page_size: 5, has_more: false, next_cursor: null },
    }));
    asMock(markNotificationRead).mockImplementation(async (_token: string, notificationId: string) => {
      state.items = state.items.map((item) =>
        item.notification_id === notificationId ? { ...item, unread: false } : item,
      );
      return {
        notification_id: notificationId,
        updated: true,
        unread_count: state.items.filter((item) => item.unread).length,
      };
    });
    asMock(fetchNotificationSubscriptions).mockResolvedValue({ items: [] });
    asMock(markAllNotificationsRead).mockResolvedValue({ updated_count: 0, unread_count: 0 });
    asMock(markNotificationUnread).mockResolvedValue({
      notification_id: "notification-1",
      updated: true,
      unread_count: 1,
    });

    render(<SiteHeader />);

    fireEvent.click(screen.getByTestId("navbar-notifications-control"));

    await waitFor(() => {
      expect(screen.getByTestId("navbar-notifications-badge").textContent).toBe("1");
    });
    expect(screen.getByText("Trend reversed")).not.toBeNull();

    fireEvent.click(screen.getByTestId("navbar-notification-mark-read-notification-1"));

    await waitFor(() => {
      expect(screen.queryByTestId("navbar-notifications-badge")).toBeNull();
    });
  });

  it("keeps unread totals consistent between dropdown actions and notifications page", async () => {
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
    asMock(markNotificationRead).mockImplementation(async (_token: string, notificationId: string) => {
      state.items = state.items.map((item) =>
        item.notification_id === notificationId ? { ...item, unread: false } : item,
      );
      return {
        notification_id: notificationId,
        updated: true,
        unread_count: state.items.filter((item) => item.unread).length,
      };
    });
    asMock(fetchNotificationSubscriptions).mockResolvedValue({
      items: [{ dataset_id: "PRICE.US.CPI", subscribed_at: "2026-04-05T00:00:00+00:00", unsubscribed_at: null }],
    });
    asMock(markAllNotificationsRead).mockResolvedValue({ updated_count: 0, unread_count: 0 });
    asMock(markNotificationUnread).mockResolvedValue({
      notification_id: "notification-1",
      updated: true,
      unread_count: 1,
    });

    render(<SiteHeader />);

    fireEvent.click(screen.getByTestId("navbar-notifications-control"));
    await waitFor(() => {
      expect(screen.getByTestId("navbar-notifications-badge").textContent).toBe("1");
    });

    fireEvent.click(screen.getByTestId("navbar-notification-mark-read-notification-1"));

    await waitFor(() => {
      expect(screen.queryByTestId("navbar-notifications-badge")).toBeNull();
    });

    render(<NotificationsPageClient />);
    await waitFor(() => {
      expect(screen.getByTestId("notifications-unread-count").textContent).toContain("Unread: 0");
    });
  });

  it("routes unauthenticated dropdown and page views to sign-in", async () => {
    asMock(requireNotificationSessionToken).mockRejectedValue(
      new AuthManagementApiError("Authentication required", 401, "unauthorized"),
    );
    asMock(fetchNotificationSummary).mockResolvedValue({
      unread_count: 0,
      last_notification_at: null,
      generated_at: "2026-04-05T00:00:00+00:00",
    });
    asMock(fetchNotificationList).mockResolvedValue({
      items: [],
      pagination: { page_size: 5, has_more: false, next_cursor: null },
    });
    asMock(fetchNotificationSubscriptions).mockResolvedValue({ items: [] });

    render(<SiteHeader />);
    fireEvent.click(screen.getByTestId("navbar-notifications-control"));

    await waitFor(() => {
      expect(screen.getByTestId("navbar-notifications-unauthenticated").textContent).toContain(
        "Sign in to view notifications.",
      );
    });

    const dropdownSignIn = screen.getByRole("link", { name: "Sign in" });
    expect(dropdownSignIn.getAttribute("href")).toBe("/login");

    render(<NotificationsPageClient />);
    await waitFor(() => {
      expect(screen.getByTestId("notifications-page-unauthenticated").textContent).toContain(
        "Sign in to manage notifications.",
      );
    });
  });

  it("treats deactivated sessions as unauthenticated in dropdown and page views", async () => {
    asMock(requireNotificationSessionToken).mockRejectedValue(
      new AuthManagementApiError("Account deactivated", 401, "unauthorized"),
    );
    asMock(fetchNotificationSummary).mockResolvedValue({
      unread_count: 0,
      last_notification_at: null,
      generated_at: "2026-04-05T00:00:00+00:00",
    });
    asMock(fetchNotificationList).mockResolvedValue({
      items: [],
      pagination: { page_size: 5, has_more: false, next_cursor: null },
    });
    asMock(fetchNotificationSubscriptions).mockResolvedValue({ items: [] });

    render(<SiteHeader />);
    fireEvent.click(screen.getByTestId("navbar-notifications-control"));

    await waitFor(() => {
      expect(screen.getByTestId("navbar-notifications-unauthenticated").textContent).toContain(
        "Sign in to view notifications.",
      );
    });

    render(<NotificationsPageClient />);
    await waitFor(() => {
      expect(screen.getByTestId("notifications-page-unauthenticated")).not.toBeNull();
    });
  });
});
