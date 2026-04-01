"use client";

import React from "react";
import type { JSX } from "react";

import type { TrendVisualizationSpan } from "../../lib/api/discovery-types";
import { TrendOverlayLayer } from "./TrendOverlayLayer";

interface TrendTooltipControllerProps {
  chartDates: string[];
  spans: TrendVisualizationSpan[];
}

const toSpanId = (span: TrendVisualizationSpan, index: number): string =>
  `${span.trend_label}-${span.start_period}-${span.end_period}-${index}`;

export const TrendTooltipController = ({
  chartDates,
  spans,
}: TrendTooltipControllerProps): JSX.Element | null => {
  const [hoveredSpanId, setHoveredSpanId] = React.useState<string | null>(null);
  const [pinnedSpanId, setPinnedSpanId] = React.useState<string | null>(null);

  React.useEffect(() => {
    const onPointerDown = (): void => {
      setPinnedSpanId(null);
      setHoveredSpanId(null);
    };

    window.addEventListener("pointerdown", onPointerDown);
    return () => {
      window.removeEventListener("pointerdown", onPointerDown);
    };
  }, []);

  if (spans.length === 0) {
    return null;
  }

  const activeSpanId = pinnedSpanId ?? hoveredSpanId;
  const activeSpanIndex = spans.findIndex((span, index) => toSpanId(span, index) === activeSpanId);
  const activeSpan = activeSpanIndex >= 0 ? spans[activeSpanIndex] : null;

  return (
    <>
      <TrendOverlayLayer
        activeSpanId={activeSpanId}
        chartDates={chartDates}
        onHoverSpan={(spanId) => {
          if (pinnedSpanId) {
            return;
          }
          setHoveredSpanId(spanId);
        }}
        onTogglePinnedSpan={(spanId) => {
          setPinnedSpanId((current) => (current === spanId ? null : spanId));
          setHoveredSpanId(spanId);
        }}
        spans={spans}
      />
      {activeSpan ? (
        <div
          className="pointer-events-none absolute top-3 left-3 z-4 max-w-72 rounded-md border border-(--shell-border) bg-(--shell-surface) px-3 py-2 text-[0.78rem] shadow-sm"
          data-testid="trend-overlay-tooltip"
        >
          <p className="m-0 font-semibold">{activeSpan.tooltip.headline}</p>
          <p className="m-0 mt-1 text-(--shell-muted)">{activeSpan.tooltip.detail}</p>
        </div>
      ) : null}
    </>
  );
};
