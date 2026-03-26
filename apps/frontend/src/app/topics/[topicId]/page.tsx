import { notFound } from "next/navigation";
import React from "react";
import type { JSX } from "react";

import { DatasetCatalogList } from "../../../components/discovery/DatasetCatalogList";
import { EmptyState } from "../../../components/discovery/EmptyState";
import { ErrorState } from "../../../components/discovery/ErrorState";
import { TopicDetailHeader } from "../../../components/discovery/TopicDetailHeader";
import { fetchTopicDetail } from "../../../lib/api/discovery-client";
import { SiteHeader } from "../../../shell/site-header";
import { SHELL_LAYOUT_CLASS_NAMES } from "../../../theme/monochrome-theme";

interface TopicDetailPageProps {
  params: Promise<{ topicId: string }>;
}

const isNotFoundError = (error: unknown): boolean => {
  if (!error || typeof error !== "object") {
    return false;
  }

  return "status" in error && (error as { status?: number }).status === 404;
};

const TopicDetailPage = async ({ params }: TopicDetailPageProps): Promise<JSX.Element> => {
  try {
    const { topicId } = await params;
    const detail = await fetchTopicDetail(topicId);

    return (
      <div className="shell-page shell-scroll-anchor" data-testid="site-shell">
        <SiteHeader activeTab="datasets" />
        <main
          className={SHELL_LAYOUT_CLASS_NAMES.constrainedContent}
          data-testid="topic-detail-page"
        >
          <TopicDetailHeader topic={detail.topic} />
          {detail.datasets.length > 0 ? (
            <DatasetCatalogList
              emptyMessage="No datasets are currently available for this topic."
              items={detail.datasets}
            />
          ) : (
            <EmptyState message="No datasets are currently available for this topic." />
          )}
        </main>
      </div>
    );
  } catch (error) {
    if (isNotFoundError(error)) {
      notFound();
    }

    return (
      <div className="shell-page shell-scroll-anchor" data-testid="site-shell">
        <SiteHeader activeTab="datasets" />
        <main
          className={SHELL_LAYOUT_CLASS_NAMES.constrainedContent}
          data-testid="topic-detail-page"
        >
          <ErrorState />
        </main>
      </div>
    );
  }
};

export default TopicDetailPage;
