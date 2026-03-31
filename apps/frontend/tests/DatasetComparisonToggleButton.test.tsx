/** @vitest-environment jsdom */

import { fireEvent, render, screen, waitFor } from "@testing-library/react";
import React from "react";
import { beforeEach, describe, expect, it } from "vitest";
import { DatasetComparisonToggleButton } from "../src/components/discovery/DatasetComparisonToggleButton";
import {
  COMPARISON_STATE_STORAGE_KEY,
  MAX_COMPARISON_DATASETS,
  resetComparisonState,
} from "../src/components/discovery/comparison-state";

describe("DatasetComparisonToggleButton", () => {
  beforeEach(() => {
    window.localStorage.clear();
    resetComparisonState();
  });

  it("toggles add and remove actions", async () => {
    render(<DatasetComparisonToggleButton datasetId="SERIES_A" />);

    const actionButton = screen.getByRole("button", { name: "Add to Comparison" });
    fireEvent.click(actionButton);

    await waitFor(() => {
      expect(screen.getByRole("button", { name: "Remove from Comparison" })).toBeTruthy();
    });

    const nextState = JSON.parse(window.localStorage.getItem(COMPARISON_STATE_STORAGE_KEY) ?? "{}");
    expect(nextState.selectedDatasetIds).toContain("SERIES_A");

    fireEvent.click(screen.getByRole("button", { name: "Remove from Comparison" }));

    const finalState = JSON.parse(
      window.localStorage.getItem(COMPARISON_STATE_STORAGE_KEY) ?? "{}",
    );
    expect(finalState.selectedDatasetIds).toEqual([]);
  });

  it("disables add action when comparison is at max capacity", () => {
    window.localStorage.setItem(
      COMPARISON_STATE_STORAGE_KEY,
      JSON.stringify({
        version: 1,
        selectedDatasetIds: Array.from(
          { length: MAX_COMPARISON_DATASETS },
          (_, index) => `S${index}`,
        ),
        chartSettings: {
          valueMode: "observed",
          baselineMode: "rolling",
          rollingOffset: 1,
          fixedBaselineDate: null,
        },
        updatedAt: new Date().toISOString(),
      }),
    );

    render(<DatasetComparisonToggleButton datasetId="NEW_SERIES" />);

    const button = screen.getByRole("button", {
      name: `Comparison Full (${MAX_COMPARISON_DATASETS})`,
    });
    expect(button.getAttribute("disabled")).not.toBeNull();
  });

  it("shows reset action for corrupted state", () => {
    window.localStorage.setItem(COMPARISON_STATE_STORAGE_KEY, "{not-json}");

    render(<DatasetComparisonToggleButton datasetId="SERIES_A" />);

    fireEvent.click(screen.getByRole("button", { name: "Reset Comparison State" }));

    const state = JSON.parse(window.localStorage.getItem(COMPARISON_STATE_STORAGE_KEY) ?? "{}");
    expect(state.version).toBe(1);
    expect(state.selectedDatasetIds).toEqual([]);
  });
});
