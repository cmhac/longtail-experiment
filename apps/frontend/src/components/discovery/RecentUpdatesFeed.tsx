import { Card } from "@heroui/react/card";
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
    <Card
      className="recent-updates-feed grid gap-0 border-border/70 bg-surface/90 p-5 shadow-sm sm:p-6"
      data-testid="recent-updates-feed"
      variant="default"
    >
      <header
        className="recent-updates-header flex items-baseline justify-between gap-4 border-b border-[color-mix(in_srgb,var(--shell-border)_82%,transparent)] pb-[0.65rem] max-[720px]:flex-col max-[720px]:items-start max-[720px]:gap-[0.45rem]"
        data-testid="recent-updates-header"
      >
        <h2 className="m-0 font-serif text-[clamp(1.7rem,2.3vw,2.05rem)] leading-[1.1]">
          Recent Updates
        </h2>
      </header>
      {items.slice(0, 5).map((item) => (
        <UnifiedDatasetRow key={item.dataset_id} {...toUnifiedRecentUpdatesRow(item)} />
      ))}
    </Card>
  );
};
