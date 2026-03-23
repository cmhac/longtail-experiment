import React from "react";
import { describe, expect, it } from "vitest";
import { EmptyState } from "../src/components/discovery/EmptyState";
import { renderMarkup } from "./test-utils";

describe("EmptyState", () => {
  it("renders default message", () => {
    const markup = renderMarkup(<EmptyState />);

    expect(markup).toContain("No results found.");
    expect(markup).toContain("<output");
  });

  it("renders custom message", () => {
    const markup = renderMarkup(<EmptyState message="Nothing matched your query." />);

    expect(markup).toContain("Nothing matched your query.");
  });
});
