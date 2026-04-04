"use client";

import { Card } from "@heroui/react";
import Link from "next/link";
import { useRouter } from "next/navigation";
import React from "react";
import { useEffect, useMemo, useState } from "react";
import type { JSX } from "react";
import {
  PageHeaderSubtitle,
  PageHeaderTitle,
  PageHeaderWrapper,
} from "../../components/discovery/PageHeader";
import type {
  AdminNavigationResponse,
  AuthErrorEnvelope,
} from "../../lib/api/auth-management-types";
import { buildLoginRedirectPath } from "../../lib/auth/route-guard";
import {
  type AuthSessionState,
  clearAuthSessionState,
  loadAuthSessionState,
} from "../../lib/auth/session-state";
import { SitePageFrame } from "../../shell/site-page-frame";

const ADMIN_PATH = "/admin";

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

const AdminLandingPage = (): JSX.Element => {
  const router = useRouter();
  const [session, setSession] = useState<AuthSessionState | null>(null);
  const [items, setItems] = useState<AdminNavigationResponse["items"]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [errorMessage, setErrorMessage] = useState<string | null>(null);

  const redirectToLogin = useMemo(() => buildLoginRedirectPath(ADMIN_PATH), []);

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

  useEffect(() => {
    if (!session) {
      return;
    }
    const loadNavigation = async (): Promise<void> => {
      setIsLoading(true);
      setErrorMessage(null);
      try {
        const response = await fetch("/api/admin/navigation", {
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
          throw new Error(await parseApiErrorMessage(response, "Unable to load admin pages."));
        }
        const payload = (await response.json()) as AdminNavigationResponse;
        setItems(payload.items);
      } catch (error) {
        setErrorMessage(error instanceof Error ? error.message : "Unable to load admin pages.");
      } finally {
        setIsLoading(false);
      }
    };
    void loadNavigation();
  }, [redirectToLogin, router, session]);

  return (
    <SitePageFrame activeTab="datasets" mainClassName="grid gap-4" mainTestId="admin-page">
      <PageHeaderWrapper testId="admin-page-header">
        <PageHeaderTitle>Admin</PageHeaderTitle>
        <PageHeaderSubtitle>Navigate to protected administration surfaces.</PageHeaderSubtitle>
      </PageHeaderWrapper>

      {isLoading ? <Card className="p-5">Loading admin pages...</Card> : null}
      {errorMessage ? (
        <Card className="p-5 text-danger" data-testid="admin-page-error-message">
          {errorMessage}
        </Card>
      ) : null}

      {!isLoading && !errorMessage ? (
        <Card className="grid gap-3 p-5" data-testid="admin-page-links">
          {items.length === 0 ? (
            <p className="text-default-600 text-sm">No admin pages available.</p>
          ) : (
            items.map((item) => (
              <Link key={item.item_key} className="grid gap-1" href={item.route}>
                <span className="font-medium text-sm">{item.label}</span>
                <span className="text-default-600 text-xs">{item.description}</span>
              </Link>
            ))
          )}
        </Card>
      ) : null}
    </SitePageFrame>
  );
};

export default AdminLandingPage;
