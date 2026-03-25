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
    page: 1,
    page_size: 20,
    total_items: 14282,
    total_pages: 715,
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
    expect(markup).toContain("TOTAL SERIES: 14,282");
    expect(markup).toContain('data-testid="dataset-source-filter"');
    expect(markup).toContain('data-testid="dataset-category-filter"');
    expect(markup).toContain('data-testid="dataset-sort-control"');
    expect(markup).not.toContain('data-testid="request-new-dataset-cta"');
  });

  it("preserves catalog-total summary when source/category filters are applied", async () => {
    mockCatalogResponse();

    const element = await CatalogPage({
      searchParams: Promise.resolve({ source: "eia", category: "energy" }),
    });
    const markup = renderMarkup(element);

    expect(markup).toContain("TOTAL SERIES: 14,282");
    expect(markup).toContain("Regular All Formulations Retail Gasoline Prices - Colorado");
    expect(markup).not.toContain("Consumer Price Index (CPI-U)");
  });

  it("sorts by title when title_asc sort mode is selected", async () => {
    mockCatalogResponse();

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

  it("sorts by title descending when title_desc sort mode is selected", async () => {
    mockCatalogResponse();

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
    mockCatalogResponse();

    const element = await CatalogPage({
      searchParams: Promise.resolve({ sort: "unsupported-sort" }),
    });
    const markup = renderMarkup(element);

    const gasIndex = markup.indexOf("Regular All Formulations Retail Gasoline Prices - Colorado");
    const cpiIndex = markup.indexOf("Consumer Price Index (CPI-U)");

    expect(gasIndex).toBeLessThan(cpiIndex);
  });

  it("handles invalid timestamps by prioritizing datasets with valid dates", async () => {
    vi.spyOn(discoveryClient, "fetchDatasetCatalog").mockResolvedValue({
      items: [
        {
          dataset_id: "INVALID_DATE",
          source: { id: "fred", name: "FRED" },
          title: "Invalid Date Dataset",
          description: null,
          geographic_scope: "US",
          topic_tags: ["rates"],
          latest_update_at: "not-a-date",
        },
        {
          dataset_id: "VALID_DATE",
          source: { id: "fred", name: "FRED" },
          title: "Valid Date Dataset",
          description: null,
          geographic_scope: "US",
          topic_tags: ["rates"],
          latest_update_at: "2026-03-22T00:00:00Z",
        },
      ],
      groups: null,
      page: 1,
      page_size: 20,
      total_items: 2,
      total_pages: 1,
      sort: "latest_update_at_desc",
    });

    const element = await CatalogPage({ searchParams: Promise.resolve({}) });
    const markup = renderMarkup(element);

    const validIndex = markup.indexOf("Valid Date Dataset");
    const invalidIndex = markup.indexOf("Invalid Date Dataset");

    expect(validIndex).toBeLessThan(invalidIndex);
  });

  it("uses title tie-breaker when recency timestamps are equal", async () => {
    vi.spyOn(discoveryClient, "fetchDatasetCatalog").mockResolvedValue({
      items: [
        {
          dataset_id: "ZETA",
          source: { id: "fred", name: "FRED" },
          title: "Zeta Dataset",
          description: null,
          geographic_scope: "US",
          topic_tags: ["rates"],
          latest_update_at: "2026-03-20T00:00:00Z",
        },
        {
          dataset_id: "ALPHA",
          source: { id: "fred", name: "FRED" },
          title: "Alpha Dataset",
          description: null,
          geographic_scope: "US",
          topic_tags: ["rates"],
          latest_update_at: "2026-03-20T00:00:00Z",
        },
      ],
      groups: null,
      page: 1,
      page_size: 20,
      total_items: 2,
      total_pages: 1,
      sort: "latest_update_at_desc",
    });

    const element = await CatalogPage({ searchParams: Promise.resolve({}) });
    const markup = renderMarkup(element);

    const alphaIndex = markup.indexOf("Alpha Dataset");
    const zetaIndex = markup.indexOf("Zeta Dataset");

    expect(alphaIndex).toBeLessThan(zetaIndex);
  });

  it("renders explicit empty-results state for no-match filters", async () => {
    mockCatalogResponse();

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

  it("renders fallback state when catalog request fails", async () => {
    vi.spyOn(discoveryClient, "fetchDatasetCatalog").mockRejectedValue(new Error("unavailable"));

    const element = await CatalogPage({ searchParams: Promise.resolve({}) });
    const markup = renderMarkup(element);

    expect(markup).toContain("Unable to load data. Please try again.");
    expect(markup).not.toContain('data-testid="request-new-dataset-cta"');
  });
});
