import React from "react";
import type { JSX } from "react";

import type { SourceSummary } from "../../lib/api/discovery-types";

interface SourceDetailHeaderProps {
  source: SourceSummary;
}

export const SourceDetailHeader = ({ source }: SourceDetailHeaderProps): JSX.Element => {
  return (
    <header className="source-detail-header" data-testid="source-detail-header">
      <div className="source-detail-header-copy">
        <p className="source-detail-eyebrow">Source</p>
        <h1 className="discovery-list-title">{source.name}</h1>
        <p className="discovery-list-total source-detail-count" data-testid="source-detail-count">
          {Intl.NumberFormat("en-US").format(source.dataset_count)} total datasets
        </p>
      </div>
    </header>
  );
};
