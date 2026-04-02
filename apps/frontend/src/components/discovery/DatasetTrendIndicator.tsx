"use client";

import { Chip } from "@heroui/react";
import React from "react";
import type { JSX } from "react";

import type { CanonicalTrendDescriptor } from "../../lib/api/discovery-types";

interface DatasetTrendIndicatorProps {
  descriptor?: CanonicalTrendDescriptor;
  className?: string;
  testId?: string;
}

type IndicatorState = "up" | "down" | "unavailable";

interface IndicatorContent {
  glyph: string;
  label: string;
  state: IndicatorState;
  chipColor: "success" | "danger" | "default";
  accentClassName: string;
}

const joinClassNames = (...values: Array<string | undefined>): string => {
  return values.filter(Boolean).join(" ");
};

const getIndicatorContent = (descriptor?: CanonicalTrendDescriptor): IndicatorContent | null => {
  if (!descriptor) {
    return null;
  }

  if (
    descriptor.descriptor_state === "available" &&
    (descriptor.direction === "up" || descriptor.direction === "down")
  ) {
    return descriptor.direction === "up"
      ? {
          glyph: "↑",
          label: "Uptrend",
          state: "up",
          chipColor: "success",
          accentClassName: "text-success",
        }
      : {
          glyph: "↓",
          label: "Downtrend",
          state: "down",
          chipColor: "danger",
          accentClassName: "text-danger",
        };
  }

  return {
    glyph: "–",
    label: "Trend unavailable",
    state: "unavailable",
    chipColor: "default",
    accentClassName: "text-(--shell-muted)",
  };
};

export const DatasetTrendIndicator = ({
  descriptor,
  className,
  testId = "dataset-trend-indicator",
}: DatasetTrendIndicatorProps): JSX.Element | null => {
  const content = getIndicatorContent(descriptor);

  if (!content) {
    return null;
  }

  return (
    <Chip
      color={content.chipColor}
      variant={content.state === "unavailable" ? "secondary" : "soft"}
      size="sm"
      className={joinClassNames(
        "inline-flex items-center justify-end gap-1.5 whitespace-nowrap px-2 py-0.5 text-[0.8rem] leading-none",
        className,
      )}
      data-state={content.state}
      data-testid={testId}
    >
      <span
        className={joinClassNames("font-semibold text-[0.95rem]", content.accentClassName)}
        data-testid={`${testId}-glyph`}
      >
        {content.glyph}
      </span>
      <Chip.Label
        className={joinClassNames("font-medium max-[720px]:sr-only", content.accentClassName)}
        data-testid={`${testId}-label`}
      >
        {content.label}
      </Chip.Label>
    </Chip>
  );
};
