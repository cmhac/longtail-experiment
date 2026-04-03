/** @vitest-environment jsdom */

import { cleanup, render, screen, waitFor } from "@testing-library/react";
import React from "react";
import type { ReactNode } from "react";
import { beforeEach, describe, expect, it, vi } from "vitest";
import AdminPage from "../src/app/admin/page";

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

describe("admin page", () => {
  beforeEach(() => {
    cleanup();
    window.localStorage.clear();
    pushMock.mockReset();
  });

  it("lists admin navigation destinations", async () => {
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
        return createJsonResponse({
          items: [
            {
              item_key: "admin_users",
              label: "Users",
              route: "/admin/users",
              description: "Manage account status, sessions, and admin roles.",
            },
          ],
        });
      }),
    );

    render(<AdminPage />);

    await waitFor(() => {
      const usersLabel = screen.getByText("Users");
      const usersLink = usersLabel.closest("a");
      expect(usersLink?.getAttribute("href")).toBe("/admin/users");
    });
  });

  it("redirects to login when no local session exists", async () => {
    render(<AdminPage />);

    await waitFor(() => {
      expect(pushMock).toHaveBeenCalledWith("/login?next=%2Fadmin");
    });
  });

  it("shows an error message for non-admin users", async () => {
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

    render(<AdminPage />);

    await waitFor(() => {
      expect(screen.getByTestId("admin-page-error-message").textContent).toContain(
        "Admin access is required",
      );
    });
  });

  it("renders empty state when admin navigation has no items", async () => {
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
        return createJsonResponse({ items: [] });
      }),
    );

    render(<AdminPage />);

    await waitFor(() => {
      expect(screen.getByText("No admin pages available.")).toBeTruthy();
    });
  });

  it("redirects to login on 401 admin navigation response", async () => {
    window.localStorage.setItem(
      "longtail.auth.session",
      JSON.stringify({
        sessionToken: "expired-admin-session",
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
        return createJsonResponse({ error: { code: "unauthorized" } }, 401);
      }),
    );

    render(<AdminPage />);

    await waitFor(() => {
      expect(pushMock).toHaveBeenCalledWith("/login?next=%2Fadmin");
    });
    expect(window.localStorage.getItem("longtail.auth.session")).toBeNull();
  });

  it("shows API fallback error message when admin navigation fails", async () => {
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
        return createJsonResponse({ error: { code: "oops" } }, 500);
      }),
    );

    render(<AdminPage />);

    await waitFor(() => {
      expect(screen.getByTestId("admin-page-error-message").textContent).toContain(
        "Unable to load admin pages.",
      );
    });
  });

  it("shows admin-access error message on 403 response", async () => {
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
        return createJsonResponse({ error: { code: "forbidden" } }, 403);
      }),
    );

    render(<AdminPage />);

    await waitFor(() => {
      expect(screen.getByTestId("admin-page-error-message").textContent).toContain(
        "Admin access is required to view this page.",
      );
    });
  });

  it("uses fallback error message when response body is not JSON", async () => {
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
        return new Response("not-json", {
          status: 500,
          headers: { "content-type": "text/plain" },
        });
      }),
    );

    render(<AdminPage />);

    await waitFor(() => {
      expect(screen.getByTestId("admin-page-error-message").textContent).toContain(
        "Unable to load admin pages.",
      );
    });
  });
});
