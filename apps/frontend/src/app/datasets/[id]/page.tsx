import { notFound } from "next/navigation";
import React from "react";
import type { JSX } from "react";
import { DatasetDetailAnalysis } from "../../../components/discovery/DatasetDetailAnalysis";
import { DatasetDetailHeader } from "../../../components/discovery/DatasetDetailHeader";
import { ErrorState } from "../../../components/discovery/ErrorState";
import { ObservationsTable } from "../../../components/discovery/ObservationsTable";
import { fetchDatasetDetail } from "../../../lib/api/discovery-client";
import { SiteHeader } from "../../../shell/site-header";
import { SHELL_LAYOUT_CLASS_NAMES } from "../../../theme/monochrome-theme";

interface DatasetDetailPageProps {
  params: Promise<{ id: string }>;
}

const isNotFoundError = (error: unknown): boolean => {
  if (!error || typeof error !== "object") {
    return false;
  }

  return "status" in error && (error as { status?: number }).status === 404;
};

const DatasetDetailPage = async ({ params }: DatasetDetailPageProps): Promise<JSX.Element> => {
  try {
    const { id } = await params;
    const detail = await fetchDatasetDetail(id);
    const encodedId = encodeURIComponent(detail.dataset_id);

    return (
      <div className="shell-page shell-scroll-anchor" data-testid="site-shell">
        <SiteHeader activeTab="datasets" />
        <main
          className={SHELL_LAYOUT_CLASS_NAMES.constrainedContent}
          data-testid="dataset-detail-page"
        >
          <section className="dataset-detail-overview" data-testid="dataset-detail-overview">
            <DatasetDetailHeader data={detail} exportHref={`/api/datasets/${encodedId}.csv`} />
          </section>

          <section className="dataset-detail-analysis" data-testid="dataset-detail-analysis">
            <DatasetDetailAnalysis data={detail} />
          </section>

          <section
            className="dataset-detail-observed"
            data-testid="dataset-detail-observed-values-section"
          >
            <h2>Observed Values</h2>
            <ObservationsTable
              observations={detail.observations}
              unitType={(detail.metadata.unit_type ?? null) as string | null}
              unitLabel={(detail.metadata.unit ?? detail.metadata.units ?? null) as string | null}
            />
          </section>
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
          data-testid="dataset-detail-page"
        >
          <ErrorState />
        </main>
      </div>
    );
  }
};

export default DatasetDetailPage;
