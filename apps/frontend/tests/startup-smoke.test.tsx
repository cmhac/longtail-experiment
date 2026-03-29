import React from "react";
import { describe, expect, it, vi } from "vitest";
import HomePage from "../src/app/page";
import * as discoveryClient from "../src/lib/api/discovery-client";
import { renderMarkup } from "./test-utils";

vi.mock("next/navigation", () => ({
  usePathname: () => "/",
  useRouter: () => ({ push: () => undefined }),
  useSearchParams: () => new URLSearchParams(),
}));

const renderHomePage = async (): Promise<string> => {
  vi.spyOn(discoveryClient, "fetchRecentDatasets").mockResolvedValue({
    items: [],
    limit: 5,
    sort: "latest_update_at_desc",
  });

  const element = await HomePage({ searchParams: Promise.resolve({}) });
  return renderMarkup(element);
};

describe("frontend shell startup", () => {
  it("renders root shell without runtime errors", async () => {
    const markup = await renderHomePage();

    expect(markup).toContain('data-testid="site-shell"');
    expect(markup).toContain('data-testid="navbar-brand-link"');
    expect(markup).toContain("Longtail");
  });

  it("renders required header, home content, and footer regions", async () => {
    const markup = await renderHomePage();

    expect(markup).toContain('data-testid="shell-header"');
    expect(markup).toContain('data-testid="home-content"');
    expect(markup).toContain('data-testid="shell-footer"');
    expect(markup).toContain('data-testid="footer-content-container"');
    expect(markup).toContain('data-testid="footer-brand"');
    expect(markup).toContain('data-testid="footer-mission"');
    expect(markup).toContain("shell-footer-content");
    expect(markup).toContain("Longtail");
  });
});
