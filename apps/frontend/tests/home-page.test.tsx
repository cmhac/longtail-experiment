import { describe, expect, it, vi } from "vitest";
import HomePage from "../src/app/page";
import * as discoveryClient from "../src/lib/api/discovery-client";
import { renderMarkup } from "./test-utils";

vi.mock("next/navigation", () => ({
  usePathname: () => "/",
  useRouter: () => ({ push: () => undefined }),
  useSearchParams: () => new URLSearchParams(),
}));

describe("home page", () => {
  it("renders search box and recent updates when query is absent", async () => {
    vi.spyOn(discoveryClient, "fetchRecentDatasets").mockResolvedValue({
      items: [
        {
          dataset_id: "FEDFUNDS",
          source: { id: "fred", name: "FRED" },
          title: "Federal Funds Effective Rate",
          latest_update_at: "2026-02-01T00:00:00Z",
        },
      ],
      limit: 5,
      sort: "latest_update_at_desc",
    });
    vi.spyOn(discoveryClient, "fetchDatasetSearch").mockResolvedValue({
      items: [],
      page: 1,
      page_size: 20,
      total_items: 0,
      total_pages: 0,
      sort: "latest_update_at_desc",
    });

    const element = await HomePage({ searchParams: Promise.resolve({}) });
    const markup = renderMarkup(element);

    expect(markup).toContain("Search datasets");
    expect(markup).toContain('data-testid="recent-updates-feed"');
    expect(markup).toContain("Federal Funds Effective Rate");
    expect(markup).toContain('data-testid="navbar-brand-link"');
    expect(markup).toContain('data-testid="navbar-tab-home"');
    expect(markup).toContain('data-testid="navbar-tab-datasets"');
    expect(markup).toContain('data-testid="navbar-tab-trends"');
    expect(markup).toContain('data-testid="navbar-search-control"');
    expect(markup).toContain('data-testid="navbar-profile-control"');
    expect(markup).toContain('data-testid="navbar-brand-link"');
    expect(markup).toContain('data-testid="navbar-tab-home" href="/"');
    expect(markup).toContain('data-testid="navbar-tab-datasets"');
    expect(markup).toContain('data-testid="navbar-tab-trends"');
    expect(markup).toContain('data-testid="navbar-search-control"');
    expect(markup).toContain('aria-label="Search"');
    expect(markup).toContain('disabled=""');
  });

  it("renders search results when q is present", async () => {
    vi.spyOn(discoveryClient, "fetchRecentDatasets").mockResolvedValue({
      items: [],
      limit: 5,
      sort: "latest_update_at_desc",
    });
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
      total_items: 1,
      total_pages: 1,
      sort: "latest_update_at_desc",
    });

    const element = await HomePage({ searchParams: Promise.resolve({ q: "unemployment" }) });
    const markup = renderMarkup(element);

    expect(searchSpy).toHaveBeenCalledWith({ q: "unemployment" });
    expect(markup).toContain('data-testid="dataset-search-results"');
    expect(markup).toContain("Unemployment Rate");
  });

  it("renders error state when backend requests fail", async () => {
    vi.spyOn(discoveryClient, "fetchRecentDatasets").mockRejectedValue(new Error("down"));

    const element = await HomePage({ searchParams: Promise.resolve({}) });
    const markup = renderMarkup(element);

    expect(markup).toContain("Unable to load data. Please try again.");
  });
});
