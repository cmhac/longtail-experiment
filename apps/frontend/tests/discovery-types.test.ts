import { describe, expect, it } from "vitest";
import { DISCOVERY_TYPES_SCHEMA_VERSION } from "../src/lib/api/discovery-types";
import type {
  CatalogViewMode,
  DatasetCatalogResponse,
  DatasetDetail,
  DatasetRecentUpdatesResponse,
  DatasetSearchResponse,
  GeographyDetail,
  SourceDetail,
  SourceListResponse,
  TopicDetail,
} from "../src/lib/api/discovery-types";

describe("discovery types", () => {
  it("exposes discovery schema version marker", () => {
    expect(DISCOVERY_TYPES_SCHEMA_VERSION).toBe("v1");
  });

  it("supports nullable optional fields in summary and detail payloads", () => {
    const searchPayload: DatasetSearchResponse = {
      items: [
        {
          dataset_id: "UNRATE",
          source: { id: "fred", name: "FRED" },
          title: "Unemployment Rate",
          description: null,
          geographic_scope: null,
          topic_tags: [],
          latest_update_at: "2026-02-01T00:00:00Z",
        },
      ],
      page: 1,
      page_size: 20,
      total_items: 1,
      total_pages: 1,
      sort: "latest_update_at_desc",
    };

    const detailPayload: DatasetDetail = {
      dataset_id: "UNRATE",
      source: { id: "fred", name: "FRED" },
      title: "Unemployment Rate",
      description: null,
      geographic_scope: null,
      topic_tags: [],
      metadata: {},
      observations: [],
      observation_sort: "observed_on_asc",
    };

    expect(searchPayload.items[0]?.description).toBeNull();
    expect(detailPayload.geographic_scope).toBeNull();
  });

  it("supports canonical trend descriptor payloads for dataset detail", () => {
    const detailPayload: DatasetDetail = {
      dataset_id: "UNRATE",
      source: { id: "fred", name: "FRED" },
      title: "Unemployment Rate",
      description: null,
      geographic_scope: null,
      topic_tags: [],
      metadata: {},
      observations: [],
      canonical_trend_descriptor: {
        descriptor_version: "v2",
        descriptor_state: "available",
        trend_label: "strong_sustained_uptrend",
        direction: "up",
        confidence_score: 0.91,
        dominant_measure_family: "theil_sen",
        selected_lookback_points: 100,
        observed_on: "2026-03-01",
        reason_code: null,
      },
      lookback_trend_evidence: [
        {
          lookback_points: 100,
          applicability_state: "applicable",
          descriptor_state: "available",
          trend_label: "strong_sustained_uptrend",
          direction: "up",
          confidence_score: 0.91,
          dominant_measure_family: "theil_sen",
          theil_sen_slope: 1.2,
          theil_sen_low_slope: 1.0,
          theil_sen_high_slope: 1.4,
          kendall_tau: 0.81,
          kendall_p_value: 0.01,
          preprocessing: {
            smoothing_method: "ewma",
            smoothing_parameters: { halflife: 3 },
            seasonal_adjustment_method: "none",
            seasonal_periods: [],
            seasonal_reliability_state: "not_applicable",
            preprocess_version: "v2",
          },
          ols_diagnostics: {
            slope: 1.1,
            intercept: 50.0,
            r_squared: 0.72,
            p_value: 0.03,
          },
          reason_code: null,
        },
      ],
      observation_sort: "observed_on_asc",
    };

    expect(detailPayload.canonical_trend_descriptor?.descriptor_state).toBe("available");
    expect(detailPayload.lookback_trend_evidence?.[0]?.lookback_points).toBe(100);
  });

  it("preserves required arrays for items, groups, tags, and observations", () => {
    const recentPayload: DatasetRecentUpdatesResponse = {
      items: [
        {
          dataset_id: "ENERGY.US.GASREGW",
          source: { id: "eia", name: "EIA" },
          title: "Regular Retail Gasoline Prices",
          description: "Weekly gasoline price update",
          geographic_scope: "US",
          topic_tags: ["energy", "gasoline"],
          latest_update_at: "2026-03-24T00:00:00Z",
          action_links: {
            view_table_href: "/datasets/ENERGY.US.GASREGW",
            download_csv_href: "/api/datasets/ENERGY.US.GASREGW.csv",
          },
        },
      ],
      limit: 5,
      sort: "latest_update_at_desc",
    };

    const catalogPayload: DatasetCatalogResponse = {
      items: [],
      groups: [],
      aggregations: {
        total_dataset_count: 0,
        sources: [],
        categories: [],
      },
      page: 1,
      page_size: 20,
      total_items: 0,
      total_pages: 0,
      sort: "source_name_asc",
    };

    expect(Array.isArray(recentPayload.items)).toBe(true);
    expect(recentPayload.items[0]?.action_links.download_csv_href).toContain(".csv");
    expect(Array.isArray(catalogPayload.items)).toBe(true);
    expect(Array.isArray(catalogPayload.groups)).toBe(true);
    expect(Array.isArray(catalogPayload.aggregations.categories)).toBe(true);
  });

  it("supports valid catalog view modes", () => {
    const flatMode: CatalogViewMode = "flat";
    const groupedMode: CatalogViewMode = "grouped";

    expect(flatMode).toBe("flat");
    expect(groupedMode).toBe("grouped");
  });

  it("supports source discovery payloads", () => {
    const sourceList: SourceListResponse = {
      items: [
        {
          id: "fred",
          title: "Federal Reserve Economic Data",
          description: "Economic time series published by the St. Louis Fed.",
          dataset_count: 2,
          source_type: "external",
        },
      ],
      total_items: 1,
      sort: "source_title_asc,source_id_asc",
    };
    const sourceDetail: SourceDetail = {
      source: {
        id: "fred",
        title: "Federal Reserve Economic Data",
        description: "Economic time series published by the St. Louis Fed.",
        dataset_count: 2,
        source_type: "external",
      },
      items: [],
      page: 1,
      page_size: 20,
      total_items: 0,
      total_pages: 0,
      sort: "title_asc,dataset_id_asc",
    };

    expect(sourceList.items[0]?.dataset_count).toBe(2);
    expect(sourceList.items[0]?.title).toContain("Federal Reserve");
    expect(sourceDetail.source.id).toBe("fred");
  });

  it("supports metadata discovery payloads", () => {
    const topicDetail: TopicDetail = {
      topic: { id: "inflation", label: "inflation", dataset_count: 1 },
      items: [],
      page: 1,
      page_size: 20,
      total_items: 0,
      total_pages: 0,
      sort: "title_asc,dataset_id_asc",
    };
    const geographyDetail: GeographyDetail = {
      geography: { id: "us", label: "US", dataset_count: 2 },
      items: [],
      page: 1,
      page_size: 20,
      total_items: 0,
      total_pages: 0,
      sort: "title_asc,dataset_id_asc",
    };

    expect(topicDetail.topic.id).toBe("inflation");
    expect(geographyDetail.geography.label).toBe("US");
  });
});
