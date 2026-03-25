import Link from "next/link";
import React from "react";
import type { JSX } from "react";

export interface UnifiedDatasetRowProps {
  datasetId: string;
  destinationHref: string;
  sourceLabel: string;
  updatedLabel: string;
  title: string;
  summaryText?: string;
  tagPills: string[];
  emphasizedPills?: string[];
  interactionMode: "row_link" | "title_link";
}

const renderPills = (tagPills: string[], emphasizedPills: string[]): JSX.Element | null => {
  const hasPills = emphasizedPills.length > 0 || tagPills.length > 0;

  if (!hasPills) {
    return null;
  }

  return (
    <div className="recent-updates-pills" data-testid="unified-dataset-row-pills">
      {emphasizedPills.map((pill) => (
        <span className="recent-updates-pill recent-updates-geography-pill" key={`em-${pill}`}>
          {pill}
        </span>
      ))}
      {tagPills.map((tag) => (
        <span className="recent-updates-pill" key={`tag-${tag}`}>
          {tag}
        </span>
      ))}
    </div>
  );
};

export const UnifiedDatasetRow = ({
  datasetId,
  destinationHref,
  emphasizedPills = [],
  interactionMode,
  sourceLabel,
  summaryText,
  tagPills,
  title,
  updatedLabel,
}: UnifiedDatasetRowProps): JSX.Element => {
  const pills = renderPills(tagPills, emphasizedPills);

  if (interactionMode === "row_link") {
    return (
      <Link
        className="recent-updates-row unified-dataset-row"
        data-testid="unified-dataset-row"
        href={destinationHref}
      >
        <div className="recent-updates-meta-rail">
          <span className="recent-updates-source">{sourceLabel}</span>
          <span className="recent-updates-date">{updatedLabel}</span>
        </div>
        <div className="recent-updates-body">
          <h3 data-testid="unified-dataset-row-title">{title}</h3>
          {summaryText ? <p>{summaryText}</p> : null}
          {pills}
        </div>
      </Link>
    );
  }

  return (
    <article className="recent-updates-row unified-dataset-row" data-testid="unified-dataset-row">
      <div className="recent-updates-meta-rail">
        <span className="recent-updates-source">{sourceLabel}</span>
        <span className="recent-updates-date">{updatedLabel}</span>
      </div>
      <div className="recent-updates-body">
        <h3 data-testid="unified-dataset-row-title">
          <Link href={destinationHref}>{title}</Link>
        </h3>
        {summaryText ? <p>{summaryText}</p> : null}
        {pills}
      </div>
    </article>
  );
};

export const UNIFIED_DATASET_ROW_VERSION = "v1";
