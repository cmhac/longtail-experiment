import React from "react";
import type { JSX } from "react";
import type { DatasetSummary } from "../../lib/api/discovery-types";
import { DatasetCard } from "./DatasetCard";
import { EmptyState } from "./EmptyState";

interface DatasetSearchResultsProps {
  items: DatasetSummary[];
  query: string;
}

export const DatasetSearchResults = ({ items, query }: DatasetSearchResultsProps): JSX.Element => {
  if (items.length === 0) {
    return <EmptyState message="No datasets matched your search." />;
  }

  return (
    <section aria-label="Search results" data-testid="dataset-search-results">
      <h2>Results for "{query}"</h2>
      {items.map((item) => (
        <DatasetCard item={item} key={item.dataset_id} />
      ))}
    </section>
  );
};
