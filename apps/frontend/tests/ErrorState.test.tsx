import React from "react";
import { describe, expect, it } from "vitest";
import { ErrorState } from "../src/components/discovery/ErrorState";
import { renderMarkup } from "./test-utils";

describe("ErrorState", () => {
  it("renders default error message", () => {
    const markup = renderMarkup(<ErrorState />);

    expect(markup).toContain("Unable to load data. Please try again.");
    expect(markup).toContain('role="alert"');
  });

  it("renders custom error message", () => {
    const markup = renderMarkup(<ErrorState message="Backend unavailable" />);

    expect(markup).toContain("Backend unavailable");
  });
});
