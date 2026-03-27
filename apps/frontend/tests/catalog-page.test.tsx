import { describe, expect, it, vi } from "vitest";
import CatalogPage from "../src/app/datasets/page";
import * as discoveryClient from "../src/lib/api/discovery-client";
import { renderMarkup } from "./test-utils";

vi.mock("next/navigation", () => ({
  usePathname: () => "/datasets",
  useRouter: () => ({ replace: () => undefined }),
  useSearchParams: () => new URLSearchParams(),
}));

describe("catalog page", () => {
  it("renders list controls and catalog list from API response", async () => {
    const catalogSpy = vi.spyOn(discoveryClient, "fetchDatasetCatalog").mockResolvedValue({
      items: [
        {
          dataset_id: "UNRATE",
          source: { id: "fred", name: "FRED" },
          title: "Unemployment Rate",
          description: null,
          geographic_scope: "US",
          topic_tags: [],
          latest_update_at: "2026-02-01T00:00:00Z",
        },
      ],
      groups: null,
      aggregations: {
        total_dataset_count: 1,
        sources: [{ source: { id: "fred", name: "FRED" }, dataset_count: 1 }],
        categories: [],
      },
      page: 1,
      page_size: 20,
      total_items: 1,
      total_pages: 1,
      sort: "latest_update_at_desc",
    });

    const element = await CatalogPage({ searchParams: Promise.resolve({}) });
    const markup = renderMarkup(element);

    expect(catalogSpy).toHaveBeenCalledWith({
      page: 1,
      source: undefined,
      category: undefined,
      sort: "recency",
    });
    expect(markup).toContain('data-testid="catalog-page"');
    expect(markup).toContain("shell-content-constrained");
    expect(markup).toContain('data-testid="dataset-list-controls"');
    expect(markup).toContain('data-testid="unified-dataset-row"');
    expect(markup).not.toContain('data-testid="discovery-pagination"');
    expect(markup).not.toContain('data-testid="request-new-dataset-cta"');
    expect(markup).toContain("Unemployment Rate");
  });

  it("applies source/category filtering from URL parameters", async () => {
    const catalogSpy = vi.spyOn(discoveryClient, "fetchDatasetCatalog").mockResolvedValue({
      items: [
        {
          dataset_id: "DCOILWTICO",
          source: { id: "eia", name: "EIA" },
          title: "Crude Oil Prices",
          description: null,
          geographic_scope: "US",
          topic_tags: ["energy"],
          latest_update_at: "2026-02-02T00:00:00Z",
        },
      ],
      groups: null,
      aggregations: {
        total_dataset_count: 2,
        sources: [
          { source: { id: "eia", name: "EIA" }, dataset_count: 1 },
          { source: { id: "fred", name: "FRED" }, dataset_count: 1 },
        ],
        categories: [
          { value: "energy", dataset_count: 1 },
          { value: "labor", dataset_count: 1 },
        ],
      },
      page: 1,
      page_size: 20,
      total_items: 1,
      total_pages: 1,
      sort: "latest_update_at_desc",
    });

    const element = await CatalogPage({
      searchParams: Promise.resolve({ source: "eia", category: "energy" }),
    });
    const markup = renderMarkup(element);

    expect(catalogSpy).toHaveBeenCalledWith({
      page: 1,
      source: "eia",
      category: "energy",
      sort: "recency",
    });
    expect(markup).toContain("shell-content-constrained");
    expect(markup).toContain("2 total series");
    expect(markup).toContain("Crude Oil Prices");
    expect(markup).not.toContain("Unemployment Rate");
    expect(markup).not.toContain('data-testid="discovery-pagination"');
  });

  it("renders error state when fetch fails", async () => {
    vi.spyOn(discoveryClient, "fetchDatasetCatalog").mockRejectedValue(new Error("down"));

    const element = await CatalogPage({ searchParams: Promise.resolve({}) });
    const markup = renderMarkup(element);

    expect(markup).toContain("shell-content-constrained");
    expect(markup).toContain("Unable to load data. Please try again.");
  });

  it("keeps sort/filter aligned in requests", async () => {
    const catalogSpy = vi.spyOn(discoveryClient, "fetchDatasetCatalog").mockResolvedValue({
      items: [],
      groups: null,
      aggregations: {
        total_dataset_count: 2,
        sources: [
          { source: { id: "eia", name: "EIA" }, dataset_count: 1 },
          { source: { id: "fred", name: "FRED" }, dataset_count: 1 },
        ],
        categories: [{ value: "energy", dataset_count: 1 }],
      },
      page: 1,
      page_size: 20,
      total_items: 0,
      total_pages: 1,
      sort: "title_desc,dataset_id_desc",
    });

    await CatalogPage({
      searchParams: Promise.resolve({
        source: "eia",
        category: "energy",
        sort: "title_desc",
      }),
    });

    expect(catalogSpy).toHaveBeenCalledWith({
      page: 1,
      source: "eia",
      category: "energy",
      sort: "title_desc",
    });
  });

  it("boots with first page and renders infinite-scroll sentinel", async () => {
    const catalogSpy = vi.spyOn(discoveryClient, "fetchDatasetCatalog").mockResolvedValue({
      items: [
        {
          dataset_id: "PAGE1",
          source: { id: "fred", name: "FRED" },
          title: "Page One Dataset",
          description: null,
          geographic_scope: "US",
          topic_tags: [],
          latest_update_at: "2026-02-01T00:00:00Z",
        },
      ],
      groups: null,
      aggregations: {
        total_dataset_count: 2,
        sources: [{ source: { id: "fred", name: "FRED" }, dataset_count: 2 }],
        categories: [],
      },
      page: 1,
      page_size: 20,
      total_items: 2,
      total_pages: 2,
      sort: "latest_update_at_desc",
    });

    const element = await CatalogPage({ searchParams: Promise.resolve({}) });
    const markup = renderMarkup(element);

    expect(catalogSpy).toHaveBeenCalledTimes(1);
    expect(markup).toContain("Page One Dataset");
    expect(markup).toContain('data-testid="infinite-scroll-sentinel"');
  });
});
