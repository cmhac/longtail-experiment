import React from "react";
import type { JSX } from "react";

interface EmptyStateProps {
  message?: string;
}

export const EmptyState = ({ message = "No results found." }: EmptyStateProps): JSX.Element => {
  return (
    <output className="discovery-empty-state" data-testid="discovery-empty-state">
      {message}
    </output>
  );
};
