import React from "react";
import { describe, expect, it } from "vitest";
import { UnifiedDatasetRow } from "../src/components/discovery/UnifiedDatasetRow";
import { renderMarkup } from "./test-utils";

describe("UnifiedDatasetRow", () => {
  it("renders row-link mode with metadata hierarchy", () => {
    const markup = renderMarkup(
      <UnifiedDatasetRow
        datasetId="DATASET_1"
        destinationHref="/datasets/DATASET_1"
        emphasizedPills={["US"]}
        interactionMode="row_link"
        sourceLabel="EIA"
        summaryText="Weekly update summary for editorial dataset 1."
        tagPills={["energy", "retail fuel prices"]}
        title="Editorial Dataset 1"
        trendDescriptor={{
          descriptor_state: "available",
          trend_label: "sustained_uptrend",
          direction: "up",
          strength: "moderate",
          selected_lookback_points: 10,
          observed_on: "2026-03-25",
          reason_code: null,
        }}
        updatedLabel="Mar 25, 2026"
      />,
    );

    expect(markup).toContain('data-testid="unified-dataset-row"');
    expect(markup).toContain('href="/datasets/DATASET_1"');
    expect(markup).toContain("EIA");
    expect(markup).toContain("Mar 25, 2026");
    expect(markup).toContain("Editorial Dataset 1");
    expect(markup).toContain("Weekly update summary for editorial dataset 1.");
    expect(markup).toContain("US");
    expect(markup).toContain("energy");
    expect(markup).toContain("retail fuel prices");
    expect(markup).toContain('data-testid="unified-dataset-row-title"');
    expect(markup).toContain('data-testid="discovery-feed-list-row"');
    expect(markup).toContain('data-testid="discovery-feed-list-metadata-rail"');
    expect(markup).toContain('data-testid="discovery-feed-list-display-category"');
    expect(markup).toContain('data-testid="discovery-feed-list-update-date"');
    expect(markup).toContain('data-testid="discovery-feed-list-title-text"');
    expect(markup).toContain('data-testid="discovery-feed-list-subtitle"');
    expect(markup).toContain('data-testid="unified-dataset-row-trend-indicator"');
    expect(markup).toContain('data-state="up"');
    expect(markup).toContain('href="/geographies/us"');
    expect(markup).toContain('href="/topics/energy"');
    expect(markup).toContain('href="/topics/retail-fuel-prices"');
    expect(markup).not.toContain(
      'class="recent-updates-row unified-dataset-row" data-testid="unified-dataset-row" href="/datasets/DATASET_1"',
    );
  });

  it("renders title-link mode without row-level link", () => {
    const markup = renderMarkup(
      <UnifiedDatasetRow
        datasetId="UNRATE"
        destinationHref="/datasets/UNRATE"
        interactionMode="title_link"
        sourceLabel="FRED"
        summaryText="Unemployment data summary"
        tagPills={["labor"]}
        title="Unemployment Rate"
        updatedLabel="Mar 20, 2026"
      />,
    );

    expect(markup).toContain("Unemployment Rate");
    expect(markup).toContain('href="/datasets/UNRATE"');
    expect(markup).toContain('data-testid="unified-dataset-row-title"');
    expect(markup).toContain('data-testid="discovery-feed-list-display-category"');
    expect(markup).toContain('data-testid="discovery-feed-list-update-date"');
    expect(markup).toContain('href="/topics/labor"');
    expect(markup).not.toContain('data-testid="unified-dataset-row-trend-indicator"');
    expect(markup).not.toContain(
      'class="recent-updates-row unified-dataset-row" data-testid="unified-dataset-row" href="/datasets/UNRATE"',
    );
  });

  it("omits summary and pills cleanly when optional metadata is missing", () => {
    const markup = renderMarkup(
      <UnifiedDatasetRow
        datasetId="NOSUMMARY"
        destinationHref="/datasets/NOSUMMARY"
        interactionMode="title_link"
        sourceLabel="BLS"
        tagPills={[]}
        title="No Summary Dataset"
        updatedLabel="not-a-date"
      />,
    );

    expect(markup).toContain("No Summary Dataset");
    expect(markup).toContain("not-a-date");
    expect(markup).toContain('data-testid="discovery-feed-list-display-category"');
    expect(markup).toContain('data-testid="discovery-feed-list-update-date"');
    expect(markup).not.toContain('data-testid="discovery-feed-list-subtitle"');
    expect(markup).not.toContain('data-testid="unified-dataset-row-pills"');
  });
});
