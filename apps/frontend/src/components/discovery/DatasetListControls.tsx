"use client";

import { ComboBox, Input, ListBox, ListBoxItem } from "@heroui/react";
import { usePathname, useRouter, useSearchParams } from "next/navigation";
import React from "react";
import type { JSX } from "react";

export type DatasetSortMode = "recency" | "title_asc" | "title_desc";

interface FilterOption {
  value: string;
  label: string;
}

interface DatasetListControlsProps {
  sourceOptions: FilterOption[];
  categoryOptions: FilterOption[];
  selectedSource: string;
  selectedCategory: string;
  selectedSort: DatasetSortMode;
}

const DEFAULT_SOURCE = "all";
const DEFAULT_CATEGORY = "all";
const DEFAULT_SORT: DatasetSortMode = "recency";

interface ComboBoxControlProps {
  id: string;
  label: string;
  options: FilterOption[];
  inputValue: string;
  selectedValue: string;
  testId: string;
  noMatchLabel: string;
  onInputChange: (value: string) => void;
  onSelect: (value: string) => void;
}

const resolveSelectedLabel = (options: FilterOption[], selectedValue: string): string => {
  const selectedOption = options.find((option) => option.value === selectedValue);
  return selectedOption?.label ?? "";
};

const createNextUrl = (pathname: string, params: URLSearchParams): string => {
  const query = params.toString();
  return query.length > 0 ? `${pathname}?${query}` : pathname;
};

export const DatasetListControls = ({
  sourceOptions,
  categoryOptions,
  selectedSource,
  selectedCategory,
  selectedSort,
}: DatasetListControlsProps): JSX.Element => {
  const sortOptions: FilterOption[] = [
    { value: "recency", label: "Recency" },
    { value: "title_asc", label: "Title (A-Z)" },
    { value: "title_desc", label: "Title (Z-A)" },
  ];
  const router = useRouter();
  const pathname = usePathname();
  const searchParams = useSearchParams();
  const [sourceInputValue, setSourceInputValue] = React.useState(() =>
    resolveSelectedLabel(sourceOptions, selectedSource),
  );
  const [categoryInputValue, setCategoryInputValue] = React.useState(() =>
    resolveSelectedLabel(categoryOptions, selectedCategory),
  );
  const [sortInputValue, setSortInputValue] = React.useState(() =>
    resolveSelectedLabel(sortOptions, selectedSort),
  );

  React.useEffect(() => {
    setSourceInputValue(resolveSelectedLabel(sourceOptions, selectedSource));
  }, [sourceOptions, selectedSource]);

  React.useEffect(() => {
    setCategoryInputValue(resolveSelectedLabel(categoryOptions, selectedCategory));
  }, [categoryOptions, selectedCategory]);

  React.useEffect(() => {
    setSortInputValue(resolveSelectedLabel(sortOptions, selectedSort));
  }, [selectedSort]);

  const applyParam = (key: string, value: string, defaultValue: string): void => {
    const nextParams = new URLSearchParams(searchParams.toString());

    if (value === defaultValue) {
      nextParams.delete(key);
    } else {
      nextParams.set(key, value);
    }

    // Filter and sort updates should always reconcile to page one.
    nextParams.delete("page");

    router.replace(createNextUrl(pathname, nextParams));
  };

  const renderComboBox = ({
    id,
    label,
    options,
    inputValue,
    selectedValue,
    testId,
    noMatchLabel,
    onInputChange,
    onSelect,
  }: ComboBoxControlProps): JSX.Element => {
    const selectedLabel = resolveSelectedLabel(options, selectedValue);
    const normalizedInput = inputValue.trim().toLowerCase();
    const normalizedSelectedLabel = selectedLabel.trim().toLowerCase();
    const shouldFilter = normalizedInput.length > 0 && normalizedInput !== normalizedSelectedLabel;
    const filteredOptions = shouldFilter
      ? options.filter((option) => option.label.toLowerCase().includes(normalizedInput))
      : options;
    const noMatchValue = `${id}-no-match`;
    const renderedOptions =
      filteredOptions.length > 0
        ? filteredOptions
        : [{ value: noMatchValue, label: noMatchLabel } satisfies FilterOption];

    return (
      <label
        className="dataset-list-control-group grid w-full min-w-0 gap-[0.3rem] md:w-[min(100%,12.5rem)]"
        htmlFor={id}
      >
        <span className="dataset-list-control-label text-(--shell-muted) text-[0.68rem] uppercase tracking-[0.11em]">
          {label}
        </span>
        <ComboBox
          aria-label={label}
          className="w-full"
          data-testid={testId}
          id={id}
          inputValue={inputValue}
          items={renderedOptions}
          onInputChange={onInputChange}
          onSelectionChange={(key) => {
            if (typeof key === "string" && key !== noMatchValue) {
              onInputChange(resolveSelectedLabel(options, key));
              onSelect(key);
            }
          }}
          selectedKey={selectedValue}
        >
          <ComboBox.InputGroup
            className="box-border overflow-hidden rounded-[0.8rem] border border-(--shell-border) bg-(--shell-surface) transition-[border-width,border-color] duration-150 focus-within:border-(--shell-foreground) focus-within:border-2 focus-within:ring-0"
            data-testid={`${testId}-input-group`}
          >
            <Input className="min-h-8 truncate border-0 bg-transparent py-[0.28rem] pr-[2.15rem] pl-[0.45rem] text-(--shell-foreground) outline-none focus:outline-none focus:ring-0 focus-visible:outline-none focus-visible:ring-0" />
            <ComboBox.Trigger
              aria-label={`Open ${label} options`}
              className="min-w-[2.15rem] px-[0.45rem] text-(--shell-muted)"
            />
          </ComboBox.InputGroup>
          <ComboBox.Popover className="rounded-[0.8rem] border border-(--shell-border) bg-(--shell-surface)">
            <ListBox>
              {(option: FilterOption) =>
                option.value === noMatchValue ? (
                  <ListBoxItem
                    className="pointer-events-none cursor-default text-(--shell-muted)"
                    id={option.value}
                    key={option.value}
                    textValue={noMatchLabel}
                  >
                    {noMatchLabel}
                  </ListBoxItem>
                ) : (
                  <ListBoxItem
                    className="text-(--shell-foreground) data-[focused=true]:bg-(--shell-background) data-[hovered=true]:bg-(--shell-background) data-[selected=true]:bg-(--shell-background) data-[focused=true]:text-(--shell-foreground) data-[hovered=true]:text-(--shell-foreground) data-[selected=true]:text-(--shell-foreground)"
                    id={option.value}
                    key={option.value}
                    textValue={option.label}
                  >
                    {option.label}
                  </ListBoxItem>
                )
              }
            </ListBox>
          </ComboBox.Popover>
        </ComboBox>
      </label>
    );
  };

  return (
    <section
      className="dataset-list-controls dataset-list-controls-surface flex items-end justify-between gap-[1.6rem] bg-transparent p-[0.9rem] max-[720px]:flex-col max-[720px]:items-stretch max-[720px]:gap-[0.9rem]"
      data-testid="dataset-list-controls"
    >
      <div
        className="dataset-list-controls-left-group flex flex-1 items-end gap-[0.8rem] max-[720px]:w-full max-[720px]:flex-wrap max-[720px]:justify-start"
        data-testid="dataset-filter-left-group"
      >
        {renderComboBox({
          id: "dataset-source-filter",
          label: "Source",
          options: sourceOptions,
          inputValue: sourceInputValue,
          selectedValue: selectedSource,
          testId: "dataset-source-filter",
          noMatchLabel: "No matching sources",
          onInputChange: setSourceInputValue,
          onSelect: (value) => applyParam("source", value, DEFAULT_SOURCE),
        })}

        {renderComboBox({
          id: "dataset-category-filter",
          label: "Category",
          options: categoryOptions,
          inputValue: categoryInputValue,
          selectedValue: selectedCategory,
          testId: "dataset-category-filter",
          noMatchLabel: "No matching categories",
          onInputChange: setCategoryInputValue,
          onSelect: (value) => applyParam("category", value, DEFAULT_CATEGORY),
        })}
      </div>

      <div
        className="dataset-list-controls-right-group ml-auto flex flex-none items-end gap-[0.8rem] max-[720px]:ml-0 max-[720px]:w-full max-[720px]:flex-wrap max-[720px]:justify-start"
        data-testid="dataset-sort-right-group"
      >
        {renderComboBox({
          id: "dataset-sort-control",
          label: "Sort By",
          options: sortOptions,
          inputValue: sortInputValue,
          selectedValue: selectedSort,
          testId: "dataset-sort-control",
          noMatchLabel: "No matching sort modes",
          onInputChange: setSortInputValue,
          onSelect: (value) => applyParam("sort", value, DEFAULT_SORT),
        })}
      </div>
    </section>
  );
};
