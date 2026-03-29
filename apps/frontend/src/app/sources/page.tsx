import React from "react";
import type { JSX } from "react";

import { DiscoveryListPageHeader } from "../../components/discovery/DiscoveryListPageHeader";
import { ErrorState } from "../../components/discovery/ErrorState";
import { SourceCatalogList } from "../../components/discovery/SourceCatalogList";
import { fetchSourceList } from "../../lib/api/discovery-client";
import { SitePageFrame } from "../../shell/site-page-frame";

const SourceListPage = async (): Promise<JSX.Element> => {
  try {
    const payload = await fetchSourceList();

    return (
      <SitePageFrame
        activeTab="sources"
        mainClassName="grid content-start gap-[1.2rem]"
        mainTestId="source-list-page"
      >
        <DiscoveryListPageHeader
          headerTestId="source-list-page-header"
          title="Sources"
          totalNoun="sources"
          totalTestId="source-list-total"
          totalValue={Intl.NumberFormat("en-US").format(payload.total_items)}
        />
        <SourceCatalogList items={payload.items} />
      </SitePageFrame>
    );
  } catch {
    return (
      <SitePageFrame
        activeTab="sources"
        mainClassName="grid content-start gap-[1.2rem]"
        mainTestId="source-list-page"
      >
        <DiscoveryListPageHeader
          headerTestId="source-list-page-header"
          title="Sources"
          totalNoun="sources"
          totalTestId="source-list-total"
          totalValue="--"
        />
        <ErrorState />
      </SitePageFrame>
    );
  }
};

export default SourceListPage;
