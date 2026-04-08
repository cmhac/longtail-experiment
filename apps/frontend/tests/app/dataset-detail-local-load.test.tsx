import React from "react";
import { describe, expect, it, vi } from "vitest";

import DatasetDetailPage from "../../src/app/datasets/[id]/page";
import * as discoveryClient from "../../src/lib/api/discovery-client";
import {
  buildDatasetDetailFixture,
  buildLongHistoryDatasetDetailFixture,
} from "../fixtures/dataset-detail-fixtures";
import { renderMarkup } from "../test-utils";

describe("dataset detail local loading behavior", () => {
  it("renders detail page markup for local route quickly", async () => {
    vi.spyOn(discoveryClient, "fetchDatasetDetail").mockResolvedValue(buildDatasetDetailFixture());

    const startedAt = Date.now();
    const element = await DatasetDetailPage({ params: Promise.resolve({ id: "UNRATE" }) });
    const elapsedMs = Date.now() - startedAt;
    const markup = renderMarkup(element);

    expect(markup).toContain('data-testid="dataset-detail-page"');
    expect(markup).toContain('data-testid="dataset-detail-analysis"');
    expect(elapsedMs).toBeLessThan(250);
  });

  it("keeps loading-state dwell bounded for long observation histories", async () => {
    vi.spyOn(discoveryClient, "fetchDatasetDetail").mockResolvedValue(
      buildLongHistoryDatasetDetailFixture(),
    );

    const startedAt = Date.now();
    const element = await DatasetDetailPage({ params: Promise.resolve({ id: "GAS.REG.CO" }) });
    const elapsedMs = Date.now() - startedAt;
    const markup = renderMarkup(element);

    expect(markup).toContain('data-testid="observations-table"');
    expect(elapsedMs).toBeLessThan(400);
  });
});
