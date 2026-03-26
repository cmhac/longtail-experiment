import React from "react";
import { describe, expect, it } from "vitest";
import { DatasetDetailHeader } from "../src/components/discovery/DatasetDetailHeader";
import { buildDatasetDetailFixture } from "./fixtures/dataset-detail-fixtures";
import { renderMarkup } from "./test-utils";

const baseDataset = buildDatasetDetailFixture();

describe("DatasetDetailHeader", () => {
  it("renders full metadata", () => {
    const markup = renderMarkup(
      <DatasetDetailHeader data={baseDataset} exportHref="/api/export.csv" />,
    );

    expect(markup).toContain("Data Source: EIA");
    expect(markup).toContain("Retail gasoline prices for Colorado.");
    expect(markup).toContain('href="/geographies/colorado"');
    expect(markup).toContain('href="/api/export.csv"');
    expect(markup).not.toContain("Share");
    expect(markup).toContain('href="/topics/energy"');
    expect(markup).toContain('href="/topics/gasoline"');
  });

  it("handles null description and geographic scope", () => {
    const markup = renderMarkup(
      <DatasetDetailHeader
        data={{ ...baseDataset, description: null, geographic_scope: null }}
        exportHref="/api/export.csv"
      />,
    );

    expect(markup).toContain("No description available");
    expect(markup).not.toContain("Geographic scope:");
  });

  it("handles empty topic tags", () => {
    const markup = renderMarkup(
      <DatasetDetailHeader
        data={{ ...baseDataset, topic_tags: [] }}
        exportHref="/api/export.csv"
      />,
    );

    expect(markup).toContain("No topic tags");
  });

  it("renders utility actions with default href fallbacks", () => {
    const markup = renderMarkup(<DatasetDetailHeader data={baseDataset} />);

    expect(markup).toContain('href="#"');
    expect(markup).toContain("Export CSV");
    expect(markup).not.toContain("Share");
  });
});
