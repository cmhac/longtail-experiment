import React from "react";
import type { JSX } from "react";

import { DiscoveryListPageHeader } from "../../components/discovery/DiscoveryListPageHeader";
import { ErrorState } from "../../components/discovery/ErrorState";
import { SourceCatalogList } from "../../components/discovery/SourceCatalogList";
import { fetchSourceList } from "../../lib/api/discovery-client";
import { SiteHeader } from "../../shell/site-header";
import { SHELL_LAYOUT_CLASS_NAMES } from "../../theme/monochrome-theme";

const SourceListPage = async (): Promise<JSX.Element> => {
  try {
    const payload = await fetchSourceList();

    return (
      <div className="shell-page shell-scroll-anchor" data-testid="site-shell">
        <SiteHeader activeTab="sources" />
        <main
          className={SHELL_LAYOUT_CLASS_NAMES.constrainedContent}
          data-testid="source-list-page"
        >
          <DiscoveryListPageHeader
            headerTestId="source-list-page-header"
            title="Sources"
            totalNoun="sources"
            totalTestId="source-list-total"
            totalValue={Intl.NumberFormat("en-US").format(payload.total_items)}
          />
          <SourceCatalogList items={payload.items} />
        </main>
      </div>
    );
  } catch {
    return (
      <div className="shell-page shell-scroll-anchor" data-testid="site-shell">
        <SiteHeader activeTab="sources" />
        <main
          className={SHELL_LAYOUT_CLASS_NAMES.constrainedContent}
          data-testid="source-list-page"
        >
          <DiscoveryListPageHeader
            headerTestId="source-list-page-header"
            title="Sources"
            totalNoun="sources"
            totalTestId="source-list-total"
            totalValue="--"
          />
          <ErrorState />
        </main>
      </div>
    );
  }
};

export default SourceListPage;
