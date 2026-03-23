import React from "react";
import { describe, expect, it } from "vitest";
import HomePage from "../src/app/page";
import { CONTENT_PLACEHOLDER_VARIANT } from "../src/shell/content-placeholder";
import { SITE_FOOTER_VARIANT } from "../src/shell/site-footer";
import { SITE_HEADER_VARIANT } from "../src/shell/site-header";
import {
  FORBIDDEN_ACCENT_VARIANTS,
  isMonochromeVariantAllowed,
} from "../src/theme/monochrome-theme";
import { renderMarkup } from "./test-utils";

describe("shell structure and monochrome contract", () => {
  it("asserts header region presence and semantics", () => {
    const markup = renderMarkup(<HomePage />);

    expect(markup).toContain("<header");
    expect(markup).toContain('data-shell-region="header"');
    expect(markup).toContain('data-testid="shell-header"');
  });

  it("asserts main placeholder region presence and placeholder text", () => {
    const markup = renderMarkup(<HomePage />);

    expect(markup).toContain("<main");
    expect(markup).toContain('data-shell-region="main-placeholder"');
    expect(markup).toContain('data-testid="shell-main-placeholder"');
    expect(markup).toContain("Feature content will appear here soon.");
  });

  it("asserts footer region presence and ordering", () => {
    const markup = renderMarkup(<HomePage />);
    const headerIndex = markup.indexOf('data-shell-region="header"');
    const mainIndex = markup.indexOf('data-shell-region="main-placeholder"');
    const footerIndex = markup.indexOf('data-shell-region="footer"');

    expect(markup).toContain("<footer");
    expect(markup).toContain('data-testid="shell-footer"');
    expect(headerIndex).toBeGreaterThan(-1);
    expect(mainIndex).toBeGreaterThan(headerIndex);
    expect(footerIndex).toBeGreaterThan(mainIndex);
  });

  it("asserts shell remains structurally valid during page scroll", () => {
    const markup = renderMarkup(<HomePage />);

    expect(markup).toContain('class="shell-page shell-scroll-anchor"');
    expect(markup).toContain("Baseline shell footer for release readiness.");
  });

  it("asserts header uses monochrome classes and tokens only", () => {
    const markup = renderMarkup(<HomePage />);

    expect(markup).toContain('data-shell-region="header"');
    expect(markup).toContain("shell-monochrome");
    expect(isMonochromeVariantAllowed(SITE_HEADER_VARIANT)).toBe(true);
  });

  it("asserts placeholder uses monochrome classes and tokens only", () => {
    const markup = renderMarkup(<HomePage />);

    expect(markup).toContain('data-shell-region="main-placeholder"');
    expect(markup).toContain("shell-monochrome");
    expect(isMonochromeVariantAllowed(CONTENT_PLACEHOLDER_VARIANT)).toBe(true);
  });

  it("asserts footer uses monochrome classes and tokens only", () => {
    const markup = renderMarkup(<HomePage />);

    expect(markup).toContain('data-shell-region="footer"');
    expect(markup).toContain("shell-monochrome");
    expect(isMonochromeVariantAllowed(SITE_FOOTER_VARIANT)).toBe(true);
  });

  it("rejects accent variant usage in shell components", () => {
    for (const variant of FORBIDDEN_ACCENT_VARIANTS) {
      expect(isMonochromeVariantAllowed(variant)).toBe(false);
    }
  });
});
