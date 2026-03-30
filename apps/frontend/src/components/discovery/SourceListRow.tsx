import Link from "next/link";
import React from "react";
import type { JSX } from "react";

import type { SourceSummary } from "../../lib/api/discovery-types";
import { DiscoveryFeedList } from "./DiscoveryFeedList";

interface SourceListRowProps {
  source: SourceSummary;
}

const formatDatasetCount = (count: number): string => {
  return `${Intl.NumberFormat("en-US").format(count)} ${count === 1 ? "dataset" : "datasets"}`;
};

const buildSummaryText = (source: SourceSummary): string => {
  const countLabel = formatDatasetCount(source.dataset_count);
  if (source.description) {
    return source.description;
  }
  if (source.source_type) {
    return `Browse ${countLabel} from this ${source.source_type.toLowerCase()} source.`;
  }

  return `Browse ${countLabel} from this source.`;
};

export const SourceListRow = ({ source }: SourceListRowProps): JSX.Element => {
  return (
    <DiscoveryFeedList.Row cardClassName="source-directory-row">
      <Link
        className="contents"
        data-testid="source-list-row"
        href={`/sources/${encodeURIComponent(source.id)}`}
      >
        <DiscoveryFeedList.MetadataRail className="source-directory-meta-rail">
          <DiscoveryFeedList.DisplayCategory>
            {source.source_type ? source.source_type.toUpperCase() : "SOURCE"}
          </DiscoveryFeedList.DisplayCategory>
          <DiscoveryFeedList.UpdateDate>
            {formatDatasetCount(source.dataset_count)}
          </DiscoveryFeedList.UpdateDate>
        </DiscoveryFeedList.MetadataRail>
        <DiscoveryFeedList.Body>
          <DiscoveryFeedList.Title
            className="source-directory-title"
            testId="source-list-row-title"
          >
            {source.title}
          </DiscoveryFeedList.Title>
          <DiscoveryFeedList.Subtitle>{buildSummaryText(source)}</DiscoveryFeedList.Subtitle>
        </DiscoveryFeedList.Body>
      </Link>
    </DiscoveryFeedList.Row>
  );
};
