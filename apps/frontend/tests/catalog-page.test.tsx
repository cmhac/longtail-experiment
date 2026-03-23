import { describe, expect, it, vi } from "vitest";
import CatalogPage from "../src/app/datasets/page";
import * as discoveryClient from "../src/lib/api/discovery-client";
import { renderMarkup } from "./test-utils";

vi.mock("next/navigation", () => ({
  usePathname: () => "/datasets",
  useRouter: () => ({ push: () => undefined }),
  useSearchParams: () => new URLSearchParams(),
}));

describe("catalog page", () => {
  it("renders search controls and catalog list from API response", async () => {
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
      groups: [],
      page: 1,
      page_size: 20,
      total_items: 1,
      total_pages: 1,
      sort: "source_name_asc",
    });

    const element = await CatalogPage({ searchParams: Promise.resolve({ q: "rate" }) });
    const markup = renderMarkup(element);

    expect(catalogSpy).toHaveBeenCalledWith({ groupBySource: false, q: "rate" });
    expect(markup).toContain('data-testid="catalog-page"');
    expect(markup).toContain('data-testid="group-by-source-toggle"');
    expect(markup).toContain("Unemployment Rate");
  });

  it("passes group_by_source=true in grouped mode", async () => {
    const catalogSpy = vi.spyOn(discoveryClient, "fetchDatasetCatalog").mockResolvedValue({
      items: [],
      groups: [],
      page: 1,
      page_size: 20,
      total_items: 0,
      total_pages: 0,
      sort: "source_name_asc",
    });

    await CatalogPage({ searchParams: Promise.resolve({ group: "source" }) });

    expect(catalogSpy).toHaveBeenCalledWith({ groupBySource: true, q: undefined });
  });

  it("renders error state when fetch fails", async () => {
    vi.spyOn(discoveryClient, "fetchDatasetCatalog").mockRejectedValue(new Error("down"));

    const element = await CatalogPage({ searchParams: Promise.resolve({}) });
    const markup = renderMarkup(element);

    expect(markup).toContain("Unable to load data. Please try again.");
  });
});
