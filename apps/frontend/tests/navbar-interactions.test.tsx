/** @vitest-environment jsdom */

import { fireEvent, render, screen } from "@testing-library/react";
import React from "react";
import { afterEach, describe, expect, it } from "vitest";
import { SiteHeader } from "../src/shell/site-header";

afterEach(() => {
  document.body.innerHTML = "";
});

describe("navbar limited-scope interactions", () => {
  it("keeps Datasets and Trends disabled while Home remains routable", () => {
    render(<SiteHeader />);

    const homeLink = screen.getByTestId("navbar-tab-home");
    const datasetsButton = screen.getByTestId("navbar-tab-datasets");
    const trendsButton = screen.getByTestId("navbar-tab-trends");

    expect(homeLink.getAttribute("href")).toBe("/");
    expect(datasetsButton.getAttribute("disabled")).not.toBeNull();
    expect(trendsButton.getAttribute("disabled")).not.toBeNull();
  });

  it("keeps search control disabled and inert", () => {
    render(<SiteHeader />);

    const searchButton = screen.getByTestId("navbar-search-control");
    fireEvent.click(searchButton);

    expect(searchButton.getAttribute("disabled")).not.toBeNull();
  });

  it("routes brand link to homepage", () => {
    render(<SiteHeader />);

    const brandLink = screen.getByTestId("navbar-brand-link");
    expect(brandLink.getAttribute("href")).toBe("/");
  });
});
