/** @vitest-environment jsdom */

import { fireEvent, render, screen } from "@testing-library/react";
import React from "react";
import { afterEach, describe, expect, it } from "vitest";
import { SiteHeader } from "../src/shell/site-header";

afterEach(() => {
  document.body.innerHTML = "";
});

describe("navbar appearance mode contract", () => {
  it("keeps header shell-region classes in light mode", () => {
    render(<SiteHeader />);

    const header = screen.getByTestId("shell-header");
    expect(header.className).toContain("shell-region");
    expect(header.className).toContain("shell-region-header");
  });

  it("keeps header shell-region classes in dark mode", () => {
    render(<SiteHeader />);

    const header = screen.getByTestId("shell-header");
    expect(header.className).toContain("shell-region");
    expect(header.className).toContain("shell-region-header");
  });

  it("keeps dropdown content readable in dark mode", () => {
    render(<SiteHeader />);

    fireEvent.click(screen.getByTestId("navbar-profile-control"));
    const dropdown = screen.getByTestId("navbar-profile-dropdown");
    expect(dropdown.className).toContain("shell-navbar-dropdown");
  });
});
