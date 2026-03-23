import React from "react";
import type { JSX } from "react";
import type { DatasetRecentItem } from "../../lib/api/discovery-types";
import { DatasetCard } from "./DatasetCard";
import { EmptyState } from "./EmptyState";

interface RecentUpdatesFeedProps {
  items: DatasetRecentItem[];
}

export const RecentUpdatesFeed = ({ items }: RecentUpdatesFeedProps): JSX.Element => {
  if (items.length === 0) {
    return <EmptyState message="No recent updates." />;
  }

  return (
    <section data-testid="recent-updates-feed">
      <h2>Recent Updates</h2>
      {items.slice(0, 5).map((item) => (
        <DatasetCard item={item} key={item.dataset_id} />
      ))}
    </section>
  );
};
