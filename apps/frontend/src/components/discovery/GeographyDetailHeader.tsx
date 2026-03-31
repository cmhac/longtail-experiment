import React from "react";
import type { JSX } from "react";

import type { GeographySummary } from "../../lib/api/discovery-types";
import { PageHeaderKicker, PageHeaderTitle, PageHeaderWrapper } from "./PageHeader";

interface GeographyDetailHeaderProps {
  geography: GeographySummary;
}

export const GeographyDetailHeader = ({ geography }: GeographyDetailHeaderProps): JSX.Element => {
  return (
    <PageHeaderWrapper className="mb-4! pt-2" testId="geography-detail-header">
      <div className="grid gap-[0.35rem]">
        <PageHeaderKicker>Geography</PageHeaderKicker>
        <PageHeaderTitle>{geography.label}</PageHeaderTitle>
        <PageHeaderKicker className="tracking-[0.16em]" testId="geography-detail-count">
          {Intl.NumberFormat("en-US").format(geography.dataset_count)} total datasets
        </PageHeaderKicker>
      </div>
    </PageHeaderWrapper>
  );
};
