import React from "react";
import type { JSX } from "react";

interface ErrorStateProps {
  message?: string;
}

export const ErrorState = ({
  message = "Unable to load data. Please try again.",
}: ErrorStateProps): JSX.Element => {
  return (
    <div className="discovery-error-state" data-testid="discovery-error-state" role="alert">
      {message}
    </div>
  );
};
