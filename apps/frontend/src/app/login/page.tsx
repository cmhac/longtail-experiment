"use client";

import { Button, Card, Input } from "@heroui/react";
import Link from "next/link";
import { useRouter, useSearchParams } from "next/navigation";
import React from "react";
import { type FormEvent, useMemo, useState } from "react";
import type { JSX } from "react";
import type { AuthSessionResponse } from "../../lib/api/auth-management-types";
import { resolvePostLoginRedirect } from "../../lib/auth/route-guard";
import { persistAuthSessionState } from "../../lib/auth/session-state";

const LOGIN_API_PATH = "/api/auth/sessions";

const loginThroughFrontendRoute = async (payload: {
  email: string;
  password: string;
}): Promise<AuthSessionResponse> => {
  const response = await fetch(LOGIN_API_PATH, {
    method: "POST",
    headers: { "content-type": "application/json", accept: "application/json" },
    body: JSON.stringify({ action: "login", ...payload }),
  });

  if (!response.ok) {
    throw new Error("login_failed");
  }

  return (await response.json()) as AuthSessionResponse;
};

const LoginPage = (): JSX.Element => {
  const router = useRouter();
  const searchParams = useSearchParams();
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [submitting, setSubmitting] = useState(false);
  const [errorMessage, setErrorMessage] = useState<string | null>(null);

  const nextPath = useMemo(() => {
    return resolvePostLoginRedirect(searchParams.get("next"));
  }, [searchParams]);

  const canSubmit = email.trim().length > 0 && password.length > 0;

  const handleSubmit = async (event: FormEvent<HTMLFormElement>): Promise<void> => {
    event.preventDefault();
    if (!canSubmit || submitting) {
      return;
    }

    setSubmitting(true);
    setErrorMessage(null);
    try {
      const payload = await loginThroughFrontendRoute({
        email: email.trim(),
        password,
      });
      persistAuthSessionState({
        sessionToken: payload.session.session_id,
        user: payload.user,
        restoredAt: new Date().toISOString(),
      });
      router.push(nextPath);
    } catch {
      setErrorMessage("Sign-in failed. Check your credentials and try again.");
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <main
      className="mx-auto grid min-h-[65vh] w-full max-w-md items-center px-4"
      data-testid="login-page"
    >
      <Card className="grid gap-5 p-6" data-testid="login-card">
        <div className="grid gap-1">
          <h1 className="font-semibold text-2xl">Sign in</h1>
          <p className="text-default-600 text-sm">Access your Longtail account.</p>
        </div>

        <form className="grid gap-4" data-testid="login-form" onSubmit={handleSubmit}>
          <label className="grid gap-1 text-sm" htmlFor="login-email-input">
            <span>Email</span>
            <Input
              autoComplete="email"
              className="w-full"
              data-testid="login-email"
              id="login-email-input"
              type="email"
              value={email}
              onChange={(event) => {
                setEmail(event.target.value);
              }}
            />
          </label>
          <label className="grid gap-1 text-sm" htmlFor="login-password-input">
            <span>Password</span>
            <Input
              autoComplete="current-password"
              className="w-full"
              data-testid="login-password"
              id="login-password-input"
              type="password"
              value={password}
              onChange={(event) => {
                setPassword(event.target.value);
              }}
            />
          </label>

          {errorMessage ? (
            <p className="text-danger text-sm" data-testid="login-error-message">
              {errorMessage}
            </p>
          ) : null}

          <Button
            data-testid="login-submit"
            isDisabled={!canSubmit || submitting}
            type="submit"
            variant="primary"
          >
            {submitting ? "Signing in..." : "Continue"}
          </Button>
        </form>

        <p className="text-default-600 text-sm">
          New to Longtail?{" "}
          <Link className="font-medium text-primary" href="/register">
            Create an account
          </Link>
          .
        </p>
      </Card>
    </main>
  );
};

export default LoginPage;
