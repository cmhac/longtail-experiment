import React from "react";
import { describe, expect, it } from "vitest";

import { RecentUpdatesFeed } from "../../src/components/discovery/RecentUpdatesFeed";
import { renderMarkup } from "../test-utils";

describe("TrendFeedItem", () => {
  it("renders trend events in unified recent feed", () => {
    const markup = renderMarkup(
      <RecentUpdatesFeed
        items={[
          {
            item_type: "trend_event",
            dataset_id: "UNRATE",
            source: { id: "bls", name: "BLS" },
            title: "Unemployment trend",
            direction: "down",
            strength: "mild",
            start_period: "2026-03-01",
            latest_update_at: "2026-03-01",
            action_links: {
              view_table_href: "/datasets/UNRATE",
              download_csv_href: "/api/datasets/UNRATE.csv",
            },
          },
        ]}
      />,
    );

    expect(markup).toContain("TREND EVENT");
    expect(markup).toContain("Unemployment trend");
    expect(markup).toContain("Start 2026-03-01");
    expect(markup).toContain('href="/datasets/UNRATE"');
  });
});
