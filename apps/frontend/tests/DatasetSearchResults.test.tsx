import React from "react";
import { describe, expect, it } from "vitest";
import { DatasetSearchResults } from "../src/components/discovery/DatasetSearchResults";
import { renderMarkup } from "./test-utils";

describe("DatasetSearchResults", () => {
  it("renders cards for each result item", () => {
    const markup = renderMarkup(
      <DatasetSearchResults
        items={[
          {
            dataset_id: "UNRATE",
            source: { id: "fred", name: "FRED" },
            title: "Unemployment Rate",
            description: null,
            geographic_scope: "US",
            topic_tags: ["labor"],
            latest_update_at: "2026-02-01T00:00:00Z",
          },
        ]}
        query="unemployment"
      />,
    );

    expect(markup).toContain('data-testid="dataset-search-results"');
    expect(markup).toContain("Results for &quot;unemployment&quot;");
    expect(markup).toContain("Unemployment Rate");
  });

  it("renders empty state when no items are returned", () => {
    const markup = renderMarkup(<DatasetSearchResults items={[]} query="missing" />);

    expect(markup).toContain("No datasets matched your search.");
  });
});
