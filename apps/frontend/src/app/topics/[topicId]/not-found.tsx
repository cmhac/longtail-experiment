import Link from "next/link";
import React from "react";
import type { JSX } from "react";

import { SiteHeader } from "../../../shell/site-header";
import { SHELL_LAYOUT_CLASS_NAMES } from "../../../theme/monochrome-theme";

const TopicNotFoundPage = (): JSX.Element => {
  return (
    <div className="shell-page shell-scroll-anchor" data-testid="site-shell">
      <SiteHeader activeTab="datasets" />
      <main
        className={SHELL_LAYOUT_CLASS_NAMES.constrainedContent}
        data-testid="topic-not-found-page"
      >
        <h1>Topic not found</h1>
        <p>The topic you requested does not exist.</p>
        <p>
          <Link href="/datasets">Back to all datasets</Link>
        </p>
      </main>
    </div>
  );
};

export default TopicNotFoundPage;
