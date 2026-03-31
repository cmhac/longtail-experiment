import { Input } from "@heroui/react";
import React from "react";
import type { JSX } from "react";
import { ChartControlField } from "./ChartControlField";

interface ChartNumberInputControlProps {
  className?: string;
  disabled?: boolean;
  id: string;
  label: string;
  max?: number;
  min?: number;
  onChange: (value: string) => void;
  value: string;
}

export const ChartNumberInputControl = ({
  className,
  disabled,
  id,
  label,
  max,
  min,
  onChange,
  value,
}: ChartNumberInputControlProps): JSX.Element => {
  return (
    <ChartControlField htmlFor={id} label={label}>
      <Input
        {...(className ? { className } : {})}
        disabled={disabled}
        id={id}
        max={max}
        min={min}
        type="number"
        value={value}
        variant="secondary"
        onChange={(event) => {
          onChange(event.target.value);
        }}
      />
    </ChartControlField>
  );
};
