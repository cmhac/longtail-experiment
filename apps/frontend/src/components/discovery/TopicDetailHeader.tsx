import React from "react";
import type { JSX } from "react";

import type { TopicSummary } from "../../lib/api/discovery-types";
import { PageHeaderKicker, PageHeaderTitle, PageHeaderWrapper } from "./PageHeader";

interface TopicDetailHeaderProps {
  topic: TopicSummary;
}

export const TopicDetailHeader = ({ topic }: TopicDetailHeaderProps): JSX.Element => {
  return (
    <PageHeaderWrapper className="!mb-4 pt-2" testId="topic-detail-header">
      <div className="grid gap-[0.35rem]">
        <PageHeaderKicker>Topic</PageHeaderKicker>
        <PageHeaderTitle>{topic.label}</PageHeaderTitle>
        <PageHeaderKicker className="tracking-[0.16em]" testId="topic-detail-count">
          {Intl.NumberFormat("en-US").format(topic.dataset_count)} total datasets
        </PageHeaderKicker>
      </div>
    </PageHeaderWrapper>
  );
};
