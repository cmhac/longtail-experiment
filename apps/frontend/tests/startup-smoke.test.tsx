import React from "react";
import { renderToStaticMarkup } from "react-dom/server";
import { describe, expect, it } from "vitest";
import HomePage from "../src/app/page";

describe("frontend shell startup", () => {
  it("renders root shell without runtime errors", () => {
    const markup = renderToStaticMarkup(<HomePage />);

    expect(markup).toContain('data-testid="site-shell"');
    expect(markup).toContain("Minimal Site Shell");
  });

  it("renders required header, placeholder, and footer regions", () => {
    const markup = renderToStaticMarkup(<HomePage />);

    expect(markup).toContain('data-testid="shell-header"');
    expect(markup).toContain('data-testid="shell-main-placeholder"');
    expect(markup).toContain('data-testid="shell-footer"');
  });
});
