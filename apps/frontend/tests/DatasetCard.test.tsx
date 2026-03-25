import React from "react";
import { describe, expect, it } from "vitest";
import { DatasetCard } from "../src/components/discovery/DatasetCard";
import { renderMarkup } from "./test-utils";

describe("DatasetCard", () => {
  it("renders title, source, summary metadata, update date, tags, and destination link", () => {
    const markup = renderMarkup(
      <DatasetCard
        item={{
          dataset_id: "UNRATE",
          source: { id: "fred", name: "FRED" },
          title: "Unemployment Rate",
          description: "Civilian unemployment rate, seasonally adjusted.",
          geographic_scope: "US",
          topic_tags: ["labor", "employment"],
          latest_update_at: "2026-02-01T00:00:00Z",
        }}
      />,
    );

    expect(markup).toContain("Unemployment Rate");
    expect(markup).toContain("FRED");
    expect(markup).toContain("Civilian unemployment rate");
    expect(markup).toContain("labor");
    expect(markup).toContain("Last updated:");
    expect(markup).toContain('href="/datasets/UNRATE"');
    expect(markup).not.toContain("#labor");
    expect(markup).not.toContain('data-testid="dataset-card-actions"');
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

    expect(markup).toContain("Last updated: not-a-date");
  });

  it("falls back to placeholder summary when description is unavailable", () => {
    const markup = renderMarkup(
      <DatasetCard
        item={{
          dataset_id: "NOSUMMARY",
          source: { id: "fred", name: "FRED" },
          title: "No Summary Dataset",
          description: null,
          geographic_scope: "US",
          topic_tags: [],
          latest_update_at: "2026-02-01T00:00:00Z",
        }}
      />,
    );

    expect(markup).toContain("No summary available.");
  });
});
