import React from "react";
import type { ReactElement } from "react";
import type { FurnitureAdapterProps } from "../contracts";

export const AdsSubscriptionPlaceholder = ({ slot }: FurnitureAdapterProps): ReactElement => {
  return <div data-testid={slot.testId}>{slot.label}</div>;
};
