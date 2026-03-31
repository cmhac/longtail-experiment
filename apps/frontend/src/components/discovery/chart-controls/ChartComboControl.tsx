import { ComboBox, Input, ListBox, ListBoxItem, Spinner } from "@heroui/react";
import React from "react";
import type { JSX, RefObject } from "react";

export interface ChartComboOption {
  label: string;
  value: string;
}

interface ChartComboControlProps {
  className?: string;
  emptyLabel?: string;
  infiniteScrollRef?: RefObject<HTMLDivElement | null>;
  inputValue: string;
  isInfiniteLoading?: boolean;
  label: string;
  listContainerRef?: RefObject<HTMLDivElement | null>;
  onInputChange?: (value: string) => void;
  onSelect: (value: string) => void;
  options: ChartComboOption[];
  paginated?: boolean;
  selectedValue: string;
  testId: string;
  visibleCount?: number;
}

const NO_MATCH_VALUE = "__no_match__";

export const ChartComboControl = ({
  className,
  emptyLabel,
  infiniteScrollRef,
  inputValue,
  isInfiniteLoading,
  label,
  listContainerRef,
  onInputChange,
  onSelect,
  options,
  paginated,
  selectedValue,
  testId,
  visibleCount,
}: ChartComboControlProps): JSX.Element => {
  const normalizedInput = inputValue.trim().toLowerCase();
  const selectedOption = options.find((option) => option.value === selectedValue);
  const normalizedSelectedLabel = selectedOption?.label.trim().toLowerCase() ?? "";
  const shouldFilter = normalizedInput.length > 0 && normalizedInput !== normalizedSelectedLabel;
  const filteredOptions = !shouldFilter
    ? options
    : options.filter((option) => option.label.toLowerCase().includes(normalizedInput));
  const visibleOptions =
    paginated && !shouldFilter && typeof visibleCount === "number"
      ? (() => {
          const pagedOptions = filteredOptions.slice(0, visibleCount);
          if (
            !selectedOption ||
            pagedOptions.some((option) => option.value === selectedOption.value)
          ) {
            return pagedOptions;
          }

          return [selectedOption, ...pagedOptions];
        })()
      : filteredOptions;
  const hasMore =
    Boolean(paginated) &&
    !shouldFilter &&
    typeof visibleCount === "number" &&
    filteredOptions.length > visibleOptions.length;
  const renderedOptions =
    visibleOptions.length > 0
      ? visibleOptions
      : [{ label: emptyLabel ?? "No matching options", value: NO_MATCH_VALUE }];

  return (
    <ComboBox
      aria-label={label}
      className={className ?? "w-37 min-w-32"}
      data-testid={testId}
      inputValue={inputValue}
      items={renderedOptions}
      onInputChange={onInputChange ?? (() => {})}
      onSelectionChange={(key) => {
        if (typeof key === "string") {
          if (key === NO_MATCH_VALUE) {
            return;
          }
          onSelect(key);
        }
      }}
      selectedKey={selectedValue}
    >
      <ComboBox.InputGroup className="box-border overflow-hidden rounded-[0.8rem] border border-(--shell-border) bg-(--shell-surface) transition-[border-width,border-color] duration-150 focus-within:border-(--shell-foreground) focus-within:border-2 focus-within:ring-0">
        <Input className="min-h-8 truncate border-0 bg-transparent py-[0.28rem] pr-[2.15rem] pl-[0.45rem] text-(--shell-foreground) outline-none focus:outline-none focus:ring-0 focus-visible:outline-none focus-visible:ring-0" />
        <ComboBox.Trigger
          aria-label={`Open ${label} options`}
          className="min-w-[2.15rem] px-[0.45rem] text-(--shell-muted)"
        />
      </ComboBox.InputGroup>
      <ComboBox.Popover className="rounded-[0.8rem] border border-(--shell-border) bg-(--shell-surface)">
        <div className="max-h-56 overflow-y-auto" ref={listContainerRef}>
          <ListBox>
            {renderedOptions.map((option) => (
              <ListBoxItem
                className="text-(--shell-foreground) data-[focused=true]:bg-(--shell-background) data-[hovered=true]:bg-(--shell-background) data-[selected=true]:bg-(--shell-background) data-[focused=true]:text-(--shell-foreground) data-[hovered=true]:text-(--shell-foreground) data-[selected=true]:text-(--shell-foreground)"
                id={option.value}
                key={option.value}
                textValue={option.label}
              >
                {option.label}
              </ListBoxItem>
            ))}
          </ListBox>
          {hasMore ? (
            <div
              className="h-2 w-full"
              data-testid={`${testId}-infinite-sentinel`}
              ref={infiniteScrollRef}
            />
          ) : null}
          {isInfiniteLoading ? (
            <div className="flex justify-center py-2" data-testid={`${testId}-infinite-loading`}>
              <Spinner color="current" size="sm" style={{ color: "var(--foreground)" }} />
            </div>
          ) : null}
        </div>
      </ComboBox.Popover>
    </ComboBox>
  );
};
