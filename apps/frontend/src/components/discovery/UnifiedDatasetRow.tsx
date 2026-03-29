import { Card } from "@heroui/react/card";
import Link from "next/link";
import React from "react";
import type { JSX } from "react";
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
    <Card
      className="recent-updates-row unified-dataset-row unified-dataset-row-card grid grid-cols-[minmax(7.5rem,9.25rem)_1fr] gap-[1.15rem] rounded-none border-0 border-t border-t-[color-mix(in_srgb,var(--shell-border)_68%,transparent)] bg-transparent px-0 py-[1.55rem] text-inherit no-underline shadow-none first:border-t-0 max-[720px]:grid-cols-1 max-[720px]:gap-[0.52rem] max-[720px]:py-[1.1rem]"
      data-testid="unified-dataset-row"
      variant="transparent"
    >
      <div className="recent-updates-meta-rail grid min-w-0 content-start gap-[0.32rem] max-[720px]:flex max-[720px]:items-center max-[720px]:gap-[0.6rem]">
        <span className="recent-updates-source font-bold text-[0.73rem] tracking-[0.08em]">
          {sourceLabel}
        </span>
        <span className="recent-updates-date text-(--shell-muted) text-[0.82rem]">
          {updatedLabel}
        </span>
      </div>
      <div className="recent-updates-body grid min-w-0 gap-[0.42rem]">
        <h3
          className="m-0 font-serif text-[clamp(1.18rem,2.1vw,1.95rem)] leading-[1.05] max-[720px]:leading-[1.13]"
          data-testid="unified-dataset-row-title"
        >
          <Link className="text-inherit no-underline" href={destinationHref}>
            {title}
          </Link>
        </h3>
        {summaryText ? (
          <p className="m-0 max-w-[70ch] text-(--shell-muted) leading-[1.4]">{summaryText}</p>
        ) : null}
        <TagPillGroup
          emphasizedPills={emphasizedPills}
          groupClassName="mt-[0.18rem]"
          tagPills={tagPills}
          testId="unified-dataset-row-pills"
        />
      </div>
    </Card>
  );
};

export const UNIFIED_DATASET_ROW_VERSION = "v1";
