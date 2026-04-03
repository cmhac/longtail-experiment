import { beforeEach, describe, expect, it, vi } from "vitest";

import {
  clearAuthSessionState,
  loadAuthSessionState,
  persistAuthSessionState,
} from "../src/lib/auth/session-state";

describe("session-state", () => {
  beforeEach(() => {
    const store = new Map<string, string>();
    vi.stubGlobal("window", {
      localStorage: {
        getItem: (key: string) => store.get(key) ?? null,
        setItem: (key: string, value: string) => {
          store.set(key, value);
        },
        removeItem: (key: string) => {
          store.delete(key);
        },
      },
    });
  });

  it("persists and loads auth session state", () => {
    clearAuthSessionState();

    persistAuthSessionState({
      sessionToken: "session-1",
      user: {
        user_id: "user-1",
        email: "user@example.com",
        display_name: "User",
        account_status: "active",
        is_admin: false,
        privilege_level: "user",
      },
      restoredAt: "2026-04-02T00:00:00+00:00",
    });

    const loaded = loadAuthSessionState();
    expect(loaded?.sessionToken).toBe("session-1");
    expect(loaded?.user.user_id).toBe("user-1");
  });

  it("returns null for missing or invalid state and clears storage", () => {
    clearAuthSessionState();
    expect(loadAuthSessionState()).toBeNull();

    window.localStorage.setItem("longtail.auth.session", "{invalid-json");
    expect(loadAuthSessionState()).toBeNull();

    window.localStorage.setItem(
      "longtail.auth.session",
      JSON.stringify({
        sessionToken: "",
        user: { user_id: "" },
      }),
    );
    expect(loadAuthSessionState()).toBeNull();

    clearAuthSessionState();
    expect(window.localStorage.getItem("longtail.auth.session")).toBeNull();
  });

  it("no-ops safely when window storage is unavailable", () => {
    vi.stubGlobal("window", undefined);

    expect(loadAuthSessionState()).toBeNull();
    persistAuthSessionState({
      sessionToken: "session-1",
      user: {
        user_id: "user-1",
        email: "user@example.com",
        display_name: "User",
        account_status: "active",
        is_admin: false,
        privilege_level: "user",
      },
      restoredAt: "2026-04-02T00:00:00+00:00",
    });
    clearAuthSessionState();
  });
});
