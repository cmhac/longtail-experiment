import React from "react";
import { describe, expect, it } from "vitest";
import { DatasetCatalogList } from "../src/components/discovery/DatasetCatalogList";
import type { DatasetSummary } from "../src/lib/api/discovery-types";
import { renderMarkup } from "./test-utils";

const items: DatasetSummary[] = [
  {
    dataset_id: "UNRATE",
    source: { id: "fred", name: "FRED" },
    title: "Unemployment Rate",
    description: null,
    geographic_scope: "US",
    topic_tags: [],
    latest_update_at: "2026-02-01T00:00:00Z",
    canonical_trend_descriptor: {
      descriptor_version: "v2",
      descriptor_state: "available",
      trend_label: "sustained_downtrend",
      direction: "down",
      confidence_score: 0.62,
      dominant_measure_family: "theil_sen",
      selected_lookback_points: 25,
      observed_on: "2026-02-01",
      reason_code: null,
    },
  },
  {
    dataset_id: "CPIAUCSL",
    source: { id: "fred", name: "FRED" },
    title: "Consumer Price Index",
    description: null,
    geographic_scope: "US",
    topic_tags: [],
    latest_update_at: "2026-02-01T00:00:00Z",
    canonical_trend_descriptor: {
      descriptor_version: "v2",
      descriptor_state: "unavailable",
      trend_label: null,
      direction: null,
      confidence_score: null,
      dominant_measure_family: "none",
      selected_lookback_points: null,
      observed_on: null,
      reason_code: "no_applicable_lookbacks",
    },
  },
];

const primaryItem: DatasetSummary = {
  dataset_id: "UNRATE",
  source: { id: "fred", name: "FRED" },
  title: "Unemployment Rate",
  description: null,
  geographic_scope: "US",
  topic_tags: [],
  latest_update_at: "2026-02-01T00:00:00Z",
  canonical_trend_descriptor: {
    descriptor_version: "v2",
    descriptor_state: "available",
    trend_label: "sustained_downtrend",
    direction: "down",
    confidence_score: 0.62,
    dominant_measure_family: "theil_sen",
    selected_lookback_points: 25,
    observed_on: "2026-02-01",
    reason_code: null,
  },
};

const secondaryItem: DatasetSummary = {
  dataset_id: "CPIAUCSL",
  source: { id: "fred", name: "FRED" },
  title: "Consumer Price Index",
  description: null,
  geographic_scope: "US",
  topic_tags: [],
  latest_update_at: "2026-02-01T00:00:00Z",
  canonical_trend_descriptor: {
    descriptor_version: "v2",
    descriptor_state: "unavailable",
    trend_label: null,
    direction: null,
    confidence_score: null,
    dominant_measure_family: "none",
    selected_lookback_points: null,
    observed_on: null,
    reason_code: "no_applicable_lookbacks",
  },
};

describe("DatasetCatalogList", () => {
  it("renders flat list mode", () => {
    const markup = renderMarkup(<DatasetCatalogList items={items} />);

    expect(markup).toContain('data-testid="catalog-flat-list"');
    expect(markup).toContain('data-testid="discovery-feed-list-wrapper"');
    expect(markup).not.toContain('data-testid="discovery-feed-list-title-region"');
    expect(markup).toContain("Unemployment Rate");
    expect(markup).toContain("Consumer Price Index");
    expect(markup).toContain('data-testid="unified-dataset-row-trend-indicator"');
  });

  it("deduplicates repeated datasets", () => {
    const duplicateItem: DatasetSummary = {
      ...primaryItem,
    };

    const markup = renderMarkup(
      <DatasetCatalogList items={[primaryItem, secondaryItem, duplicateItem]} />,
    );

    const matchCount = markup.match(/href="\/datasets\/UNRATE"/g)?.length ?? 0;
    expect(matchCount).toBe(1);
  });

  it("renders empty state when no catalog items are present", () => {
    const markup = renderMarkup(
      <DatasetCatalogList emptyMessage="Nothing matches your selected filters." items={[]} />,
    );

    expect(markup).toContain("Nothing matches your selected filters.");
  });
});
