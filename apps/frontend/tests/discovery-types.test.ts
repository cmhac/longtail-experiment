import { describe, expect, it } from "vitest";
import { DISCOVERY_TYPES_SCHEMA_VERSION } from "../src/lib/api/discovery-types";
import type {
  CatalogViewMode,
  DatasetCatalogResponse,
  DatasetDetail,
  DatasetRecentUpdatesResponse,
  DatasetSearchResponse,
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
  });

  it("supports valid catalog view modes", () => {
    const flatMode: CatalogViewMode = "flat";
    const groupedMode: CatalogViewMode = "grouped";

    expect(flatMode).toBe("flat");
    expect(groupedMode).toBe("grouped");
  });
});
