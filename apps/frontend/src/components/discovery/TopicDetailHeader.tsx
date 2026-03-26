import React from "react";
import type { JSX } from "react";

import type { TopicSummary } from "../../lib/api/discovery-types";

interface TopicDetailHeaderProps {
  topic: TopicSummary;
}

export const TopicDetailHeader = ({ topic }: TopicDetailHeaderProps): JSX.Element => {
  return (
    <header className="topic-detail-header" data-testid="topic-detail-header">
      <div className="topic-detail-header-copy">
        <p className="source-detail-eyebrow">Topic</p>
        <h1 className="discovery-list-title">{topic.label}</h1>
        <p className="discovery-list-total topic-detail-count" data-testid="topic-detail-count">
          {Intl.NumberFormat("en-US").format(topic.dataset_count)} total datasets
        </p>
      </div>
    </header>
  );
};
