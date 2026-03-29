import { Card } from "@heroui/react/card";
import React from "react";
import type { JSX } from "react";

interface EmptyStateProps {
  message?: string;
}

export const EmptyState = ({ message = "No results found." }: EmptyStateProps): JSX.Element => {
  return (
    <Card
      className="rounded-lg border border-(--shell-border) border-border/70 bg-(--shell-surface) bg-surface/95 p-6 text-center shadow-sm"
      data-testid="discovery-empty-state"
      variant="default"
    >
      <output>{message}</output>
    </Card>
  );
};
