import { Card } from "@heroui/react/card";
import React from "react";
import type { JSX } from "react";
import type { DatasetDetail } from "../../lib/api/discovery-types";
import {
  type TrendRangeKey,
  buildInsightMetrics,
  getMetadataRows,
} from "./dataset-detail-view-model";

interface DatasetDetailInsightsProps {
  data: DatasetDetail;
  selectedRange?: TrendRangeKey;
}

export const DatasetDetailInsights = ({
  data,
  selectedRange = "1Y",
}: DatasetDetailInsightsProps): JSX.Element => {
  const metrics = buildInsightMetrics(data, selectedRange);
  const metadataRows = getMetadataRows(data);

  return (
    <aside className="grid gap-3" data-testid="dataset-detail-insights">
      <section className="grid gap-[0.65rem]" data-testid="dataset-detail-metric-rail">
        {metrics.map((metric) => (
          <Card
            className="border border-(--shell-border) bg-[color-mix(in_srgb,var(--shell-background)_98%,#000000)] p-[1.2rem]"
            key={metric.label}
            variant="default"
          >
            <p className="m-0 text-(--shell-muted) text-[0.7rem] uppercase tracking-widest">
              {metric.label}
            </p>
            <p className="mt-[0.28rem] font-[Iowan_Old_Style,Palatino_Linotype,Times_New_Roman,serif] text-[1.65rem] leading-none">
              {metric.value}
            </p>
            {metric.movementSummary ? (
              <p
                className={`dataset-detail-metric-movement dataset-detail-metric-movement-${metric.movementState} mt-[0.3rem] text-[0.82rem]`}
              >
                {metric.movementSummary}
              </p>
            ) : null}
          </Card>
        ))}
      </section>

      <Card
        className="bg-transparent p-[0.8rem] shadow-none"
        data-testid="dataset-detail-metadata"
        variant="default"
      >
        <h2 className="m-0 font-[Iowan_Old_Style,Palatino_Linotype,Times_New_Roman,serif] text-[1.4rem]">
          Metadata
        </h2>
        <dl className="mt-[0.7rem] grid gap-2">
          {metadataRows.map((row) => (
            <div className="flex justify-between gap-[0.85rem]" key={row.key}>
              <dt className="text-(--shell-muted)">{row.key}</dt>
              <dd className="m-0 font-bold">{row.value}</dd>
            </div>
          ))}
        </dl>
      </Card>
    </aside>
  );
};
