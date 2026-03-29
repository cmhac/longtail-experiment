"use client";

import React from "react";
import type { JSX } from "react";
import { Line, LineChart, Tooltip, XAxis, YAxis } from "recharts";
import type { ChartDataPoint, ObservationPoint } from "../../lib/api/discovery-types";
import { EmptyState } from "./EmptyState";
import { type TrendRangeKey, filterObservationRange } from "./dataset-detail-view-model";

interface ObservationsChartProps {
  observations: ObservationPoint[];
  selectedRange?: TrendRangeKey;
  onRangeChange?: (range: TrendRangeKey) => void;
}

const toChartData = (observations: ObservationPoint[]): ChartDataPoint[] => {
  return observations.map((observation) => ({
    date: observation.observed_on,
    value: observation.value,
  }));
};

export const ObservationsChart = ({
  observations,
  selectedRange,
  onRangeChange,
}: ObservationsChartProps): JSX.Element => {
  const [internalRange, setInternalRange] = React.useState<TrendRangeKey>("1Y");
  const activeRange = selectedRange ?? internalRange;

  if (observations.length === 0) {
    return <EmptyState message="No observation data available" />;
  }

  const filtered = filterObservationRange(observations, activeRange);
  const chartData = toChartData(filtered);
  const rangeOptions: TrendRangeKey[] = ["1M", "6M", "1Y", "ALL"];

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
      className="overflow-x-auto rounded-lg border border-(--shell-border) bg-(--shell-surface) p-2"
      data-testid="observations-chart"
    >
      <div
        className="mb-[0.45rem] flex justify-end gap-[0.35rem]"
        data-testid="observations-chart-controls"
      >
        {rangeOptions.map((range) => (
          <button
            aria-pressed={activeRange === range}
            className="border border-(--shell-border) bg-(--shell-surface) px-[0.52rem] py-[0.2rem] text-[0.68rem] tracking-[0.06em] aria-pressed:border-[var(--shell-foreground)] aria-pressed:bg-[var(--shell-foreground)] aria-pressed:text-[var(--shell-surface)]"
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
      <LineChart data={chartData} height={300} width={700}>
        <XAxis dataKey="date" />
        <YAxis />
        <Tooltip />
        <Line dataKey="value" stroke="#111111" type="monotone" />
      </LineChart>
      <p
        className="mt-[0.45rem] mb-0 text-(--shell-muted) text-[0.8rem]"
        data-testid="observations-chart-footnote"
      >
        Showing {chartData.length} observations
      </p>
    </div>
  );
};
