import React from "react";
import { describe, expect, it } from "vitest";
import { DatasetDetailHeader } from "../src/components/discovery/DatasetDetailHeader";
import { buildDatasetDetailFixture } from "./fixtures/dataset-detail-fixtures";
import { renderMarkup } from "./test-utils";

const baseDataset = buildDatasetDetailFixture();

describe("DatasetDetailHeader", () => {
  it("renders full metadata", () => {
    const markup = renderMarkup(<DatasetDetailHeader data={baseDataset} />);

    expect(markup).toContain("Data Source: EIA");
    expect(markup).toContain("Retail gasoline prices for Colorado.");
    expect(markup).toContain('href="/geographies/colorado"');
    expect(markup).toContain("Add to Comparison");
    expect(markup).not.toContain("Share");
    expect(markup).toContain('href="/topics/energy"');
    expect(markup).toContain('href="/topics/gasoline"');
  });

  it("handles null description and geographic scope", () => {
    const markup = renderMarkup(
      <DatasetDetailHeader data={{ ...baseDataset, description: null, geographic_scope: null }} />,
    );

    expect(markup).toContain("No description available");
    expect(markup).not.toContain("Geographic scope:");
  });

  it("handles empty topic tags", () => {
    const markup = renderMarkup(<DatasetDetailHeader data={{ ...baseDataset, topic_tags: [] }} />);

    expect(markup).toContain("No topic tags");
  });

  it("renders utility actions with comparison toggle", () => {
    const markup = renderMarkup(<DatasetDetailHeader data={baseDataset} />);

    expect(markup).toContain("Add to Comparison");
    expect(markup).not.toContain("Share");
  });

  it("shows recent notification chip only when flagged", () => {
    const withChip = renderMarkup(<DatasetDetailHeader data={baseDataset} />);
    const withoutChip = renderMarkup(
      <DatasetDetailHeader data={{ ...baseDataset, has_recent_notification: false }} />,
    );

    expect(withChip).toContain('data-testid="dataset-detail-recent-notification-chip"');
    expect(withoutChip).not.toContain('data-testid="dataset-detail-recent-notification-chip"');
  });
});
