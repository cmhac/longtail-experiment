import React from "react";
import type { JSX } from "react";

import type { SourceSummary } from "../../lib/api/discovery-types";
import { PageHeaderKicker, PageHeaderTitle, PageHeaderWrapper } from "./PageHeader";

interface SourceDetailHeaderProps {
  source: SourceSummary;
}

export const SourceDetailHeader = ({ source }: SourceDetailHeaderProps): JSX.Element => {
  return (
    <PageHeaderWrapper className="max-md:flex-col" testId="source-detail-header">
      <div className="grid gap-1">
        <PageHeaderKicker>Source</PageHeaderKicker>
        <PageHeaderTitle>{source.title}</PageHeaderTitle>
        <p className="m-0 max-w-[70ch] text-(--shell-muted) leading-[1.5]">{source.description}</p>
        <PageHeaderKicker className="tracking-[0.16em]" testId="source-detail-count">
          {Intl.NumberFormat("en-US").format(source.dataset_count)} total datasets
        </PageHeaderKicker>
      </div>
    </PageHeaderWrapper>
  );
};
