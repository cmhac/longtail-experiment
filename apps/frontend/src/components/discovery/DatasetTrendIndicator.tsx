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
      ? { glyph: "↑", label: "Uptrend", state: "up" }
      : { glyph: "↓", label: "Downtrend", state: "down" };
  }

  return { glyph: "–", label: "Trend unavailable", state: "unavailable" };
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
    <span
      className={joinClassNames(
        "inline-flex items-center justify-end gap-1.5 whitespace-nowrap text-(--shell-muted) text-[0.8rem] leading-none",
        className,
      )}
      data-state={content.state}
      data-testid={testId}
    >
      <span
        className="font-semibold text-(--shell-text) text-[0.95rem]"
        data-testid={`${testId}-glyph`}
      >
        {content.glyph}
      </span>
      <span className="font-medium max-[720px]:sr-only" data-testid={`${testId}-label`}>
        {content.label}
      </span>
    </span>
  );
};
