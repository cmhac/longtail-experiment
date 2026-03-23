import React from "react";
import { renderToStaticMarkup } from "react-dom/server";
import { describe, expect, it } from "vitest";
import HomePage from "../src/app/page";

describe("frontend shell startup", () => {
  it("renders root shell without runtime errors", () => {
    const markup = renderToStaticMarkup(<HomePage />);

    expect(markup).toContain('data-testid="app-shell"');
    expect(markup).toContain("Longtail Frontend Shell");
  });

  it("renders all required furniture slot placeholders", () => {
    const markup = renderToStaticMarkup(<HomePage />);

    expect(markup).toContain('data-testid="top-navigation-slot"');
    expect(markup).toContain('data-testid="secondary-navigation-slot"');
    expect(markup).toContain('data-testid="scripts-analytics-slot"');
    expect(markup).toContain('data-testid="ads-subscription-slot"');
    expect(markup).toContain('data-testid="footer-slot"');
  });
});
