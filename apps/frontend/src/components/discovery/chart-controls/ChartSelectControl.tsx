import { ListBox, Select } from "@heroui/react";
import React from "react";
import type { JSX } from "react";
import { ChartControlField } from "./ChartControlField";

export interface ChartSelectOption {
  label: string;
  value: string;
}

interface ChartSelectControlProps {
  className?: string;
  isDisabled?: boolean;
  label: string;
  onChange: (value: string) => void;
  optionClassName?: string;
  options: ChartSelectOption[];
  placeholder: string;
  popoverClassName?: string;
  testId?: string;
  value: string | null;
}

export const ChartSelectControl = ({
  className,
  isDisabled,
  label,
  onChange,
  optionClassName,
  options,
  placeholder,
  popoverClassName,
  testId,
  value,
}: ChartSelectControlProps): JSX.Element => {
  return (
    <ChartControlField label={label}>
      <Select
        aria-label={label}
        {...(className ? { className } : {})}
        {...(testId ? { "data-testid": testId } : {})}
        {...(typeof isDisabled === "boolean" ? { isDisabled } : {})}
        placeholder={placeholder}
        value={value}
        variant="secondary"
        onChange={(nextValue) => {
          onChange(nextValue === null ? "" : String(nextValue));
        }}
      >
        <Select.Trigger>
          <Select.Value />
          <Select.Indicator />
        </Select.Trigger>
        <Select.Popover {...(popoverClassName ? { className: popoverClassName } : {})}>
          <ListBox>
            {options.map((option) => (
              <ListBox.Item
                {...(optionClassName ? { className: optionClassName } : {})}
                id={option.value}
                key={option.value}
                textValue={option.label}
              >
                {option.label}
              </ListBox.Item>
            ))}
          </ListBox>
        </Select.Popover>
      </Select>
    </ChartControlField>
  );
};
