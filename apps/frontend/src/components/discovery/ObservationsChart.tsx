"use client";

import React from "react";
import type { JSX } from "react";
import { Line, LineChart, ResponsiveContainer, Tooltip, XAxis, YAxis } from "recharts";
import type { ObservationPoint } from "../../lib/api/discovery-types";
import { EmptyState } from "./EmptyState";
import {
  type TrendRangeKey,
  filterObservationRange,
  formatObservedOn,
  formatValue,
  getAvailableTrendRanges,
} from "./dataset-detail-view-model";

interface ObservationsChartProps {
  observations: ObservationPoint[];
  unitLabel?: string | null | undefined;
  unitType?: string | null | undefined;
  selectedRange?: TrendRangeKey;
  onRangeChange?: (range: TrendRangeKey) => void;
}

interface ObservationChartPoint {
  changePercent: number | null;
  changeValue: number | null;
  date: string;
  dateLabel: string;
  value: number;
  valueLabel: string;
}

interface ObservationTooltipContentProps {
  active?: boolean;
  payload?: Array<{
    payload?: ObservationChartPoint;
  }>;
}

const formatSignedNumber = (value: number, maximumFractionDigits: number): string => {
  const abs = Math.abs(value);
  const sign = value > 0 ? "+" : value < 0 ? "-" : "";
  return `${sign}${new Intl.NumberFormat("en-US", {
    maximumFractionDigits,
    minimumFractionDigits: maximumFractionDigits,
  }).format(abs)}`;
};

const toChartData = (
  observations: ObservationPoint[],
  unitType?: string | null,
  unitLabel?: string | null,
): ObservationChartPoint[] => {
  return observations.map((observation, index) => {
    const previous = index > 0 ? observations[index - 1] : null;
    const changeValue = previous ? observation.value - previous.value : null;
    const changePercent =
      previous && previous.value !== 0 && changeValue !== null
        ? (changeValue / previous.value) * 100
        : null;

    return {
      changePercent,
      changeValue,
      date: observation.observed_on,
      dateLabel: formatObservedOn(observation.observed_on),
      value: observation.value,
      valueLabel: formatValue(observation.value, unitType, unitLabel),
    };
  });
};

const ObservationsChartTooltip = ({
  active,
  payload,
}: ObservationTooltipContentProps): JSX.Element | null => {
  if (!active || !payload?.length || !payload[0]?.payload) {
    return null;
  }

  const point = payload[0].payload;
  const isPositive = (point.changeValue ?? 0) > 0;
  const isNegative = (point.changeValue ?? 0) < 0;
  const movementClass = isPositive
    ? "text-emerald-700 dark:text-emerald-300"
    : isNegative
      ? "text-rose-700 dark:text-rose-300"
      : "text-(--shell-muted)";

  return (
    <div className="min-w-[12rem] rounded-[1.15rem] bg-[color-mix(in_srgb,var(--shell-background)_96%,#ffffff)] px-5 py-4 shadow-[0_18px_50px_rgba(15,23,42,0.14)] ring-1 ring-[color-mix(in_srgb,var(--shell-border)_82%,transparent)] backdrop-blur-sm">
      <p className="m-0 font-[Iowan_Old_Style,Palatino_Linotype,Times_New_Roman,serif] text-(--shell-muted) text-[1.05rem] italic">
        {point.dateLabel}
      </p>
      <div className="mt-4 h-px w-16 bg-(--shell-border)" />
      <p className="mt-5 font-[Iowan_Old_Style,Palatino_Linotype,Times_New_Roman,serif] text-(--shell-foreground) text-[2.4rem] leading-none">
        {point.valueLabel}
      </p>
      {point.changeValue !== null && point.changePercent !== null ? (
        <p className={`mt-3 font-semibold text-[1.05rem] ${movementClass}`}>
          {`${formatSignedNumber(point.changeValue, 3)} (${formatSignedNumber(point.changePercent, 2)}%)`}
        </p>
      ) : (
        <p className="mt-3 text-(--shell-muted) text-[0.95rem]">No prior observation</p>
      )}
    </div>
  );
};

export const ObservationsChart = ({
  observations,
  unitLabel,
  unitType,
  selectedRange,
  onRangeChange,
}: ObservationsChartProps): JSX.Element => {
  const availableRanges = getAvailableTrendRanges(observations);
  const [internalRange, setInternalRange] = React.useState<TrendRangeKey>("ALL");
  const preferredRange = selectedRange ?? internalRange;
  const activeRange = availableRanges.includes(preferredRange) ? preferredRange : "ALL";

  if (observations.length === 0) {
    return <EmptyState message="No observation data available" />;
  }

  const filtered = filterObservationRange(observations, activeRange);
  const chartData = toChartData(filtered, unitType, unitLabel);

  const handleRangeChange = (range: TrendRangeKey): void => {
    if (onRangeChange) {
      onRangeChange(range);
      return;
    }
    setInternalRange(range);
  };

  return (
    <div
      aria-label="Time series chart"
      className="flex h-full min-h-[20rem] min-w-0 flex-col bg-(--shell-surface) pt-1"
      data-testid="observations-chart"
    >
      {availableRanges.length > 1 ? (
        <div
          className="mb-[0.7rem] flex flex-wrap justify-end gap-[0.35rem]"
          data-testid="observations-chart-controls"
        >
          {availableRanges.map((range) => (
            <button
              aria-pressed={activeRange === range}
              className="cursor-pointer border border-(--shell-border) bg-(--shell-surface) px-[0.52rem] py-[0.2rem] text-[0.68rem] tracking-[0.06em] aria-pressed:border-[var(--shell-foreground)] aria-pressed:bg-[var(--shell-foreground)] aria-pressed:text-[var(--shell-surface)]"
              key={range}
              onClick={() => {
                handleRangeChange(range);
              }}
              type="button"
            >
              {range}
            </button>
          ))}
        </div>
      ) : null}
      <div className="min-h-[18rem] w-full min-w-0 flex-1">
        <ResponsiveContainer height="100%" minHeight={288} minWidth={0} width="100%">
          <LineChart data={chartData} margin={{ bottom: 18, left: 8, right: 8, top: 8 }}>
            <XAxis dataKey="date" minTickGap={32} tickMargin={14} />
            <YAxis />
            <Tooltip content={<ObservationsChartTooltip />} cursor={false} />
            <Line dataKey="value" dot={false} stroke="var(--shell-foreground)" type="monotone" />
          </LineChart>
        </ResponsiveContainer>
      </div>
    </div>
  );
};
