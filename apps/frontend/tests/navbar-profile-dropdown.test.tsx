/** @vitest-environment jsdom */

import { fireEvent, render, screen } from "@testing-library/react";
import React from "react";
import { afterEach, describe, expect, it, vi } from "vitest";
import { SiteHeader } from "../src/shell/site-header";

vi.mock("next/navigation", () => ({
  usePathname: () => "/",
  useRouter: () => ({ push: () => undefined }),
  useSearchParams: () => new URLSearchParams("q="),
}));

afterEach(() => {
  document.body.innerHTML = "";
});

describe("navbar profile dropdown", () => {
  it("opens and closes the profile dropdown", () => {
    render(<SiteHeader />);

    const profileButton = screen.getByTestId("navbar-profile-control");
    expect(screen.queryByTestId("navbar-profile-dropdown")).toBeNull();

    fireEvent.click(profileButton);
    expect(screen.getByTestId("navbar-profile-dropdown")).not.toBeNull();

    fireEvent.click(profileButton);
    expect(screen.queryByTestId("navbar-profile-dropdown")).toBeNull();
  });

  it("renders the exact placeholder content", () => {
    render(<SiteHeader />);

    fireEvent.click(screen.getByTestId("navbar-profile-control"));
    expect(screen.getByTestId("header-auth-signed-out").textContent).toContain("Sign in");
    expect(screen.getByTestId("header-auth-signed-out").textContent).toContain("Create account");
  });

  it("closes when clicking outside the profile menu", () => {
    render(
      <>
        <button type="button" data-testid="outside-target">
          Outside
        </button>
        <SiteHeader />
      </>,
    );

    fireEvent.click(screen.getByTestId("navbar-profile-control"));
    expect(screen.getByTestId("navbar-profile-dropdown")).not.toBeNull();

    fireEvent.mouseDown(screen.getByTestId("outside-target"));
    expect(screen.queryByTestId("navbar-profile-dropdown")).toBeNull();
  });
});
