import React from "react";
import { describe, expect, it, vi } from "vitest";
import HomePage from "../src/app/page";
import * as discoveryClient from "../src/lib/api/discovery-client";
import { SITE_FOOTER_VARIANT } from "../src/shell/site-footer";
import { SITE_HEADER_VARIANT } from "../src/shell/site-header";
import {
  FORBIDDEN_ACCENT_VARIANTS,
  isMonochromeVariantAllowed,
} from "../src/theme/monochrome-theme";
import { renderMarkup } from "./test-utils";

vi.mock("next/navigation", () => ({
  usePathname: () => "/",
  useRouter: () => ({ push: () => undefined }),
  useSearchParams: () => new URLSearchParams(),
}));

const renderHomePage = async (): Promise<string> => {
  vi.spyOn(discoveryClient, "fetchRecentDatasets").mockResolvedValue({
    items: [
      {
        dataset_id: "FEDFUNDS",
        source: { id: "fred", name: "FRED" },
        title: "Federal Funds Effective Rate",
        description: "Policy rate",
        geographic_scope: "US",
        topic_tags: ["rates", "policy"],
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
  return renderMarkup(element);
};

describe("shell structure and monochrome contract", () => {
  it("asserts header region presence and semantics", async () => {
    const markup = await renderHomePage();

    expect(markup).toContain("<header");
    expect(markup).toContain('data-shell-region="header"');
    expect(markup).toContain('data-testid="shell-header"');
    expect(markup).toContain('data-testid="navbar-container"');
    expect(markup).toContain('aria-label="Primary"');
  });

  it("asserts navbar contains brand, tabs, and utility controls", async () => {
    const markup = await renderHomePage();

    expect(markup).toContain('data-testid="navbar-brand-link"');
    expect(markup).toContain("Longtail");
    expect(markup).toContain('data-testid="navbar-tab-home"');
    expect(markup).toContain('data-testid="navbar-tab-datasets"');
    expect(markup).toContain('data-testid="navbar-tab-trends"');
    expect(markup).toContain('data-testid="navbar-search-control"');
    expect(markup).toContain('data-testid="navbar-profile-control"');
  });

  it("asserts main discovery region presence and text", async () => {
    const markup = await renderHomePage();

    expect(markup).toContain("<main");
    expect(markup).toContain('data-testid="home-content"');
    expect(markup).toContain('data-testid="dataset-search-hero"');
    expect(markup).toContain('class="search-hero"');
    expect(markup).toContain('data-testid="dataset-search-input-wrap"');
    expect(markup).toContain("Search datasets");
    expect(markup).toContain("Searching 48 active datasets from 3 sources.");
    expect(markup).toContain("Recent Updates");
  });

  it("asserts footer region presence and ordering", async () => {
    const markup = await renderHomePage();
    const headerIndex = markup.indexOf('data-shell-region="header"');
    const mainIndex = markup.indexOf('data-testid="home-content"');
    const footerIndex = markup.indexOf('data-shell-region="footer"');

    expect(markup).toContain("<footer");
    expect(markup).toContain('data-testid="shell-footer"');
    expect(headerIndex).toBeGreaterThan(-1);
    expect(mainIndex).toBeGreaterThan(headerIndex);
    expect(footerIndex).toBeGreaterThan(mainIndex);
  });

  it("asserts shell remains structurally valid during page scroll", async () => {
    const markup = await renderHomePage();

    expect(markup).toContain('class="shell-page shell-scroll-anchor"');
    expect(markup).toContain("Baseline shell footer for release readiness.");
  });

  it("asserts header uses monochrome classes and tokens only", async () => {
    const markup = await renderHomePage();

    expect(markup).toContain('data-shell-region="header"');
    expect(markup).toContain("shell-monochrome");
    expect(isMonochromeVariantAllowed(SITE_HEADER_VARIANT)).toBe(true);
  });

  it("asserts main content remains monochrome-compatible", async () => {
    const markup = await renderHomePage();

    expect(markup).toContain('data-testid="home-content"');
    expect(markup).toContain("shell-monochrome");
  });

  it("asserts footer uses monochrome classes and tokens only", async () => {
    const markup = await renderHomePage();

    expect(markup).toContain('data-shell-region="footer"');
    expect(markup).toContain("shell-monochrome");
    expect(isMonochromeVariantAllowed(SITE_FOOTER_VARIANT)).toBe(true);
  });

  it("rejects accent variant usage in shell components", () => {
    for (const variant of FORBIDDEN_ACCENT_VARIANTS) {
      expect(isMonochromeVariantAllowed(variant)).toBe(false);
    }
  });

  it("asserts navbar order remains brand then tabs then utility", async () => {
    const markup = await renderHomePage();
    const brandIndex = markup.indexOf('data-testid="navbar-brand-link"');
    const tabsIndex = markup.indexOf('data-testid="navbar-tab-home"');
    const utilityIndex = markup.indexOf('data-testid="navbar-search-control"');

    expect(brandIndex).toBeGreaterThan(-1);
    expect(tabsIndex).toBeGreaterThan(brandIndex);
    expect(utilityIndex).toBeGreaterThan(tabsIndex);
  });
});
