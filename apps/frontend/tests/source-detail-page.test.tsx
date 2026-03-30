import React from "react";
import { afterEach, describe, expect, it, vi } from "vitest";

import SourceNotFoundPage from "../src/app/sources/[sourceId]/not-found";
import SourceDetailPage from "../src/app/sources/[sourceId]/page";
import * as discoveryClient from "../src/lib/api/discovery-client";
import { buildSourceDetailFixture } from "./fixtures/source-discovery-fixtures";
import { renderMarkup } from "./test-utils";

const notFoundMock = vi.fn(() => {
  throw new Error("NOT_FOUND");
});

vi.mock("next/navigation", () => ({
  notFound: () => notFoundMock(),
}));

afterEach(() => {
  notFoundMock.mockClear();
});

describe("source detail page", () => {
  it("renders source context and only matching datasets", async () => {
    const detailSpy = vi
      .spyOn(discoveryClient, "fetchSourceDetail")
      .mockResolvedValue(buildSourceDetailFixture());

    const element = await SourceDetailPage({
      params: Promise.resolve({ sourceId: "fred" }),
    });
    const markup = renderMarkup(element);

    expect(detailSpy).toHaveBeenCalledWith("fred", { page: 1 });
    expect(markup).toContain("Federal Reserve Economic Data");
    expect(markup).toContain("Economic time series published by the St. Louis Fed.");
    expect(markup).toContain("2 total datasets");
    expect(markup).toContain('data-testid="source-detail-page"');
    expect(markup).toContain('data-testid="source-detail-header"');
    expect(markup).toContain("page-header-wrapper");
    expect(markup).toContain('data-testid="catalog-flat-list"');
    expect(markup).toContain("Consumer Price Index");
    expect(markup).toContain('href="/datasets/CPIAUCSL"');
    expect(markup).toContain('data-testid="discovery-feed-list-wrapper"');
  });

  it("renders explicit no-datasets state for valid sources with no datasets", async () => {
    vi.spyOn(discoveryClient, "fetchSourceDetail").mockResolvedValue({
      source: {
        id: "fred",
        title: "Federal Reserve Economic Data",
        description: "Economic time series published by the St. Louis Fed.",
        dataset_count: 0,
      },
      items: [],
      page: 1,
      page_size: 20,
      total_items: 0,
      total_pages: 0,
      sort: "title_asc,dataset_id_asc",
    });

    const element = await SourceDetailPage({ params: Promise.resolve({ sourceId: "fred" }) });
    const markup = renderMarkup(element);

    expect(markup).toContain("No datasets are currently available for this source.");
  });

  it("renders generic error state for non-404 fetch failures", async () => {
    vi.spyOn(discoveryClient, "fetchSourceDetail").mockRejectedValue(new Error("down"));

    const element = await SourceDetailPage({ params: Promise.resolve({ sourceId: "fred" }) });
    const markup = renderMarkup(element);

    expect(markup).toContain("Unable to load data. Please try again.");
  });

  it("calls notFound for 404-like source errors", async () => {
    vi.spyOn(discoveryClient, "fetchSourceDetail").mockRejectedValue({ status: 404 });

    await expect(
      SourceDetailPage({ params: Promise.resolve({ sourceId: "unknown" }) }),
    ).rejects.toThrow("NOT_FOUND");
    expect(notFoundMock).toHaveBeenCalledTimes(1);
  });

  it("always starts source detail from page one", async () => {
    const detailSpy = vi
      .spyOn(discoveryClient, "fetchSourceDetail")
      .mockResolvedValue(buildSourceDetailFixture());

    await SourceDetailPage({ params: Promise.resolve({ sourceId: "fred" }) });

    expect(detailSpy).toHaveBeenCalledWith("fred", { page: 1 });
  });

  it("boots source detail from first page only", async () => {
    const detailSpy = vi
      .spyOn(discoveryClient, "fetchSourceDetail")
      .mockResolvedValue(buildSourceDetailFixture());

    const element = await SourceDetailPage({ params: Promise.resolve({ sourceId: "fred" }) });
    const markup = renderMarkup(element);

    expect(detailSpy).toHaveBeenCalledTimes(1);
    expect(markup).not.toContain('data-testid="infinite-scroll-sentinel"');
  });

  it("renders the source not-found route inside the shared shell", () => {
    const markup = renderMarkup(<SourceNotFoundPage />);

    expect(markup).toContain('data-testid="site-shell"');
    expect(markup).toContain('data-testid="navbar-tab-sources"');
    expect(markup).toContain("Source not found");
    expect(markup).toContain('href="/sources"');
  });
});
