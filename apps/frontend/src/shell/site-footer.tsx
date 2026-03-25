"use client";

import React from "react";
import type { JSX } from "react";
import { SHELL_REGION_CLASS_NAMES } from "../theme/monochrome-theme";
import { FOOTER_CONTENT } from "./footer-content";

export const SITE_FOOTER_VARIANT = "bordered";

export const SiteFooter = (): JSX.Element => {
  return (
    <footer
      className={SHELL_REGION_CLASS_NAMES.footer}
      data-shell-region="footer"
      data-testid="shell-footer"
    >
      <div className="shell-footer-content" data-testid="footer-content-container">
        <p className="shell-footer-brand" data-testid="footer-brand">
          {FOOTER_CONTENT.brandText}
        </p>
        <p className="shell-footer-mission" data-testid="footer-mission">
          {FOOTER_CONTENT.missionText}
        </p>
      </div>
    </footer>
  );
};
