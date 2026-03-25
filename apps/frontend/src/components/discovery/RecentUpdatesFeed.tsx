import React from "react";
import type { JSX } from "react";
import type { DatasetRecentItem } from "../../lib/api/discovery-types";
import { EmptyState } from "./EmptyState";
import { UnifiedDatasetRow } from "./UnifiedDatasetRow";
import { toUnifiedRecentUpdatesRow } from "./unified-dataset-row-mappers";

interface RecentUpdatesFeedProps {
  items: DatasetRecentItem[];
  unavailable?: boolean;
}

export const RecentUpdatesFeed = ({
  items,
  unavailable = false,
}: RecentUpdatesFeedProps): JSX.Element => {
  if (unavailable) {
    return <EmptyState message="Recent updates are temporarily unavailable." />;
  }

  if (items.length === 0) {
    return <EmptyState message="No recent updates." />;
  }

  return (
    <section className="recent-updates-feed" data-testid="recent-updates-feed">
      <header className="recent-updates-header" data-testid="recent-updates-header">
        <h2>Recent Updates</h2>
      </header>
      {items.slice(0, 5).map((item) => (
        <UnifiedDatasetRow key={item.dataset_id} {...toUnifiedRecentUpdatesRow(item)} />
      ))}
    </section>
  );
};
