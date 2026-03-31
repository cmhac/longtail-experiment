"use client";

import type { ComparisonSelectionState } from "../../lib/api/discovery-types";

export const MAX_COMPARISON_DATASETS = 5;
export const COMPARISON_STATE_STORAGE_KEY = "lt.datasetComparison.v1";
export const COMPARISON_STATE_EVENT = "lt:comparison-state";

const DEFAULT_CHART_SETTINGS: ComparisonSelectionState["chartSettings"] = {
  valueMode: "observed",
  baselineMode: "rolling",
  rollingOffset: 1,
  fixedBaselineDate: null,
};

const DEFAULT_STATE: ComparisonSelectionState = {
  version: 1,
  selectedDatasetIds: [],
  chartSettings: DEFAULT_CHART_SETTINGS,
  updatedAt: new Date(0).toISOString(),
};

export class ComparisonStateCorruptedError extends Error {
  constructor() {
    super("Comparison state is invalid. Reset is required.");
    this.name = "ComparisonStateCorruptedError";
  }
}

const isValidState = (value: unknown): value is ComparisonSelectionState => {
  if (!value || typeof value !== "object") {
    return false;
  }

  const state = value as Partial<ComparisonSelectionState>;
  if (state.version !== 1 || !Array.isArray(state.selectedDatasetIds)) {
    return false;
  }

  if (
    !state.selectedDatasetIds.every(
      (datasetId) => typeof datasetId === "string" && datasetId.trim().length > 0,
    )
  ) {
    return false;
  }

  if (
    !state.chartSettings ||
    typeof state.chartSettings !== "object" ||
    typeof state.chartSettings.rollingOffset !== "number" ||
    state.chartSettings.rollingOffset < 1 ||
    (state.chartSettings.valueMode !== "observed" &&
      state.chartSettings.valueMode !== "relative") ||
    (state.chartSettings.baselineMode !== "rolling" &&
      state.chartSettings.baselineMode !== "fixed") ||
    !(
      state.chartSettings.fixedBaselineDate === null ||
      typeof state.chartSettings.fixedBaselineDate === "string"
    )
  ) {
    return false;
  }

  if (typeof state.updatedAt !== "string") {
    return false;
  }

  return state.selectedDatasetIds.length <= MAX_COMPARISON_DATASETS;
};

const toUniqueIds = (ids: string[]): string[] => {
  const unique = new Set<string>();
  for (const id of ids) {
    const normalized = id.trim();
    if (normalized !== "") {
      unique.add(normalized);
    }
  }
  return [...unique];
};

const emitStateEvent = (): void => {
  if (typeof window === "undefined") {
    return;
  }
  window.dispatchEvent(new Event(COMPARISON_STATE_EVENT));
};

const writeState = (state: ComparisonSelectionState): ComparisonSelectionState => {
  if (typeof window !== "undefined") {
    window.localStorage.setItem(COMPARISON_STATE_STORAGE_KEY, JSON.stringify(state));
    emitStateEvent();
  }
  return state;
};

export const defaultComparisonState = (): ComparisonSelectionState => ({
  ...DEFAULT_STATE,
  chartSettings: { ...DEFAULT_CHART_SETTINGS },
  updatedAt: new Date().toISOString(),
});

export const resetComparisonState = (): ComparisonSelectionState => {
  return writeState(defaultComparisonState());
};

export const getComparisonState = (): ComparisonSelectionState => {
  if (typeof window === "undefined") {
    return defaultComparisonState();
  }

  const raw = window.localStorage.getItem(COMPARISON_STATE_STORAGE_KEY);
  if (!raw) {
    return defaultComparisonState();
  }

  let parsed: unknown;
  try {
    parsed = JSON.parse(raw);
  } catch {
    throw new ComparisonStateCorruptedError();
  }

  if (!isValidState(parsed)) {
    throw new ComparisonStateCorruptedError();
  }

  return {
    ...parsed,
    chartSettings: { ...parsed.chartSettings },
    selectedDatasetIds: [...parsed.selectedDatasetIds],
  };
};

export const upsertComparisonDataset = (datasetId: string): ComparisonSelectionState => {
  const state = getComparisonState();
  const nextIds = toUniqueIds([...state.selectedDatasetIds, datasetId]);

  if (nextIds.length > MAX_COMPARISON_DATASETS) {
    return state;
  }

  return writeState({
    ...state,
    selectedDatasetIds: nextIds,
    updatedAt: new Date().toISOString(),
  });
};

export const removeComparisonDataset = (datasetId: string): ComparisonSelectionState => {
  const state = getComparisonState();
  return writeState({
    ...state,
    selectedDatasetIds: state.selectedDatasetIds.filter((id) => id !== datasetId),
    updatedAt: new Date().toISOString(),
  });
};

export const setComparisonChartSettings = (
  next: Partial<ComparisonSelectionState["chartSettings"]>,
): ComparisonSelectionState => {
  const state = getComparisonState();
  const rollingOffset = Math.max(
    1,
    Math.floor(next.rollingOffset ?? state.chartSettings.rollingOffset),
  );

  return writeState({
    ...state,
    chartSettings: {
      ...state.chartSettings,
      ...next,
      rollingOffset,
    },
    updatedAt: new Date().toISOString(),
  });
};

export const getComparisonCount = (): number => {
  return getComparisonState().selectedDatasetIds.length;
};

export const isDatasetSelectedForComparison = (datasetId: string): boolean => {
  return getComparisonState().selectedDatasetIds.includes(datasetId);
};

export const isComparisonSelectionCompatible = (
  unitTypes: Array<string | null | undefined>,
): boolean => {
  const normalized = unitTypes
    .map((value) => (typeof value === "string" ? value.trim().toLowerCase() : null))
    .filter((value): value is string => Boolean(value));
  if (normalized.length <= 1) {
    return true;
  }
  return new Set(normalized).size === 1;
};

const LINE_COLOR_PALETTE = [
  "#2563eb",
  "#dc2626",
  "#16a34a",
  "#ca8a04",
  "#7c3aed",
  "#0891b2",
  "#ea580c",
  "#9333ea",
  "#4f46e5",
  "#0f766e",
] as const;

const hashDatasetId = (datasetId: string): number => {
  let hash = 0;
  for (let index = 0; index < datasetId.length; index += 1) {
    hash = (hash * 31 + datasetId.charCodeAt(index)) >>> 0;
  }
  return hash;
};

export const getComparisonLineColor = (
  datasetId: string,
  selectedDatasetIds?: readonly string[],
): string => {
  if (selectedDatasetIds && selectedDatasetIds.length > 0) {
    const index = selectedDatasetIds.indexOf(datasetId);
    if (index >= 0) {
      return LINE_COLOR_PALETTE[index % LINE_COLOR_PALETTE.length] ?? "#2563eb";
    }
  }

  const hash = hashDatasetId(datasetId);
  return LINE_COLOR_PALETTE[hash % LINE_COLOR_PALETTE.length] ?? "#2563eb";
};
