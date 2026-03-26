import React from "react";
import type { JSX } from "react";

import type { GeographySummary } from "../../lib/api/discovery-types";

interface GeographyDetailHeaderProps {
  geography: GeographySummary;
}

export const GeographyDetailHeader = ({ geography }: GeographyDetailHeaderProps): JSX.Element => {
  return (
    <header className="geography-detail-header" data-testid="geography-detail-header">
      <div className="geography-detail-header-copy">
        <p className="source-detail-eyebrow">Geography</p>
        <h1 className="discovery-list-title">{geography.label}</h1>
        <p
          className="discovery-list-total geography-detail-count"
          data-testid="geography-detail-count"
        >
          {Intl.NumberFormat("en-US").format(geography.dataset_count)} total datasets
        </p>
      </div>
    </header>
  );
};
