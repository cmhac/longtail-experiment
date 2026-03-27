import { notFound } from "next/navigation";
import React from "react";
import type { JSX } from "react";

import { EmptyState } from "../../../components/discovery/EmptyState";
import { ErrorState } from "../../../components/discovery/ErrorState";
import { InfiniteCatalogList } from "../../../components/discovery/InfiniteCatalogList";
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
    const firstPage = await fetchTopicDetail(topicId, { page: 1 });

    return (
      <div className="shell-page shell-scroll-anchor" data-testid="site-shell">
        <SiteHeader activeTab="datasets" />
        <main
          className={SHELL_LAYOUT_CLASS_NAMES.constrainedContent}
          data-testid="topic-detail-page"
        >
          <TopicDetailHeader topic={firstPage.topic} />
          {firstPage.items.length > 0 ? (
            <InfiniteCatalogList
              emptyMessage="No datasets are currently available for this topic."
              initialItems={firstPage.items}
              initialPage={firstPage.page}
              initialTotalPages={firstPage.total_pages}
              requestPath={`/api/discovery/topics/${encodeURIComponent(topicId)}`}
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
