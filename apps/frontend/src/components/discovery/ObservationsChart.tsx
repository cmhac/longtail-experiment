"use client";

import React from "react";
import type { JSX } from "react";
import { Line, LineChart, Tooltip, XAxis, YAxis } from "recharts";
import type { ChartDataPoint, ObservationPoint } from "../../lib/api/discovery-types";
import { EmptyState } from "./EmptyState";
import { type TrendRangeKey, filterObservationRange } from "./dataset-detail-view-model";

interface ObservationsChartProps {
  observations: ObservationPoint[];
}

const toChartData = (observations: ObservationPoint[]): ChartDataPoint[] => {
  return observations.map((observation) => ({
    date: observation.observed_on,
    value: observation.value,
  }));
};

export const ObservationsChart = ({ observations }: ObservationsChartProps): JSX.Element => {
  const [selectedRange, setSelectedRange] = React.useState<TrendRangeKey>("1Y");

  if (observations.length === 0) {
    return <EmptyState message="No observation data available" />;
  }

  const filtered = filterObservationRange(observations, selectedRange);
  const chartData = toChartData(filtered);
  const rangeOptions: TrendRangeKey[] = ["1M", "6M", "1Y", "ALL"];

  return (
    <div aria-label="Time series chart" data-testid="observations-chart">
      <div className="observations-chart-controls" data-testid="observations-chart-controls">
        {rangeOptions.map((range) => (
          <button
            aria-pressed={selectedRange === range}
            className="observations-chart-range"
            key={range}
            onClick={() => {
              setSelectedRange(range);
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
      <p className="observations-chart-footnote" data-testid="observations-chart-footnote">
        Showing {chartData.length} observations
      </p>
    </div>
  );
};
