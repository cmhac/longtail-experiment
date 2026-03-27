import { notFound } from "next/navigation";
import React from "react";
import type { JSX } from "react";

import { EmptyState } from "../../../components/discovery/EmptyState";
import { ErrorState } from "../../../components/discovery/ErrorState";
import { GeographyDetailHeader } from "../../../components/discovery/GeographyDetailHeader";
import { InfiniteCatalogList } from "../../../components/discovery/InfiniteCatalogList";
import { fetchGeographyDetail } from "../../../lib/api/discovery-client";
import { SiteHeader } from "../../../shell/site-header";
import { SHELL_LAYOUT_CLASS_NAMES } from "../../../theme/monochrome-theme";

interface GeographyDetailPageProps {
  params: Promise<{ geographyId: string }>;
}

const isNotFoundError = (error: unknown): boolean => {
  if (!error || typeof error !== "object") {
    return false;
  }

  return "status" in error && (error as { status?: number }).status === 404;
};

const GeographyDetailPage = async ({ params }: GeographyDetailPageProps): Promise<JSX.Element> => {
  try {
    const { geographyId } = await params;
    const firstPage = await fetchGeographyDetail(geographyId, { page: 1 });

    return (
      <div className="shell-page shell-scroll-anchor" data-testid="site-shell">
        <SiteHeader activeTab="datasets" />
        <main
          className={SHELL_LAYOUT_CLASS_NAMES.constrainedContent}
          data-testid="geography-detail-page"
        >
          <GeographyDetailHeader geography={firstPage.geography} />
          {firstPage.items.length > 0 ? (
            <InfiniteCatalogList
              emptyMessage="No datasets are currently available for this geography."
              initialItems={firstPage.items}
              initialPage={firstPage.page}
              initialTotalPages={firstPage.total_pages}
              requestPath={`/api/discovery/geographies/${encodeURIComponent(geographyId)}`}
            />
          ) : (
            <EmptyState message="No datasets are currently available for this geography." />
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
          data-testid="geography-detail-page"
        >
          <ErrorState />
        </main>
      </div>
    );
  }
};

export default GeographyDetailPage;
