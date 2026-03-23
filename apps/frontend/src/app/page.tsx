import React from "react";
import type { JSX } from "react";
import { ContentPlaceholder } from "../shell/content-placeholder";
import { SiteFooter } from "../shell/site-footer";
import { SiteHeader } from "../shell/site-header";

const HomePage = (): JSX.Element => {
  return (
    <div className="shell-page shell-scroll-anchor" data-testid="site-shell">
      <SiteHeader />
      <ContentPlaceholder />
      <SiteFooter />
    </div>
  );
};

export default HomePage;
