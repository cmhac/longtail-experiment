import React from "react";
import { describe, expect, it } from "vitest";
import { ContentPlaceholder } from "../src/shell/content-placeholder";
import { renderMarkup } from "./test-utils";

describe("content placeholder", () => {
  it("renders legacy shell placeholder region and copy", () => {
    const markup = renderMarkup(<ContentPlaceholder />);

    expect(markup).toContain('data-testid="shell-main-placeholder"');
    expect(markup).toContain("Feature content will appear here soon.");
  });
});
