/** @vitest-environment jsdom */

import { fireEvent, render, screen, waitFor } from "@testing-library/react";
import React from "react";
import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";
import { AuthManagementApiError } from "../src/lib/api/auth-management-client";
import { DatasetDetailHeader } from "../src/components/discovery/DatasetDetailHeader";
import { NotificationSubscriptionControl } from "../src/components/notifications/NotificationSubscriptionControl";
import { buildDatasetDetailFixture } from "./fixtures/dataset-detail-fixtures";
import { renderMarkup } from "./test-utils";

vi.mock("../src/lib/auth/session-state", () => ({
  loadAuthSessionState: vi.fn(() => ({ sessionToken: "session-1" })),
}));

vi.mock("../src/lib/api/notification-client", () => ({
  requireNotificationSessionToken: vi.fn(async (token?: string) => token ?? "session-1"),
  createNotificationSubscription: vi.fn(),
  deleteNotificationSubscription: vi.fn(),
}));

import {
  createNotificationSubscription,
  deleteNotificationSubscription,
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

describe("dataset detail notification subscription control", () => {
  it("renders notification subscription control in dataset detail utility actions", () => {
    const markup = renderMarkup(<DatasetDetailHeader data={buildDatasetDetailFixture()} />);

    expect(markup).toContain('data-testid="notification-subscription-control"');
    expect(markup).toContain("Follow Alerts");
  });

  it("toggles from follow to unfollow and back", async () => {
    asMock(createNotificationSubscription).mockResolvedValue({
      dataset_id: "PRICE.US.CPI",
      subscribed_at: "2026-04-05T00:00:00+00:00",
      created: true,
    });
    asMock(deleteNotificationSubscription).mockResolvedValue({
      dataset_id: "PRICE.US.CPI",
      removed: true,
    });

    render(<NotificationSubscriptionControl datasetId="PRICE.US.CPI" initiallySubscribed={false} />);

    const toggle = screen.getByTestId("notification-subscription-toggle");
    expect(toggle.textContent).toContain("Follow Alerts");

    fireEvent.click(toggle);

    await waitFor(() => {
      expect(screen.getByTestId("notification-subscription-toggle").textContent).toContain(
        "Unfollow Alerts",
      );
    });

    fireEvent.click(screen.getByTestId("notification-subscription-toggle"));

    await waitFor(() => {
      expect(screen.getByTestId("notification-subscription-toggle").textContent).toContain(
        "Follow Alerts",
      );
    });
  });

  it("redirects unauthenticated users to login", async () => {
    const assignSpy = vi.fn();
    Object.defineProperty(window, "location", {
      configurable: true,
      value: {
        assign: assignSpy,
      },
    });

    asMock(requireNotificationSessionToken).mockRejectedValue(
      new AuthManagementApiError("Authentication required", 401, "unauthorized"),
    );
    asMock(createNotificationSubscription).mockResolvedValue({
      dataset_id: "PRICE.US.CPI",
      subscribed_at: "2026-04-05T00:00:00+00:00",
      created: true,
    });
    asMock(deleteNotificationSubscription).mockResolvedValue({
      dataset_id: "PRICE.US.CPI",
      removed: true,
    });

    render(<NotificationSubscriptionControl datasetId="PRICE.US.CPI" initiallySubscribed={false} />);

    fireEvent.click(screen.getByTestId("notification-subscription-toggle"));

    await waitFor(() => {
      expect(assignSpy).toHaveBeenCalledWith("/login");
    });
  });
});
