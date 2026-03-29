import React from "react";
import { afterEach, describe, expect, it, vi } from "vitest";
import DatasetDetailPage from "../src/app/datasets/[id]/page";
import * as discoveryClient from "../src/lib/api/discovery-client";
import { buildDatasetDetailFixture } from "./fixtures/dataset-detail-fixtures";
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

describe("dataset detail page", () => {
  it("renders hero, insights, trend, and observed sections for valid datasets", async () => {
    vi.spyOn(discoveryClient, "fetchDatasetDetail").mockResolvedValue(buildDatasetDetailFixture());

    const element = await DatasetDetailPage({ params: Promise.resolve({ id: "GAS.REG.CO" }) });
    const markup = renderMarkup(element);

    expect(markup).toContain("Regular All Formulations Retail Gasoline Prices - Colorado");
    expect(markup).toContain('data-testid="site-shell"');
    expect(markup).toContain('data-testid="shell-header"');
    expect(markup).toContain('data-testid="navbar-tab-datasets" href="/datasets"');
    expect(markup).toContain('aria-current="page" data-testid="navbar-tab-datasets"');
    expect(markup).toContain('data-testid="dataset-detail-overview"');
    expect(markup).toContain("page-header-wrapper");
    expect(markup).toContain('data-testid="dataset-detail-insights"');
    expect(markup).toContain('data-testid="dataset-detail-trend-section"');
    expect(markup).toContain('data-testid="dataset-detail-observed-values-section"');
    expect(markup).toContain('data-testid="dataset-detail-utility-actions"');
    expect(markup).toContain('class="dataset-detail-utility-actions"');
    expect(markup).toContain('href="/api/datasets/GAS.REG.CO.csv"');
    expect(markup).toContain('data-testid="observations-chart-controls"');
    expect(markup).toContain('data-testid="observations-chart"');
    expect(markup).toContain('data-testid="observations-table"');
    expect(markup).not.toContain('data-testid="observations-load-archive"');
    expect(discoveryClient.fetchDatasetDetail).toHaveBeenCalledWith("GAS.REG.CO");
  });

  it("renders generic error state for non-404 fetch failures", async () => {
    vi.spyOn(discoveryClient, "fetchDatasetDetail").mockRejectedValue(
      new Error("backend unavailable"),
    );

    const element = await DatasetDetailPage({ params: Promise.resolve({ id: "GAS.REG.CO" }) });
    const markup = renderMarkup(element);

    expect(markup).toContain("Unable to load data. Please try again.");
    expect(markup).toContain('data-testid="shell-header"');
    expect(markup).toContain('data-testid="navbar-tab-datasets" href="/datasets"');
  });

  it("calls notFound for 404-like errors", async () => {
    vi.spyOn(discoveryClient, "fetchDatasetDetail").mockRejectedValue({ status: 404 });

    await expect(DatasetDetailPage({ params: Promise.resolve({ id: "UNKNOWN" }) })).rejects.toThrow(
      "NOT_FOUND",
    );
    expect(notFoundMock).toHaveBeenCalledTimes(1);
  });

  it("renders generic error state when rejection is null", async () => {
    vi.spyOn(discoveryClient, "fetchDatasetDetail").mockRejectedValue(null);

    const element = await DatasetDetailPage({ params: Promise.resolve({ id: "FEDFUNDS" }) });
    const markup = renderMarkup(element);

    expect(markup).toContain("Unable to load data. Please try again.");
  });

  it("renders generic error state when status is not 404", async () => {
    vi.spyOn(discoveryClient, "fetchDatasetDetail").mockRejectedValue({ status: 500 });

    const element = await DatasetDetailPage({ params: Promise.resolve({ id: "FEDFUNDS" }) });
    const markup = renderMarkup(element);

    expect(markup).toContain("Unable to load data. Please try again.");
    expect(notFoundMock).toHaveBeenCalledTimes(0);
  });
});
