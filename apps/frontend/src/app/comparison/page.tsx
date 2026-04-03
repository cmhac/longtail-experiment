import React from "react";
import type { JSX } from "react";
import { ProtectedRouteGate } from "../../components/auth/ProtectedRouteGate";
import { ComparisonPageClient } from "../../components/discovery/ComparisonPageClient";
import { SitePageFrame } from "../../shell/site-page-frame";

const ComparisonPage = (): JSX.Element => {
  return (
    <SitePageFrame
      activeTab="datasets"
      mainClassName="flex flex-col gap-4"
      mainTestId="comparison-page"
    >
      <ProtectedRouteGate pathname="/comparison" fallbackTestId="comparison-auth-redirecting">
        <ComparisonPageClient />
      </ProtectedRouteGate>
    </SitePageFrame>
  );
};

export default ComparisonPage;
