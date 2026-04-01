/** @vitest-environment jsdom */

import { fireEvent, render, screen } from "@testing-library/react";
import React from "react";
import { describe, expect, it } from "vitest";

import { TrendTooltipController } from "../../src/components/trends/TrendTooltipController";

describe("TrendOverlayInteractions", () => {
  it("supports desktop hover and touch tap-to-pin behavior", () => {
    render(
      <TrendTooltipController
        chartDates={["2026-01-01", "2026-02-01", "2026-03-01"]}
        spans={[
          {
            start_period: "2026-01-01",
            end_period: "2026-02-01",
            direction: "up",
            trend_label: "uptrend",
            tooltip: { headline: "Up trend", detail: "Increasing" },
          },
        ]}
      />,
    );

    const span = screen.getByTestId("trend-overlay-span");
    fireEvent.mouseEnter(span);
    expect(screen.getByTestId("trend-overlay-tooltip")).toBeTruthy();

    fireEvent.click(span);
    expect(screen.getByTestId("trend-overlay-tooltip")).toBeTruthy();

    fireEvent.pointerDown(window);
    expect(screen.queryByTestId("trend-overlay-tooltip")).toBeNull();
  });
});
