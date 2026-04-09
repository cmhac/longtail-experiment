import React from "react";
import { describe, expect, it } from "vitest";

import { DatasetDetailAnalysis } from "../../src/components/discovery/DatasetDetailAnalysis";
import { buildDatasetDetailFixture } from "../fixtures/dataset-detail-fixtures";
import { renderMarkup } from "../test-utils";

describe("DatasetDetail no overlay regression", () => {
  it("renders chart without overlay artifacts", () => {
    const markup = renderMarkup(
      <DatasetDetailAnalysis
        data={buildDatasetDetailFixture({
          canonical_trend_descriptor: {
            descriptor_version: "v2",
            descriptor_state: "available",
            trend_label: "sustained_downtrend",
            direction: "down",
            confidence_score: 0.62,
            dominant_measure_family: "theil_sen",
            selected_lookback_points: 25,
            observed_on: "2026-03-01",
            reason_code: null,
          },
        })}
      />,
    );

    expect(markup).toContain('data-testid="observations-chart"');
    expect(markup).not.toContain("trend-overlay-layer");
    expect(markup).not.toContain("trend-overlay-tooltip");
  });
});
