import React from "react";
import type { JSX } from "react";
import type { CanonicalTrendDescriptor } from "../../lib/api/discovery-types";

interface DatasetTrendChipProps {
  canonicalTrendDescriptor: CanonicalTrendDescriptor | undefined;
}

const toDirectionLabel = (direction: CanonicalTrendDescriptor["direction"]): string | null => {
  if (direction === "up") {
    return "Up";
  }
  if (direction === "down") {
    return "Down";
  }
  return null;
};

export const DatasetTrendChip = ({
  canonicalTrendDescriptor,
}: DatasetTrendChipProps): JSX.Element => {
  if (!canonicalTrendDescriptor || canonicalTrendDescriptor.descriptor_state !== "available") {
    return (
      <p
        className="inline-flex w-fit items-center rounded-full border border-(--shell-border) bg-(--shell-surface) px-3 py-1 text-(--shell-muted) text-[0.76rem]"
        data-testid="dataset-trend-chip"
      >
        Trend unavailable
        {canonicalTrendDescriptor?.reason_code ? ` (${canonicalTrendDescriptor.reason_code})` : ""}
      </p>
    );
  }

  const directionLabel = toDirectionLabel(canonicalTrendDescriptor.direction);
  const lookbackLabel =
    canonicalTrendDescriptor.selected_lookback_points === null
      ? null
      : `${canonicalTrendDescriptor.selected_lookback_points}-point lookback`;

  return (
    <p
      className="inline-flex w-fit flex-wrap items-center gap-2 rounded-full border border-(--shell-border) bg-(--shell-surface) px-3 py-1 text-(--shell-foreground) text-[0.76rem]"
      data-testid="dataset-trend-chip"
    >
      <span>{canonicalTrendDescriptor.trend_label ?? "Trend available"}</span>
      {directionLabel ? <span>{directionLabel}</span> : null}
      {lookbackLabel ? <span>{lookbackLabel}</span> : null}
    </p>
  );
};
