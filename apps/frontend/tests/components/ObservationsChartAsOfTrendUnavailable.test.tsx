import React from "react";
import { describe, expect, it } from "vitest";

import { ObservationsChartTooltip } from "../../src/components/discovery/ObservationsChart";
import { renderMarkup } from "../test-utils";

describe("ObservationsChartTooltip unavailable as-of trend", () => {
  it("renders explicit unavailable chip for unavailable descriptor", () => {
    const markup = renderMarkup(
      <ObservationsChartTooltip
        active
        payload={[
          {
            payload: {
              asOfTrendDescriptor: {
                descriptor_state: "unavailable",
                trend_label: null,
                direction: null,
                strength: null,
                selected_lookback_points: null,
                observed_on: null,
                reason_code: "no_historical_candidate",
              },
              changePercent: null,
              changeValue: null,
              date: "2026-03-01",
              dateLabel: "Mar 01, 2026",
              dateMs: 1772323200000,
              value: 200,
              valueLabel: "200.000",
            },
          },
        ]}
      />,
    );

    expect(markup).toContain('data-testid="observation-as-of-trend-indicator"');
    expect(markup).toContain('data-state="unavailable"');
    expect(markup).toContain("Trend unavailable");
  });

  it("falls back to explicit unavailable chip when descriptor is missing", () => {
    const markup = renderMarkup(
      <ObservationsChartTooltip
        active
        payload={[
          {
            payload: {
              asOfTrendDescriptor: undefined,
              changePercent: null,
              changeValue: null,
              date: "2026-03-08",
              dateLabel: "Mar 08, 2026",
              dateMs: 1772928000000,
              value: 198,
              valueLabel: "198.000",
            },
          },
        ]}
      />,
    );

    expect(markup).not.toContain('data-testid="observation-as-of-trend-indicator"');
  });
});
