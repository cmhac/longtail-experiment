import { Card } from "@heroui/react/card";
import React from "react";
import type { JSX } from "react";
import type { DatasetSummary } from "../../lib/api/discovery-types";
import { EmptyState } from "./EmptyState";
import { UnifiedDatasetRow } from "./UnifiedDatasetRow";
import { toUnifiedCatalogRow } from "./unified-dataset-row-mappers";

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
    <Card className="grid gap-0 p-5 sm:p-6" data-testid="catalog-flat-list" variant="default">
      {dedupedItems.map((item) => (
        <UnifiedDatasetRow key={item.dataset_id} {...toUnifiedCatalogRow(item)} />
      ))}
    </Card>
  );
};
