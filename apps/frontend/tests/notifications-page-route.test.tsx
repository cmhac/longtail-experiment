import React from "react";
import { describe, expect, it } from "vitest";
import NotificationsPage from "../src/app/notifications/page";
import { renderMarkup } from "./test-utils";

describe("notifications page route", () => {
  it("renders notification page shell and headings", () => {
    const markup = renderMarkup(<NotificationsPage />);

    expect(markup).toContain('data-testid="notifications-page"');
    expect(markup).toContain('data-testid="notifications-page-header"');
    expect(markup).toContain("Notifications");
    expect(markup).toContain("Notification Center");
    expect(markup).toContain('data-testid="notifications-page-loading"');
  });
});
