import React from "react";
import type { JSX, ReactNode } from "react";
import { PageHeaderKicker, PageHeaderTitle, PageHeaderWrapper } from "./PageHeader";

interface DiscoveryListPageHeaderProps {
  title: string;
  totalNoun: string;
  totalValue: string;
  headerTestId: string;
  totalTestId: string;
  actions?: ReactNode;
}

export const DiscoveryListPageHeader = ({
  actions,
  headerTestId,
  title,
  totalNoun,
  totalTestId,
  totalValue,
}: DiscoveryListPageHeaderProps): JSX.Element => {
  return (
    <PageHeaderWrapper className="pt-2 max-[720px]:items-stretch" testId={headerTestId}>
      <div className="flex items-start justify-between gap-4 max-[720px]:flex-col max-[720px]:items-stretch">
        <div>
          <PageHeaderTitle>{title}</PageHeaderTitle>
          <PageHeaderKicker className="m-[0.35rem_0_0] tracking-[0.16em]" testId={totalTestId}>
            {totalValue} total {totalNoun}
          </PageHeaderKicker>
        </div>
        {actions ? <div className="inline-flex items-center gap-2">{actions}</div> : null}
      </div>
    </PageHeaderWrapper>
  );
};
