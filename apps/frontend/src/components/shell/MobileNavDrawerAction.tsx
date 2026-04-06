"use client";

import { Button } from "@heroui/react";
import React from "react";
import type { JSX } from "react";
import { SHELL_NAVBAR_CLASS_NAMES } from "../../theme/monochrome-theme";

type MobileNavDrawerActionTone = "default" | "danger";

interface MobileNavDrawerActionProps {
  label: string;
  testId: string;
  tone?: MobileNavDrawerActionTone;
  countValue?: string;
  onPress: () => void;
  isDisabled?: boolean;
}

export const MobileNavDrawerAction = ({
  label,
  testId,
  tone = "default",
  countValue,
  onPress,
  isDisabled = false,
}: MobileNavDrawerActionProps): JSX.Element => {
  return (
    <Button
      className={`${SHELL_NAVBAR_CLASS_NAMES.mobileDrawerActionRow} ${
        tone === "danger" ? " is-danger" : ""
      }`}
      data-testid={testId}
      fullWidth
      isDisabled={isDisabled}
      size="lg"
      variant="ghost"
      onPress={onPress}
    >
      <span className={SHELL_NAVBAR_CLASS_NAMES.mobileDrawerActionLabel}>{label}</span>
      {countValue ? (
        <span
          className={SHELL_NAVBAR_CLASS_NAMES.mobileDrawerActionCount}
          data-testid={`${testId}-count`}
        >
          {countValue}
        </span>
      ) : null}
    </Button>
  );
};
