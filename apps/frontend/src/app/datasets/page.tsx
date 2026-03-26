import React from "react";
import type { JSX } from "react";
import { DatasetCatalogList } from "../../components/discovery/DatasetCatalogList";
import {
  DatasetListControls,
  type DatasetSortMode,
} from "../../components/discovery/DatasetListControls";
import { DiscoveryListPageHeader } from "../../components/discovery/DiscoveryListPageHeader";
import { ErrorState } from "../../components/discovery/ErrorState";
import { fetchDatasetCatalog } from "../../lib/api/discovery-client";
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

const CatalogPage = async ({ searchParams }: CatalogPageProps): Promise<JSX.Element> => {
  const params = searchParams ? await searchParams : undefined;
  const sourceFilter = normalizeParam(params?.source, "all");
  const categoryFilter = normalizeParam(params?.category, "all");
  const sortParam = normalizeParam(params?.sort, "recency") as DatasetSortMode;
  const sortMode: DatasetSortMode =
    sortParam === "title_asc" || sortParam === "title_desc" ? sortParam : "recency";

  try {
    const result = await fetchDatasetCatalog({
      pageSize: 100,
      sort: sortMode,
      ...(sourceFilter === "all" ? {} : { source: sourceFilter }),
      ...(categoryFilter === "all" ? {} : { category: categoryFilter }),
    });
    const sourceOptions = [
      { label: "All Sources", value: "all" },
      ...result.aggregations.sources.map((item) => ({
        label: item.source.name,
        value: item.source.id,
      })),
    ];
    const categoryOptions = [
      { label: "All Categories", value: "all" },
      ...result.aggregations.categories.map((item) => ({
        label: item.value,
        value: item.value,
      })),
    ];

    return (
      <div className="shell-page shell-scroll-anchor" data-testid="site-shell">
        <SiteHeader activeTab="datasets" />
        <main className={SHELL_LAYOUT_CLASS_NAMES.constrainedContent} data-testid="catalog-page">
          <DiscoveryListPageHeader
            headerTestId="dataset-list-page-header"
            title="Datasets"
            totalNoun="series"
            totalTestId="dataset-list-total-series"
            totalValue={formatSeriesCount(result.aggregations.total_dataset_count)}
          />

          <DatasetListControls
            categoryOptions={categoryOptions}
            selectedCategory={categoryFilter}
            selectedSort={sortMode}
            selectedSource={sourceFilter}
            sourceOptions={sourceOptions}
          />

          <DatasetCatalogList items={result.items} />
        </main>
      </div>
    );
  } catch {
    return (
      <div className="shell-page shell-scroll-anchor" data-testid="site-shell">
        <SiteHeader activeTab="datasets" />
        <main className={SHELL_LAYOUT_CLASS_NAMES.constrainedContent} data-testid="catalog-page">
          <DiscoveryListPageHeader
            headerTestId="dataset-list-page-header"
            title="Datasets"
            totalNoun="series"
            totalTestId="dataset-list-total-series"
            totalValue="--"
          />
          <ErrorState />
        </main>
      </div>
    );
  }
};

export default CatalogPage;
