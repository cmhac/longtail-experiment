import React from "react";
import { describe, expect, it } from "vitest";
import { DatasetDetailHeader } from "../src/components/discovery/DatasetDetailHeader";
import { renderMarkup } from "./test-utils";

const baseDataset = {
  dataset_id: "UNRATE",
  source: { id: "fred", name: "FRED" },
  title: "Unemployment Rate",
  description: "Share of labor force unemployed",
  geographic_scope: "US",
  topic_tags: ["labor", "employment"],
  metadata: {},
  observations: [],
  observation_sort: "observed_on_asc",
};

describe("DatasetDetailHeader", () => {
  it("renders full metadata", () => {
    const markup = renderMarkup(<DatasetDetailHeader data={baseDataset} />);

    expect(markup).toContain("Unemployment Rate");
    expect(markup).toContain("Share of labor force unemployed");
    expect(markup).toContain("Geographic scope: US");
    expect(markup).toContain("labor");
    expect(markup).toContain("employment");
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
});
