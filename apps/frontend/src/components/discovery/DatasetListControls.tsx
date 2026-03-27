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
  selectedValue: string;
  testId: string;
  onSelect: (value: string) => void;
}

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
  const router = useRouter();
  const pathname = usePathname();
  const searchParams = useSearchParams();

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
    selectedValue,
    testId,
    onSelect,
  }: ComboBoxControlProps): JSX.Element => {
    return (
      <label className="dataset-list-control-group" htmlFor={id}>
        <span className="dataset-list-control-label">{label}</span>
        <ComboBox
          aria-label={label}
          className="dataset-list-control-combobox"
          data-testid={testId}
          id={id}
          items={options}
          onSelectionChange={(key) => {
            if (typeof key === "string") {
              onSelect(key);
            }
          }}
          selectedKey={selectedValue}
        >
          <ComboBox.InputGroup>
            <Input data-testid={testId} />
            <ComboBox.Trigger aria-label={`Open ${label} options`} />
          </ComboBox.InputGroup>
          <ComboBox.Popover>
            <ListBox>
              {(option: FilterOption) => (
                <ListBoxItem id={option.value} key={option.value} textValue={option.label}>
                  {option.label}
                </ListBoxItem>
              )}
            </ListBox>
          </ComboBox.Popover>
        </ComboBox>
      </label>
    );
  };

  return (
    <section
      className="dataset-list-controls dataset-list-controls-surface"
      data-testid="dataset-list-controls"
    >
      <div className="dataset-list-controls-left-group" data-testid="dataset-filter-left-group">
        {renderComboBox({
          id: "dataset-source-filter",
          label: "Source",
          options: sourceOptions,
          selectedValue: selectedSource,
          testId: "dataset-source-filter",
          onSelect: (value) => applyParam("source", value, DEFAULT_SOURCE),
        })}

        {renderComboBox({
          id: "dataset-category-filter",
          label: "Category",
          options: categoryOptions,
          selectedValue: selectedCategory,
          testId: "dataset-category-filter",
          onSelect: (value) => applyParam("category", value, DEFAULT_CATEGORY),
        })}
      </div>

      <div className="dataset-list-controls-right-group" data-testid="dataset-sort-right-group">
        {renderComboBox({
          id: "dataset-sort-control",
          label: "Sort By",
          options: [
            { value: "recency", label: "Recency" },
            { value: "title_asc", label: "Title (A-Z)" },
            { value: "title_desc", label: "Title (Z-A)" },
          ],
          selectedValue: selectedSort,
          testId: "dataset-sort-control",
          onSelect: (value) => applyParam("sort", value, DEFAULT_SORT),
        })}
      </div>
    </section>
  );
};
