/** @vitest-environment jsdom */

import { cleanup, fireEvent, render, screen, waitFor } from "@testing-library/react";
import React from "react";
import { beforeEach, describe, expect, it, vi } from "vitest";

import { AccountSettingsForm } from "../src/components/account/AccountSettingsForm";

const profile = {
  user_id: "user-1",
  email: "user@example.com",
  display_name: "User",
  account_status: "active" as const,
  is_admin: false,
  updated_at: "2026-04-03T00:00:00+00:00",
};

const getInputById = (id: string): HTMLInputElement => {
  const input = document.getElementById(id);
  if (!(input instanceof HTMLInputElement)) {
    throw new Error(`Expected input with id ${id}`);
  }
  return input;
};

const jsonResponse = (payload: object, status = 200): Response => {
  return new Response(JSON.stringify(payload), {
    status,
    headers: { "content-type": "application/json" },
  });
};

describe("AccountSettingsForm", () => {
  beforeEach(() => {
    cleanup();
    vi.restoreAllMocks();
  });

  it("invokes onSessionInvalidated when session list fetch returns 401", async () => {
    const onSessionInvalidated = vi.fn();
    vi.stubGlobal("fetch", vi.fn().mockResolvedValue(new Response(null, { status: 401 })));

    render(
      <AccountSettingsForm
        initialProfile={profile}
        onSessionInvalidated={onSessionInvalidated}
        sessionToken="session-1"
      />,
    );

    await waitFor(() => {
      expect(onSessionInvalidated).toHaveBeenCalledTimes(1);
    });
  });

  it("shows profile update error when backend rejects patch", async () => {
    vi.stubGlobal(
      "fetch",
      vi
        .fn()
        .mockResolvedValueOnce(jsonResponse({ items: [] }))
        .mockResolvedValueOnce(
          jsonResponse(
            { error: { code: "invalid_request", message: "Profile update failed" } },
            400,
          ),
        ),
    );

    render(
      <AccountSettingsForm
        initialProfile={profile}
        onSessionInvalidated={() => {}}
        sessionToken="session-1"
      />,
    );

    await screen.findByTestId("account-settings-profile-form");
    fireEvent.change(getInputById("account-settings-display-name-input"), {
      target: { value: "Updated User" },
    });
    fireEvent.submit(screen.getByTestId("account-settings-profile-form"));

    await waitFor(() => {
      expect(screen.getByTestId("account-settings-error-message").textContent).toContain(
        "Profile update failed",
      );
    });
  });

  it("shows revoke-session error and password error states", async () => {
    vi.stubGlobal(
      "fetch",
      vi
        .fn()
        .mockResolvedValueOnce(
          jsonResponse({
            items: [
              {
                session_id: "session-other",
                created_at: "2026-04-03T00:00:00+00:00",
                expires_at: "2026-05-03T00:00:00+00:00",
                session_status: "active",
                client_label: "Phone",
              },
            ],
          }),
        )
        .mockResolvedValueOnce(
          jsonResponse({ error: { code: "not_found", message: "Unable to revoke" } }, 404),
        )
        .mockResolvedValueOnce(
          jsonResponse({ error: { code: "unauthorized", message: "Password rejected" } }, 401),
        ),
    );

    const onSessionInvalidated = vi.fn();
    render(
      <AccountSettingsForm
        initialProfile={profile}
        onSessionInvalidated={onSessionInvalidated}
        sessionToken="session-1"
      />,
    );

    await screen.findByTestId("account-settings-revoke-session-other");
    fireEvent.click(screen.getByTestId("account-settings-revoke-session-other"));

    await waitFor(() => {
      expect(screen.getByTestId("account-settings-error-message").textContent).toContain(
        "Unable to revoke",
      );
    });

    fireEvent.change(getInputById("account-settings-current-password-input"), {
      target: { value: "oldpassword123" },
    });
    fireEvent.change(getInputById("account-settings-new-password-input"), {
      target: { value: "newpassword123" },
    });
    fireEvent.submit(screen.getByTestId("account-settings-password-form"));

    await waitFor(() => {
      expect(onSessionInvalidated).toHaveBeenCalledTimes(1);
    });
  });

  it("shows deletion error when request fails", async () => {
    vi.stubGlobal(
      "fetch",
      vi
        .fn()
        .mockResolvedValueOnce(jsonResponse({ items: [] }))
        .mockResolvedValueOnce(
          jsonResponse({ error: { code: "http_error", message: "Deletion failed" } }, 500),
        ),
    );

    render(
      <AccountSettingsForm
        initialProfile={profile}
        onSessionInvalidated={() => {}}
        sessionToken="session-1"
      />,
    );

    await screen.findByTestId("account-settings-delete-button");
    fireEvent.click(screen.getByTestId("account-settings-delete-button"));

    await waitFor(() => {
      expect(screen.getByTestId("account-settings-error-message").textContent).toContain(
        "Deletion failed",
      );
    });
  });

  it("uses fallback errors when payload is not valid JSON", async () => {
    vi.stubGlobal(
      "fetch",
      vi
        .fn()
        .mockResolvedValueOnce(jsonResponse({ items: [] }))
        .mockResolvedValueOnce(
          new Response("bad-response", {
            status: 500,
            headers: { "content-type": "text/plain" },
          }),
        ),
    );

    render(
      <AccountSettingsForm
        initialProfile={profile}
        onSessionInvalidated={() => {}}
        sessionToken="session-1"
      />,
    );

    await screen.findByTestId("account-settings-profile-form");
    fireEvent.submit(screen.getByTestId("account-settings-profile-form"));

    await waitFor(() => {
      expect(screen.getByTestId("account-settings-error-message").textContent).toContain(
        "Unable to update profile.",
      );
    });
  });

  it("invalidates session when revoking or deleting receives 401", async () => {
    vi.stubGlobal(
      "fetch",
      vi
        .fn()
        .mockResolvedValueOnce(
          jsonResponse({
            items: [
              {
                session_id: "session-other",
                created_at: "2026-04-03T00:00:00+00:00",
                expires_at: "2026-05-03T00:00:00+00:00",
                session_status: "active",
                client_label: null,
              },
            ],
          }),
        )
        .mockResolvedValueOnce(new Response(null, { status: 401 }))
        .mockResolvedValueOnce(new Response(null, { status: 401 })),
    );

    const onSessionInvalidated = vi.fn();
    render(
      <AccountSettingsForm
        initialProfile={profile}
        onSessionInvalidated={onSessionInvalidated}
        sessionToken="session-1"
      />,
    );

    await screen.findByText("Unknown device");
    fireEvent.click(screen.getByTestId("account-settings-revoke-session-other"));
    await waitFor(() => {
      expect(onSessionInvalidated).toHaveBeenCalledTimes(1);
    });

    fireEvent.click(screen.getByTestId("account-settings-delete-button"));
    await waitFor(() => {
      expect(onSessionInvalidated).toHaveBeenCalledTimes(2);
    });
  });

  it("does not submit password change when policy requirements are unmet", async () => {
    const fetchMock = vi.fn().mockResolvedValue(jsonResponse({ items: [] }));
    vi.stubGlobal("fetch", fetchMock);

    render(
      <AccountSettingsForm
        initialProfile={profile}
        onSessionInvalidated={() => {}}
        sessionToken="session-1"
      />,
    );

    await screen.findByTestId("account-settings-password-form");
    fireEvent.change(getInputById("account-settings-current-password-input"), {
      target: { value: "oldpassword123" },
    });
    fireEvent.change(getInputById("account-settings-new-password-input"), {
      target: { value: "short" },
    });
    fireEvent.submit(screen.getByTestId("account-settings-password-form"));

    await waitFor(() => {
      expect(fetchMock).toHaveBeenCalledTimes(1);
    });
  });

  it("shows password error response message for non-401 failure", async () => {
    vi.stubGlobal(
      "fetch",
      vi
        .fn()
        .mockResolvedValueOnce(jsonResponse({ items: [] }))
        .mockResolvedValueOnce(
          jsonResponse(
            { error: { code: "invalid_request", message: "Password policy failed" } },
            400,
          ),
        ),
    );

    render(
      <AccountSettingsForm
        initialProfile={profile}
        onSessionInvalidated={() => {}}
        sessionToken="session-1"
      />,
    );

    await screen.findByTestId("account-settings-password-form");
    fireEvent.change(getInputById("account-settings-current-password-input"), {
      target: { value: "oldpassword123" },
    });
    fireEvent.change(getInputById("account-settings-new-password-input"), {
      target: { value: "newpassword123" },
    });
    fireEvent.submit(screen.getByTestId("account-settings-password-form"));

    await waitFor(() => {
      expect(screen.getByTestId("account-settings-error-message").textContent).toContain(
        "Password policy failed",
      );
    });
  });

  it("invalidates session when profile update returns 401", async () => {
    vi.stubGlobal(
      "fetch",
      vi
        .fn()
        .mockResolvedValueOnce(jsonResponse({ items: [] }))
        .mockResolvedValueOnce(new Response(null, { status: 401 })),
    );

    const onSessionInvalidated = vi.fn();
    render(
      <AccountSettingsForm
        initialProfile={profile}
        onSessionInvalidated={onSessionInvalidated}
        sessionToken="session-1"
      />,
    );

    await screen.findByTestId("account-settings-profile-form");
    fireEvent.submit(screen.getByTestId("account-settings-profile-form"));

    await waitFor(() => {
      expect(onSessionInvalidated).toHaveBeenCalledTimes(1);
    });
  });

  it("shows fallback password error when request throws non-Error value", async () => {
    vi.stubGlobal(
      "fetch",
      vi
        .fn()
        .mockResolvedValueOnce(jsonResponse({ items: [] }))
        .mockRejectedValueOnce("network-failure"),
    );

    render(
      <AccountSettingsForm
        initialProfile={profile}
        onSessionInvalidated={() => {}}
        sessionToken="session-1"
      />,
    );

    await screen.findByTestId("account-settings-password-form");
    fireEvent.change(getInputById("account-settings-current-password-input"), {
      target: { value: "oldpassword123" },
    });
    fireEvent.change(getInputById("account-settings-new-password-input"), {
      target: { value: "newpassword123" },
    });
    fireEvent.submit(screen.getByTestId("account-settings-password-form"));

    await waitFor(() => {
      expect(screen.getByTestId("account-settings-error-message").textContent).toContain(
        "Unable to change password.",
      );
    });
  });
});
