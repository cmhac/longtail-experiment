import React from "react";
import { describe, expect, it } from "vitest";

import { DatasetDetailAnalysis } from "../../src/components/discovery/DatasetDetailAnalysis";
import { buildDatasetDetailFixture } from "../fixtures/dataset-detail-fixtures";
import { renderMarkup } from "../test-utils";

describe("DatasetDetail trend indicator placement", () => {
  it("renders indicator adjacent to Historical Trend heading", () => {
    const markup = renderMarkup(
      <DatasetDetailAnalysis
        data={buildDatasetDetailFixture({
          canonical_trend_descriptor: {
            descriptor_state: "available",
            trend_label: "sustained_downtrend",
            direction: "down",
            strength: "moderate",
            selected_lookback_points: 25,
            observed_on: "2026-03-01",
            reason_code: null,
          },
        })}
      />,
    );

    expect(markup).toContain("Historical Trend");
    expect(markup).toContain('data-testid="dataset-detail-trend-indicator"');
    expect(markup).toContain('data-state="down"');
  });
});
