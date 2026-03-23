import React from "react";
import { describe, expect, it } from "vitest";
import { RecentUpdatesFeed } from "../src/components/discovery/RecentUpdatesFeed";
import { renderMarkup } from "./test-utils";

const makeItem = (index: number) => ({
  dataset_id: `DATASET_${index}`,
  source: { id: "fred", name: "FRED" },
  title: `Dataset ${index}`,
  latest_update_at: "2026-02-01T00:00:00Z",
});

describe("RecentUpdatesFeed", () => {
  it("renders at most five recent items with heading", () => {
    const markup = renderMarkup(
      <RecentUpdatesFeed items={[1, 2, 3, 4, 5, 6].map((value) => makeItem(value))} />,
    );

    expect(markup).toContain('data-testid="recent-updates-feed"');
    expect(markup).toContain("Recent Updates");
    expect(markup).toContain("Dataset 1");
    expect(markup).toContain("Dataset 5");
    expect(markup).not.toContain("Dataset 6");
  });

  it("renders empty state when no recent items exist", () => {
    const markup = renderMarkup(<RecentUpdatesFeed items={[]} />);

    expect(markup).toContain("No recent updates.");
  });
});
