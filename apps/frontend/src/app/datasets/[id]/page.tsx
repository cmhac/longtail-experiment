import { notFound } from "next/navigation";
import React from "react";
import type { JSX } from "react";
import { DatasetDetailAnalysis } from "../../../components/discovery/DatasetDetailAnalysis";
import { DatasetDetailHeader } from "../../../components/discovery/DatasetDetailHeader";
import { ErrorState } from "../../../components/discovery/ErrorState";
import { ObservationsTable } from "../../../components/discovery/ObservationsTable";
import { fetchDatasetDetail } from "../../../lib/api/discovery-client";
import { SitePageFrame } from "../../../shell/site-page-frame";

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
      <SitePageFrame
        activeTab="datasets"
        mainClassName="grid gap-4"
        mainTestId="dataset-detail-page"
      >
        <section className="grid gap-3" data-testid="dataset-detail-overview">
          <DatasetDetailHeader data={detail} exportHref={`/api/datasets/${encodedId}.csv`} />
        </section>

        <section
          className="grid gap-4 md:grid-cols-[18rem_minmax(0,1fr)] md:items-stretch"
          data-testid="dataset-detail-analysis"
        >
          <DatasetDetailAnalysis data={detail} />
        </section>

        <section
          className="border-0 bg-transparent p-0"
          data-testid="dataset-detail-observed-values-section"
        >
          <ObservationsTable
            observations={detail.observations}
            unitType={(detail.metadata.unit_type ?? null) as string | null}
            unitLabel={(detail.metadata.unit ?? detail.metadata.units ?? null) as string | null}
          />
        </section>
      </SitePageFrame>
    );
  } catch (error) {
    if (isNotFoundError(error)) {
      notFound();
    }

    return (
      <SitePageFrame
        activeTab="datasets"
        mainClassName="grid gap-4"
        mainTestId="dataset-detail-page"
      >
        <ErrorState />
      </SitePageFrame>
    );
  }
};

export default DatasetDetailPage;
