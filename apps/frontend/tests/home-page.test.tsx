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
          description: "Policy rate update",
          geographic_scope: "US",
          topic_tags: ["rates", "monetary policy"],
          latest_update_at: "2026-02-01T00:00:00Z",
          action_links: {
            view_table_href: "/datasets/FEDFUNDS",
            download_csv_href: "/api/datasets/FEDFUNDS.csv",
          },
        },
      ],
      limit: 5,
      sort: "latest_update_at_desc",
    });
    vi.spyOn(discoveryClient, "fetchSearchSummary").mockResolvedValue({
      active_dataset_count: 48,
      active_source_count: 3,
      generated_at: "2026-03-24T00:00:00Z",
    });

    const element = await HomePage({ searchParams: Promise.resolve({}) });
    const markup = renderMarkup(element);

    expect(markup).toContain("Search datasets");
    expect(markup).toContain('data-testid="dataset-search-hero"');
    expect(markup).toContain("Searching 48 active datasets from 3 sources.");
    expect(markup).toContain('data-testid="home-content"');
    expect(markup).toContain("shell-content-constrained");
    expect(markup).toContain('data-testid="recent-updates-feed"');
    expect(markup).toContain("Federal Funds Effective Rate");
    expect(markup).toContain('href="/datasets/FEDFUNDS"');
    expect(markup).not.toContain("Download CSV");
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
    expect(markup).toContain('data-testid="shell-footer"');
    expect(markup).toContain("shell-region-full-width");
    expect(markup).toContain('data-testid="footer-content-container"');
    expect(markup).toContain('data-testid="footer-brand"');
    expect(markup).toContain('data-testid="footer-mission"');
    expect(markup).toContain("Longtail");
    expect(markup).toContain(
      "An editorial archive of time series data across sources, topics, and geographies.",
    );
    expect(markup).toContain("shell-footer-content");
    expect(markup).toContain("shell-footer-brand");
    expect(markup).toContain("shell-footer-mission");
    expect(markup).toContain('data-testid="footer-content-container"');
    expect(markup).not.toContain('data-testid="footer-utility-links"');
  });

  it("keeps homepage as search entry only when q is present", async () => {
    vi.spyOn(discoveryClient, "fetchRecentDatasets").mockResolvedValue({
      items: [],
      limit: 5,
      sort: "latest_update_at_desc",
    });
    const searchSpy = vi.spyOn(discoveryClient, "fetchDatasetSearch");
    vi.spyOn(discoveryClient, "fetchSearchSummary").mockResolvedValue({
      active_dataset_count: 48,
      active_source_count: 3,
      generated_at: "2026-03-24T00:00:00Z",
    });

    const element = await HomePage({ searchParams: Promise.resolve({ q: "unemployment" }) });
    const markup = renderMarkup(element);

    expect(searchSpy).not.toHaveBeenCalled();
    expect(markup).not.toContain('data-testid="dataset-search-results"');
    expect(markup).toContain("shell-content-constrained");
    expect(markup).toContain('value="unemployment"');
    expect(markup).toContain('data-testid="footer-brand"');
  });

  it("renders error state when backend requests fail", async () => {
    vi.spyOn(discoveryClient, "fetchRecentDatasets").mockRejectedValue(new Error("down"));
    vi.spyOn(discoveryClient, "fetchSearchSummary").mockResolvedValue({
      active_dataset_count: 48,
      active_source_count: 3,
      generated_at: "2026-03-24T00:00:00Z",
    });
    const element = await HomePage({ searchParams: Promise.resolve({ q: "rates" }) });
    const markup = renderMarkup(element);

    expect(markup).toContain("Recent updates are temporarily unavailable.");
    expect(markup).toContain("shell-content-constrained");
    expect(markup).toContain('data-testid="footer-content-container"');
    expect(markup).toContain("shell-footer-mission");
  });
});
