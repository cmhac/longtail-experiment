import Link from "next/link";
import React from "react";
import type { JSX } from "react";

import type { SourceSummary } from "../../lib/api/discovery-types";

interface SourceListRowProps {
  source: SourceSummary;
}

const formatDatasetCount = (count: number): string => {
  return `${Intl.NumberFormat("en-US").format(count)} ${count === 1 ? "dataset" : "datasets"}`;
};

const buildSummaryText = (source: SourceSummary): string => {
  const countLabel = formatDatasetCount(source.dataset_count);
  if (source.source_type) {
    return `Browse ${countLabel} from this ${source.source_type.toLowerCase()} source.`;
  }

  return `Browse ${countLabel} from this source.`;
};

export const SourceListRow = ({ source }: SourceListRowProps): JSX.Element => {
  return (
    <Link
      className="recent-updates-row source-directory-row"
      data-testid="source-list-row"
      href={`/sources/${encodeURIComponent(source.id)}`}
    >
      <div className="recent-updates-meta-rail source-directory-meta-rail">
        <span className="recent-updates-source">
          {source.source_type ? source.source_type.toUpperCase() : "SOURCE"}
        </span>
        <span className="recent-updates-date">{formatDatasetCount(source.dataset_count)}</span>
      </div>
      <div className="recent-updates-body">
        <h3 className="source-directory-title" data-testid="source-list-row-title">
          {source.name}
        </h3>
        <p>{buildSummaryText(source)}</p>
      </div>
    </Link>
  );
};
