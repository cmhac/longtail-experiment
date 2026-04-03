"use client";

import { Button, Card, Input } from "@heroui/react";
import * as React from "react";
import type { JSX } from "react";
import type {
  AuthErrorEnvelope,
  ChangePasswordRequest,
  DeletionRequestResponse,
  ProfileResponse,
  SessionListResponse,
  SessionSummary,
  UpdateProfileRequest,
} from "../../lib/api/auth-management-types";

interface AccountSettingsFormProps {
  initialProfile: ProfileResponse;
  sessionToken: string;
  onSessionInvalidated: () => void;
}

const parseApiErrorMessage = async (response: Response, fallback: string): Promise<string> => {
  try {
    const payload = (await response.json()) as AuthErrorEnvelope;
    return payload.error?.message ?? fallback;
  } catch {
    return fallback;
  }
};

const withAuthHeaders = (sessionToken: string): HeadersInit => ({
  "content-type": "application/json",
  accept: "application/json",
  authorization: `Bearer ${sessionToken}`,
});

export const AccountSettingsForm = ({
  initialProfile,
  sessionToken,
  onSessionInvalidated,
}: AccountSettingsFormProps): JSX.Element => {
  const passwordHintId = React.useId();
  const [profile, setProfile] = React.useState<ProfileResponse>(initialProfile);
  const [emailInput, setEmailInput] = React.useState(initialProfile.email);
  const [displayNameInput, setDisplayNameInput] = React.useState(initialProfile.display_name ?? "");
  const [currentPassword, setCurrentPassword] = React.useState("");
  const [newPassword, setNewPassword] = React.useState("");
  const [sessions, setSessions] = React.useState<SessionSummary[]>([]);
  const [isLoadingSessions, setIsLoadingSessions] = React.useState(true);
  const [isSavingProfile, setIsSavingProfile] = React.useState(false);
  const [isChangingPassword, setIsChangingPassword] = React.useState(false);
  const [isRequestingDeletion, setIsRequestingDeletion] = React.useState(false);
  const [isSigningOut, setIsSigningOut] = React.useState(false);
  const [errorMessage, setErrorMessage] = React.useState<string | null>(null);
  const [successMessage, setSuccessMessage] = React.useState<string | null>(null);

  const fetchSessions = React.useCallback(async (): Promise<void> => {
    setIsLoadingSessions(true);
    try {
      const response = await fetch("/api/auth/sessions", {
        method: "GET",
        headers: withAuthHeaders(sessionToken),
      });
      if (response.status === 401) {
        onSessionInvalidated();
        return;
      }
      if (!response.ok) {
        throw new Error(await parseApiErrorMessage(response, "Unable to load active sessions."));
      }
      const payload = (await response.json()) as SessionListResponse;
      setSessions(payload.items);
    } catch (error) {
      setErrorMessage(error instanceof Error ? error.message : "Unable to load active sessions.");
    } finally {
      setIsLoadingSessions(false);
    }
  }, [onSessionInvalidated, sessionToken]);

  React.useEffect(() => {
    void fetchSessions();
  }, [fetchSessions]);

  const profileCanSubmit = React.useMemo(() => {
    return !isSavingProfile;
  }, [isSavingProfile]);

  const passwordCanSubmit = React.useMemo(() => {
    return currentPassword.trim().length > 0 && newPassword.length >= 12 && !isChangingPassword;
  }, [currentPassword, newPassword, isChangingPassword]);

  const handleProfileSubmit = async (event: React.FormEvent<HTMLFormElement>): Promise<void> => {
    event.preventDefault();
    if (!profileCanSubmit) {
      return;
    }
    setErrorMessage(null);
    setSuccessMessage(null);
    setIsSavingProfile(true);
    try {
      const payload: UpdateProfileRequest = {
        email: emailInput.trim(),
        display_name: displayNameInput.trim() === "" ? null : displayNameInput.trim(),
      };
      const response = await fetch("/api/account/profile", {
        method: "PATCH",
        headers: withAuthHeaders(sessionToken),
        body: JSON.stringify(payload),
      });
      if (response.status === 401) {
        onSessionInvalidated();
        return;
      }
      if (!response.ok) {
        throw new Error(await parseApiErrorMessage(response, "Unable to update profile."));
      }
      const updated = (await response.json()) as ProfileResponse;
      setProfile(updated);
      setEmailInput(updated.email);
      setDisplayNameInput(updated.display_name ?? "");
      setSuccessMessage("Profile updated.");
    } catch (error) {
      setErrorMessage(error instanceof Error ? error.message : "Unable to update profile.");
    } finally {
      setIsSavingProfile(false);
    }
  };

  const handleSignOut = async (): Promise<void> => {
    if (isSigningOut) {
      return;
    }
    setErrorMessage(null);
    setSuccessMessage(null);
    setIsSigningOut(true);
    try {
      await fetch("/api/auth/sessions", {
        method: "POST",
        headers: withAuthHeaders(sessionToken),
        body: JSON.stringify({ action: "logout" }),
      });
    } finally {
      setIsSigningOut(false);
      onSessionInvalidated();
    }
  };

  const handlePasswordSubmit = async (event: React.FormEvent<HTMLFormElement>): Promise<void> => {
    event.preventDefault();
    if (!passwordCanSubmit) {
      return;
    }
    setErrorMessage(null);
    setSuccessMessage(null);
    setIsChangingPassword(true);
    try {
      const payload: ChangePasswordRequest = {
        current_password: currentPassword,
        new_password: newPassword,
      };
      const response = await fetch("/api/account/password", {
        method: "POST",
        headers: withAuthHeaders(sessionToken),
        body: JSON.stringify(payload),
      });
      if (response.status === 401) {
        onSessionInvalidated();
        return;
      }
      if (!response.ok) {
        throw new Error(await parseApiErrorMessage(response, "Unable to change password."));
      }
      onSessionInvalidated();
    } catch (error) {
      setErrorMessage(error instanceof Error ? error.message : "Unable to change password.");
    } finally {
      setIsChangingPassword(false);
    }
  };

  const handleRevokeSession = async (sessionId: string): Promise<void> => {
    setErrorMessage(null);
    setSuccessMessage(null);
    try {
      const response = await fetch("/api/auth/sessions", {
        method: "POST",
        headers: withAuthHeaders(sessionToken),
        body: JSON.stringify({ action: "revoke", session_id: sessionId }),
      });
      if (response.status === 401) {
        onSessionInvalidated();
        return;
      }
      if (!response.ok) {
        throw new Error(await parseApiErrorMessage(response, "Unable to revoke session."));
      }
      await fetchSessions();
      setSuccessMessage("Session revoked.");
    } catch (error) {
      setErrorMessage(error instanceof Error ? error.message : "Unable to revoke session.");
    }
  };

  const handleDeletionRequest = async (): Promise<void> => {
    if (isRequestingDeletion) {
      return;
    }
    setErrorMessage(null);
    setSuccessMessage(null);
    setIsRequestingDeletion(true);
    try {
      const response = await fetch("/api/account/deletion-request", {
        method: "POST",
        headers: withAuthHeaders(sessionToken),
      });
      if (response.status === 401) {
        onSessionInvalidated();
        return;
      }
      if (!response.ok) {
        throw new Error(await parseApiErrorMessage(response, "Unable to request deletion."));
      }
      const payload = (await response.json()) as DeletionRequestResponse;
      setProfile((previous) => ({
        ...previous,
        account_status: payload.account_status,
      }));
      setSuccessMessage(`Deletion requested. Scheduled for ${payload.deletion_due_at}.`);
      await fetchSessions();
    } catch (error) {
      setErrorMessage(error instanceof Error ? error.message : "Unable to request deletion.");
    } finally {
      setIsRequestingDeletion(false);
    }
  };

  return (
    <div className="grid gap-4" data-testid="account-settings-form">
      <Card aria-busy={isSavingProfile} className="grid gap-4 p-5">
        <div className="grid gap-1">
          <h2 className="font-semibold text-lg">Profile</h2>
          <p className="text-default-600 text-sm">Keep your account details up to date.</p>
        </div>
        <form
          className="grid gap-3"
          data-testid="account-settings-profile-form"
          onSubmit={handleProfileSubmit}
        >
          <label className="grid gap-1 text-sm" htmlFor="account-settings-email-input">
            <span>Email</span>
            <Input
              id="account-settings-email-input"
              value={emailInput}
              onChange={(event) => setEmailInput(event.target.value)}
            />
          </label>
          <label className="grid gap-1 text-sm" htmlFor="account-settings-display-name-input">
            <span>Display name</span>
            <Input
              id="account-settings-display-name-input"
              value={displayNameInput}
              onChange={(event) => setDisplayNameInput(event.target.value)}
            />
          </label>
          {(profile.privilege_level === "admin" || profile.privilege_level === "owner") && (
            <p className="text-default-600 text-xs" data-testid="account-settings-role-chip">
              {profile.privilege_level === "owner" ? "Owner" : "Admin"}
            </p>
          )}
          {(profile.privilege_level === "admin" || profile.privilege_level === "owner") && (
            <Button
              data-testid="account-settings-admin-link"
              size="sm"
              variant="secondary"
              onPress={() => {
                if (typeof window !== "undefined") {
                  window.location.assign("/admin");
                }
              }}
            >
              Open admin pages
            </Button>
          )}
          <Button
            data-testid="account-settings-profile-submit"
            isDisabled={!profileCanSubmit}
            type="submit"
            variant="primary"
          >
            {isSavingProfile ? "Saving..." : "Save profile"}
          </Button>
        </form>
      </Card>

      <Card aria-busy={isChangingPassword} className="grid gap-4 p-5">
        <div className="grid gap-1">
          <h2 className="font-semibold text-lg">Password</h2>
          <p className="text-default-600 text-sm">
            Changing your password revokes all active sessions.
          </p>
        </div>
        <form
          className="grid gap-3"
          data-testid="account-settings-password-form"
          onSubmit={handlePasswordSubmit}
        >
          <label className="grid gap-1 text-sm" htmlFor="account-settings-current-password-input">
            <span>Current password</span>
            <Input
              id="account-settings-current-password-input"
              type="password"
              value={currentPassword}
              onChange={(event) => setCurrentPassword(event.target.value)}
            />
          </label>
          <label className="grid gap-1 text-sm" htmlFor="account-settings-new-password-input">
            <span>New password</span>
            <span className="text-default-500 text-xs" id={passwordHintId}>
              Must be at least 12 characters.
            </span>
            <Input
              aria-describedby={passwordHintId}
              id="account-settings-new-password-input"
              type="password"
              value={newPassword}
              onChange={(event) => setNewPassword(event.target.value)}
            />
          </label>
          <Button
            data-testid="account-settings-password-submit"
            isDisabled={!passwordCanSubmit}
            type="submit"
            variant="primary"
          >
            {isChangingPassword ? "Updating..." : "Change password"}
          </Button>
        </form>
      </Card>

      <Card
        aria-busy={isLoadingSessions}
        className="grid gap-4 p-5"
        data-testid="account-settings-sessions-card"
      >
        <div className="grid gap-1">
          <h2 className="font-semibold text-lg">Active sessions</h2>
          <p className="text-default-600 text-sm">Revoke any session you do not recognize.</p>
        </div>
        {isLoadingSessions ? (
          <p className="text-default-600 text-sm">Loading sessions...</p>
        ) : (
          <ul className="grid gap-2" data-testid="account-settings-session-list">
            {sessions.length === 0 ? (
              <li className="text-default-600 text-sm">No active sessions.</li>
            ) : (
              sessions.map((session) => (
                <li
                  key={session.session_id}
                  className="flex items-center justify-between gap-3 rounded-medium border border-default-200 px-3 py-2"
                >
                  <div className="grid">
                    <span className="text-sm">{session.client_label ?? "Unknown device"}</span>
                    <span className="text-default-500 text-xs">{session.session_id}</span>
                  </div>
                  <Button
                    aria-label={`Revoke session ${session.client_label ?? session.session_id}`}
                    data-testid={`account-settings-revoke-${session.session_id}`}
                    size="sm"
                    variant="outline"
                    onPress={() => {
                      void handleRevokeSession(session.session_id);
                    }}
                  >
                    Revoke
                  </Button>
                </li>
              ))
            )}
          </ul>
        )}
      </Card>

      <Card
        className="grid gap-3 border-danger-200 p-5"
        data-testid="account-settings-deletion-card"
      >
        <div className="grid gap-1">
          <h2 className="font-semibold text-lg">Account deletion</h2>
          <p className="text-default-600 text-sm">
            Request deletion to deactivate your account immediately and schedule hard deletion
            later.
          </p>
        </div>
        <Button
          data-testid="account-settings-delete-button"
          isDisabled={isRequestingDeletion || profile.account_status === "deletion_pending"}
          variant="danger-soft"
          onPress={() => {
            void handleDeletionRequest();
          }}
        >
          {isRequestingDeletion ? "Submitting..." : "Request account deletion"}
        </Button>
        <Button
          data-testid="account-settings-sign-out-button"
          isDisabled={isSigningOut}
          variant="danger-soft"
          onPress={() => {
            void handleSignOut();
          }}
        >
          {isSigningOut ? "Signing out..." : "Sign out"}
        </Button>
      </Card>

      {errorMessage ? (
        <p
          aria-live="assertive"
          className="text-danger text-sm"
          data-testid="account-settings-error-message"
          role="alert"
        >
          {errorMessage}
        </p>
      ) : null}
      {successMessage ? (
        <output
          aria-live="polite"
          className="text-sm text-success"
          data-testid="account-settings-success-message"
        >
          {successMessage}
        </output>
      ) : null}
    </div>
  );
};
