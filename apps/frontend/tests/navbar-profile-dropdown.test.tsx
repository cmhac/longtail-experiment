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

  it("renders account and admin actions for admin sessions", () => {
    window.localStorage.setItem(
      "longtail.auth.session",
      JSON.stringify({
        sessionToken: "admin-session",
        user: {
          user_id: "admin-1",
          email: "admin@example.com",
          display_name: "Admin",
          account_status: "active",
          is_admin: true,
          privilege_level: "admin",
        },
        restoredAt: "2026-04-03T00:00:00+00:00",
      }),
    );

    render(<SiteHeader />);

    fireEvent.click(screen.getByTestId("navbar-profile-control"));
    expect(screen.getByTestId("header-auth-account-button").textContent).toContain("Account");
    expect(screen.getByRole("link", { name: "Admin" }).getAttribute("href")).toBe("/admin");
    expect(screen.getByTestId("header-auth-role-chip").textContent).toContain("Admin");
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
