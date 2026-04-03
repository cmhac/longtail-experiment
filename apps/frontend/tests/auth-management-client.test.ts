import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";

import {
  AuthManagementApiError,
  changeAccountPassword,
  fetchAccountProfile,
  fetchAdminUsers,
  fetchCurrentSessions,
  loginAccount,
  logoutAccount,
  registerAccount,
  requestAccountDeletion,
  revokeSession,
  updateAccountProfile,
  updateAdminUserStatus,
} from "../src/lib/api/auth-management-client";

const originalBaseUrl = process.env.DISCOVERY_API_BASE_URL;

const mockJsonResponse = (payload: unknown, status = 200): Response => {
  return {
    ok: status >= 200 && status < 300,
    status,
    json: async () => payload,
  } as Response;
};

describe("auth-management-client", () => {
  beforeEach(() => {
    process.env.DISCOVERY_API_BASE_URL = "http://localhost:8080";
    vi.restoreAllMocks();
  });

  afterEach(() => {
    process.env.DISCOVERY_API_BASE_URL = originalBaseUrl;
  });

  it("supports register, login, session list, profile, and admin reads", async () => {
    const fetchSpy = vi
      .spyOn(globalThis, "fetch")
      .mockResolvedValueOnce(
        mockJsonResponse({
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
      )
      .mockResolvedValueOnce(
        mockJsonResponse({
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
      )
      .mockResolvedValueOnce(
        mockJsonResponse({
          items: [
            {
              session_id: "session-1",
              created_at: "2026-04-02T00:00:00+00:00",
              expires_at: "2026-05-02T00:00:00+00:00",
              session_status: "active",
              client_label: "Browser",
            },
          ],
        }),
      )
      .mockResolvedValueOnce(
        mockJsonResponse({
          user_id: "user-1",
          email: "user@example.com",
          display_name: "User",
          account_status: "active",
          is_admin: false,
          updated_at: "2026-04-02T00:00:00+00:00",
        }),
      )
      .mockResolvedValueOnce(
        mockJsonResponse({
          items: [
            {
              user_id: "user-2",
              email: "admin@example.com",
              display_name: "Admin",
              account_status: "active",
              is_admin: true,
              updated_at: "2026-04-02T00:00:00+00:00",
            },
          ],
        }),
      );

    const register = await registerAccount({
      email: "user@example.com",
      password: "verysecure123",
    });
    const login = await loginAccount({ email: "user@example.com", password: "verysecure123" });
    const sessions = await fetchCurrentSessions("session-1");
    const profile = await fetchAccountProfile("session-1");
    const adminUsers = await fetchAdminUsers("session-1");

    expect(register.user.user_id).toBe("user-1");
    expect(login.session.session_id).toBe("session-1");
    expect(sessions.items).toHaveLength(1);
    expect(profile.email).toBe("user@example.com");
    expect(adminUsers.items[0]?.is_admin).toBe(true);

    const firstCall = fetchSpy.mock.calls[0]?.[0];
    expect(String(firstCall)).toContain("/api/auth/sessions");
  });

  it("supports write calls with auth headers and no-content handling", async () => {
    vi.spyOn(globalThis, "fetch")
      .mockResolvedValueOnce({ ok: true, status: 204, json: async () => ({}) } as Response)
      .mockResolvedValueOnce({ ok: true, status: 204, json: async () => ({}) } as Response)
      .mockResolvedValueOnce(
        mockJsonResponse({
          user_id: "user-1",
          email: "user@example.com",
          display_name: "Updated",
          account_status: "active",
          is_admin: false,
          updated_at: "2026-04-02T00:00:00+00:00",
        }),
      )
      .mockResolvedValueOnce({ ok: true, status: 204, json: async () => ({}) } as Response)
      .mockResolvedValueOnce(
        mockJsonResponse({
          user_id: "user-1",
          account_status: "deletion_pending",
          deletion_due_at: "2026-04-09T00:00:00+00:00",
        }),
      )
      .mockResolvedValueOnce({ ok: true, status: 204, json: async () => ({}) } as Response)
      .mockResolvedValueOnce({ ok: true, status: 205, json: async () => ({}) } as Response);

    await logoutAccount("session-1");
    await revokeSession("session-1", "session-2");
    const updatedProfile = await updateAccountProfile("session-1", { display_name: "Updated" });
    await changeAccountPassword("session-1", {
      current_password: "oldpassword123",
      new_password: "newpassword123",
    });
    const deletion = await requestAccountDeletion("session-1");
    await updateAdminUserStatus("session-1", "user-2", { account_status: "deactivated" });

    expect(vi.mocked(globalThis.fetch).mock.calls[0]?.[1]).toMatchObject({
      method: "POST",
    });
    expect(String(vi.mocked(globalThis.fetch).mock.calls[0]?.[0])).toContain("/api/auth/sessions");

    expect(updatedProfile.display_name).toBe("Updated");
    expect(deletion.account_status).toBe("deletion_pending");
  });

  it("throws AuthManagementApiError for failed responses", async () => {
    vi.spyOn(globalThis, "fetch").mockResolvedValue(
      mockJsonResponse(
        {
          error: {
            code: "unauthorized",
            message: "Authentication required",
          },
        },
        401,
      ),
    );

    await expect(fetchCurrentSessions("bad-token")).rejects.toBeInstanceOf(AuthManagementApiError);
  });

  it("uses fallback error metadata when error payload is not JSON", async () => {
    vi.spyOn(globalThis, "fetch").mockResolvedValue({
      ok: false,
      status: 502,
      json: async () => {
        throw new Error("invalid json");
      },
    } as unknown as Response);

    await expect(fetchCurrentSessions("token")).rejects.toMatchObject({
      code: "http_error",
      status: 502,
    });
  });

  it("throws when API base URL is missing", async () => {
    process.env.DISCOVERY_API_BASE_URL = "";

    await expect(fetchCurrentSessions("token")).rejects.toThrow("Missing DISCOVERY_API_BASE_URL");
  });
});
