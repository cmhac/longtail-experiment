import Link from "next/link";
import React from "react";
import type { JSX } from "react";
import type { DatasetDetail } from "../../lib/api/discovery-types";

interface DatasetDetailHeaderProps {
  data: DatasetDetail;
  exportHref?: string;
}

const toMetadataSlug = (value: string): string => {
  return (
    value
      .trim()
      .toLowerCase()
      .replace(/[^a-z0-9]+/g, "-")
      .replace(/^-+|-+$/g, "") || "unknown"
  );
};

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
            <Link
              className="discovery-topic-tag recent-updates-geography-pill"
              href={`/geographies/${encodeURIComponent(toMetadataSlug(data.geographic_scope))}`}
            >
              {data.geographic_scope}
            </Link>
          ) : null}
          {data.topic_tags.length > 0 ? (
            data.topic_tags.map((tag) => (
              <Link
                href={`/topics/${encodeURIComponent(toMetadataSlug(tag))}`}
                key={tag}
                className="discovery-topic-tag"
              >
                {tag}
              </Link>
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
