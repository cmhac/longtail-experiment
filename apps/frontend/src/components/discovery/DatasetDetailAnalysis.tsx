"use client";

import React from "react";
import type { JSX } from "react";
import type { DatasetDetail } from "../../lib/api/discovery-types";
import { DatasetDetailInsights } from "./DatasetDetailInsights";
import { ObservationsChart } from "./ObservationsChart";
import { ChartSurfaceCard } from "./chart-controls/ChartSurfaceCard";
import {
  DEFAULT_RELATIVE_CHANGE_SETTINGS,
  type RelativeChangeSettings,
  type TrendRangeKey,
} from "./dataset-detail-view-model";

interface DatasetDetailAnalysisProps {
  data: DatasetDetail;
}

export const DatasetDetailAnalysis = ({ data }: DatasetDetailAnalysisProps): JSX.Element => {
  const [selectedRange, setSelectedRange] = React.useState<TrendRangeKey>("ALL");
  const [relativeSettings, setRelativeSettings] = React.useState<RelativeChangeSettings>(
    DEFAULT_RELATIVE_CHANGE_SETTINGS,
  );

  return (
    <>
      <DatasetDetailInsights
        data={data}
        relativeSettings={relativeSettings}
        selectedRange={selectedRange}
      />

      <ChartSurfaceCard
        className="grid h-full min-h-96 min-w-0 grid-rows-[auto_minmax(0,1fr)] gap-[0.7rem] border border-(--shell-border) bg-(--shell-surface) p-4 shadow-sm max-md:p-[0.8rem]"
        testId="dataset-detail-trend-section"
        title="Historical Trend"
      >
        <ObservationsChart
          onRelativeSettingsChange={setRelativeSettings}
          observations={data.observations}
          relativeSettings={relativeSettings}
          onRangeChange={setSelectedRange}
          selectedRange={selectedRange}
          unitLabel={data.metadata.unit ?? data.metadata.units}
          unitType={data.metadata.unit_type}
        />
      </ChartSurfaceCard>
    </>
  );
};
