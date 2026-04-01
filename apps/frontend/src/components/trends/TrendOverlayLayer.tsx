"use client";

import React from "react";
import type { JSX } from "react";

import type { TrendVisualizationSpan } from "../../lib/api/discovery-types";
import { TREND_DIRECTION_TOKENS } from "./trendDirectionTokens";

export interface TrendOverlayLayerProps {
  activeSpanId: string | null;
  chartDates: string[];
  onHoverSpan: (spanId: string | null) => void;
  onTogglePinnedSpan: (spanId: string) => void;
  spans: TrendVisualizationSpan[];
}

const toDateMs = (value: string): number => Date.parse(`${value}T00:00:00Z`);

const toSpanId = (span: TrendVisualizationSpan, index: number): string =>
  `${span.trend_label}-${span.start_period}-${span.end_period}-${index}`;

const toPercent = (value: number, min: number, max: number): number => {
  if (max <= min) {
    return 0;
  }
  return ((value - min) / (max - min)) * 100;
};

export const TrendOverlayLayer = ({
  activeSpanId,
  chartDates,
  onHoverSpan,
  onTogglePinnedSpan,
  spans,
}: TrendOverlayLayerProps): JSX.Element | null => {
  if (spans.length === 0 || chartDates.length === 0) {
    return null;
  }

  const datePoints = chartDates.map(toDateMs).filter((value) => Number.isFinite(value));
  if (datePoints.length === 0) {
    return null;
  }

  const min = Math.min(...datePoints);
  const max = Math.max(...datePoints);

  return (
    <div className="pointer-events-none absolute inset-0 z-3" data-testid="trend-overlay-layer">
      {spans.map((span, index) => {
        const startMs = toDateMs(span.start_period);
        const endMs = toDateMs(span.end_period);
        if (!Number.isFinite(startMs) || !Number.isFinite(endMs)) {
          return null;
        }

        const left = Math.max(0, Math.min(100, toPercent(startMs, min, max)));
        const right = Math.max(0, Math.min(100, toPercent(endMs, min, max)));
        const width = Math.max(1, right - left);
        const spanId = toSpanId(span, index);
        const token = TREND_DIRECTION_TOKENS[span.direction];
        const isActive = activeSpanId === spanId;

        return (
          <button
            aria-label={`${token.ariaLabel}: ${span.tooltip.headline}`}
            className={`pointer-events-auto absolute top-[8%] h-[84%] rounded-sm border transition-opacity ${token.overlayClassName} ${isActive ? "opacity-100" : "opacity-70"}`}
            data-testid="trend-overlay-span"
            key={spanId}
            onBlur={() => onHoverSpan(null)}
            onClick={() => onTogglePinnedSpan(spanId)}
            onMouseEnter={() => onHoverSpan(spanId)}
            onMouseLeave={() => onHoverSpan(null)}
            style={{ left: `${left}%`, width: `${width}%` }}
            type="button"
          >
            <span
              className="absolute top-1 right-1 font-bold text-[0.66rem]"
              data-testid="trend-direction-icon"
            >
              {token.icon}
            </span>
          </button>
        );
      })}
    </div>
  );
};
