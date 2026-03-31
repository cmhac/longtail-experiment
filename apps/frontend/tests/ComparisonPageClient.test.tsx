/** @vitest-environment jsdom */

import { fireEvent, render, screen, waitFor } from "@testing-library/react";
import React from "react";
import type { ReactNode } from "react";
import { beforeEach, describe, expect, it, vi } from "vitest";
import {
  ComparisonPageClient,
  buildChartRows,
  resolveFixedBaseline,
} from "../src/components/discovery/ComparisonPageClient";
import { COMPARISON_STATE_STORAGE_KEY } from "../src/components/discovery/comparison-state";
import { buildDatasetDetailFixture } from "./fixtures/dataset-detail-fixtures";

vi.mock("recharts", () => ({
  CartesianGrid: () => <div data-testid="mock-cartesian-grid" />,
  Legend: () => <div data-testid="mock-legend" />,
  Line: () => <div data-testid="mock-line" />,
  LineChart: ({ children }: { children: ReactNode }) => <div>{children}</div>,
  ResponsiveContainer: ({ children }: { children: ReactNode }) => <div>{children}</div>,
  Tooltip: () => <div data-testid="mock-tooltip" />,
  XAxis: () => <div data-testid="mock-x-axis" />,
  YAxis: () => <div data-testid="mock-y-axis" />,
}));

const { fetchDatasetDetailMock } = vi.hoisted(() => ({
  fetchDatasetDetailMock: vi.fn(),
}));

vi.mock("../src/lib/api/discovery-client", () => ({
  fetchDatasetDetail: fetchDatasetDetailMock,
}));

describe("ComparisonPageClient", () => {
  beforeEach(() => {
    window.localStorage.clear();
    fetchDatasetDetailMock.mockReset();
    fetchDatasetDetailMock.mockImplementation(async (datasetId: string) => {
      return buildDatasetDetailFixture({
        dataset_id: datasetId,
        title: `Dataset ${datasetId}`,
        metadata: { unit_type: "usd" },
      });
    });
  });

  it("renders empty state when no datasets are selected", () => {
    window.localStorage.setItem(
      COMPARISON_STATE_STORAGE_KEY,
      JSON.stringify({
        version: 1,
        selectedDatasetIds: [],
        chartSettings: {
          valueMode: "observed",
          baselineMode: "rolling",
          rollingOffset: 1,
          fixedBaselineDate: null,
        },
        updatedAt: new Date().toISOString(),
      }),
    );

    const { container } = render(<ComparisonPageClient />);

    expect(screen.getByTestId("comparison-empty-state")).toBeTruthy();
  });

  it("shows controls but hides chart when exactly one dataset is selected", async () => {
    window.localStorage.setItem(
      COMPARISON_STATE_STORAGE_KEY,
      JSON.stringify({
        version: 1,
        selectedDatasetIds: ["ONLY_ONE"],
        chartSettings: {
          valueMode: "observed",
          baselineMode: "rolling",
          rollingOffset: 1,
          fixedBaselineDate: null,
        },
        updatedAt: new Date().toISOString(),
      }),
    );

    const rendered = render(<ComparisonPageClient />);
    const { container } = rendered;

    await waitFor(() => {
      expect(container.querySelector('[data-testid="comparison-controls"]')).toBeTruthy();
    });
    expect(screen.getByText("Dataset ONLY_ONE")).toBeTruthy();
    expect(screen.queryByTestId("comparison-chart-card")).toBeNull();
    expect(screen.getByTestId("comparison-chart-disabled-message")).toBeTruthy();

    fireEvent.click(screen.getByText("Dataset ONLY_ONE"));
    const nextState = JSON.parse(window.localStorage.getItem(COMPARISON_STATE_STORAGE_KEY) ?? "{}");
    expect(nextState.selectedDatasetIds).toEqual([]);
  });

  it("renders state error when persisted data is corrupted", () => {
    window.localStorage.setItem(COMPARISON_STATE_STORAGE_KEY, "not-json");

    render(<ComparisonPageClient />);

    expect(screen.getByTestId("comparison-state-error")).toBeTruthy();
    expect(screen.getByText("Reset comparison state")).toBeTruthy();

    fireEvent.click(screen.getByText("Reset comparison state"));
    const nextState = JSON.parse(window.localStorage.getItem(COMPARISON_STATE_STORAGE_KEY) ?? "{}");
    expect(nextState.version).toBe(1);
  });

  it("renders populated comparison controls and allows removal", async () => {
    window.localStorage.setItem(
      COMPARISON_STATE_STORAGE_KEY,
      JSON.stringify({
        version: 1,
        selectedDatasetIds: ["A", "B"],
        chartSettings: {
          valueMode: "observed",
          baselineMode: "rolling",
          rollingOffset: 1,
          fixedBaselineDate: null,
        },
        updatedAt: new Date().toISOString(),
      }),
    );

    fetchDatasetDetailMock
      .mockResolvedValueOnce(
        buildDatasetDetailFixture({
          dataset_id: "A",
          title: "Dataset A",
          metadata: { unit_type: "usd" },
        }),
      )
      .mockResolvedValueOnce(
        buildDatasetDetailFixture({
          dataset_id: "B",
          title: "Dataset B",
          metadata: { unit_type: "usd" },
        }),
      );

    const rendered = render(<ComparisonPageClient />);
    const { container } = rendered;

    await waitFor(() => {
      expect(container.querySelector('[data-testid="comparison-controls"]')).toBeTruthy();
    });

    expect(screen.getByTestId("comparison-chart-card")).toBeTruthy();
    expect(screen.getByText("Dataset A")).toBeTruthy();
    expect(screen.getByText("Dataset B")).toBeTruthy();

    fireEvent.click(screen.getByText("Dataset A"));

    const nextState = JSON.parse(window.localStorage.getItem(COMPARISON_STATE_STORAGE_KEY) ?? "{}");
    expect(nextState.selectedDatasetIds).toEqual(["B"]);
  });

  it("disables baseline controls when mode is absolute", async () => {
    window.localStorage.setItem(
      COMPARISON_STATE_STORAGE_KEY,
      JSON.stringify({
        version: 1,
        selectedDatasetIds: ["A", "B"],
        chartSettings: {
          valueMode: "observed",
          baselineMode: "rolling",
          rollingOffset: 1,
          fixedBaselineDate: null,
        },
        updatedAt: new Date().toISOString(),
      }),
    );

    const rendered = render(<ComparisonPageClient />);
    const { container } = rendered;

    await waitFor(() => {
      expect(container.querySelector('[data-testid="comparison-controls"]')).toBeTruthy();
    });

    const hiddenSelects = Array.from(
      container.querySelectorAll('[data-testid="hidden-select-container"] select'),
    ) as HTMLSelectElement[];
    const baselineNativeSelect = hiddenSelects.find((selectElement) =>
      Array.from(selectElement.options).some((option) => option.value === "fixed"),
    );
    expect(baselineNativeSelect?.disabled).toBe(true);

    const offsetInput = screen.getByLabelText("Offset") as HTMLInputElement;
    expect(offsetInput.disabled).toBe(true);
  });

  it("auto-switches to relative mode when selected units are incompatible", async () => {
    window.localStorage.setItem(
      COMPARISON_STATE_STORAGE_KEY,
      JSON.stringify({
        version: 1,
        selectedDatasetIds: ["A", "B"],
        chartSettings: {
          valueMode: "observed",
          baselineMode: "rolling",
          rollingOffset: 1,
          fixedBaselineDate: null,
        },
        updatedAt: new Date().toISOString(),
      }),
    );

    fetchDatasetDetailMock
      .mockResolvedValueOnce(
        buildDatasetDetailFixture({ dataset_id: "A", metadata: { unit_type: "usd" } }),
      )
      .mockResolvedValueOnce(
        buildDatasetDetailFixture({ dataset_id: "B", metadata: { unit_type: "percent" } }),
      );

    render(<ComparisonPageClient />);

    await waitFor(() => {
      expect(screen.getByTestId("comparison-compatibility-message")).toBeTruthy();
    });

    const nextState = JSON.parse(window.localStorage.getItem(COMPARISON_STATE_STORAGE_KEY) ?? "{}");
    expect(nextState.chartSettings.valueMode).toBe("relative");
  });
});

describe("ComparisonPageClient helpers", () => {
  it("falls back to nearest prior and nearest-any fixed baseline", () => {
    const dataset = buildDatasetDetailFixture({
      observations: [
        {
          observed_on: "2024-01-10",
          value: 100,
          reported_at: "2024-01-10T00:00:00Z",
          attributes: {},
        },
        {
          observed_on: "2024-01-20",
          value: 110,
          reported_at: "2024-01-20T00:00:00Z",
          attributes: {},
        },
      ],
    });

    const prior = resolveFixedBaseline(dataset.observations, "2024-01-15");
    expect(prior.baselineDate).toBe("2024-01-10");

    const nearestAny = resolveFixedBaseline(dataset.observations, "2023-12-01");
    expect(nearestAny.baselineDate).toBe("2024-01-10");

    const missing = resolveFixedBaseline(dataset.observations, null);
    expect(missing.baselineDate).toBeNull();
    expect(missing.baselineValue).toBeNull();
  });

  it("builds union-date rows with null gaps and relative values", () => {
    const first = buildDatasetDetailFixture({
      dataset_id: "A",
      observations: [
        {
          observed_on: "2024-01-01",
          value: 100,
          reported_at: "2024-01-01T00:00:00Z",
          attributes: {},
        },
        {
          observed_on: "2024-01-08",
          value: 110,
          reported_at: "2024-01-08T00:00:00Z",
          attributes: {},
        },
      ],
    });

    const second = buildDatasetDetailFixture({
      dataset_id: "B",
      observations: [
        {
          observed_on: "2024-01-08",
          value: 50,
          reported_at: "2024-01-08T00:00:00Z",
          attributes: {},
        },
      ],
    });

    const observedRows = buildChartRows([first, second], "observed", "rolling", 1, null);
    expect(observedRows).toHaveLength(2);
    expect(observedRows[0]?.B).toBeNull();

    const relativeRows = buildChartRows([first], "relative", "rolling", 1, null);
    expect(relativeRows[0]?.A).toBeNull();
    expect(relativeRows[1]?.A).toBe(10);

    const fixedRows = buildChartRows([first], "relative", "fixed", 1, "2024-01-01");
    expect(fixedRows[0]?.A).toBe(0);
  });

  it("returns null relative values when fixed baseline is zero", () => {
    const zeroBaseline = buildDatasetDetailFixture({
      dataset_id: "A",
      observations: [
        {
          observed_on: "2024-01-01",
          value: 0,
          reported_at: "2024-01-01T00:00:00Z",
          attributes: {},
        },
        {
          observed_on: "2024-01-08",
          value: 10,
          reported_at: "2024-01-08T00:00:00Z",
          attributes: {},
        },
      ],
    });

    const rows = buildChartRows([zeroBaseline], "relative", "fixed", 1, "2024-01-01");
    expect(rows[1]?.A).toBeNull();
  });
});
