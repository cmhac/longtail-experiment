import { notFound } from "next/navigation";
import React from "react";
import type { JSX } from "react";

import { EmptyState } from "../../../components/discovery/EmptyState";
import { ErrorState } from "../../../components/discovery/ErrorState";
import { InfiniteCatalogList } from "../../../components/discovery/InfiniteCatalogList";
import { SourceDetailHeader } from "../../../components/discovery/SourceDetailHeader";
import { fetchSourceDetail } from "../../../lib/api/discovery-client";
import { SitePageFrame } from "../../../shell/site-page-frame";

interface SourceDetailPageProps {
  params: Promise<{ sourceId: string }>;
}

const isNotFoundError = (error: unknown): boolean => {
  if (!error || typeof error !== "object") {
    return false;
  }

  return "status" in error && (error as { status?: number }).status === 404;
};

const SourceDetailPage = async ({ params }: SourceDetailPageProps): Promise<JSX.Element> => {
  try {
    const { sourceId } = await params;
    const firstPage = await fetchSourceDetail(sourceId, { page: 1 });

    return (
      <SitePageFrame
        activeTab="sources"
        mainClassName="grid content-start gap-4"
        mainTestId="source-detail-page"
      >
        <SourceDetailHeader source={firstPage.source} />
        {firstPage.items.length > 0 ? (
          <InfiniteCatalogList
            emptyMessage="No datasets are currently available for this source."
            initialItems={firstPage.items}
            initialPage={firstPage.page}
            initialTotalPages={firstPage.total_pages}
            requestPath={`/api/discovery/sources/${encodeURIComponent(sourceId)}`}
          />
        ) : (
          <EmptyState message="No datasets are currently available for this source." />
        )}
      </SitePageFrame>
    );
  } catch (error) {
    if (isNotFoundError(error)) {
      notFound();
    }

    return (
      <SitePageFrame
        activeTab="sources"
        mainClassName="grid content-start gap-4"
        mainTestId="source-detail-page"
      >
        <ErrorState />
      </SitePageFrame>
    );
  }
};

export default SourceDetailPage;
