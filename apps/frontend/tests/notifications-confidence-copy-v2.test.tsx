/** @vitest-environment jsdom */

import { render, screen } from "@testing-library/react";
import React from "react";
import { describe, expect, it } from "vitest";
import type { NotificationListItem } from "../src/lib/api/notification-types";
import { formatNotificationBody } from "../src/lib/notifications/notification-copy";

const buildItem = (confidenceScore: number | null): NotificationListItem => ({
  notification_id: "notification-1",
  event_id: "event-1",
  dataset_id: "PRICE.US.CPI",
  title: "Trend reversal detected",
  body: "placeholder",
  previous_direction: "up",
  current_direction: "down",
  confidence_score: confidenceScore,
  effective_observed_on: "2026-01-01",
  destination_path: "/datasets/PRICE.US.CPI",
  unread: true,
  read_at: null,
  delivered_at: "2026-01-02T00:00:00+00:00",
  channel: "in_app",
  delivery_status: "delivered",
  processing_context: "incremental",
  visibility_classification: "user_visible",
});

describe("notification confidence copy", () => {
  it("includes confidence detail when score meets threshold", () => {
    render(<p>{formatNotificationBody(buildItem(0.7))}</p>);

    expect(screen.getByText("PRICE.US.CPI: up to down (confidence 0.70)")).not.toBeNull();
  });

  it("omits confidence detail when score is below threshold", () => {
    render(<p>{formatNotificationBody(buildItem(0.69))}</p>);

    expect(screen.getByText("PRICE.US.CPI: up to down")).not.toBeNull();
  });
});
