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
        <div className="mx-auto grid w-[min(100%,74rem)] gap-[0.55rem] px-[1.2rem] pb-[1.8rem] pt-[1.5rem] max-[720px]:px-4 max-[720px]:pb-[1.45rem] max-[720px]:pt-[1.25rem]">
          <p className="shell-footer-brand" data-testid="footer-brand">
            <span className="m-0 font-serif text-[1.15rem] font-bold leading-[1.3] text-[var(--shell-foreground)] max-[720px]:text-[1.05rem]">
              {FOOTER_CONTENT.brandText}
            </span>
          </p>
          <p className="shell-footer-mission" data-testid="footer-mission">
            <span className="m-0 max-w-[58ch] text-[0.92rem] leading-[1.55] text-(--shell-muted) [text-wrap:pretty] max-[720px]:max-w-none max-[720px]:text-[0.9rem]">
              {FOOTER_CONTENT.missionText}
            </span>
          </p>
        </div>
      </div>
    </footer>
  );
};
