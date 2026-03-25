import React from "react";
import type { JSX } from "react";
import { DatasetCatalogList } from "../../components/discovery/DatasetCatalogList";
import {
  DatasetListControls,
  type DatasetSortMode,
} from "../../components/discovery/DatasetListControls";
import { ErrorState } from "../../components/discovery/ErrorState";
import { fetchDatasetCatalog } from "../../lib/api/discovery-client";
import type { DatasetSummary } from "../../lib/api/discovery-types";
import { SiteHeader } from "../../shell/site-header";
import { SHELL_LAYOUT_CLASS_NAMES } from "../../theme/monochrome-theme";

interface CatalogPageProps {
  searchParams?: Promise<Record<string, string | string[] | undefined>>;
}

const formatSeriesCount = (value: number): string => {
  return Intl.NumberFormat("en-US").format(value);
};

const normalizeParam = (value: string | string[] | undefined, fallback: string): string => {
  if (typeof value !== "string") {
    return fallback;
  }

  const normalized = value.trim();
  return normalized.length > 0 ? normalized : fallback;
};

const toCategoryValues = (items: DatasetSummary[]): string[] => {
  const values = new Set<string>();

  for (const item of items) {
    for (const tag of item.topic_tags ?? []) {
      const value = tag.trim();
      if (value.length > 0) {
        values.add(value);
      }
    }
  }

  return [...values].sort((left, right) => left.localeCompare(right));
};

const applyFiltersAndSort = (
  items: DatasetSummary[],
  sourceFilter: string,
  categoryFilter: string,
  sortMode: DatasetSortMode,
): DatasetSummary[] => {
  const bySource =
    sourceFilter === "all"
      ? items
      : items.filter((item) => item.source.id.toLowerCase() === sourceFilter.toLowerCase());

  const byCategory =
    categoryFilter === "all"
      ? bySource
      : bySource.filter((item) =>
          (item.topic_tags ?? []).some((tag) => tag.toLowerCase() === categoryFilter.toLowerCase()),
        );

  const deduped = [...new Map(byCategory.map((item) => [item.dataset_id, item])).values()];

  return deduped.sort((left, right) => {
    if (sortMode === "title_asc") {
      return left.title.localeCompare(right.title);
    }

    if (sortMode === "title_desc") {
      return right.title.localeCompare(left.title);
    }

    const leftTime = Date.parse(left.latest_update_at);
    const rightTime = Date.parse(right.latest_update_at);

    if (Number.isNaN(leftTime) && Number.isNaN(rightTime)) {
      return left.title.localeCompare(right.title);
    }

    if (Number.isNaN(leftTime)) {
      return 1;
    }

    if (Number.isNaN(rightTime)) {
      return -1;
    }

    if (leftTime === rightTime) {
      return left.title.localeCompare(right.title);
    }

    return rightTime - leftTime;
  });
};

const CatalogPage = async ({ searchParams }: CatalogPageProps): Promise<JSX.Element> => {
  const params = searchParams ? await searchParams : undefined;
  const sourceFilter = normalizeParam(params?.source, "all");
  const categoryFilter = normalizeParam(params?.category, "all");
  const sortParam = normalizeParam(params?.sort, "recency") as DatasetSortMode;
  const sortMode: DatasetSortMode =
    sortParam === "title_asc" || sortParam === "title_desc" ? sortParam : "recency";

  try {
    const result = await fetchDatasetCatalog({ pageSize: 100 });
    const sourceOptions = [
      { label: "All Sources", value: "all" },
      ...[...new Map(result.items.map((item) => [item.source.id, item.source])).values()]
        .sort((left, right) => left.name.localeCompare(right.name))
        .map((source) => ({
          label: source.name,
          value: source.id,
        })),
    ];
    const categoryOptions = [
      { label: "All Categories", value: "all" },
      ...toCategoryValues(result.items).map((value) => ({
        label: value,
        value,
      })),
    ];
    const visibleItems = applyFiltersAndSort(result.items, sourceFilter, categoryFilter, sortMode);

    return (
      <div className="shell-page shell-scroll-anchor" data-testid="site-shell">
        <SiteHeader activeTab="datasets" />
        <main className={SHELL_LAYOUT_CLASS_NAMES.constrainedContent} data-testid="catalog-page">
          <header className="dataset-list-page-header" data-testid="dataset-list-page-header">
            <div>
              <h1 className="dataset-list-title">Datasets</h1>
              <p className="dataset-list-total-series" data-testid="dataset-list-total-series">
                TOTAL SERIES: {formatSeriesCount(result.total_items)}
              </p>
            </div>
          </header>

          <DatasetListControls
            categoryOptions={categoryOptions}
            selectedCategory={categoryFilter}
            selectedSort={sortMode}
            selectedSource={sourceFilter}
            sourceOptions={sourceOptions}
          />

          <DatasetCatalogList items={visibleItems} />
        </main>
      </div>
    );
  } catch {
    return (
      <div className="shell-page shell-scroll-anchor" data-testid="site-shell">
        <SiteHeader activeTab="datasets" />
        <main className={SHELL_LAYOUT_CLASS_NAMES.constrainedContent} data-testid="catalog-page">
          <header className="dataset-list-page-header" data-testid="dataset-list-page-header">
            <div>
              <h1 className="dataset-list-title">Datasets</h1>
              <p className="dataset-list-total-series" data-testid="dataset-list-total-series">
                TOTAL SERIES: --
              </p>
            </div>
          </header>
          <ErrorState />
        </main>
      </div>
    );
  }
};

export default CatalogPage;
