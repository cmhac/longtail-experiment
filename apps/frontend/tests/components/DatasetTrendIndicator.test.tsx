import React from "react";
import { describe, expect, it } from "vitest";

import { DatasetTrendIndicator } from "../../src/components/discovery/DatasetTrendIndicator";
import { renderMarkup } from "../test-utils";

describe("DatasetTrendIndicator", () => {
  it("renders uptrend state from available descriptor", () => {
    const markup = renderMarkup(
      <DatasetTrendIndicator
        descriptor={{
          descriptor_state: "available",
          trend_label: "sustained_uptrend",
          direction: "up",
          confidence_score: 0.85,
          selected_lookback_points: 50,
          observed_on: "2026-03-01",
          reason_code: null,
        }}
      />,
    );

    expect(markup).toContain('data-testid="dataset-trend-indicator"');
    expect(markup).toContain('data-state="up"');
    expect(markup).toContain("↑");
    expect(markup).toContain("Uptrend");
  });

  it("renders downtrend state from available descriptor", () => {
    const markup = renderMarkup(
      <DatasetTrendIndicator
        descriptor={{
          descriptor_state: "available",
          trend_label: "sustained_downtrend",
          direction: "down",
          confidence_score: 0.62,
          selected_lookback_points: 25,
          observed_on: "2026-03-01",
          reason_code: null,
        }}
      />,
    );

    expect(markup).toContain('data-state="down"');
    expect(markup).toContain("↓");
    expect(markup).toContain("Downtrend");
  });

  it("renders unavailable state when descriptor is unavailable", () => {
    const markup = renderMarkup(
      <DatasetTrendIndicator
        descriptor={{
          descriptor_state: "unavailable",
          trend_label: null,
          direction: null,
          confidence_score: null,
          selected_lookback_points: null,
          observed_on: null,
          reason_code: "no_applicable_lookbacks",
        }}
      />,
    );

    expect(markup).toContain('data-state="unavailable"');
    expect(markup).toContain("Trend unavailable");
  });

  it("does not render when descriptor is absent", () => {
    const markup = renderMarkup(<DatasetTrendIndicator />);

    expect(markup).toBe("");
  });
});
