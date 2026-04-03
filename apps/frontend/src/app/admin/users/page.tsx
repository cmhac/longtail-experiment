"use client";

import { Card } from "@heroui/react";
import { useRouter } from "next/navigation";
import React from "react";
import { useEffect, useMemo, useState } from "react";
import type { JSX } from "react";
import { AdminUserTable } from "../../../components/account/AdminUserTable";
import {
  PageHeaderSubtitle,
  PageHeaderTitle,
  PageHeaderWrapper,
} from "../../../components/discovery/PageHeader";
import type {
  AdminUserListResponse,
  AdminUserSummary,
  AuthErrorEnvelope,
} from "../../../lib/api/auth-management-types";
import { buildLoginRedirectPath } from "../../../lib/auth/route-guard";
import {
  type AuthSessionState,
  clearAuthSessionState,
  loadAuthSessionState,
} from "../../../lib/auth/session-state";
import { SitePageFrame } from "../../../shell/site-page-frame";

const ADMIN_USERS_PATH = "/admin/users";

const parseApiErrorMessage = async (response: Response, fallback: string): Promise<string> => {
  try {
    const payload = (await response.json()) as AuthErrorEnvelope;
    return payload.error?.message ?? fallback;
  } catch {
    return fallback;
  }
};

const authHeaders = (sessionToken: string): HeadersInit => ({
  "content-type": "application/json",
  accept: "application/json",
  authorization: `Bearer ${sessionToken}`,
});

const AdminUsersPage = (): JSX.Element => {
  const router = useRouter();
  const [session, setSession] = useState<AuthSessionState | null>(null);
  const [users, setUsers] = useState<AdminUserSummary[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [isUpdatingUserId, setIsUpdatingUserId] = useState<string | null>(null);
  const [isUpdatingRoleUserId, setIsUpdatingRoleUserId] = useState<string | null>(null);
  const [isRevokingUserId, setIsRevokingUserId] = useState<string | null>(null);
  const [errorMessage, setErrorMessage] = useState<string | null>(null);
  const [successMessage, setSuccessMessage] = useState<string | null>(null);

  const redirectToLogin = useMemo(() => buildLoginRedirectPath(ADMIN_USERS_PATH), []);

  useEffect(() => {
    const restored = loadAuthSessionState();
    if (!restored) {
      router.push(redirectToLogin);
      return;
    }
    if (!restored.user.is_admin) {
      setErrorMessage("Admin access is required to view this page.");
      setIsLoading(false);
      return;
    }
    setSession(restored);
  }, [redirectToLogin, router]);

  const loadUsers = React.useCallback(async (): Promise<void> => {
    if (!session) {
      return;
    }
    setIsLoading(true);
    setErrorMessage(null);
    try {
      const response = await fetch("/api/admin/users", {
        method: "GET",
        headers: authHeaders(session.sessionToken),
      });
      if (response.status === 401) {
        clearAuthSessionState();
        router.push(redirectToLogin);
        return;
      }
      if (response.status === 403) {
        throw new Error("Admin access is required to view this page.");
      }
      if (!response.ok) {
        throw new Error(await parseApiErrorMessage(response, "Unable to load admin users."));
      }
      const payload = (await response.json()) as AdminUserListResponse;
      setUsers(payload.items);
    } catch (error) {
      setErrorMessage(error instanceof Error ? error.message : "Unable to load admin users.");
    } finally {
      setIsLoading(false);
    }
  }, [redirectToLogin, router, session]);

  useEffect(() => {
    void loadUsers();
  }, [loadUsers]);

  const handleToggleStatus = async (user: AdminUserSummary): Promise<void> => {
    setIsUpdatingUserId(user.user_id);
    setErrorMessage(null);
    setSuccessMessage(null);
    try {
      const response = await fetch("/api/admin/users", {
        method: "PATCH",
        headers: authHeaders((session as AuthSessionState).sessionToken),
        body: JSON.stringify({
          user_id: user.user_id,
          account_status: user.account_status === "active" ? "deactivated" : "active",
        }),
      });
      if (!response.ok) {
        throw new Error(await parseApiErrorMessage(response, "Unable to update user status."));
      }
      const updated = (await response.json()) as AdminUserSummary;
      setUsers((previous) =>
        previous.map((item) => (item.user_id === updated.user_id ? updated : item)),
      );
      setSuccessMessage(`Updated ${updated.email} to ${updated.account_status}.`);
    } catch (error) {
      setErrorMessage(error instanceof Error ? error.message : "Unable to update user status.");
    } finally {
      setIsUpdatingUserId(null);
    }
  };

  const handleRevokeSessions = async (user: AdminUserSummary): Promise<void> => {
    setIsRevokingUserId(user.user_id);
    setErrorMessage(null);
    setSuccessMessage(null);
    try {
      const response = await fetch("/api/admin/users", {
        method: "POST",
        headers: authHeaders((session as AuthSessionState).sessionToken),
        body: JSON.stringify({
          action: "revoke_sessions",
          user_id: user.user_id,
        }),
      });
      if (!response.ok) {
        throw new Error(await parseApiErrorMessage(response, "Unable to revoke user sessions."));
      }
      setSuccessMessage(`Revoked active sessions for ${user.email}.`);
    } catch (error) {
      setErrorMessage(error instanceof Error ? error.message : "Unable to revoke user sessions.");
    } finally {
      setIsRevokingUserId(null);
    }
  };

  const handleToggleAdminRole = async (user: AdminUserSummary): Promise<void> => {
    setIsUpdatingRoleUserId(user.user_id);
    setErrorMessage(null);
    setSuccessMessage(null);
    try {
      const response = await fetch("/api/admin/users", {
        method: "PATCH",
        headers: authHeaders((session as AuthSessionState).sessionToken),
        body: JSON.stringify({
          user_id: user.user_id,
          role_action: user.is_admin ? "revoke_admin" : "grant_admin",
        }),
      });
      if (!response.ok) {
        throw new Error(await parseApiErrorMessage(response, "Unable to update user role."));
      }
      const updated = (await response.json()) as AdminUserSummary;
      setUsers((previous) =>
        previous.map((item) => (item.user_id === updated.user_id ? updated : item)),
      );
      setSuccessMessage(
        `${updated.is_admin ? "Granted" : "Revoked"} admin role for ${updated.email}.`,
      );
    } catch (error) {
      setErrorMessage(error instanceof Error ? error.message : "Unable to update user role.");
    } finally {
      setIsUpdatingRoleUserId(null);
    }
  };

  return (
    <SitePageFrame activeTab="datasets" mainClassName="grid gap-4" mainTestId="admin-users-page">
      <PageHeaderWrapper testId="admin-users-page-header">
        <PageHeaderTitle>Admin users</PageHeaderTitle>
        <PageHeaderSubtitle>
          Review account status, roles, and revoke active sessions for any user.
        </PageHeaderSubtitle>
      </PageHeaderWrapper>

      {isLoading ? <Card className="p-5">Loading user management...</Card> : null}
      {errorMessage ? (
        <Card className="p-5 text-danger" data-testid="admin-users-error-message">
          {errorMessage}
        </Card>
      ) : null}

      {!isLoading && !errorMessage ? (
        <AdminUserTable
          users={users}
          isUpdatingUserId={isUpdatingUserId}
          isRevokingUserId={isRevokingUserId}
          isUpdatingRoleUserId={isUpdatingRoleUserId}
          onToggleStatus={(user) => {
            void handleToggleStatus(user);
          }}
          onToggleAdminRole={(user) => {
            void handleToggleAdminRole(user);
          }}
          onRevokeSessions={(user) => {
            void handleRevokeSessions(user);
          }}
        />
      ) : null}

      {successMessage ? (
        <p className="text-sm text-success" data-testid="admin-users-success-message">
          {successMessage}
        </p>
      ) : null}
    </SitePageFrame>
  );
};

export default AdminUsersPage;
