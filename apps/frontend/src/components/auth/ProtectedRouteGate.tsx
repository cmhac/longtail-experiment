"use client";

import { Card } from "@heroui/react";
import { useRouter } from "next/navigation";
import React from "react";
import { type ReactNode, useEffect, useState } from "react";
import type { JSX } from "react";
import { evaluateProtectedRoute } from "../../lib/auth/route-guard";

interface ProtectedRouteGateProps {
  pathname: string;
  children: ReactNode;
  fallbackMessage?: string;
  fallbackTestId?: string;
}

export const ProtectedRouteGate = ({
  pathname,
  children,
  fallbackMessage = "Redirecting to sign in...",
  fallbackTestId = "protected-route-redirecting",
}: ProtectedRouteGateProps): JSX.Element => {
  const router = useRouter();
  const [allowAccess, setAllowAccess] = useState(false);

  useEffect(() => {
    const decision = evaluateProtectedRoute(pathname);
    if (!decision.allow) {
      if (decision.redirectTo) {
        router.push(decision.redirectTo);
      }
      setAllowAccess(false);
      return;
    }
    setAllowAccess(true);
  }, [pathname, router]);

  if (!allowAccess) {
    return (
      <Card className="p-5" data-testid={fallbackTestId}>
        {fallbackMessage}
      </Card>
    );
  }

  return <>{children}</>;
};
