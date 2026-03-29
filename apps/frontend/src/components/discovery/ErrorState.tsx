import { Card } from "@heroui/react/card";
import React from "react";
import type { JSX } from "react";

interface ErrorStateProps {
  message?: string;
}

export const ErrorState = ({
  message = "Unable to load data. Please try again.",
}: ErrorStateProps): JSX.Element => {
  return (
    <Card
      className="rounded-lg border border-(--shell-border) bg-surface/95 p-6 text-center shadow-sm"
      data-testid="discovery-error-state"
      role="alert"
      variant="default"
    >
      {message}
    </Card>
  );
};
