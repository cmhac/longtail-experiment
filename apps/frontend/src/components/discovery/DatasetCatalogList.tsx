import React from "react";
import type { JSX } from "react";
import type { DatasetSummary } from "../../lib/api/discovery-types";
import { DatasetCard } from "./DatasetCard";
import { EmptyState } from "./EmptyState";

interface DatasetCatalogListProps {
  items: DatasetSummary[];
  emptyMessage?: string;
}

export const DatasetCatalogList = ({
  items,
  emptyMessage = "No datasets match the selected filters. Reset filters to see the full catalog.",
}: DatasetCatalogListProps): JSX.Element => {
  const dedupedItems = [...new Map(items.map((item) => [item.dataset_id, item])).values()];

  if (dedupedItems.length === 0) {
    return <EmptyState message={emptyMessage} />;
  }

  return (
    <section className="dataset-list-results" data-testid="catalog-flat-list">
      {dedupedItems.map((item) => (
        <DatasetCard item={item} key={item.dataset_id} />
      ))}
    </section>
  );
};
