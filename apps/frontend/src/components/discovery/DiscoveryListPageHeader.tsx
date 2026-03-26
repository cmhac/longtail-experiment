import React from "react";
import type { JSX, ReactNode } from "react";

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
    <header className="discovery-list-page-header" data-testid={headerTestId}>
      <div>
        <h1 className="discovery-list-title">{title}</h1>
        <p className="discovery-list-total" data-testid={totalTestId}>
          {totalValue} total {totalNoun}
        </p>
      </div>
      {actions ? <div className="discovery-list-page-actions">{actions}</div> : null}
    </header>
  );
};
