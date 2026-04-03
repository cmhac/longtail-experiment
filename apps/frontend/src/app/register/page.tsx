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

const REGISTER_API_PATH = "/api/auth/sessions";

const registerThroughFrontendRoute = async (payload: {
  email: string;
  password: string;
  display_name: string | null;
}): Promise<AuthSessionResponse> => {
  const response = await fetch(REGISTER_API_PATH, {
    method: "POST",
    headers: { "content-type": "application/json", accept: "application/json" },
    body: JSON.stringify({ action: "register", ...payload }),
  });

  if (!response.ok) {
    throw new Error("register_failed");
  }

  return (await response.json()) as AuthSessionResponse;
};

const RegisterPage = (): JSX.Element => {
  const router = useRouter();
  const searchParams = useSearchParams();
  const [email, setEmail] = useState("");
  const [displayName, setDisplayName] = useState("");
  const [password, setPassword] = useState("");
  const [submitting, setSubmitting] = useState(false);
  const [errorMessage, setErrorMessage] = useState<string | null>(null);

  const nextPath = useMemo(() => {
    return resolvePostLoginRedirect(searchParams.get("next"));
  }, [searchParams]);

  const canSubmit = email.trim().length > 0 && password.length >= 12;

  const handleSubmit = async (event: FormEvent<HTMLFormElement>): Promise<void> => {
    event.preventDefault();
    if (!canSubmit || submitting) {
      return;
    }

    setSubmitting(true);
    setErrorMessage(null);
    try {
      const payload = await registerThroughFrontendRoute({
        email: email.trim(),
        password,
        display_name: displayName.trim() === "" ? null : displayName.trim(),
      });
      persistAuthSessionState({
        sessionToken: payload.session.session_id,
        user: payload.user,
        restoredAt: new Date().toISOString(),
      });
      router.push(nextPath);
    } catch {
      setErrorMessage("Registration failed. Try a different email or check your input.");
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <main
      className="mx-auto grid min-h-[65vh] w-full max-w-md items-center px-4"
      data-testid="register-page"
    >
      <Card className="grid gap-5 p-6" data-testid="register-card">
        <div className="grid gap-1">
          <h1 className="font-semibold text-2xl">Create account</h1>
          <p className="text-default-600 text-sm">Set up your Longtail account to continue.</p>
        </div>

        <form className="grid gap-4" data-testid="register-form" onSubmit={handleSubmit}>
          <label className="grid gap-1 text-sm" htmlFor="register-email-input">
            <span>Email</span>
            <Input
              autoComplete="email"
              className="w-full"
              data-testid="register-email"
              id="register-email-input"
              type="email"
              value={email}
              onChange={(event) => {
                setEmail(event.target.value);
              }}
            />
          </label>

          <label className="grid gap-1 text-sm" htmlFor="register-display-name-input">
            <span>Display name (optional)</span>
            <Input
              autoComplete="name"
              className="w-full"
              data-testid="register-display-name"
              id="register-display-name-input"
              type="text"
              value={displayName}
              onChange={(event) => {
                setDisplayName(event.target.value);
              }}
            />
          </label>

          <label className="grid gap-1 text-sm" htmlFor="register-password-input">
            <span>Password (12+ characters)</span>
            <Input
              autoComplete="new-password"
              className="w-full"
              data-testid="register-password"
              id="register-password-input"
              type="password"
              value={password}
              onChange={(event) => {
                setPassword(event.target.value);
              }}
            />
          </label>

          {errorMessage ? (
            <p className="text-danger text-sm" data-testid="register-error-message">
              {errorMessage}
            </p>
          ) : null}

          <Button
            data-testid="register-submit"
            isDisabled={!canSubmit || submitting}
            type="submit"
            variant="primary"
          >
            {submitting ? "Creating account..." : "Create account"}
          </Button>
        </form>

        <p className="text-default-600 text-sm">
          Already registered?{" "}
          <Link className="font-medium text-primary" href="/login">
            Sign in
          </Link>
          .
        </p>
      </Card>
    </main>
  );
};

export default RegisterPage;
