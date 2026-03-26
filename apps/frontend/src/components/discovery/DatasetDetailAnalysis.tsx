"use client";

import React from "react";
import type { JSX } from "react";
import type { DatasetDetail } from "../../lib/api/discovery-types";
import { DatasetDetailInsights } from "./DatasetDetailInsights";
import { ObservationsChart } from "./ObservationsChart";
import type { TrendRangeKey } from "./dataset-detail-view-model";

interface DatasetDetailAnalysisProps {
  data: DatasetDetail;
}

export const DatasetDetailAnalysis = ({ data }: DatasetDetailAnalysisProps): JSX.Element => {
  const [selectedRange, setSelectedRange] = React.useState<TrendRangeKey>("1Y");

  return (
    <>
      <DatasetDetailInsights data={data} selectedRange={selectedRange} />

      <section className="dataset-detail-trend" data-testid="dataset-detail-trend-section">
        <h2>Historical Trend</h2>
        <ObservationsChart
          observations={data.observations}
          onRangeChange={setSelectedRange}
          selectedRange={selectedRange}
        />
      </section>
    </>
  );
};
