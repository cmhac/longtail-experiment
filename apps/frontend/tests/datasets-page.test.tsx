import { describe, expect, it, vi } from "vitest";
import CatalogPage from "../src/app/datasets/page";
import * as discoveryClient from "../src/lib/api/discovery-client";
import type { DatasetSummary } from "../src/lib/api/discovery-types";
import { renderMarkup } from "./test-utils";

vi.mock("next/navigation", () => ({
  usePathname: () => "/datasets",
  useRouter: () => ({ replace: () => undefined }),
  useSearchParams: () => new URLSearchParams(),
}));

const CATALOG_ITEMS: DatasetSummary[] = [
  {
    dataset_id: "EIA.GAS.CO",
    source: { id: "eia", name: "EIA" },
    title: "Regular All Formulations Retail Gasoline Prices - Colorado",
    description: "Weekly EIA retail regular gasoline prices for Colorado.",
    geographic_scope: "Colorado",
    topic_tags: ["energy", "gasoline"],
    latest_update_at: "2026-03-24T00:00:00Z",
  },
  {
    dataset_id: "BLS.CPI.CORE",
    source: { id: "bls", name: "BLS" },
    title: "Consumer Price Index (CPI-U) - All Items Less Food and Energy",
    description: "Core CPI excluding food and energy components.",
    geographic_scope: "US",
    topic_tags: ["inflation", "economy"],
    latest_update_at: "2026-03-01T00:00:00Z",
  },
  {
    dataset_id: "BLS.CPI.CORE",
    source: { id: "bls", name: "BLS" },
    title: "Consumer Price Index (CPI-U) - All Items Less Food and Energy",
    description: "Duplicate payload row used for dedupe validation.",
    geographic_scope: "US",
    topic_tags: ["inflation", "economy"],
    latest_update_at: "2026-03-01T00:00:00Z",
  },
];

const mockCatalogResponse = (): void => {
  vi.spyOn(discoveryClient, "fetchDatasetCatalog").mockResolvedValue({
    items: [...CATALOG_ITEMS],
    groups: null,
    aggregations: {
      total_dataset_count: 14282,
      sources: [
        { source: { id: "bls", name: "BLS" }, dataset_count: 1 },
        { source: { id: "eia", name: "EIA" }, dataset_count: 1 },
      ],
      categories: [
        { value: "economy", dataset_count: 1 },
        { value: "energy", dataset_count: 1 },
        { value: "gasoline", dataset_count: 1 },
        { value: "inflation", dataset_count: 1 },
      ],
    },
    page: 1,
    page_size: 20,
    total_items: 3,
    total_pages: 1,
    sort: "latest_update_at_desc",
  });
};

describe("datasets page", () => {
  it("renders heading, catalog total summary, and controls", async () => {
    mockCatalogResponse();

    const element = await CatalogPage({ searchParams: Promise.resolve({}) });
    const markup = renderMarkup(element);

    expect(markup).toContain("Datasets");
    expect(markup).toContain('data-testid="dataset-list-total-series"');
    expect(markup).toContain("page-header-wrapper");
    expect(markup).toContain("14,282 total series");
    expect(markup).toContain('data-testid="dataset-source-filter"');
    expect(markup).toContain('data-testid="dataset-category-filter"');
    expect(markup).toContain('data-testid="dataset-sort-control"');
    expect(markup).toContain('data-testid="dataset-filter-left-group"');
    expect(markup).toContain('data-testid="dataset-sort-right-group"');
    expect(markup).toContain("dataset-list-controls-surface");
    expect(markup).toContain('data-testid="unified-dataset-row"');
    expect(markup).not.toContain('data-testid="discovery-pagination"');
    expect(markup).not.toContain('data-testid="request-new-dataset-cta"');
  });

  it("preserves catalog-total summary when source/category filters are applied", async () => {
    vi.spyOn(discoveryClient, "fetchDatasetCatalog").mockResolvedValue({
      items: [CATALOG_ITEMS[0] as DatasetSummary],
      groups: null,
      aggregations: {
        total_dataset_count: 14282,
        sources: [
          { source: { id: "bls", name: "BLS" }, dataset_count: 1 },
          { source: { id: "eia", name: "EIA" }, dataset_count: 1 },
        ],
        categories: [
          { value: "economy", dataset_count: 1 },
          { value: "energy", dataset_count: 1 },
          { value: "gasoline", dataset_count: 1 },
          { value: "inflation", dataset_count: 1 },
        ],
      },
      page: 1,
      page_size: 20,
      total_items: 1,
      total_pages: 1,
      sort: "latest_update_at_desc,title_asc,dataset_id_asc",
    });

    const element = await CatalogPage({
      searchParams: Promise.resolve({ source: "eia", category: "energy" }),
    });
    const markup = renderMarkup(element);

    expect(markup).toContain("14,282 total series");
    expect(markup).toContain("Regular All Formulations Retail Gasoline Prices - Colorado");
    expect(markup).not.toContain("Consumer Price Index (CPI-U)");
  });

  it("renders server-provided title ascending order when title_asc sort mode is selected", async () => {
    vi.spyOn(discoveryClient, "fetchDatasetCatalog").mockResolvedValue({
      items: [CATALOG_ITEMS[1] as DatasetSummary, CATALOG_ITEMS[0] as DatasetSummary],
      groups: null,
      aggregations: {
        total_dataset_count: 14282,
        sources: [
          { source: { id: "bls", name: "BLS" }, dataset_count: 1 },
          { source: { id: "eia", name: "EIA" }, dataset_count: 1 },
        ],
        categories: [
          { value: "economy", dataset_count: 1 },
          { value: "energy", dataset_count: 1 },
        ],
      },
      page: 1,
      page_size: 20,
      total_items: 2,
      total_pages: 1,
      sort: "title_asc,dataset_id_asc",
    });

    const element = await CatalogPage({
      searchParams: Promise.resolve({ sort: "title_asc" }),
    });
    const markup = renderMarkup(element);

    const cpiIndex = markup.indexOf("Consumer Price Index (CPI-U)");
    const gasIndex = markup.indexOf("Regular All Formulations Retail Gasoline Prices - Colorado");

    expect(cpiIndex).toBeGreaterThan(-1);
    expect(gasIndex).toBeGreaterThan(-1);
    expect(cpiIndex).toBeLessThan(gasIndex);
  });

  it("renders server-provided title descending order when title_desc sort mode is selected", async () => {
    vi.spyOn(discoveryClient, "fetchDatasetCatalog").mockResolvedValue({
      items: [CATALOG_ITEMS[0] as DatasetSummary, CATALOG_ITEMS[1] as DatasetSummary],
      groups: null,
      aggregations: {
        total_dataset_count: 14282,
        sources: [
          { source: { id: "bls", name: "BLS" }, dataset_count: 1 },
          { source: { id: "eia", name: "EIA" }, dataset_count: 1 },
        ],
        categories: [
          { value: "economy", dataset_count: 1 },
          { value: "energy", dataset_count: 1 },
        ],
      },
      page: 1,
      page_size: 20,
      total_items: 2,
      total_pages: 1,
      sort: "title_desc,dataset_id_desc",
    });

    const element = await CatalogPage({
      searchParams: Promise.resolve({ sort: "title_desc" }),
    });
    const markup = renderMarkup(element);

    const cpiIndex = markup.indexOf("Consumer Price Index (CPI-U)");
    const gasIndex = markup.indexOf("Regular All Formulations Retail Gasoline Prices - Colorado");

    expect(cpiIndex).toBeGreaterThan(-1);
    expect(gasIndex).toBeGreaterThan(-1);
    expect(gasIndex).toBeLessThan(cpiIndex);
  });

  it("falls back to recency sort when an unknown sort value is provided", async () => {
    const catalogSpy = vi.spyOn(discoveryClient, "fetchDatasetCatalog").mockResolvedValue({
      items: [...CATALOG_ITEMS],
      groups: null,
      aggregations: {
        total_dataset_count: 14282,
        sources: [
          { source: { id: "bls", name: "BLS" }, dataset_count: 1 },
          { source: { id: "eia", name: "EIA" }, dataset_count: 1 },
        ],
        categories: [
          { value: "economy", dataset_count: 1 },
          { value: "energy", dataset_count: 1 },
        ],
      },
      page: 1,
      page_size: 20,
      total_items: 2,
      total_pages: 1,
      sort: "latest_update_at_desc,title_asc,dataset_id_asc",
    });

    await CatalogPage({
      searchParams: Promise.resolve({ sort: "unsupported-sort" }),
    });

    expect(catalogSpy).toHaveBeenCalledWith({
      page: 1,
      source: undefined,
      category: undefined,
      sort: "recency",
    });
  });

  it("renders explicit empty-results state for no-match filters", async () => {
    vi.spyOn(discoveryClient, "fetchDatasetCatalog").mockResolvedValue({
      items: [],
      groups: null,
      aggregations: {
        total_dataset_count: 14282,
        sources: [
          { source: { id: "bls", name: "BLS" }, dataset_count: 1 },
          { source: { id: "eia", name: "EIA" }, dataset_count: 1 },
        ],
        categories: [
          { value: "energy", dataset_count: 1 },
          { value: "inflation", dataset_count: 1 },
        ],
      },
      page: 1,
      page_size: 20,
      total_items: 0,
      total_pages: 0,
      sort: "latest_update_at_desc",
    });

    const element = await CatalogPage({
      searchParams: Promise.resolve({ source: "census", category: "housing" }),
    });
    const markup = renderMarkup(element);

    expect(markup).toContain("No datasets match the selected filters.");
    expect(markup).toContain('data-testid="discovery-empty-state"');
  });

  it("prevents duplicate dataset cards from being rendered", async () => {
    mockCatalogResponse();

    const element = await CatalogPage({ searchParams: Promise.resolve({}) });
    const markup = renderMarkup(element);

    const duplicateCardCount = markup.match(/href="\/datasets\/BLS\.CPI\.CORE"/g)?.length ?? 0;
    expect(duplicateCardCount).toBe(1);
  });

  it("renders geography as an emphasized pill in unified row output", async () => {
    mockCatalogResponse();

    const element = await CatalogPage({ searchParams: Promise.resolve({}) });
    const markup = renderMarkup(element);

    expect(markup).toContain('class="recent-updates-pill recent-updates-geography-pill"');
    expect(markup).toContain("Colorado");
  });

  it("renders fallback state when catalog request fails", async () => {
    vi.spyOn(discoveryClient, "fetchDatasetCatalog").mockRejectedValue(new Error("unavailable"));

    const element = await CatalogPage({ searchParams: Promise.resolve({}) });
    const markup = renderMarkup(element);

    expect(markup).toContain("Unable to load data. Please try again.");
    expect(markup).not.toContain('data-testid="request-new-dataset-cta"');
  });

  it("keeps empty state behavior stable with explicit page query", async () => {
    vi.spyOn(discoveryClient, "fetchDatasetCatalog").mockResolvedValue({
      items: [],
      groups: null,
      aggregations: {
        total_dataset_count: 14282,
        sources: [{ source: { id: "eia", name: "EIA" }, dataset_count: 1 }],
        categories: [{ value: "energy", dataset_count: 1 }],
      },
      page: 4,
      page_size: 20,
      total_items: 0,
      total_pages: 0,
      sort: "latest_update_at_desc,title_asc,dataset_id_asc",
    });

    const element = await CatalogPage({ searchParams: Promise.resolve({ page: "4" }) });
    const markup = renderMarkup(element);

    expect(markup).toContain('data-testid="discovery-empty-state"');
    expect(markup).toContain("No datasets match the selected filters.");
  });

  it("keeps error state behavior stable with explicit page query", async () => {
    vi.spyOn(discoveryClient, "fetchDatasetCatalog").mockRejectedValue(new Error("unavailable"));

    const element = await CatalogPage({ searchParams: Promise.resolve({ page: "5" }) });
    const markup = renderMarkup(element);

    expect(markup).toContain('data-testid="discovery-error-state"');
    expect(markup).toContain("Unable to load data. Please try again.");
  });

  it("requests server-side filtered and sorted catalog data", async () => {
    const catalogSpy = vi.spyOn(discoveryClient, "fetchDatasetCatalog").mockResolvedValue({
      items: [
        {
          dataset_id: "EIA.GAS.CO",
          source: { id: "eia", name: "EIA" },
          title: "Regular All Formulations Retail Gasoline Prices - Colorado",
          description: "Weekly EIA retail regular gasoline prices for Colorado.",
          geographic_scope: "Colorado",
          topic_tags: ["energy", "gasoline"],
          latest_update_at: "2026-03-24T00:00:00Z",
        },
      ],
      groups: null,
      aggregations: {
        total_dataset_count: 14282,
        sources: [{ source: { id: "eia", name: "EIA" }, dataset_count: 1 }],
        categories: [{ value: "energy", dataset_count: 1 }],
      },
      page: 1,
      page_size: 20,
      total_items: 1,
      total_pages: 1,
      sort: "title_asc,dataset_id_asc",
    });

    await CatalogPage({
      searchParams: Promise.resolve({ source: "eia", category: "energy", sort: "title_asc" }),
    });

    expect(catalogSpy).toHaveBeenCalledWith({
      page: 1,
      source: "eia",
      category: "energy",
      sort: "title_asc",
    });
  });

  it("starts from page one even when a page query is present", async () => {
    const catalogSpy = vi.spyOn(discoveryClient, "fetchDatasetCatalog").mockResolvedValue({
      items: [CATALOG_ITEMS[0] as DatasetSummary],
      groups: null,
      aggregations: {
        total_dataset_count: 14282,
        sources: [{ source: { id: "eia", name: "EIA" }, dataset_count: 1 }],
        categories: [{ value: "energy", dataset_count: 1 }],
      },
      page: 1,
      page_size: 20,
      total_items: 1,
      total_pages: 1,
      sort: "latest_update_at_desc,title_asc,dataset_id_asc",
    });

    const element = await CatalogPage({ searchParams: Promise.resolve({ page: "3" }) });
    const markup = renderMarkup(element);

    expect(catalogSpy).toHaveBeenCalledWith({
      page: 1,
      source: undefined,
      category: undefined,
      sort: "recency",
    });
    expect(markup).not.toContain('data-testid="discovery-pagination"');
  });

  it("falls back to page one when the page query is invalid", async () => {
    const catalogSpy = vi.spyOn(discoveryClient, "fetchDatasetCatalog").mockResolvedValue({
      items: [CATALOG_ITEMS[0] as DatasetSummary],
      groups: null,
      aggregations: {
        total_dataset_count: 14282,
        sources: [{ source: { id: "eia", name: "EIA" }, dataset_count: 1 }],
        categories: [{ value: "energy", dataset_count: 1 }],
      },
      page: 1,
      page_size: 20,
      total_items: 1,
      total_pages: 1,
      sort: "latest_update_at_desc,title_asc,dataset_id_asc",
    });

    await CatalogPage({ searchParams: Promise.resolve({ page: "invalid" }) });

    expect(catalogSpy).toHaveBeenCalledWith({
      page: 1,
      source: undefined,
      category: undefined,
      sort: "recency",
    });
  });

  it("treats all filter sentinels as unset request params", async () => {
    const catalogSpy = vi.spyOn(discoveryClient, "fetchDatasetCatalog").mockResolvedValue({
      items: [CATALOG_ITEMS[0] as DatasetSummary],
      groups: null,
      aggregations: {
        total_dataset_count: 14282,
        sources: [{ source: { id: "eia", name: "EIA" }, dataset_count: 1 }],
        categories: [{ value: "energy", dataset_count: 1 }],
      },
      page: 1,
      page_size: 20,
      total_items: 1,
      total_pages: 1,
      sort: "latest_update_at_desc,title_asc,dataset_id_asc",
    });

    await CatalogPage({
      searchParams: Promise.resolve({ source: "all", category: " all ", sort: "recency" }),
    });

    expect(catalogSpy).toHaveBeenCalledWith({
      page: 1,
      source: undefined,
      category: undefined,
      sort: "recency",
    });
  });
});
