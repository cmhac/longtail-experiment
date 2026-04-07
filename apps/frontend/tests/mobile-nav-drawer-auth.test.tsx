/** @vitest-environment jsdom */

import { cleanup, fireEvent, render, screen, waitFor } from "@testing-library/react";
import React from "react";
import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";
import type { AuthSessionState } from "../src/lib/auth/session-state";
import { SiteHeader } from "../src/shell/site-header";

vi.mock("../src/lib/navigation-client", () => ({
  navigateTo: vi.fn(),
}));

vi.mock("next/navigation", () => ({
  usePathname: () => "/",
  useRouter: () => ({ push: () => undefined }),
  useSearchParams: () => new URLSearchParams("q="),
}));

vi.mock("../src/lib/api/auth-management-client", async () => {
  const actual = await vi.importActual("../src/lib/api/auth-management-client");
  return {
    ...actual,
    logoutAccount: vi.fn(),
  };
});

vi.mock("../src/lib/api/notification-client", async () => {
  const actual = await vi.importActual("../src/lib/api/notification-client");
  return {
    ...actual,
    requireNotificationSessionToken: vi.fn(async (token?: string) => token ?? "session-token"),
    fetchNotificationSummary: vi.fn(async () => ({
      unread_count: 0,
      last_notification_at: null,
      generated_at: "2026-04-06T00:00:00Z",
    })),
  };
});

import { logoutAccount } from "../src/lib/api/auth-management-client";
import {
  fetchNotificationSummary,
  requireNotificationSessionToken,
} from "../src/lib/api/notification-client";
import { navigateTo } from "../src/lib/navigation-client";

const asMock = <T extends (...args: never[]) => unknown>(value: T) => {
  return vi.mocked(value);
};

let viewportWidth = 390;

const mediaQueryMatches = (query: string, width: number): boolean => {
  const maxWidthMatch = query.match(/max-width:\s*(\d+)px/);
  if (maxWidthMatch && width > Number(maxWidthMatch[1])) {
    return false;
  }

  const minWidthMatch = query.match(/min-width:\s*(\d+)px/);
  if (minWidthMatch && width < Number(minWidthMatch[1])) {
    return false;
  }

  return true;
};

const setAuthSession = (state: AuthSessionState | null): void => {
  if (!state) {
    window.localStorage.removeItem("longtail.auth.session");
    return;
  }

  window.localStorage.setItem("longtail.auth.session", JSON.stringify(state));
};

const openDrawer = async (): Promise<void> => {
  fireEvent.click(screen.getByTestId("mobile-nav-drawer-trigger"));
  await waitFor(() => {
    expect(screen.getByTestId("mobile-nav-drawer-panel")).not.toBeNull();
  });
};

beforeEach(() => {
  viewportWidth = 390;
  Object.defineProperty(window, "innerWidth", {
    configurable: true,
    writable: true,
    value: viewportWidth,
  });
  vi.stubGlobal(
    "matchMedia",
    vi.fn((query: string) => ({
      matches: mediaQueryMatches(query, viewportWidth),
      media: query,
      onchange: null,
      addEventListener: vi.fn(),
      removeEventListener: vi.fn(),
      addListener: vi.fn(),
      removeListener: vi.fn(),
      dispatchEvent: vi.fn(),
    })),
  );
  asMock(logoutAccount).mockReset();
  asMock(navigateTo).mockReset();
  asMock(fetchNotificationSummary).mockClear();
  asMock(requireNotificationSessionToken).mockClear();
  vi.spyOn(window, "scrollTo").mockImplementation(() => {
    return;
  });
  window.localStorage.clear();
});

afterEach(() => {
  cleanup();
  window.localStorage.clear();
  vi.restoreAllMocks();
  vi.unstubAllGlobals();
});

describe("mobile nav drawer auth and role behaviors", () => {
  it("redirects signed-out protected taps to /login", async () => {
    render(<SiteHeader />);

    await openDrawer();
    fireEvent.click(screen.getByTestId("mobile-nav-drawer-action-account"));
    expect(navigateTo).toHaveBeenCalledWith("/login");

    await openDrawer();
    fireEvent.click(screen.getByTestId("mobile-nav-drawer-action-comparison"));
    expect(navigateTo).toHaveBeenCalledWith("/login");
  });

  it("signs out from drawer and redirects home", async () => {
    setAuthSession({
      sessionToken: "session-logout",
      user: {
        user_id: "user-1",
        email: "user@example.com",
        display_name: "User",
        account_status: "active",
        is_admin: false,
        privilege_level: "user",
      },
      restoredAt: "2026-04-06T00:00:00Z",
    });
    asMock(logoutAccount).mockResolvedValue(undefined);

    render(<SiteHeader />);

    await openDrawer();
    fireEvent.click(screen.getByTestId("mobile-nav-drawer-action-sign-out"));

    await waitFor(() => {
      expect(logoutAccount).toHaveBeenCalledWith("session-logout");
    });
    expect(navigateTo).toHaveBeenCalledWith("/");
  });

  it("shows admin above sign out for admin and hides for non-admin and signed-out", async () => {
    setAuthSession({
      sessionToken: "admin-session",
      user: {
        user_id: "admin-1",
        email: "admin@example.com",
        display_name: "Admin",
        account_status: "active",
        is_admin: true,
        privilege_level: "admin",
      },
      restoredAt: "2026-04-06T00:00:00Z",
    });

    const { unmount } = render(<SiteHeader />);

    await openDrawer();
    const footer = screen.getByTestId("mobile-nav-drawer-footer");
    const footerOrder = Array.from(footer.children).map((element) =>
      element.getAttribute("data-testid"),
    );
    expect(footerOrder).toEqual([
      "mobile-nav-drawer-action-admin",
      "mobile-nav-drawer-action-sign-out",
    ]);

    fireEvent.click(screen.getByTestId("mobile-nav-drawer-action-admin"));
    expect(navigateTo).toHaveBeenCalledWith("/admin");

    unmount();

    setAuthSession({
      sessionToken: "user-session",
      user: {
        user_id: "user-2",
        email: "user2@example.com",
        display_name: "User",
        account_status: "active",
        is_admin: false,
        privilege_level: "user",
      },
      restoredAt: "2026-04-06T00:00:00Z",
    });
    render(<SiteHeader />);
    await openDrawer();
    expect(screen.queryByTestId("mobile-nav-drawer-action-admin")).toBeNull();
    fireEvent.click(screen.getByTestId("mobile-nav-drawer-backdrop"));

    cleanup();

    setAuthSession(null);
    render(<SiteHeader />);
    await openDrawer();
    expect(screen.queryByTestId("mobile-nav-drawer-action-admin")).toBeNull();
  });

  it("keeps bell unread parity and supports loading-state transitions", async () => {
    setAuthSession({
      sessionToken: "session-bell",
      user: {
        user_id: "user-3",
        email: "notify@example.com",
        display_name: "Notify",
        account_status: "active",
        is_admin: false,
        privilege_level: "user",
      },
      restoredAt: "2026-04-06T00:00:00Z",
    });

    let resolveSummary: (value: {
      unread_count: number;
      last_notification_at: string | null;
      generated_at: string;
    }) => void = () => undefined;
    asMock(fetchNotificationSummary).mockImplementation(
      () =>
        new Promise((resolve) => {
          resolveSummary = resolve;
        }),
    );

    render(<SiteHeader />);

    await openDrawer();
    expect(screen.queryByTestId("mobile-nav-drawer-bell-badge")).toBeNull();

    resolveSummary({
      unread_count: 4,
      last_notification_at: "2026-04-06T00:00:00Z",
      generated_at: "2026-04-06T00:00:00Z",
    });

    await waitFor(() => {
      expect(screen.getByTestId("navbar-notifications-badge").textContent).toBe("4");
    });
    expect(screen.getByTestId("mobile-nav-drawer-bell-badge").textContent).toBe("4");

    fireEvent.click(screen.getByTestId("mobile-nav-drawer-bell"));
    await waitFor(() => {
      expect(navigateTo).toHaveBeenCalledWith("/notifications");
    });
    expect(screen.queryByTestId("navbar-notifications-dropdown")).toBeNull();
  });
});
