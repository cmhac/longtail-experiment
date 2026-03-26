import React from "react";
import type { JSX } from "react";

import type { SourceSummary } from "../../lib/api/discovery-types";
import { EmptyState } from "./EmptyState";
import { SourceListRow } from "./SourceListRow";

interface SourceCatalogListProps {
  items: SourceSummary[];
  emptyMessage?: string;
}

export const SourceCatalogList = ({
  items,
  emptyMessage = "No sources are available.",
}: SourceCatalogListProps): JSX.Element => {
  if (items.length === 0) {
    return <EmptyState message={emptyMessage} />;
  }

  return (
    <section className="source-catalog-list" data-testid="source-catalog-list">
      {items.map((item) => (
        <SourceListRow key={item.id} source={item} />
      ))}
    </section>
  );
};
