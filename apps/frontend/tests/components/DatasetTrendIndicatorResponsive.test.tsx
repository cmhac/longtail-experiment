import React from "react";
import { describe, expect, it } from "vitest";

import { DatasetTrendIndicator } from "../../src/components/discovery/DatasetTrendIndicator";
import { renderMarkup } from "../test-utils";

describe("DatasetTrendIndicator responsive/unavailable regressions", () => {
  it("keeps label available for desktop and sr-only on compact breakpoints", () => {
    const markup = renderMarkup(
      <DatasetTrendIndicator
        descriptor={{
          descriptor_state: "available",
          trend_label: "sustained_uptrend",
          direction: "up",
          strength: "moderate",
          selected_lookback_points: 25,
          observed_on: "2026-03-01",
          reason_code: null,
        }}
      />,
    );

    expect(markup).toContain('data-testid="dataset-trend-indicator-label"');
    expect(markup).toContain("max-[720px]:sr-only");
  });

  it("uses neutral unavailable rendering when available descriptor lacks direction", () => {
    const markup = renderMarkup(
      <DatasetTrendIndicator
        descriptor={{
          descriptor_state: "available",
          trend_label: "trend_without_direction",
          direction: null,
          strength: "weak",
          selected_lookback_points: 25,
          observed_on: "2026-03-01",
          reason_code: "no_significant_trend",
        }}
      />,
    );

    expect(markup).toContain('data-state="unavailable"');
    expect(markup).toContain("Trend unavailable");
  });
});
