import React from "react";
import { describe, expect, it, vi } from "vitest";

import DatasetDetailPage from "../../src/app/datasets/[id]/page";
import * as discoveryClient from "../../src/lib/api/discovery-client";
import { buildDatasetDetailFixture } from "../fixtures/dataset-detail-fixtures";
import { renderMarkup } from "../test-utils";

describe("dataset detail trend payload error state", () => {
  it("hard-fails to error state when trend payload is malformed", async () => {
    vi.spyOn(discoveryClient, "fetchDatasetDetail").mockRejectedValue({
      status: 400,
      code: "dataset_detail_trend_payload_invalid",
    });

    const element = await DatasetDetailPage({ params: Promise.resolve({ id: "UNRATE" }) });
    const markup = renderMarkup(element);

    expect(markup).toContain("Unable to load data. Please try again.");
  });

  it("keeps baseline rendering when canonical trend data is unavailable", async () => {
    vi.spyOn(discoveryClient, "fetchDatasetDetail").mockResolvedValue(
      buildDatasetDetailFixture({
        canonical_trend_descriptor: {
          descriptor_state: "unavailable",
          trend_label: null,
          direction: null,
          strength: null,
          selected_lookback_points: null,
          observed_on: null,
          reason_code: "no_applicable_lookbacks",
        },
      }),
    );

    const element = await DatasetDetailPage({ params: Promise.resolve({ id: "UNRATE" }) });
    const markup = renderMarkup(element);

    expect(markup).toContain('data-testid="dataset-detail-trend-section"');
    expect(markup).toContain('data-testid="observations-chart"');
    expect(markup).not.toContain('data-testid="dataset-trend-chip"');
  });
});
