import { notFound } from "next/navigation";
import React from "react";
import type { JSX } from "react";

import { DatasetCatalogList } from "../../../components/discovery/DatasetCatalogList";
import { EmptyState } from "../../../components/discovery/EmptyState";
import { ErrorState } from "../../../components/discovery/ErrorState";
import { SourceDetailHeader } from "../../../components/discovery/SourceDetailHeader";
import { fetchSourceDetail } from "../../../lib/api/discovery-client";
import { SiteHeader } from "../../../shell/site-header";
import { SHELL_LAYOUT_CLASS_NAMES } from "../../../theme/monochrome-theme";

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
    const detail = await fetchSourceDetail(sourceId);

    return (
      <div className="shell-page shell-scroll-anchor" data-testid="site-shell">
        <SiteHeader activeTab="sources" />
        <main
          className={SHELL_LAYOUT_CLASS_NAMES.constrainedContent}
          data-testid="source-detail-page"
        >
          <SourceDetailHeader source={detail.source} />
          {detail.datasets.length > 0 ? (
            <DatasetCatalogList
              emptyMessage="No datasets are currently available for this source."
              items={detail.datasets}
            />
          ) : (
            <EmptyState message="No datasets are currently available for this source." />
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
        <SiteHeader activeTab="sources" />
        <main
          className={SHELL_LAYOUT_CLASS_NAMES.constrainedContent}
          data-testid="source-detail-page"
        >
          <ErrorState />
        </main>
      </div>
    );
  }
};

export default SourceDetailPage;
