/** @vitest-environment jsdom */

import { fireEvent, render, screen } from "@testing-library/react";
import React from "react";
import { afterEach, describe, expect, it } from "vitest";
import { SiteHeader } from "../src/shell/site-header";

afterEach(() => {
  document.body.innerHTML = "";
});

describe("navbar appearance mode contract", () => {
  it("keeps shell-readable classes in light mode", () => {
    document.documentElement.setAttribute("data-theme-preference", "light");
    render(<SiteHeader />);

    const header = screen.getByTestId("shell-header");
    expect(header.className).toContain("shell-readable");
  });

  it("keeps shell-readable classes in dark mode", () => {
    document.documentElement.setAttribute("data-theme-preference", "dark");
    render(<SiteHeader />);

    const header = screen.getByTestId("shell-header");
    expect(header.className).toContain("shell-readable");
  });

  it("keeps dropdown content readable in dark mode", () => {
    document.documentElement.setAttribute("data-theme-preference", "dark");
    render(<SiteHeader />);

    fireEvent.click(screen.getByTestId("navbar-profile-control"));
    const dropdown = screen.getByTestId("navbar-profile-dropdown");
    expect(dropdown.className).toContain("shell-navbar-dropdown");
  });
});
