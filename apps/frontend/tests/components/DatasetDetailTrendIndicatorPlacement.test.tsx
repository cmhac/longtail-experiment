import React from "react";
import { describe, expect, it } from "vitest";

import { DatasetDetailHeader } from "../../src/components/discovery/DatasetDetailHeader";
import { buildDatasetDetailFixture } from "../fixtures/dataset-detail-fixtures";
import { renderMarkup } from "../test-utils";

describe("DatasetDetail trend indicator placement", () => {
  it("renders indicator as the first item in the detail tags row", () => {
    const markup = renderMarkup(
      <DatasetDetailHeader
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

    const indicatorIndex = markup.indexOf('data-testid="dataset-detail-trend-indicator"');
    const firstTagIndex = markup.indexOf('href="/geographies/');

    expect(indicatorIndex).toBeGreaterThan(-1);
    expect(firstTagIndex).toBeGreaterThan(-1);
    expect(indicatorIndex).toBeLessThan(firstTagIndex);
    expect(markup).toContain('data-state="down"');
    expect(markup).not.toContain("Historical Trend");
  });
});
