import React from "react";
import { describe, expect, it } from "vitest";

import { ObservationsChartTooltip } from "../../src/components/discovery/ObservationsChart";
import { renderMarkup } from "../test-utils";

describe("ObservationsChartTooltip as-of trend chip", () => {
  it("returns null when tooltip is inactive", () => {
    const markup = renderMarkup(<ObservationsChartTooltip active={false} payload={[]} />);

    expect(markup).toBe("");
  });

  it("renders uptrend chip for hovered observation descriptor", () => {
    const markup = renderMarkup(
      <ObservationsChartTooltip
        active
        payload={[
          {
            payload: {
              asOfTrendDescriptor: {
                descriptor_state: "available",
                trend_label: "strong_sustained_uptrend",
                direction: "up",
                confidence_score: 0.85,
                selected_lookback_points: 100,
                observed_on: "2026-03-01",
                reason_code: null,
              },
              changePercent: 1.25,
              changeValue: 2.5,
              date: "2026-03-01",
              dateLabel: "Mar 01, 2026",
              dateMs: 1772323200000,
              value: 202.5,
              valueLabel: "202.500",
            },
          },
        ]}
      />,
    );

    expect(markup).toContain('data-testid="observation-as-of-trend-indicator"');
    expect(markup).toContain('data-state="up"');
    expect(markup).toContain("Uptrend");
  });

  it("switches chip direction based on hovered observation descriptor", () => {
    const markup = renderMarkup(
      <ObservationsChartTooltip
        active
        payload={[
          {
            payload: {
              asOfTrendDescriptor: {
                descriptor_state: "available",
                trend_label: "moderate_sustained_downtrend",
                direction: "down",
                confidence_score: 0.62,
                selected_lookback_points: 50,
                observed_on: "2026-03-08",
                reason_code: null,
              },
              changePercent: -0.75,
              changeValue: -1.2,
              date: "2026-03-08",
              dateLabel: "Mar 08, 2026",
              dateMs: 1772928000000,
              value: 201.3,
              valueLabel: "201.300",
            },
          },
        ]}
      />,
    );

    expect(markup).toContain('data-state="down"');
    expect(markup).toContain("Downtrend");
  });
});
