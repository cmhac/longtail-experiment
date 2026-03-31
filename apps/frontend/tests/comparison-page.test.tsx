import React from "react";
import { describe, expect, it } from "vitest";
import ComparisonPage from "../src/app/comparison/page";
import { renderMarkup } from "./test-utils";

describe("comparison page", () => {
  it("renders comparison shell and empty-state container", () => {
    const markup = renderMarkup(<ComparisonPage />);

    expect(markup).toContain('data-testid="comparison-page"');
    expect(markup).toContain('data-testid="comparison-empty-state"');
    expect(markup).toContain('data-testid="navbar-comparison-link"');
  });
});
