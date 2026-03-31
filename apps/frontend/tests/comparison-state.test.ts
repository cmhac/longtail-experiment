/** @vitest-environment jsdom */

import { describe, expect, it } from "vitest";
import {
  COMPARISON_STATE_STORAGE_KEY,
  ComparisonStateCorruptedError,
  MAX_COMPARISON_DATASETS,
  getComparisonLineColor,
  getComparisonState,
  isComparisonSelectionCompatible,
  removeComparisonDataset,
  resetComparisonState,
  setComparisonChartSettings,
  upsertComparisonDataset,
} from "../src/components/discovery/comparison-state";

describe("comparison-state", () => {
  it("returns default state when local storage is empty", () => {
    window.localStorage.clear();

    const state = getComparisonState();
    expect(state.version).toBe(1);
    expect(state.selectedDatasetIds).toEqual([]);
    expect(state.chartSettings.valueMode).toBe("observed");
  });

  it("caps selected dataset ids at max size", () => {
    window.localStorage.clear();
    resetComparisonState();

    for (let index = 0; index < MAX_COMPARISON_DATASETS + 2; index += 1) {
      upsertComparisonDataset(`DATASET_${index}`);
    }

    const state = getComparisonState();
    expect(state.selectedDatasetIds).toHaveLength(MAX_COMPARISON_DATASETS);
  });

  it("throws corrupted-state error on invalid JSON", () => {
    window.localStorage.setItem(COMPARISON_STATE_STORAGE_KEY, "{not-json}");

    expect(() => getComparisonState()).toThrow(ComparisonStateCorruptedError);
  });

  it("assigns deterministic palette colors by selected order", () => {
    const selected = ["A", "B", "C"];

    expect(getComparisonLineColor("A", selected)).toBe(getComparisonLineColor("A", selected));
    expect(getComparisonLineColor("A", selected)).not.toBe(getComparisonLineColor("B", selected));
  });

  it("supports compatibility checks across mixed unit types", () => {
    expect(isComparisonSelectionCompatible(["usd", "usd"])).toBe(true);
    expect(isComparisonSelectionCompatible(["usd", "percent"])).toBe(false);
    expect(isComparisonSelectionCompatible([null, undefined])).toBe(true);
  });

  it("updates chart settings and clamps rolling offset", () => {
    window.localStorage.clear();
    resetComparisonState();

    setComparisonChartSettings({ rollingOffset: 0, baselineMode: "fixed" });

    const state = getComparisonState();
    expect(state.chartSettings.rollingOffset).toBe(1);
    expect(state.chartSettings.baselineMode).toBe("fixed");
  });

  it("removes selected datasets", () => {
    window.localStorage.clear();
    resetComparisonState();
    upsertComparisonDataset("A");
    upsertComparisonDataset("B");

    removeComparisonDataset("A");

    const state = getComparisonState();
    expect(state.selectedDatasetIds).toEqual(["B"]);
  });
});
