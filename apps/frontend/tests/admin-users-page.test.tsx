/** @vitest-environment jsdom */

import { cleanup, fireEvent, render, screen, waitFor } from "@testing-library/react";
import React from "react";
import type { ReactNode } from "react";
import { beforeEach, describe, expect, it, vi } from "vitest";
import AdminUsersPage from "../src/app/admin/users/page";

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

describe("admin users page", () => {
  beforeEach(() => {
    cleanup();
    window.localStorage.clear();
    pushMock.mockReset();
  });

  it("lists users and supports status updates plus session revocation", async () => {
    const users: Array<{
      user_id: string;
      email: string;
      display_name: string;
      account_status: string;
      is_admin: boolean;
      privilege_level: "user" | "admin" | "owner";
      updated_at: string;
    }> = [
      {
        user_id: "user-1",
        email: "user@example.com",
        display_name: "User",
        account_status: "active",
        is_admin: false,
        privilege_level: "user",
        updated_at: "2026-04-03T00:00:00+00:00",
      },
    ];

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

    vi.stubGlobal(
      "fetch",
      vi.fn(async (input: RequestInfo | URL, init?: RequestInit) => {
        const url = String(input);
        const method = init?.method ?? "GET";

        if (url === "/api/admin/users" && method === "GET") {
          return createJsonResponse({ items: users });
        }

        if (url === "/api/admin/users" && method === "PATCH") {
          const payload = JSON.parse(String(init?.body ?? "{}")) as {
            user_id?: string;
            account_status?: string;
            role_action?: "grant_admin" | "revoke_admin";
          };
          const current = users[0];
          if (!current) {
            throw new Error("Expected seeded user");
          }
          const next = {
            ...current,
            account_status: payload.account_status ?? current.account_status,
            is_admin:
              payload.role_action === "grant_admin"
                ? true
                : payload.role_action === "revoke_admin"
                  ? false
                  : current.is_admin,
            privilege_level:
              payload.role_action === "grant_admin"
                ? "admin"
                : payload.role_action === "revoke_admin"
                  ? "user"
                  : current.privilege_level,
          };
          users[0] = next;
          return createJsonResponse(next);
        }

        if (url === "/api/admin/users" && method === "POST") {
          return new Response(null, { status: 204 });
        }

        throw new Error(`Unexpected request ${method} ${url}`);
      }),
    );

    render(<AdminUsersPage />);

    await screen.findByTestId("admin-user-row-user-1");

    fireEvent.click(screen.getByTestId("admin-user-status-toggle-user-1"));

    await waitFor(() => {
      expect(screen.getByTestId("admin-user-status-user-1").textContent).toContain("deactivated");
    });

    fireEvent.click(screen.getByTestId("admin-user-revoke-user-1"));

    await waitFor(() => {
      expect(screen.getByTestId("admin-users-success-message").textContent).toContain(
        "Revoked active sessions",
      );
    });

    fireEvent.click(screen.getByTestId("admin-user-role-toggle-user-1"));

    await waitFor(() => {
      expect(screen.getByTestId("admin-users-success-message").textContent).toContain(
        "Granted admin role",
      );
    });
  });

  it("redirects to login when no local session is available", async () => {
    render(<AdminUsersPage />);

    await waitFor(() => {
      expect(pushMock).toHaveBeenCalledWith("/login?next=%2Fadmin%2Fusers");
    });
  });

  it("shows authorization error when a non-admin session is restored", async () => {
    window.localStorage.setItem(
      "longtail.auth.session",
      JSON.stringify({
        sessionToken: "user-session",
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

    render(<AdminUsersPage />);

    await waitFor(() => {
      expect(screen.getByTestId("admin-users-error-message").textContent).toContain(
        "Admin access is required",
      );
    });
  });

  it("shows revoke-session API errors from the admin action", async () => {
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

    vi.stubGlobal(
      "fetch",
      vi.fn(async (input: RequestInfo | URL, init?: RequestInit) => {
        const url = String(input);
        const method = init?.method ?? "GET";
        if (url === "/api/admin/users" && method === "GET") {
          return createJsonResponse({
            items: [
              {
                user_id: "user-1",
                email: "user@example.com",
                display_name: "User",
                account_status: "active",
                is_admin: false,
                privilege_level: "user",
                updated_at: "2026-04-03T00:00:00+00:00",
              },
            ],
          });
        }
        if (url === "/api/admin/users" && method === "POST") {
          return createJsonResponse(
            { error: { code: "forbidden", message: "Cannot revoke this user" } },
            403,
          );
        }
        throw new Error(`Unexpected request ${method} ${url}`);
      }),
    );

    render(<AdminUsersPage />);
    await screen.findByTestId("admin-user-row-user-1");

    fireEvent.click(screen.getByTestId("admin-user-revoke-user-1"));

    await waitFor(() => {
      expect(screen.getByTestId("admin-users-error-message").textContent).toContain(
        "Cannot revoke this user",
      );
    });
  });

  it("shows status-update API errors from the admin action", async () => {
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

    vi.stubGlobal(
      "fetch",
      vi.fn(async (input: RequestInfo | URL, init?: RequestInit) => {
        const url = String(input);
        const method = init?.method ?? "GET";
        if (url === "/api/admin/users" && method === "GET") {
          return createJsonResponse({
            items: [
              {
                user_id: "user-1",
                email: "user@example.com",
                display_name: "User",
                account_status: "active",
                is_admin: false,
                privilege_level: "user",
                updated_at: "2026-04-03T00:00:00+00:00",
              },
            ],
          });
        }
        if (url === "/api/admin/users" && method === "PATCH") {
          return createJsonResponse(
            { error: { code: "conflict", message: "Cannot deactivate final admin" } },
            409,
          );
        }
        throw new Error(`Unexpected request ${method} ${url}`);
      }),
    );

    render(<AdminUsersPage />);
    await screen.findByTestId("admin-user-row-user-1");

    fireEvent.click(screen.getByTestId("admin-user-status-toggle-user-1"));

    await waitFor(() => {
      expect(screen.getByTestId("admin-users-error-message").textContent).toContain(
        "Cannot deactivate final admin",
      );
    });
  });

  it("clears local auth and redirects when admin list fetch returns 401", async () => {
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

    vi.stubGlobal(
      "fetch",
      vi.fn(async () => {
        return new Response(null, { status: 401 });
      }),
    );

    render(<AdminUsersPage />);

    await waitFor(() => {
      expect(pushMock).toHaveBeenCalledWith("/login?next=%2Fadmin%2Fusers");
    });
  });

  it("shows access-required error when backend list fetch returns 403", async () => {
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

    vi.stubGlobal(
      "fetch",
      vi.fn(async () => {
        return new Response(null, { status: 403 });
      }),
    );

    render(<AdminUsersPage />);

    await waitFor(() => {
      expect(screen.getByTestId("admin-users-error-message").textContent).toContain(
        "Admin access is required",
      );
    });
  });

  it("shows owner-protected role button state", async () => {
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

    vi.stubGlobal(
      "fetch",
      vi.fn(async (input: RequestInfo | URL, init?: RequestInit) => {
        const url = String(input);
        const method = init?.method ?? "GET";
        if (url === "/api/admin/users" && method === "GET") {
          return createJsonResponse({
            items: [
              {
                user_id: "owner-1",
                email: "owner@example.com",
                display_name: "Owner",
                account_status: "active",
                is_admin: true,
                privilege_level: "owner",
                updated_at: "2026-04-03T00:00:00+00:00",
              },
            ],
          });
        }
        throw new Error(`Unexpected request ${method} ${url}`);
      }),
    );

    render(<AdminUsersPage />);
    await screen.findByTestId("admin-user-row-owner-1");
    expect(screen.getByTestId("admin-user-role-toggle-owner-1").textContent).toContain(
      "Owner protected",
    );
  });
});
