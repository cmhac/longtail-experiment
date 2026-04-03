"use client";

import { Card } from "@heroui/react";
import { useRouter } from "next/navigation";
import React from "react";
import { useEffect, useMemo, useState } from "react";
import type { JSX } from "react";
import { AccountSettingsForm } from "../../components/account/AccountSettingsForm";
import type { AuthErrorEnvelope, ProfileResponse } from "../../lib/api/auth-management-types";
import { buildLoginRedirectPath } from "../../lib/auth/route-guard";
import {
  type AuthSessionState,
  clearAuthSessionState,
  loadAuthSessionState,
} from "../../lib/auth/session-state";
import { SitePageFrame } from "../../shell/site-page-frame";

const SETTINGS_PATH = "/settings";

const parseApiErrorMessage = async (response: Response, fallback: string): Promise<string> => {
  try {
    const payload = (await response.json()) as AuthErrorEnvelope;
    return payload.error?.message ?? fallback;
  } catch {
    return fallback;
  }
};

const AccountSettingsPage = (): JSX.Element => {
  const router = useRouter();
  const [session, setSession] = useState<AuthSessionState | null>(null);
  const [profile, setProfile] = useState<ProfileResponse | null>(null);
  const [errorMessage, setErrorMessage] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(true);

  const redirectToLogin = useMemo(() => buildLoginRedirectPath(SETTINGS_PATH), []);

  useEffect(() => {
    const restored = loadAuthSessionState();
    if (!restored) {
      router.push(redirectToLogin);
      return;
    }
    setSession(restored);
  }, [redirectToLogin, router]);

  useEffect(() => {
    if (!session) {
      return;
    }
    const loadProfile = async (): Promise<void> => {
      setIsLoading(true);
      try {
        const response = await fetch("/api/account/profile", {
          method: "GET",
          headers: {
            accept: "application/json",
            authorization: `Bearer ${session.sessionToken}`,
          },
        });
        if (response.status === 401) {
          clearAuthSessionState();
          router.push(redirectToLogin);
          return;
        }
        if (!response.ok) {
          throw new Error(await parseApiErrorMessage(response, "Unable to load account settings."));
        }
        const payload = (await response.json()) as ProfileResponse;
        setProfile(payload);
      } catch (error) {
        setErrorMessage(
          error instanceof Error ? error.message : "Unable to load account settings.",
        );
      } finally {
        setIsLoading(false);
      }
    };
    void loadProfile();
  }, [redirectToLogin, router, session]);

  if (!session) {
    return (
      <SitePageFrame activeTab="datasets" mainClassName="grid gap-4" mainTestId="settings-page">
        <Card className="p-5">Redirecting to sign in...</Card>
      </SitePageFrame>
    );
  }

  return (
    <SitePageFrame activeTab="datasets" mainClassName="grid gap-4" mainTestId="settings-page">
      <Card className="grid gap-1 p-5">
        <h1 className="font-semibold text-2xl">Account settings</h1>
        <p className="text-default-600 text-sm">
          Manage your profile, password, and active sessions.
        </p>
      </Card>

      {isLoading ? <Card className="p-5">Loading account settings...</Card> : null}
      {errorMessage ? (
        <Card className="p-5 text-danger" data-testid="account-settings-page-error">
          {errorMessage}
        </Card>
      ) : null}

      {!isLoading && profile ? (
        <AccountSettingsForm
          initialProfile={profile}
          sessionToken={session.sessionToken}
          onSessionInvalidated={() => {
            clearAuthSessionState();
            router.push(redirectToLogin);
          }}
        />
      ) : null}
    </SitePageFrame>
  );
};

export default AccountSettingsPage;
