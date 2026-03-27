import { describe, expect, it, vi } from "vitest";

import SearchPage from "../src/app/search/page";
import * as discoveryClient from "../src/lib/api/discovery-client";
import { renderMarkup } from "./test-utils";

vi.mock("next/navigation", () => ({
  usePathname: () => "/search",
  useRouter: () => ({ push: () => undefined }),
  useSearchParams: () => new URLSearchParams(),
}));

describe("search page", () => {
  it("renders idle state when query is absent", async () => {
    const searchSpy = vi.spyOn(discoveryClient, "fetchDatasetSearch");
    vi.spyOn(discoveryClient, "fetchSearchSummary").mockResolvedValue({
      active_dataset_count: 48,
      active_source_count: 3,
      generated_at: "2026-03-24T00:00:00Z",
    });

    const element = await SearchPage({ searchParams: Promise.resolve({}) });
    const markup = renderMarkup(element);

    expect(searchSpy).not.toHaveBeenCalled();
    expect(markup).toContain('data-testid="search-page-content"');
    expect(markup).toContain("Enter a query to search datasets.");
    expect(markup).toContain('data-testid="dataset-search-summary"');
  });

  it("renders dataset results when query is present", async () => {
    const searchSpy = vi.spyOn(discoveryClient, "fetchDatasetSearch").mockResolvedValue({
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
      page: 2,
      page_size: 20,
      total_items: 25,
      total_pages: 2,
      sort: "latest_update_at_desc",
    });
    vi.spyOn(discoveryClient, "fetchSearchSummary").mockResolvedValue({
      active_dataset_count: 48,
      active_source_count: 3,
      generated_at: "2026-03-24T00:00:00Z",
    });

    const element = await SearchPage({
      searchParams: Promise.resolve({ q: "unemployment", page: "2" }),
    });
    const markup = renderMarkup(element);

    expect(searchSpy).toHaveBeenCalledWith({ q: "unemployment", page: 1 });
    expect(markup).toContain('data-testid="dataset-search-results"');
    expect(markup).toContain("Unemployment Rate");
    expect(markup).not.toContain('data-testid="discovery-pagination"');
  });

  it("renders error state when search request fails", async () => {
    vi.spyOn(discoveryClient, "fetchSearchSummary").mockResolvedValue({
      active_dataset_count: 48,
      active_source_count: 3,
      generated_at: "2026-03-24T00:00:00Z",
    });
    vi.spyOn(discoveryClient, "fetchDatasetSearch").mockRejectedValue(new Error("search down"));

    const element = await SearchPage({ searchParams: Promise.resolve({ q: "rates" }) });
    const markup = renderMarkup(element);

    expect(markup).toContain("Search is temporarily unavailable. Please try again.");
    expect(markup).toContain('data-testid="discovery-error-state"');
  });

  it("ignores explicit page query and starts from page one", async () => {
    const searchSpy = vi.spyOn(discoveryClient, "fetchDatasetSearch").mockResolvedValue({
      items: [],
      page: 1,
      page_size: 20,
      total_items: 0,
      total_pages: 0,
      sort: "latest_update_at_desc",
    });
    vi.spyOn(discoveryClient, "fetchSearchSummary").mockResolvedValue({
      active_dataset_count: 48,
      active_source_count: 3,
      generated_at: "2026-03-24T00:00:00Z",
    });

    await SearchPage({ searchParams: Promise.resolve({ q: "rates", page: "2" }) });

    expect(searchSpy).toHaveBeenCalledWith({ q: "rates", page: 1 });
  });

  it("continues rendering when search summary fetch fails", async () => {
    vi.spyOn(discoveryClient, "fetchSearchSummary").mockRejectedValue(new Error("summary down"));
    vi.spyOn(discoveryClient, "fetchDatasetSearch").mockResolvedValue({
      items: [],
      page: 1,
      page_size: 20,
      total_items: 0,
      total_pages: 0,
      sort: "latest_update_at_desc",
    });

    const element = await SearchPage({ searchParams: Promise.resolve({ q: "rates" }) });
    const markup = renderMarkup(element);

    expect(markup).toContain('data-testid="dataset-search-form"');
    expect(markup).not.toContain("Searching 48 active datasets from 3 sources.");
  });

  it("boots search results from first page and renders infinite sentinel", async () => {
    const searchSpy = vi.spyOn(discoveryClient, "fetchDatasetSearch").mockResolvedValue({
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
      page: 1,
      page_size: 20,
      total_items: 2,
      total_pages: 2,
      sort: "latest_update_at_desc",
    });
    vi.spyOn(discoveryClient, "fetchSearchSummary").mockResolvedValue({
      active_dataset_count: 48,
      active_source_count: 3,
      generated_at: "2026-03-24T00:00:00Z",
    });

    const element = await SearchPage({ searchParams: Promise.resolve({ q: "rate" }) });
    const markup = renderMarkup(element);

    expect(searchSpy).toHaveBeenCalledTimes(1);
    expect(markup).toContain("Unemployment Rate");
    expect(markup).toContain('data-testid="infinite-search-sentinel"');
  });
});
