"use client";

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

  return (
    <section className="dataset-list-controls" data-testid="dataset-list-controls">
      <label className="dataset-list-control-group" htmlFor="dataset-source-filter">
        <span className="dataset-list-control-label">Source</span>
        <select
          data-testid="dataset-source-filter"
          id="dataset-source-filter"
          onChange={(event) => applyParam("source", event.target.value, DEFAULT_SOURCE)}
          value={selectedSource}
        >
          {sourceOptions.map((option) => (
            <option key={option.value} value={option.value}>
              {option.label}
            </option>
          ))}
        </select>
      </label>

      <label className="dataset-list-control-group" htmlFor="dataset-category-filter">
        <span className="dataset-list-control-label">Category</span>
        <select
          data-testid="dataset-category-filter"
          id="dataset-category-filter"
          onChange={(event) => applyParam("category", event.target.value, DEFAULT_CATEGORY)}
          value={selectedCategory}
        >
          {categoryOptions.map((option) => (
            <option key={option.value} value={option.value}>
              {option.label}
            </option>
          ))}
        </select>
      </label>

      <label className="dataset-list-control-group" htmlFor="dataset-sort-control">
        <span className="dataset-list-control-label">Sort By</span>
        <select
          data-testid="dataset-sort-control"
          id="dataset-sort-control"
          onChange={(event) => applyParam("sort", event.target.value, DEFAULT_SORT)}
          value={selectedSort}
        >
          <option value="recency">Recency</option>
          <option value="title_asc">Title (A-Z)</option>
          <option value="title_desc">Title (Z-A)</option>
        </select>
      </label>
    </section>
  );
};
