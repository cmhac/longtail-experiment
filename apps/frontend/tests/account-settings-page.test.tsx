/** @vitest-environment jsdom */

import { cleanup, fireEvent, render, screen, waitFor } from "@testing-library/react";
import React from "react";
import type { ReactNode } from "react";
import { beforeEach, describe, expect, it, vi } from "vitest";
import AccountSettingsPage from "../src/app/settings/page";
import { loadAuthSessionState } from "../src/lib/auth/session-state";

const { pushMock, routerMock } = vi.hoisted(() => {
  const push = vi.fn();
  return {
    pushMock: push,
    routerMock: { push },
  };
});

vi.mock("next/navigation", () => ({
  useRouter: () => routerMock,
}));

vi.mock("../src/shell/site-page-frame", () => ({
  SitePageFrame: ({ children }: { children: ReactNode }) => <div>{children}</div>,
}));

const createJsonResponse = (payload: object, status = 200): Response => {
  return new Response(JSON.stringify(payload), {
    status,
    headers: { "content-type": "application/json" },
  });
};

describe("account settings page", () => {
  beforeEach(() => {
    cleanup();
    window.localStorage.clear();
    window.localStorage.setItem(
      "longtail.auth.session",
      JSON.stringify({
        sessionToken: "session-auth",
        user: {
          user_id: "user-1",
          email: "user@example.com",
          display_name: "User",
          account_status: "active",
          is_admin: false,
          privilege_level: "user",
        },
        restoredAt: "2026-04-03T00:00:00+00:00",
      }),
    );
    pushMock.mockReset();
  });

  const getInputById = (id: string): HTMLInputElement => {
    const input = document.getElementById(id);
    if (!(input instanceof HTMLInputElement)) {
      throw new Error(`Expected input with id ${id}`);
    }
    return input;
  };

  it("updates profile and revokes an active session", async () => {
    const sessions = [
      {
        session_id: "session-auth",
        created_at: "2026-04-03T00:00:00+00:00",
        expires_at: "2026-05-03T00:00:00+00:00",
        session_status: "active",
        client_label: "Current Browser",
      },
      {
        session_id: "session-other",
        created_at: "2026-04-02T00:00:00+00:00",
        expires_at: "2026-05-02T00:00:00+00:00",
        session_status: "active",
        client_label: "Phone",
      },
    ];

    vi.stubGlobal(
      "fetch",
      vi.fn(async (input: RequestInfo | URL, init?: RequestInit) => {
        const url = String(input);
        const method = init?.method ?? "GET";

        if (url === "/api/account/profile" && method === "GET") {
          return createJsonResponse({
            user_id: "user-1",
            email: "user@example.com",
            display_name: "User",
            account_status: "active",
            is_admin: false,
            privilege_level: "user",
            updated_at: "2026-04-03T00:00:00+00:00",
          });
        }

        if (url === "/api/auth/sessions" && method === "GET") {
          return createJsonResponse({ items: sessions });
        }

        if (url === "/api/account/profile" && method === "PATCH") {
          const parsed = JSON.parse(String(init?.body ?? "{}")) as {
            email?: string;
            display_name: string | null;
          };
          return createJsonResponse({
            user_id: "user-1",
            email: parsed.email ?? "user@example.com",
            display_name: parsed.display_name,
            account_status: "active",
            is_admin: false,
            privilege_level: "user",
            updated_at: "2026-04-03T00:10:00+00:00",
          });
        }

        if (url === "/api/auth/sessions" && method === "POST") {
          const parsed = JSON.parse(String(init?.body ?? "{}")) as {
            action?: string;
            session_id?: string;
          };
          if (parsed.action === "revoke" && parsed.session_id) {
            const index = sessions.findIndex((item) => item.session_id === parsed.session_id);
            if (index >= 0) {
              sessions.splice(index, 1);
            }
            return new Response(null, { status: 204 });
          }
        }

        throw new Error(`Unexpected request ${method} ${url}`);
      }),
    );

    render(<AccountSettingsPage />);

    await screen.findByTestId("account-settings-profile-form");

    fireEvent.change(getInputById("account-settings-email-input"), {
      target: { value: "updated@example.com" },
    });
    fireEvent.change(getInputById("account-settings-display-name-input"), {
      target: { value: "Updated User" },
    });
    fireEvent.submit(screen.getByTestId("account-settings-profile-form"));

    await screen.findByTestId("account-settings-success-message");
    expect(screen.getByTestId("account-settings-success-message").textContent).toContain(
      "Profile updated",
    );

    fireEvent.click(screen.getByTestId("account-settings-revoke-session-other"));

    await waitFor(() => {
      expect(screen.getByTestId("account-settings-success-message").textContent).toContain(
        "Session revoked",
      );
    });
  });

  it("invalidates local session after password change", async () => {
    vi.stubGlobal(
      "fetch",
      vi.fn(async (input: RequestInfo | URL, init?: RequestInit) => {
        const url = String(input);
        const method = init?.method ?? "GET";

        if (url === "/api/account/profile" && method === "GET") {
          return createJsonResponse({
            user_id: "user-1",
            email: "user@example.com",
            display_name: "User",
            account_status: "active",
            is_admin: false,
            privilege_level: "user",
            updated_at: "2026-04-03T00:00:00+00:00",
          });
        }

        if (url === "/api/auth/sessions" && method === "GET") {
          return createJsonResponse({
            items: [
              {
                session_id: "session-auth",
                created_at: "2026-04-03T00:00:00+00:00",
                expires_at: "2026-05-03T00:00:00+00:00",
                session_status: "active",
                client_label: "Current Browser",
              },
            ],
          });
        }

        if (url === "/api/account/password" && method === "POST") {
          return new Response(null, { status: 204 });
        }

        throw new Error(`Unexpected request ${method} ${url}`);
      }),
    );

    render(<AccountSettingsPage />);

    await screen.findByTestId("account-settings-password-form");

    fireEvent.change(getInputById("account-settings-current-password-input"), {
      target: { value: "oldpassword123" },
    });
    fireEvent.change(getInputById("account-settings-new-password-input"), {
      target: { value: "newpassword123" },
    });
    fireEvent.submit(screen.getByTestId("account-settings-password-form"));

    await waitFor(() => {
      expect(pushMock).toHaveBeenCalledWith("/login?next=%2Fsettings");
    });
    expect(loadAuthSessionState()).toBeNull();
  });

  it("requests account deletion and updates status message", async () => {
    vi.stubGlobal(
      "fetch",
      vi.fn(async (input: RequestInfo | URL, init?: RequestInit) => {
        const url = String(input);
        const method = init?.method ?? "GET";

        if (url === "/api/account/profile" && method === "GET") {
          return createJsonResponse({
            user_id: "user-1",
            email: "user@example.com",
            display_name: "User",
            account_status: "active",
            is_admin: false,
            privilege_level: "user",
            updated_at: "2026-04-03T00:00:00+00:00",
          });
        }

        if (url === "/api/auth/sessions" && method === "GET") {
          return createJsonResponse({ items: [] });
        }

        if (url === "/api/account/deletion-request" && method === "POST") {
          return createJsonResponse(
            {
              user_id: "user-1",
              account_status: "deletion_pending",
              deletion_due_at: "2026-04-10T00:00:00+00:00",
            },
            202,
          );
        }

        throw new Error(`Unexpected request ${method} ${url}`);
      }),
    );

    render(<AccountSettingsPage />);
    await screen.findByTestId("account-settings-delete-button");

    fireEvent.click(screen.getByTestId("account-settings-delete-button"));

    await waitFor(() => {
      expect(screen.getByTestId("account-settings-success-message").textContent).toContain(
        "Deletion requested",
      );
    });
  });

  it("redirects to login when no local session is present", async () => {
    window.localStorage.clear();

    render(<AccountSettingsPage />);

    await waitFor(() => {
      expect(pushMock).toHaveBeenCalledWith("/login?next=%2Fsettings");
    });
  });

  it("signs out from account page action", async () => {
    vi.stubGlobal(
      "fetch",
      vi.fn(async (input: RequestInfo | URL, init?: RequestInit) => {
        const url = String(input);
        const method = init?.method ?? "GET";

        if (url === "/api/account/profile" && method === "GET") {
          return createJsonResponse({
            user_id: "user-1",
            email: "user@example.com",
            display_name: "User",
            account_status: "active",
            is_admin: false,
            privilege_level: "user",
            updated_at: "2026-04-03T00:00:00+00:00",
          });
        }

        if (url === "/api/auth/sessions" && method === "GET") {
          return createJsonResponse({ items: [] });
        }

        if (url === "/api/auth/sessions" && method === "POST") {
          return new Response(null, { status: 204 });
        }

        throw new Error(`Unexpected request ${method} ${url}`);
      }),
    );

    render(<AccountSettingsPage />);
    await screen.findByTestId("account-settings-sign-out-button");

    fireEvent.click(screen.getByTestId("account-settings-sign-out-button"));

    await waitFor(() => {
      expect(pushMock).toHaveBeenCalledWith("/login?next=%2Fsettings");
    });
  });

  it("shows error state when profile fetch fails", async () => {
    vi.stubGlobal(
      "fetch",
      vi.fn(async (input: RequestInfo | URL, init?: RequestInit) => {
        const url = String(input);
        const method = init?.method ?? "GET";
        if (url === "/api/account/profile" && method === "GET") {
          return createJsonResponse(
            { error: { code: "http_error", message: "Failed to load profile" } },
            500,
          );
        }
        throw new Error(`Unexpected request ${method} ${url}`);
      }),
    );

    render(<AccountSettingsPage />);

    await waitFor(() => {
      expect(screen.getByTestId("account-settings-page-error").textContent).toContain(
        "Failed to load profile",
      );
    });
  });

  it("redirects to login when profile fetch returns 401", async () => {
    vi.stubGlobal(
      "fetch",
      vi.fn(async (input: RequestInfo | URL, init?: RequestInit) => {
        const url = String(input);
        const method = init?.method ?? "GET";
        if (url === "/api/account/profile" && method === "GET") {
          return new Response(null, { status: 401 });
        }
        throw new Error(`Unexpected request ${method} ${url}`);
      }),
    );

    render(<AccountSettingsPage />);

    await waitFor(() => {
      expect(pushMock).toHaveBeenCalledWith("/login?next=%2Fsettings");
    });
    expect(loadAuthSessionState()).toBeNull();
  });

  it("shows fallback error when profile error payload is not JSON", async () => {
    vi.stubGlobal(
      "fetch",
      vi.fn(async (input: RequestInfo | URL, init?: RequestInit) => {
        const url = String(input);
        const method = init?.method ?? "GET";
        if (url === "/api/account/profile" && method === "GET") {
          return new Response("downstream-failure", {
            status: 500,
            headers: { "content-type": "text/plain" },
          });
        }
        throw new Error(`Unexpected request ${method} ${url}`);
      }),
    );

    render(<AccountSettingsPage />);

    await waitFor(() => {
      expect(screen.getByTestId("account-settings-page-error").textContent).toContain(
        "Unable to load account settings.",
      );
    });
  });

  it("shows admin chip and admin link for admin profiles", async () => {
    window.localStorage.setItem(
      "longtail.auth.session",
      JSON.stringify({
        sessionToken: "session-auth",
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

    vi.stubGlobal(
      "fetch",
      vi.fn(async (input: RequestInfo | URL, init?: RequestInit) => {
        const url = String(input);
        const method = init?.method ?? "GET";
        if (url === "/api/account/profile" && method === "GET") {
          return createJsonResponse({
            user_id: "admin-1",
            email: "admin@example.com",
            display_name: "Admin",
            account_status: "active",
            is_admin: true,
            privilege_level: "admin",
            updated_at: "2026-04-03T00:00:00+00:00",
          });
        }
        if (url === "/api/auth/sessions" && method === "GET") {
          return createJsonResponse({ items: [] });
        }
        throw new Error(`Unexpected request ${method} ${url}`);
      }),
    );

    render(<AccountSettingsPage />);

    await screen.findByTestId("account-settings-role-chip");
    expect(screen.getByTestId("account-settings-role-chip").textContent).toContain("Admin");
    expect(screen.getByTestId("account-settings-admin-link").getAttribute("href")).toBe("/admin");
  });
});
