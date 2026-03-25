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
    vi.spyOn(discoveryClient, "fetchSearchSummary").mockResolvedValue({
      active_dataset_count: 48,
      active_source_count: 3,
      generated_at: "2026-03-24T00:00:00Z",
    });
    vi.spyOn(discoveryClient, "fetchDatasetSearch").mockResolvedValue({
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
      total_items: 1,
      total_pages: 1,
      sort: "latest_update_at_desc",
    });

    const element = await SearchPage({ searchParams: Promise.resolve({ q: "unemployment" }) });
    const markup = renderMarkup(element);

    expect(markup).toContain('data-testid="dataset-search-results"');
    expect(markup).toContain("Unemployment Rate");
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
});
