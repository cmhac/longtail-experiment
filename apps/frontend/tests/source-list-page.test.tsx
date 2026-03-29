import { describe, expect, it, vi } from "vitest";

import SourceListPage from "../src/app/sources/page";
import * as discoveryClient from "../src/lib/api/discovery-client";
import { buildSourceListFixture } from "./fixtures/source-discovery-fixtures";
import { renderMarkup } from "./test-utils";

vi.mock("next/navigation", () => ({
  usePathname: () => "/sources",
  useRouter: () => ({ replace: () => undefined, push: () => undefined }),
  useSearchParams: () => new URLSearchParams(),
}));

describe("source list page", () => {
  it("renders all sources with counts and links", async () => {
    vi.spyOn(discoveryClient, "fetchSourceList").mockResolvedValue(buildSourceListFixture());

    const element = await SourceListPage();
    const markup = renderMarkup(element);

    expect(markup).toContain("Sources");
    expect(markup).toContain('data-testid="source-list-page"');
    expect(markup).toContain("page-header-wrapper");
    expect(markup).toContain('data-testid="source-catalog-list"');
    expect(markup).toContain("FRED");
    expect(markup).toContain("2 datasets");
    expect(markup).toContain('href="/sources/fred"');
  });

  it("renders explicit empty state when no sources are available", async () => {
    vi.spyOn(discoveryClient, "fetchSourceList").mockResolvedValue({
      items: [],
      total_items: 0,
      sort: "source_name_asc,source_id_asc",
    });

    const element = await SourceListPage();
    const markup = renderMarkup(element);

    expect(markup).toContain("No sources are available.");
    expect(markup).toContain('data-testid="discovery-empty-state"');
  });

  it("renders generic error state when source list fetch fails", async () => {
    vi.spyOn(discoveryClient, "fetchSourceList").mockRejectedValue(new Error("down"));

    const element = await SourceListPage();
    const markup = renderMarkup(element);

    expect(markup).toContain("Unable to load data. Please try again.");
    expect(markup).toContain('data-testid="discovery-error-state"');
  });
});
