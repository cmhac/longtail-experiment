/** @vitest-environment jsdom */

import { render, screen } from "@testing-library/react";
import React from "react";
import { describe, expect, it, vi } from "vitest";

import { TrendOverlayLayer } from "../../src/components/trends/TrendOverlayLayer";

describe("TrendOverlayLayer", () => {
  it("renders one overlay region per span", () => {
    render(
      <TrendOverlayLayer
        activeSpanId={null}
        chartDates={["2026-01-01", "2026-02-01", "2026-03-01", "2026-04-01"]}
        onHoverSpan={vi.fn()}
        onTogglePinnedSpan={vi.fn()}
        spans={[
          {
            start_period: "2026-01-01",
            end_period: "2026-02-01",
            direction: "up",
            trend_label: "uptrend",
            tooltip: { headline: "Up trend", detail: "Increasing" },
          },
          {
            start_period: "2026-02-02",
            end_period: "2026-03-01",
            direction: "down",
            trend_label: "downtrend",
            tooltip: { headline: "Down trend", detail: "Decreasing" },
          },
        ]}
      />,
    );

    expect(screen.getAllByTestId("trend-overlay-span")).toHaveLength(2);
    expect(screen.getAllByTestId("trend-direction-icon")).toHaveLength(2);
  });
});
