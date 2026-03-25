import React from "react";
import type { JSX } from "react";
import type { DatasetDetail } from "../../lib/api/discovery-types";

interface DatasetDetailHeaderProps {
  data: DatasetDetail;
  exportHref?: string;
}

export const DatasetDetailHeader = ({
  data,
  exportHref = "#",
}: DatasetDetailHeaderProps): JSX.Element => {
  return (
    <header className="discovery-dataset-detail-header" data-testid="dataset-detail-header">
      <div className="dataset-detail-header-content">
        <p className="dataset-detail-source">Data Source: {data.source.name}</p>
        <h1>{data.title}</h1>
        <p className="dataset-detail-description">
          {data.description ?? "No description available"}
        </p>
      </div>

      <div className="dataset-detail-meta-row" data-testid="dataset-detail-meta-row">
        <div aria-label="Topic tags" className="dataset-detail-topic-tags">
          {data.geographic_scope ? (
            <span className="discovery-topic-tag recent-updates-geography-pill">
              {data.geographic_scope}
            </span>
          ) : null}
          {data.topic_tags.length > 0 ? (
            data.topic_tags.map((tag) => (
              <span key={tag} className="discovery-topic-tag">
                {tag}
              </span>
            ))
          ) : (
            <span>No topic tags</span>
          )}
        </div>

        <div
          className="dataset-detail-utility-actions"
          data-testid="dataset-detail-utility-actions"
        >
          <a className="dataset-detail-action-export" href={exportHref}>
            Export CSV
          </a>
        </div>
      </div>
    </header>
  );
};
