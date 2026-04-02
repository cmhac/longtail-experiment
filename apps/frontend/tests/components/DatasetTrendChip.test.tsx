import React from "react";
import { describe, expect, it } from "vitest";

import { DatasetTrendChip } from "../../src/components/discovery/DatasetTrendChip";
import { renderMarkup } from "../test-utils";

describe("DatasetTrendChip", () => {
  it("renders canonical descriptor values when trend is available", () => {
    const markup = renderMarkup(
      <DatasetTrendChip
        canonicalTrendDescriptor={{
          descriptor_state: "available",
          trend_label: "strong_sustained_uptrend",
          direction: "up",
          strength: "strong",
          selected_lookback_points: 50,
          observed_on: "2026-03-01",
          reason_code: null,
        }}
      />,
    );

    expect(markup).toContain('data-testid="dataset-trend-chip"');
    expect(markup).toContain("strong_sustained_uptrend");
    expect(markup).toContain("Up");
    expect(markup).toContain("50-point lookback");
  });

  it("renders unavailable state when canonical descriptor is missing or unavailable", () => {
    const missingMarkup = renderMarkup(<DatasetTrendChip canonicalTrendDescriptor={undefined} />);
    const unavailableMarkup = renderMarkup(
      <DatasetTrendChip
        canonicalTrendDescriptor={{
          descriptor_state: "unavailable",
          trend_label: null,
          direction: null,
          strength: null,
          selected_lookback_points: null,
          observed_on: null,
          reason_code: "no_applicable_lookbacks",
        }}
      />,
    );

    expect(missingMarkup).toContain("Trend unavailable");
    expect(unavailableMarkup).toContain("Trend unavailable");
    expect(unavailableMarkup).toContain("no_applicable_lookbacks");
  });
});
