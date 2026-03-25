import React from "react";
import { describe, expect, it } from "vitest";
import { DatasetCard } from "../src/components/discovery/DatasetCard";
import { renderMarkup } from "./test-utils";

describe("DatasetCard", () => {
  it("renders title, source, update date, and destination link", () => {
    const markup = renderMarkup(
      <DatasetCard
        item={{
          dataset_id: "UNRATE",
          source: { id: "fred", name: "FRED" },
          title: "Unemployment Rate",
          description: null,
          geographic_scope: "US",
          topic_tags: [],
          latest_update_at: "2026-02-01T00:00:00Z",
        }}
      />,
    );

    expect(markup).toContain("Unemployment Rate");
    expect(markup).toContain("FRED");
    expect(markup).toContain("Updated");
    expect(markup).toContain('href="/datasets/UNRATE"');
  });

  it("falls back to raw date string when update timestamp is invalid", () => {
    const markup = renderMarkup(
      <DatasetCard
        item={{
          dataset_id: "BADDATE",
          source: { id: "fred", name: "FRED" },
          title: "Broken Date Dataset",
          description: null,
          geographic_scope: "US",
          topic_tags: [],
          latest_update_at: "not-a-date",
        }}
      />,
    );

    expect(markup).toContain("Updated not-a-date");
  });
});
