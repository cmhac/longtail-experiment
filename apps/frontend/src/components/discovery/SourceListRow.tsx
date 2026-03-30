import { Card } from "@heroui/react/card";
import Link from "next/link";
import React from "react";
import type { JSX } from "react";

import type { SourceSummary } from "../../lib/api/discovery-types";

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
    <Card
      className="recent-updates-row source-directory-row grid grid-cols-[minmax(7.5rem,9.25rem)_1fr] gap-[1.15rem] rounded-none border-0 border-t border-t-[color-mix(in_srgb,var(--shell-border)_68%,transparent)] bg-transparent px-0 py-[1.55rem] text-inherit no-underline shadow-none first:border-t-0 max-[720px]:grid-cols-1 max-[720px]:gap-[0.52rem] max-[720px]:py-[1.1rem]"
      variant="transparent"
    >
      <Link
        className="contents"
        data-testid="source-list-row"
        href={`/sources/${encodeURIComponent(source.id)}`}
      >
        <div className="recent-updates-meta-rail source-directory-meta-rail grid min-w-0 content-start gap-[0.32rem] max-[720px]:flex max-[720px]:items-center max-[720px]:gap-[0.6rem]">
          <span className="recent-updates-source font-bold text-[0.73rem] tracking-[0.08em]">
            {source.source_type ? source.source_type.toUpperCase() : "SOURCE"}
          </span>
          <span className="recent-updates-date text-(--shell-muted) text-[0.82rem]">
            {formatDatasetCount(source.dataset_count)}
          </span>
        </div>
        <div className="recent-updates-body grid min-w-0 gap-[0.42rem]">
          <h3
            className="source-directory-title m-0 font-serif text-[clamp(1.18rem,2.1vw,1.95rem)] leading-[1.05] max-[720px]:leading-[1.13]"
            data-testid="source-list-row-title"
          >
            {source.title}
          </h3>
          <p className="m-0 max-w-[70ch] text-(--shell-muted) leading-[1.4]">
            {buildSummaryText(source)}
          </p>
        </div>
      </Link>
    </Card>
  );
};
