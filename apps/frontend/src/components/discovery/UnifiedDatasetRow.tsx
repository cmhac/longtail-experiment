import Link from "next/link";
import React from "react";
import type { JSX } from "react";
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
        <DiscoveryFeedList.Title testId="unified-dataset-row-title">
          <Link className="text-inherit no-underline" href={destinationHref}>
            {title}
          </Link>
        </DiscoveryFeedList.Title>
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
