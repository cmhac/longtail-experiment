import { Button, ButtonGroup } from "@heroui/react";
import React from "react";
import type { JSX } from "react";

export interface ChartToggleOption<TValue extends string> {
  disabled?: boolean;
  label: string;
  value: TValue;
}

interface ChartToggleGroupProps<TValue extends string> {
  activeValue: TValue;
  className?: string;
  disabled?: boolean;
  onChange: (value: TValue) => void;
  options: readonly ChartToggleOption<TValue>[];
  testId?: string;
}

const BASE_BUTTON_CLASS_NAME =
  "cursor-pointer px-[0.52rem] py-[0.2rem] text-[0.68rem] tracking-[0.06em] data-[pressed=true]:scale-100 disabled:cursor-not-allowed disabled:opacity-45";

const ACTIVE_BUTTON_CLASS_NAME =
  "border-(--shell-foreground) bg-(--shell-foreground) text-(--shell-surface)";

const INACTIVE_BUTTON_CLASS_NAME = "border-(--shell-border) bg-(--shell-surface) text-inherit";

export const ChartToggleGroup = <TValue extends string>({
  activeValue,
  className,
  disabled = false,
  onChange,
  options,
  testId,
}: ChartToggleGroupProps<TValue>): JSX.Element => {
  return (
    <ButtonGroup
      className={className ?? "flex flex-wrap gap-[0.35rem]"}
      data-testid={testId}
      isDisabled={disabled}
      size="sm"
      variant="outline"
    >
      {options.map((option) => {
        const isDisabled = disabled || Boolean(option.disabled);
        const isActive = activeValue === option.value;

        return (
          <Button
            aria-pressed={isActive}
            className={`${BASE_BUTTON_CLASS_NAME} ${isActive ? ACTIVE_BUTTON_CLASS_NAME : INACTIVE_BUTTON_CLASS_NAME}`}
            isDisabled={isDisabled}
            key={option.value}
            onPress={() => {
              if (!isDisabled) {
                onChange(option.value);
              }
            }}
            type="button"
          >
            {option.label}
          </Button>
        );
      })}
    </ButtonGroup>
  );
};
