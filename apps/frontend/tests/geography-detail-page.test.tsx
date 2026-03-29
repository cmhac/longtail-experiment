import React from "react";
import { afterEach, describe, expect, it, vi } from "vitest";

import GeographyNotFoundPage from "../src/app/geographies/[geographyId]/not-found";
import GeographyDetailPage from "../src/app/geographies/[geographyId]/page";
import * as discoveryClient from "../src/lib/api/discovery-client";
import { buildGeographyDetailFixture } from "./fixtures/metadata-discovery-fixtures";
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

describe("geography detail page", () => {
  it("renders geography context and only matching datasets", async () => {
    const detailSpy = vi
      .spyOn(discoveryClient, "fetchGeographyDetail")
      .mockResolvedValue(buildGeographyDetailFixture());

    const element = await GeographyDetailPage({
      params: Promise.resolve({ geographyId: "us" }),
    });
    const markup = renderMarkup(element);

    expect(detailSpy).toHaveBeenCalledWith("us", { page: 1 });
    expect(markup).toContain("US");
    expect(markup).toContain("2 total datasets");
    expect(markup).toContain('data-testid="geography-detail-page"');
    expect(markup).toContain('data-testid="geography-detail-header"');
    expect(markup).toContain("page-header-wrapper");
    expect(markup).toContain('href="/datasets/CPIAUCSL"');
  });

  it("renders explicit no-datasets state for valid geographies with no datasets", async () => {
    vi.spyOn(discoveryClient, "fetchGeographyDetail").mockResolvedValue({
      geography: { id: "us", label: "US", dataset_count: 0 },
      items: [],
      page: 1,
      page_size: 20,
      total_items: 0,
      total_pages: 0,
      sort: "title_asc,dataset_id_asc",
    });

    const element = await GeographyDetailPage({ params: Promise.resolve({ geographyId: "us" }) });
    const markup = renderMarkup(element);

    expect(markup).toContain("No datasets are currently available for this geography.");
  });

  it("renders generic error state for non-404 geography fetch failures", async () => {
    vi.spyOn(discoveryClient, "fetchGeographyDetail").mockRejectedValue(new Error("down"));

    const element = await GeographyDetailPage({ params: Promise.resolve({ geographyId: "us" }) });
    const markup = renderMarkup(element);

    expect(markup).toContain("Unable to load data. Please try again.");
  });

  it("calls notFound for 404-like geography errors", async () => {
    vi.spyOn(discoveryClient, "fetchGeographyDetail").mockRejectedValue({ status: 404 });

    await expect(
      GeographyDetailPage({ params: Promise.resolve({ geographyId: "unknown-geography" }) }),
    ).rejects.toThrow("NOT_FOUND");
    expect(notFoundMock).toHaveBeenCalledTimes(1);
  });

  it("always starts geography detail from page one", async () => {
    const detailSpy = vi
      .spyOn(discoveryClient, "fetchGeographyDetail")
      .mockResolvedValue(buildGeographyDetailFixture());

    await GeographyDetailPage({ params: Promise.resolve({ geographyId: "us" }) });

    expect(detailSpy).toHaveBeenCalledWith("us", { page: 1 });
  });

  it("boots geography detail from first page only", async () => {
    const detailSpy = vi
      .spyOn(discoveryClient, "fetchGeographyDetail")
      .mockResolvedValue(buildGeographyDetailFixture());

    const element = await GeographyDetailPage({ params: Promise.resolve({ geographyId: "us" }) });
    const markup = renderMarkup(element);

    expect(detailSpy).toHaveBeenCalledTimes(1);
    expect(markup).not.toContain('data-testid="infinite-scroll-sentinel"');
  });

  it("renders the geography not-found route inside the shared shell", () => {
    const markup = renderMarkup(<GeographyNotFoundPage />);

    expect(markup).toContain('data-testid="site-shell"');
    expect(markup).toContain("Geography not found");
    expect(markup).toContain('href="/datasets"');
  });
});
