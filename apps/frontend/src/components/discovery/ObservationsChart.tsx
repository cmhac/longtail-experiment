"use client";

import React from "react";
import type { JSX } from "react";
import { Line, LineChart, Tooltip, XAxis, YAxis } from "recharts";
import type { ChartDataPoint, ObservationPoint } from "../../lib/api/discovery-types";
import { EmptyState } from "./EmptyState";

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
  if (observations.length === 0) {
    return <EmptyState message="No observation data available" />;
  }

  const chartData = toChartData(observations);

  return (
    <div aria-label="Time series chart" data-testid="observations-chart">
      <LineChart data={chartData} height={300} width={700}>
        <XAxis dataKey="date" />
        <YAxis />
        <Tooltip />
        <Line dataKey="value" stroke="#111111" type="monotone" />
      </LineChart>
    </div>
  );
};
