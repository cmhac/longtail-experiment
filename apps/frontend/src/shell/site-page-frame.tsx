import React from "react";
import type { JSX, ReactNode } from "react";
import { SHELL_LAYOUT_CLASS_NAMES } from "../theme/monochrome-theme";
import type { NavbarTabKey } from "./navbar-config";
import { SiteFooter } from "./site-footer";
import { SiteHeader } from "./site-header";

interface SitePageFrameProps {
  activeTab?: NavbarTabKey;
  children: ReactNode;
  includeFooter?: boolean;
  mainClassName?: string;
  mainTestId: string;
}

export const SitePageFrame = ({
  activeTab,
  children,
  includeFooter = false,
  mainClassName,
  mainTestId,
}: SitePageFrameProps): JSX.Element => {
  return (
    <div className={SHELL_LAYOUT_CLASS_NAMES.page} data-testid="site-shell">
      <SiteHeader {...(activeTab ? { activeTab } : {})} />
      <main
        className={`${SHELL_LAYOUT_CLASS_NAMES.constrainedContent}${mainClassName ? ` ${mainClassName}` : ""}`}
        data-testid={mainTestId}
      >
        {children}
      </main>
      {includeFooter ? <SiteFooter /> : null}
    </div>
  );
};
