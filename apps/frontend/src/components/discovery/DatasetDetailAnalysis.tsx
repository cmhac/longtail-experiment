"use client";

import { Card } from "@heroui/react";
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

      <Card
        className="grid gap-[0.7rem] border border-(--shell-border) bg-(--shell-surface) p-4 shadow-sm max-md:p-[0.8rem]"
        data-testid="dataset-detail-trend-section"
        variant="default"
      >
        <h2 className="m-0 font-[Iowan_Old_Style,Palatino_Linotype,Times_New_Roman,serif] text-[1.4rem]">
          Historical Trend
        </h2>
        <ObservationsChart
          observations={data.observations}
          onRangeChange={setSelectedRange}
          selectedRange={selectedRange}
        />
      </Card>
    </>
  );
};
