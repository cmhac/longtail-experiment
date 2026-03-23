import React from "react";
import { describe, expect, it } from "vitest";
import { DatasetCatalogList } from "../src/components/discovery/DatasetCatalogList";
import { renderMarkup } from "./test-utils";

const items = [
  {
    dataset_id: "UNRATE",
    source: { id: "fred", name: "FRED" },
    title: "Unemployment Rate",
    description: null,
    geographic_scope: "US",
    topic_tags: [],
    latest_update_at: "2026-02-01T00:00:00Z",
  },
  {
    dataset_id: "CPIAUCSL",
    source: { id: "fred", name: "FRED" },
    title: "Consumer Price Index",
    description: null,
    geographic_scope: "US",
    topic_tags: [],
    latest_update_at: "2026-02-01T00:00:00Z",
  },
];

describe("DatasetCatalogList", () => {
  it("renders flat list mode", () => {
    const markup = renderMarkup(<DatasetCatalogList groups={null} items={items} viewMode="flat" />);

    expect(markup).toContain('data-testid="catalog-flat-list"');
    expect(markup).toContain("Unemployment Rate");
    expect(markup).toContain("Consumer Price Index");
  });

  it("renders grouped list mode", () => {
    const markup = renderMarkup(
      <DatasetCatalogList
        groups={[
          {
            source: { id: "fred", name: "FRED" },
            dataset_count: 2,
            dataset_ids: ["UNRATE", "CPIAUCSL"],
          },
        ]}
        items={items}
        viewMode="grouped"
      />,
    );

    expect(markup).toContain('data-testid="catalog-grouped-list"');
    expect(markup).toContain('data-testid="catalog-source-group"');
    expect(markup).toContain("FRED");
  });

  it("renders empty state when no catalog items are present", () => {
    const markup = renderMarkup(<DatasetCatalogList groups={[]} items={[]} viewMode="flat" />);

    expect(markup).toContain("No results found.");
  });
});
