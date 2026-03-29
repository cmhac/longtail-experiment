import { Card } from "@heroui/react/card";
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
    <Card className="grid gap-0 p-5 sm:p-6" data-testid="source-catalog-list" variant="default">
      {items.map((item) => (
        <SourceListRow key={item.id} source={item} />
      ))}
    </Card>
  );
};
