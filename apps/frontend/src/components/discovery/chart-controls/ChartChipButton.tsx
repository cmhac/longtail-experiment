import { Button } from "@heroui/react";
import React from "react";
import type { JSX } from "react";

interface ChartChipButtonProps {
  accentColor?: string;
  className?: string;
  label: string;
  onPress: () => void;
}

export const ChartChipButton = ({
  accentColor,
  className,
  label,
  onPress,
}: ChartChipButtonProps): JSX.Element => {
  return (
    <Button {...(className ? { className } : {})} size="sm" variant="secondary" onPress={onPress}>
      <span
        className="inline-block h-2 w-2 rounded-full"
        style={{ backgroundColor: accentColor ?? "var(--shell-foreground)" }}
      />
      {label}
      <span aria-hidden="true">×</span>
    </Button>
  );
};
