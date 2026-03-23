import React from "react";
import { describe, expect, it } from "vitest";
import DatasetNotFoundPage from "../src/app/datasets/[id]/not-found";
import { renderMarkup } from "./test-utils";

describe("dataset not-found page", () => {
  it("renders not-found message and catalog link", () => {
    const markup = renderMarkup(<DatasetNotFoundPage />);

    expect(markup).toContain("Dataset not found");
    expect(markup).toContain('href="/datasets"');
  });
});
