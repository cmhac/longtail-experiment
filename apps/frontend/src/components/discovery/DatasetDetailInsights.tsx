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
    <aside className="dataset-detail-insights" data-testid="dataset-detail-insights">
      <section className="dataset-detail-metric-rail" data-testid="dataset-detail-metric-rail">
        {metrics.map((metric) => (
          <article className="dataset-detail-metric-card" key={metric.label}>
            <p className="dataset-detail-metric-label">{metric.label}</p>
            <p className="dataset-detail-metric-value">{metric.value}</p>
            {metric.movementSummary ? (
              <p
                className={`dataset-detail-metric-movement dataset-detail-metric-movement-${metric.movementState}`}
              >
                {metric.movementSummary}
              </p>
            ) : null}
          </article>
        ))}
      </section>

      <section className="dataset-detail-metadata" data-testid="dataset-detail-metadata">
        <h2>Metadata</h2>
        <dl>
          {metadataRows.map((row) => (
            <div key={row.key}>
              <dt>{row.key}</dt>
              <dd>{row.value}</dd>
            </div>
          ))}
        </dl>
      </section>
    </aside>
  );
};
