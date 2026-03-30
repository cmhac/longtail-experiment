import React from "react";
import type { JSX } from "react";
import type { DatasetRecentItem } from "../../lib/api/discovery-types";
import { DiscoveryFeedList } from "./DiscoveryFeedList";
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
    <DiscoveryFeedList.Wrapper
      cardClassName="recent-updates-feed bg-surface/90 p-5 shadow-sm sm:p-6"
      cardTestId="recent-updates-feed"
    >
      <header
        className="recent-updates-header flex items-baseline justify-between gap-4 border-[color-mix(in_srgb,var(--shell-border)_82%,transparent)] border-b pb-[0.65rem] max-[720px]:flex-col max-[720px]:items-start max-[720px]:gap-[0.45rem]"
        data-testid="recent-updates-header"
      >
        <DiscoveryFeedList.TitleRegion>Recent Updates</DiscoveryFeedList.TitleRegion>
      </header>
      {items.slice(0, 5).map((item) => (
        <UnifiedDatasetRow key={item.dataset_id} {...toUnifiedRecentUpdatesRow(item)} />
      ))}
    </DiscoveryFeedList.Wrapper>
  );
};
