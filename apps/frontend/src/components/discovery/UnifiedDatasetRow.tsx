import Link from "next/link";
import React from "react";
import type { JSX } from "react";
import type { CanonicalTrendDescriptor } from "../../lib/api/discovery-types";
import { DatasetTrendIndicator } from "./DatasetTrendIndicator";
import { DiscoveryFeedList } from "./DiscoveryFeedList";
import { TagPillGroup } from "./TagPill";

export interface UnifiedDatasetRowProps {
  datasetId: string;
  destinationHref: string;
  sourceLabel: string;
  updatedLabel: string;
  title: string;
  summaryText?: string;
  tagPills: string[];
  emphasizedPills?: string[];
  interactionMode: "row_link" | "title_link";
  trendDescriptor?: CanonicalTrendDescriptor | undefined;
}

export const UnifiedDatasetRow = ({
  datasetId,
  destinationHref,
  emphasizedPills = [],
  interactionMode,
  sourceLabel,
  summaryText,
  tagPills,
  title,
  trendDescriptor,
  updatedLabel,
}: UnifiedDatasetRowProps): JSX.Element => {
  void datasetId;
  void interactionMode;

  return (
    <DiscoveryFeedList.Row
      cardClassName="unified-dataset-row unified-dataset-row-card"
      cardTestId="unified-dataset-row"
    >
      <DiscoveryFeedList.MetadataRail>
        <DiscoveryFeedList.DisplayCategory>{sourceLabel}</DiscoveryFeedList.DisplayCategory>
        <DiscoveryFeedList.UpdateDate>{updatedLabel}</DiscoveryFeedList.UpdateDate>
      </DiscoveryFeedList.MetadataRail>
      <DiscoveryFeedList.Body>
        <div className="grid grid-cols-[minmax(0,1fr)_auto] items-start gap-x-4 gap-y-1.5 max-[720px]:grid-cols-1">
          <DiscoveryFeedList.Title testId="unified-dataset-row-title">
            <Link className="text-inherit no-underline" href={destinationHref}>
              {title}
            </Link>
          </DiscoveryFeedList.Title>
          {trendDescriptor ? (
            <DatasetTrendIndicator
              className="justify-self-end pt-1 max-[720px]:justify-self-start max-[720px]:pt-0"
              descriptor={trendDescriptor}
              testId="unified-dataset-row-trend-indicator"
            />
          ) : null}
        </div>
        {summaryText ? (
          <DiscoveryFeedList.Subtitle>{summaryText}</DiscoveryFeedList.Subtitle>
        ) : null}
        <TagPillGroup
          emphasizedPills={emphasizedPills}
          groupClassName="mt-[0.18rem]"
          tagPills={tagPills}
          testId="unified-dataset-row-pills"
        />
      </DiscoveryFeedList.Body>
    </DiscoveryFeedList.Row>
  );
};

export const UNIFIED_DATASET_ROW_VERSION = "v1";
