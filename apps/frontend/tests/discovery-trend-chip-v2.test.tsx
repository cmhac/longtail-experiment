import React from "react";
import { describe, expect, it } from "vitest";

import { DatasetTrendIndicator } from "../src/components/discovery/DatasetTrendIndicator";
import { renderMarkup } from "./test-utils";

describe("DatasetTrendIndicator v2", () => {
  it("renders up/down/flat and unavailable states", () => {
    const up = renderMarkup(
      <DatasetTrendIndicator
        descriptor={{
          descriptor_state: "available",
          descriptor_version: "v2",
          trend_label: "up",
          direction: "up",
          confidence_score: 0.8,
          dominant_measure_family: "theil_sen",
          selected_lookback_points: 25,
          observed_on: "2026-03-01",
          reason_code: null,
        }}
      />,
    );
    const down = renderMarkup(
      <DatasetTrendIndicator
        descriptor={{
          descriptor_state: "available",
          descriptor_version: "v2",
          trend_label: "down",
          direction: "down",
          confidence_score: 0.8,
          dominant_measure_family: "theil_sen",
          selected_lookback_points: 25,
          observed_on: "2026-03-01",
          reason_code: null,
        }}
      />,
    );
    const flat = renderMarkup(
      <DatasetTrendIndicator
        descriptor={{
          descriptor_state: "available",
          descriptor_version: "v2",
          trend_label: "flat",
          direction: "flat",
          confidence_score: 0.4,
          dominant_measure_family: "theil_sen",
          selected_lookback_points: 25,
          observed_on: "2026-03-01",
          reason_code: null,
        }}
      />,
    );
    const unavailable = renderMarkup(
      <DatasetTrendIndicator
        descriptor={{
          descriptor_state: "unavailable",
          descriptor_version: "v2",
          trend_label: null,
          direction: null,
          confidence_score: null,
          dominant_measure_family: "none",
          selected_lookback_points: null,
          observed_on: "2026-03-01",
          reason_code: "cadence_irregular_rejected",
        }}
      />,
    );

    expect(up).toContain('data-state="up"');
    expect(down).toContain('data-state="down"');
    expect(flat).toContain('data-state="flat"');
    expect(flat).toContain("Flat trend");
    expect(unavailable).toContain('data-state="unavailable"');
  });
});
