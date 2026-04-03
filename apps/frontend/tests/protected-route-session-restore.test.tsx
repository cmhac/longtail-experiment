/** @vitest-environment jsdom */

import { render, screen } from "@testing-library/react";
import React from "react";
import { beforeEach, describe, expect, it, vi } from "vitest";

import { ProtectedRouteGate } from "../src/components/auth/ProtectedRouteGate";
import {
  buildLoginRedirectPath,
  evaluateProtectedRoute,
  resolvePostLoginRedirect,
} from "../src/lib/auth/route-guard";
import * as routeGuard from "../src/lib/auth/route-guard";
import { clearAuthSessionState, persistAuthSessionState } from "../src/lib/auth/session-state";

const { pushMock } = vi.hoisted(() => {
  return {
    pushMock: vi.fn(),
  };
});

vi.mock("next/navigation", () => ({
  useRouter: () => ({ push: pushMock }),
}));

describe("protected-route session restoration", () => {
  beforeEach(() => {
    window.localStorage.clear();
    clearAuthSessionState();
    pushMock.mockReset();
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

  it("redirects protected gate when no session is restored", () => {
    render(
      <ProtectedRouteGate pathname="/comparison" fallbackTestId="auth-gate-fallback">
        <div data-testid="protected-content">Protected content</div>
      </ProtectedRouteGate>,
    );

    expect(pushMock).toHaveBeenCalledWith("/login?next=%2Fcomparison");
    expect(screen.getByTestId("auth-gate-fallback")).toBeTruthy();
    expect(screen.queryByTestId("protected-content")).toBeNull();
  });

  it("renders protected gate children when session is restored", () => {
    persistAuthSessionState({
      sessionToken: "session-9",
      user: {
        user_id: "user-9",
        email: "gate@example.com",
        display_name: null,
        account_status: "active",
        is_admin: false,
      },
      restoredAt: "2026-04-02T00:00:00+00:00",
    });

    render(
      <ProtectedRouteGate pathname="/comparison" fallbackTestId="auth-gate-fallback">
        <div data-testid="protected-content">Protected content</div>
      </ProtectedRouteGate>,
    );

    expect(pushMock).not.toHaveBeenCalled();
    expect(screen.getByTestId("protected-content")).toBeTruthy();
  });

  it("does not navigate when protected decision omits redirect path", () => {
    const evaluateSpy = vi
      .spyOn(routeGuard, "evaluateProtectedRoute")
      .mockReturnValue({ allow: false, redirectTo: null, session: null });

    try {
      render(
        <ProtectedRouteGate pathname="/comparison" fallbackTestId="auth-gate-fallback">
          <div data-testid="protected-content">Protected content</div>
        </ProtectedRouteGate>,
      );

      expect(pushMock).not.toHaveBeenCalled();
      expect(screen.getAllByTestId("auth-gate-fallback").length).toBeGreaterThan(0);
    } finally {
      evaluateSpy.mockRestore();
    }
  });
});
