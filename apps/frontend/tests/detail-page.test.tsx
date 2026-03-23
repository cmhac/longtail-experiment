import React from "react";
import { describe, expect, it, vi } from "vitest";
import DatasetDetailPage from "../src/app/datasets/[id]/page";
import * as discoveryClient from "../src/lib/api/discovery-client";
import { renderMarkup } from "./test-utils";

const notFoundMock = vi.fn(() => {
  throw new Error("NOT_FOUND");
});

vi.mock("next/navigation", () => ({
  notFound: () => notFoundMock(),
}));

describe("dataset detail page", () => {
  it("renders detail metadata and chart sections for valid datasets", async () => {
    vi.spyOn(discoveryClient, "fetchDatasetDetail").mockResolvedValue({
      dataset_id: "FEDFUNDS",
      source: { id: "fred", name: "FRED" },
      title: "Federal Funds Effective Rate",
      description: "Target federal funds rate",
      geographic_scope: "US",
      topic_tags: ["interest rates"],
      metadata: { units: "Percent" },
      observations: [
        {
          observed_on: "2026-01-01",
          value: 4.33,
          reported_at: "2026-02-03T00:00:00Z",
          attributes: {},
        },
      ],
      observation_sort: "observed_on_asc",
    });

    const element = await DatasetDetailPage({ params: Promise.resolve({ id: "FEDFUNDS" }) });
    const markup = renderMarkup(element);

    expect(markup).toContain("Federal Funds Effective Rate");
    expect(markup).toContain('data-testid="observations-chart"');
    expect(markup).toContain('data-testid="observations-table"');
    expect(discoveryClient.fetchDatasetDetail).toHaveBeenCalledWith("FEDFUNDS");
  });

  it("renders generic error state for non-404 fetch failures", async () => {
    vi.spyOn(discoveryClient, "fetchDatasetDetail").mockRejectedValue(
      new Error("backend unavailable"),
    );

    const element = await DatasetDetailPage({ params: Promise.resolve({ id: "FEDFUNDS" }) });
    const markup = renderMarkup(element);

    expect(markup).toContain("Unable to load data. Please try again.");
  });

  it("calls notFound for 404-like errors", async () => {
    vi.spyOn(discoveryClient, "fetchDatasetDetail").mockRejectedValue({ status: 404 });

    await expect(DatasetDetailPage({ params: Promise.resolve({ id: "UNKNOWN" }) })).rejects.toThrow(
      "NOT_FOUND",
    );
    expect(notFoundMock).toHaveBeenCalledTimes(1);
  });
});
