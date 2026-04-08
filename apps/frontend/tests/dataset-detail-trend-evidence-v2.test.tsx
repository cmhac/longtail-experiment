import React from "react";
import { describe, expect, it } from "vitest";

import { ObservationsChartTooltip } from "../src/components/discovery/ObservationsChart";
import { renderMarkup } from "./test-utils";

describe("dataset detail trend evidence v2", () => {
  it("renders as-of trend indicator with flat/unavailable v2 states", () => {
    const flatMarkup = renderMarkup(
      <ObservationsChartTooltip
        active
        payload={[
          {
            payload: {
              date: "2026-01-01",
              dateMs: Date.parse("2026-01-01T00:00:00Z"),
              dateLabel: "Jan 1, 2026",
              valueLabel: "100",
              value: 100,
              changeValue: 0,
              changePercent: 0,
              asOfTrendDescriptor: {
                descriptor_version: "v2",
                descriptor_state: "available",
                trend_label: "flat",
                direction: "flat",
                confidence_score: 0.45,
                dominant_measure_family: "theil_sen",
                selected_lookback_points: 25,
                observed_on: "2026-01-01",
                reason_code: null,
              },
            },
          },
        ]}
      />,
    );

    const unavailableMarkup = renderMarkup(
      <ObservationsChartTooltip
        active
        payload={[
          {
            payload: {
              date: "2026-01-01",
              dateMs: Date.parse("2026-01-01T00:00:00Z"),
              dateLabel: "Jan 1, 2026",
              valueLabel: "100",
              value: 100,
              changeValue: 0,
              changePercent: 0,
              asOfTrendDescriptor: {
                descriptor_version: "v2",
                descriptor_state: "unavailable",
                trend_label: null,
                direction: null,
                confidence_score: null,
                dominant_measure_family: "none",
                selected_lookback_points: null,
                observed_on: "2026-01-01",
                reason_code: "cadence_irregular_rejected",
              },
            },
          },
        ]}
      />,
    );

    expect(flatMarkup).toContain("Flat trend");
    expect(unavailableMarkup).toContain("Trend unavailable");
  });
});
