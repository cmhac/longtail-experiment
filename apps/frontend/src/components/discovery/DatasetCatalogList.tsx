import React from "react";
import type { JSX } from "react";
import type {
  CatalogViewMode,
  DatasetSourceGroup,
  DatasetSummary,
} from "../../lib/api/discovery-types";
import { DatasetCard } from "./DatasetCard";
import { EmptyState } from "./EmptyState";

interface DatasetCatalogListProps {
  items: DatasetSummary[];
  groups: DatasetSourceGroup[] | null;
  viewMode: CatalogViewMode;
}

export const DatasetCatalogList = ({
  items,
  groups,
  viewMode,
}: DatasetCatalogListProps): JSX.Element => {
  if (items.length === 0) {
    return <EmptyState />;
  }

  if (viewMode === "flat" || !groups) {
    return (
      <section data-testid="catalog-flat-list">
        {items.map((item) => (
          <DatasetCard item={item} key={item.dataset_id} />
        ))}
      </section>
    );
  }

  const itemMap = new Map(items.map((item) => [item.dataset_id, item]));

  return (
    <section data-testid="catalog-grouped-list">
      {groups.map((group) => (
        <section data-testid="catalog-source-group" key={group.source.id}>
          <h2>{group.source.name}</h2>
          {group.dataset_ids.map((datasetId) => {
            const item = itemMap.get(datasetId);
            return item ? <DatasetCard item={item} key={item.dataset_id} /> : null;
          })}
        </section>
      ))}
    </section>
  );
};
