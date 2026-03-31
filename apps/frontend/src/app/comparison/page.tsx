import React from "react";
import type { JSX } from "react";
import { ComparisonPageClient } from "../../components/discovery/ComparisonPageClient";
import { SitePageFrame } from "../../shell/site-page-frame";

const ComparisonPage = (): JSX.Element => {
  return (
    <SitePageFrame
      activeTab="datasets"
      mainClassName="flex flex-col gap-4"
      mainTestId="comparison-page"
    >
      <ComparisonPageClient />
    </SitePageFrame>
  );
};

export default ComparisonPage;
