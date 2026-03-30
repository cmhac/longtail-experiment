"use client";

import React from "react";
import type { JSX } from "react";
import { Line, LineChart, Tooltip, XAxis, YAxis } from "recharts";
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

const CHART_MIN_HEIGHT = 288;
const CHART_MAX_HEIGHT = 360;
const CHART_ASPECT_RATIO = 0.54;
const CHART_DEFAULT_WIDTH = 640;
const Y_AXIS_MIN_PADDING_RATIO = 0.05;
const Y_AXIS_FALLBACK_PADDING = 1;

const formatSignedNumber = (value: number, maximumFractionDigits: number): string => {
  const abs = Math.abs(value);
  const sign = value > 0 ? "+" : value < 0 ? "-" : "";
  return `${sign}${new Intl.NumberFormat("en-US", {
    maximumFractionDigits,
    minimumFractionDigits: maximumFractionDigits,
  }).format(abs)}`;
};

const formatAxisNumber = (value: number): string => {
  return new Intl.NumberFormat("en-US", {
    maximumFractionDigits: 1,
    minimumFractionDigits: 0,
  }).format(value);
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

const getYAxisDomain = (chartData: ObservationChartPoint[]): [number, number] => {
  if (chartData.length === 0) {
    return [0, 1];
  }

  const values = chartData.map((point) => point.value);
  const minValue = Math.min(...values);
  const maxValue = Math.max(...values);
  const spread = maxValue - minValue;
  const padding =
    spread === 0
      ? Math.max(Math.abs(maxValue) * Y_AXIS_MIN_PADDING_RATIO, Y_AXIS_FALLBACK_PADDING)
      : spread * Y_AXIS_MIN_PADDING_RATIO;

  return [minValue - padding, maxValue + padding];
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
  const [chartWidth, setChartWidth] = React.useState(CHART_DEFAULT_WIDTH);
  const chartContainerRef = React.useRef<HTMLDivElement | null>(null);
  const preferredRange = selectedRange ?? internalRange;
  const activeRange = availableRanges.includes(preferredRange) ? preferredRange : "ALL";

  if (observations.length === 0) {
    return <EmptyState message="No observation data available" />;
  }

  const filtered = filterObservationRange(observations, activeRange);
  const chartData = toChartData(filtered, unitType, unitLabel);
  const yAxisDomain = getYAxisDomain(chartData);
  const chartHeight = Math.max(
    CHART_MIN_HEIGHT,
    Math.min(CHART_MAX_HEIGHT, Math.round(chartWidth * CHART_ASPECT_RATIO)),
  );

  const handleRangeChange = (range: TrendRangeKey): void => {
    if (onRangeChange) {
      onRangeChange(range);
      return;
    }
    setInternalRange(range);
  };

  React.useEffect(() => {
    const container = chartContainerRef.current;
    if (!container) {
      return;
    }

    const updateWidth = (): void => {
      const nextWidth = container.getBoundingClientRect().width;
      setChartWidth(nextWidth > 0 ? nextWidth : CHART_DEFAULT_WIDTH);
    };

    updateWidth();

    const resizeObserver = new ResizeObserver(() => {
      updateWidth();
    });
    resizeObserver.observe(container);

    return () => {
      resizeObserver.disconnect();
    };
  }, []);

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
      <div className="w-full min-w-0 flex-1" ref={chartContainerRef}>
        <LineChart
          data={chartData}
          height={chartHeight}
          margin={{ bottom: 18, left: 8, right: 8, top: 8 }}
          width={chartWidth}
        >
          <XAxis dataKey="date" minTickGap={32} tickMargin={14} />
          <YAxis domain={yAxisDomain} tickFormatter={formatAxisNumber} />
          <Tooltip content={<ObservationsChartTooltip />} cursor={false} />
          <Line
            dataKey="value"
            dot={false}
            stroke="var(--shell-foreground)"
            strokeWidth={2.25}
            type="monotone"
          />
        </LineChart>
      </div>
    </div>
  );
};
