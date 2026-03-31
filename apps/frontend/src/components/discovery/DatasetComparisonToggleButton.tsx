"use client";

import { Button } from "@heroui/react";
import React, { useCallback, useEffect, useState } from "react";
import type { JSX } from "react";
import {
  COMPARISON_STATE_EVENT,
  ComparisonStateCorruptedError,
  MAX_COMPARISON_DATASETS,
  getComparisonState,
  removeComparisonDataset,
  resetComparisonState,
  upsertComparisonDataset,
} from "./comparison-state";

interface DatasetComparisonToggleButtonProps {
  datasetId: string;
}

export const DatasetComparisonToggleButton = ({
  datasetId,
}: DatasetComparisonToggleButtonProps): JSX.Element => {
  const [isSelected, setIsSelected] = useState(false);
  const [count, setCount] = useState(0);
  const [hasCorruptedState, setHasCorruptedState] = useState(false);

  const syncState = useCallback(() => {
    try {
      const state = getComparisonState();
      setIsSelected(state.selectedDatasetIds.includes(datasetId));
      setCount(state.selectedDatasetIds.length);
      setHasCorruptedState(false);
    } catch (error) {
      if (error instanceof ComparisonStateCorruptedError) {
        setHasCorruptedState(true);
      }
    }
  }, [datasetId]);

  useEffect(() => {
    syncState();

    const handleStateChange = (): void => {
      syncState();
    };

    window.addEventListener(COMPARISON_STATE_EVENT, handleStateChange);
    window.addEventListener("storage", handleStateChange);

    return () => {
      window.removeEventListener(COMPARISON_STATE_EVENT, handleStateChange);
      window.removeEventListener("storage", handleStateChange);
    };
  }, [syncState]);

  if (hasCorruptedState) {
    return (
      <Button
        variant="danger-soft"
        className="inline-flex min-h-[2.1rem] flex-none items-center justify-center border border-red-500/70 px-[0.8rem] py-[0.35rem] text-[0.74rem] uppercase tracking-[0.08em]"
        onPress={() => {
          resetComparisonState();
          syncState();
        }}
      >
        Reset Comparison State
      </Button>
    );
  }

  const isAtLimit = !isSelected && count >= MAX_COMPARISON_DATASETS;

  return (
    <Button
      variant="secondary"
      className="dataset-detail-action-export inline-flex min-h-[2.1rem] flex-none items-center justify-center border border-(--shell-border) px-[0.8rem] py-[0.35rem] text-[0.74rem] uppercase tracking-[0.08em] disabled:cursor-not-allowed disabled:opacity-55"
      isDisabled={isAtLimit}
      onPress={() => {
        if (isSelected) {
          removeComparisonDataset(datasetId);
        } else {
          upsertComparisonDataset(datasetId);
        }
        syncState();
      }}
    >
      {isAtLimit
        ? `Comparison Full (${MAX_COMPARISON_DATASETS})`
        : isSelected
          ? "Remove from Comparison"
          : "Add to Comparison"}
    </Button>
  );
};
