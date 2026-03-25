import React from "react";
import { describe, expect, it } from "vitest";
import { RecentUpdatesFeed } from "../src/components/discovery/RecentUpdatesFeed";
import { makeEditorialFeedItem, makeEditorialFeedItems } from "./fixtures/editorial-feed-fixtures";
import { expectInOrder, renderMarkup } from "./test-utils";

describe("RecentUpdatesFeed", () => {
  it("renders editorial heading and at most five rows", () => {
    const markup = renderMarkup(<RecentUpdatesFeed items={makeEditorialFeedItems(6)} />);

    expect(markup).toContain('data-testid="recent-updates-feed"');
    expect(markup).toContain('data-testid="recent-updates-header"');
    expect(markup).toContain("Recent Updates");
    expect(markup).toContain("Editorial Dataset 1");
    expect(markup).toContain("Editorial Dataset 5");
    expect(markup).not.toContain("Editorial Dataset 6");
  });

  it("renders row metadata hierarchy and row-wide detail link", () => {
    const markup = renderMarkup(<RecentUpdatesFeed items={makeEditorialFeedItems(1)} />);

    expect(markup).toContain('data-testid="unified-dataset-row"');
    expect(markup).toContain('data-testid="unified-dataset-row-title"');
    expect(markup).toContain("EIA");
    expect(markup).toContain("Weekly update summary for editorial dataset 1.");
    expect(markup).toContain('data-testid="unified-dataset-row-pills"');
    expect(markup).toContain(">US<");
    expect(markup).toContain("energy");
    expect(markup).toContain("retail fuel prices");
    expect(markup).toContain('href="/datasets/DATASET_1"');
    expect(markup).not.toContain("View Table");
    expect(markup).not.toContain("Download CSV");
  });

  it("renders entries in newest-first order", () => {
    const markup = renderMarkup(<RecentUpdatesFeed items={makeEditorialFeedItems(3)} />);

    expectInOrder(markup, ["Editorial Dataset 1", "Editorial Dataset 2", "Editorial Dataset 3"]);
  });

  it("renders empty state when no recent items exist", () => {
    const markup = renderMarkup(<RecentUpdatesFeed items={[]} />);

    expect(markup).toContain("No recent updates.");
  });

  it("renders unavailable fallback state when feed request fails", () => {
    const markup = renderMarkup(<RecentUpdatesFeed items={[]} unavailable />);

    expect(markup).toContain("Recent updates are temporarily unavailable.");
  });

  it("falls back to raw date and hides optional metadata when absent", () => {
    const item = makeEditorialFeedItem(1);
    const markup = renderMarkup(
      <RecentUpdatesFeed
        items={[
          {
            ...item,
            description: null,
            geographic_scope: null,
            topic_tags: [],
            latest_update_at: "not-a-date",
          },
        ]}
      />,
    );

    expect(markup).toContain("not-a-date");
    expect(markup).not.toContain("Geography:");
    expect(markup).not.toContain("Weekly update summary");
  });

  it("does not duplicate geography when description already contains it", () => {
    const item = makeEditorialFeedItem(1);
    const markup = renderMarkup(
      <RecentUpdatesFeed
        items={[
          {
            ...item,
            description:
              "Weekly EIA retail regular all formulations gasoline prices in dollars per gallon. Geography: Washington.",
            geographic_scope: "Washington",
            topic_tags: ["energy"],
          },
        ]}
      />,
    );

    const geographyOccurrences = markup.split(">Washington<").length - 1;
    expect(geographyOccurrences).toBe(1);
    expect(markup).toContain('class="recent-updates-pill recent-updates-geography-pill"');
    expect(markup).toContain(
      "Weekly EIA retail regular all formulations gasoline prices in dollars per gallon.",
    );
    expect(markup).not.toContain(
      "Weekly EIA retail regular all formulations gasoline prices in dollars per gallon. Geography: Washington.",
    );
  });
});
