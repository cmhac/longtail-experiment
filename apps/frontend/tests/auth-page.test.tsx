/** @vitest-environment jsdom */

import { fireEvent, render, screen, waitFor } from "@testing-library/react";
import React from "react";
import { beforeEach, describe, expect, it, vi } from "vitest";
import LoginPage from "../src/app/login/page";
import RegisterPage from "../src/app/register/page";
import { logoutAccount } from "../src/lib/api/auth-management-client";
import { loadAuthSessionState } from "../src/lib/auth/session-state";
import { SiteHeader } from "../src/shell/site-header";

const { pushMock, searchParamsState } = vi.hoisted(() => {
  return {
    pushMock: vi.fn(),
    searchParamsState: {
      value: new URLSearchParams(),
      set(next: URLSearchParams) {
        this.value = next;
      },
    },
  };
});

vi.mock("next/navigation", () => ({
  usePathname: () => "/login",
  useRouter: () => ({ push: pushMock }),
  useSearchParams: () => searchParamsState.value,
}));

vi.mock("../src/lib/api/auth-management-client", async () => {
  const actual = await vi.importActual("../src/lib/api/auth-management-client");
  return {
    ...actual,
    logoutAccount: vi.fn(),
  };
});

const getInputById = (id: string): HTMLInputElement => {
  const input = document.getElementById(id);
  if (!(input instanceof HTMLInputElement)) {
    throw new Error(`Expected input with id ${id}`);
  }
  return input;
};

describe("auth page", () => {
  beforeEach(() => {
    window.localStorage.clear();
    pushMock.mockReset();
    searchParamsState.set(new URLSearchParams());
    vi.mocked(logoutAccount).mockReset();
    vi.stubGlobal("fetch", vi.fn());
  });

  it("covers sign-in and restores session for protected redirect", async () => {
    searchParamsState.set(new URLSearchParams("next=%2Fcomparison"));
    vi.mocked(globalThis.fetch).mockResolvedValue(
      new Response(
        JSON.stringify({
          user: {
            user_id: "user-1",
            email: "user@example.com",
            display_name: "User",
            account_status: "active",
            is_admin: false,
          },
          session: {
            session_id: "session-1",
            created_at: "2026-04-02T00:00:00+00:00",
            expires_at: "2026-05-02T00:00:00+00:00",
            session_status: "active",
            client_label: "Browser",
          },
        }),
        { status: 200, headers: { "content-type": "application/json" } },
      ),
    );

    render(<LoginPage />);

    fireEvent.change(getInputById("login-email-input"), {
      target: { value: "user@example.com" },
    });
    fireEvent.change(getInputById("login-password-input"), {
      target: { value: "verysecure123" },
    });
    fireEvent.submit(screen.getByTestId("login-form"));

    await waitFor(() => {
      expect(globalThis.fetch).toHaveBeenCalledWith(
        "/api/auth/sessions",
        expect.objectContaining({ method: "POST" }),
      );
    });
    expect(loadAuthSessionState()?.sessionToken).toBe("session-1");
    expect(pushMock).toHaveBeenCalledWith("/comparison");
  });

  it("covers registration flow and redirects after account creation", async () => {
    vi.mocked(globalThis.fetch).mockResolvedValue(
      new Response(
        JSON.stringify({
          user: {
            user_id: "user-2",
            email: "new@example.com",
            display_name: "New User",
            account_status: "active",
            is_admin: false,
          },
          session: {
            session_id: "session-2",
            created_at: "2026-04-02T00:00:00+00:00",
            expires_at: "2026-05-02T00:00:00+00:00",
            session_status: "active",
            client_label: "Browser",
          },
        }),
        { status: 201, headers: { "content-type": "application/json" } },
      ),
    );

    render(<RegisterPage />);

    fireEvent.change(getInputById("register-email-input"), {
      target: { value: "new@example.com" },
    });
    fireEvent.change(getInputById("register-display-name-input"), {
      target: { value: "New User" },
    });
    fireEvent.change(getInputById("register-password-input"), {
      target: { value: "verysecure123" },
    });
    fireEvent.submit(screen.getByTestId("register-form"));

    await waitFor(() => {
      expect(globalThis.fetch).toHaveBeenCalledWith(
        "/api/auth/sessions",
        expect.objectContaining({ method: "POST" }),
      );
    });
    expect(loadAuthSessionState()?.sessionToken).toBe("session-2");
    expect(pushMock).toHaveBeenCalledWith("/comparison");
  });

  it("covers sign-out action from header auth menu", async () => {
    window.localStorage.setItem(
      "longtail.auth.session",
      JSON.stringify({
        sessionToken: "session-logout",
        user: {
          user_id: "user-3",
          email: "logout@example.com",
          display_name: "Logout User",
          account_status: "active",
          is_admin: false,
        },
        restoredAt: "2026-04-02T00:00:00+00:00",
      }),
    );
    vi.mocked(logoutAccount).mockResolvedValue(undefined);

    render(<SiteHeader />);
    fireEvent.click(screen.getByTestId("navbar-profile-control"));
    fireEvent.click(screen.getByTestId("header-auth-sign-out"));

    await waitFor(() => {
      expect(logoutAccount).toHaveBeenCalledWith("session-logout");
    });
    expect(loadAuthSessionState()).toBeNull();
  });
});
