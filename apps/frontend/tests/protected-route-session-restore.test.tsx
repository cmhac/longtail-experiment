/** @vitest-environment jsdom */

import { beforeEach, describe, expect, it, vi } from "vitest";

import {
  buildLoginRedirectPath,
  evaluateProtectedRoute,
  resolvePostLoginRedirect,
} from "../src/lib/auth/route-guard";
import { clearAuthSessionState, persistAuthSessionState } from "../src/lib/auth/session-state";

describe("protected-route session restoration", () => {
  beforeEach(() => {
    window.localStorage.clear();
    clearAuthSessionState();
  });

  it("redirects unauthenticated users to login with encoded next path", () => {
    const decision = evaluateProtectedRoute("/comparison");

    expect(decision.allow).toBe(false);
    expect(decision.redirectTo).toBe("/login?next=%2Fcomparison");
    expect(buildLoginRedirectPath("/datasets/FEDFUNDS")).toBe("/login?next=%2Fdatasets%2FFEDFUNDS");
  });

  it("allows protected route access when session state is restored", () => {
    persistAuthSessionState({
      sessionToken: "session-1",
      user: {
        user_id: "user-1",
        email: "user@example.com",
        display_name: "User",
        account_status: "active",
        is_admin: false,
      },
      restoredAt: "2026-04-02T00:00:00+00:00",
    });

    const decision = evaluateProtectedRoute("/comparison");
    expect(decision.allow).toBe(true);
    expect(decision.redirectTo).toBeNull();
    expect(decision.session?.user.user_id).toBe("user-1");
  });

  it("resolves post-login redirects safely", () => {
    expect(resolvePostLoginRedirect("/datasets")).toBe("/datasets");
    expect(resolvePostLoginRedirect("/login")).toBe("/comparison");
    expect(resolvePostLoginRedirect("https://evil.example")).toBe("/comparison");
    expect(resolvePostLoginRedirect("//evil.example")).toBe("/comparison");
    expect(resolvePostLoginRedirect(null)).toBe("/comparison");
  });

  it("supports restoration checks with explicit session argument", () => {
    const decision = evaluateProtectedRoute("/comparison", {
      sessionToken: "session-explicit",
      user: {
        user_id: "user-2",
        email: "explicit@example.com",
        display_name: null,
        account_status: "active",
        is_admin: false,
      },
      restoredAt: "2026-04-02T00:00:00+00:00",
    });

    expect(decision.allow).toBe(true);
    expect(decision.redirectTo).toBeNull();
    expect(decision.session?.sessionToken).toBe("session-explicit");
  });

  it("falls back next path for invalid login redirects", () => {
    expect(buildLoginRedirectPath("")).toBe("/login?next=%2Fcomparison");
    expect(buildLoginRedirectPath("login")).toBe("/login?next=%2Flogin");
  });
});
