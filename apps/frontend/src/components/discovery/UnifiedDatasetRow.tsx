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

const toMetadataSlug = (value: string): string => {
  return (
    value
      .trim()
      .toLowerCase()
      .replace(/[^a-z0-9]+/g, "-")
      .replace(/^-+|-+$/g, "") || "unknown"
  );
};

const renderPill = (label: string, href: string, emphasized: boolean): JSX.Element => (
  <Link
    className={
      emphasized ? "recent-updates-pill recent-updates-geography-pill" : "recent-updates-pill"
    }
    href={href}
    key={`${emphasized ? "em" : "tag"}-${label}`}
  >
    {label}
  </Link>
);

const renderPills = (tagPills: string[], emphasizedPills: string[]): JSX.Element | null => {
  const hasPills = emphasizedPills.length > 0 || tagPills.length > 0;

  if (!hasPills) {
    return null;
  }

  return (
    <div className="recent-updates-pills" data-testid="unified-dataset-row-pills">
      {emphasizedPills.map((pill) =>
        renderPill(pill, `/geographies/${encodeURIComponent(toMetadataSlug(pill))}`, true),
      )}
      {tagPills.map((tag) =>
        renderPill(tag, `/topics/${encodeURIComponent(toMetadataSlug(tag))}`, false),
      )}
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
  void datasetId;
  void interactionMode;
  const pills = renderPills(tagPills, emphasizedPills);

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
