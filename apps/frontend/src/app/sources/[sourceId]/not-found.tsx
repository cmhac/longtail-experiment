import Link from "next/link";
import React from "react";
import type { JSX } from "react";

import { SiteHeader } from "../../../shell/site-header";
import { SHELL_LAYOUT_CLASS_NAMES } from "../../../theme/monochrome-theme";

const SourceNotFoundPage = (): JSX.Element => {
  return (
    <div className="shell-page shell-scroll-anchor" data-testid="site-shell">
      <SiteHeader activeTab="sources" />
      <main
        className={SHELL_LAYOUT_CLASS_NAMES.constrainedContent}
        data-testid="source-not-found-page"
      >
        <h1>Source not found</h1>
        <p>The source you requested does not exist.</p>
        <p>
          <Link href="/sources">Back to all sources</Link>
        </p>
      </main>
    </div>
  );
};

export default SourceNotFoundPage;
