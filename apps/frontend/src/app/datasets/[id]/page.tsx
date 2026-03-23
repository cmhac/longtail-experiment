import { notFound } from "next/navigation";
import React from "react";
import type { JSX } from "react";
import { DatasetDetailHeader } from "../../../components/discovery/DatasetDetailHeader";
import { ErrorState } from "../../../components/discovery/ErrorState";
import { ObservationsChart } from "../../../components/discovery/ObservationsChart";
import { ObservationsTable } from "../../../components/discovery/ObservationsTable";
import { fetchDatasetDetail } from "../../../lib/api/discovery-client";

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

    return (
      <main data-testid="dataset-detail-page">
        <DatasetDetailHeader data={detail} />
        <ObservationsChart observations={detail.observations} />
        <ObservationsTable observations={detail.observations} />
      </main>
    );
  } catch (error) {
    if (isNotFoundError(error)) {
      notFound();
    }

    return <ErrorState />;
  }
};

export default DatasetDetailPage;
