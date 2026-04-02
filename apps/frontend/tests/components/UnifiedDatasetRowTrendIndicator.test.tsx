import React from "react";
import { describe, expect, it } from "vitest";

import { UnifiedDatasetRow } from "../../src/components/discovery/UnifiedDatasetRow";
import { renderMarkup } from "../test-utils";

describe("UnifiedDatasetRow trend indicator placement", () => {
  it("renders right-aligned row indicator when canonical descriptor is available", () => {
    const markup = renderMarkup(
      <UnifiedDatasetRow
        datasetId="DATASET_1"
        destinationHref="/datasets/DATASET_1"
        interactionMode="row_link"
        sourceLabel="EIA"
        summaryText="Summary"
        tagPills={["energy"]}
        title="Editorial Dataset 1"
        trendDescriptor={{
          descriptor_state: "available",
          trend_label: "sustained_uptrend",
          direction: "up",
          strength: "moderate",
          selected_lookback_points: 25,
          observed_on: "2026-03-01",
          reason_code: null,
        }}
        updatedLabel="Mar 25, 2026"
      />,
    );

    expect(markup).toContain('data-testid="unified-dataset-row-trend-indicator"');
    expect(markup).toContain('data-state="up"');
  });

  it("omits row indicator when canonical descriptor is absent", () => {
    const markup = renderMarkup(
      <UnifiedDatasetRow
        datasetId="DATASET_2"
        destinationHref="/datasets/DATASET_2"
        interactionMode="title_link"
        sourceLabel="FRED"
        tagPills={["labor"]}
        title="Unemployment Rate"
        updatedLabel="Mar 25, 2026"
      />,
    );

    expect(markup).not.toContain('data-testid="unified-dataset-row-trend-indicator"');
  });
});
