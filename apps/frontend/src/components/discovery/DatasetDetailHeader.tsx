import React from "react";
import type { JSX } from "react";
import type { DatasetDetail } from "../../lib/api/discovery-types";
import {
  PageHeaderKicker,
  PageHeaderSubtitle,
  PageHeaderTitle,
  PageHeaderWrapper,
} from "./PageHeader";
import { TagPillGroup } from "./TagPill";

interface DatasetDetailHeaderProps {
  data: DatasetDetail;
  exportHref?: string;
}

export const DatasetDetailHeader = ({
  data,
  exportHref = "#",
}: DatasetDetailHeaderProps): JSX.Element => {
  return (
    <PageHeaderWrapper testId="dataset-detail-header">
      <div className="grid gap-[0.55rem]">
        <PageHeaderKicker className="text-[0.72rem] tracking-[0.12em]">
          Data Source: {data.source.name}
        </PageHeaderKicker>
        <PageHeaderTitle
          className="font-[Iowan_Old_Style,Palatino_Linotype,Times_New_Roman,serif]"
          size="hero"
        >
          {data.title}
        </PageHeaderTitle>
        <PageHeaderSubtitle>{data.description ?? "No description available"}</PageHeaderSubtitle>
      </div>

      <div
        className="flex items-start justify-between gap-3 max-md:flex-col max-md:items-center"
        data-testid="dataset-detail-meta-row"
      >
        <div aria-label="Topic tags" className="flex min-w-0 flex-1 flex-wrap items-start gap-2">
          <TagPillGroup
            emphasizedPills={data.geographic_scope ? [data.geographic_scope] : []}
            fallback={<span>No topic tags</span>}
            showFallbackWhenTagPillsEmpty
            tagPills={data.topic_tags}
          />
        </div>

        <div
          className="dataset-detail-utility-actions"
          data-testid="dataset-detail-utility-actions"
        >
          <div className="inline-flex flex-none flex-wrap gap-[0.45rem]">
            <a
              className="dataset-detail-action-export inline-flex min-h-[2.1rem] flex-none items-center justify-center border border-(--shell-border) px-[0.8rem] py-[0.35rem] text-[0.74rem] uppercase tracking-[0.08em] no-underline"
              href={exportHref}
            >
              Export CSV
            </a>
          </div>
        </div>
      </div>
    </PageHeaderWrapper>
  );
};
