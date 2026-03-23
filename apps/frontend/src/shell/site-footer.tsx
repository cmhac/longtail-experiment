"use client";

import { Card, Separator } from "@heroui/react";
import React from "react";
import type { JSX } from "react";
import { SHELL_REGION_CLASS_NAMES } from "../theme/monochrome-theme";

export const SITE_FOOTER_VARIANT = "bordered";

export const SiteFooter = (): JSX.Element => {
  return (
    <footer
      className={SHELL_REGION_CLASS_NAMES.footer}
      data-shell-region="footer"
      data-testid="shell-footer"
    >
      <Card>
        <Card.Content>
          <Separator className="shell-divider" />
          <p className="shell-copy">Baseline shell footer for release readiness.</p>
        </Card.Content>
      </Card>
    </footer>
  );
};
