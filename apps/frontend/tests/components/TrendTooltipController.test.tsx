/** @vitest-environment jsdom */

import { fireEvent, render, screen } from "@testing-library/react";
import React from "react";
import { describe, expect, it } from "vitest";

import { TrendTooltipController } from "../../src/components/trends/TrendTooltipController";

const spans = [
  {
    start_period: "2026-01-01",
    end_period: "2026-02-01",
    direction: "up" as const,
    trend_label: "uptrend",
    tooltip: { headline: "Up trend", detail: "Increasing" },
  },
  {
    start_period: "2026-02-02",
    end_period: "2026-03-01",
    direction: "down" as const,
    trend_label: "downtrend",
    tooltip: { headline: "Down trend", detail: "Decreasing" },
  },
];

describe("TrendTooltipController", () => {
  it("keeps only one active tooltip at a time", () => {
    render(
      <TrendTooltipController
        chartDates={["2026-01-01", "2026-02-01", "2026-03-01"]}
        spans={spans}
      />,
    );

    const overlaySpans = screen.getAllByTestId("trend-overlay-span");
    expect(overlaySpans).toHaveLength(2);
    const firstSpan = overlaySpans[0];
    const secondSpan = overlaySpans[1];
    if (!firstSpan || !secondSpan) {
      throw new Error("Expected overlay spans to be present");
    }

    fireEvent.click(firstSpan);
    expect(screen.getByTestId("trend-overlay-tooltip").textContent).toContain("Up trend");

    fireEvent.click(secondSpan);
    const tooltip = screen.getByTestId("trend-overlay-tooltip");
    expect(tooltip.textContent).toContain("Down trend");
    expect(tooltip.textContent).not.toContain("Up trend");
  });
});
