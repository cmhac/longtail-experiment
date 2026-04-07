import React from "react";
import type { JSX } from "react";
import { ClientScopedCatalogList } from "../../components/discovery/ClientScopedCatalogList";
import {
  DatasetListControls,
  type DatasetScopeMode,
  type DatasetSortMode,
} from "../../components/discovery/DatasetListControls";
import { DiscoveryListPageHeader } from "../../components/discovery/DiscoveryListPageHeader";
import { ErrorState } from "../../components/discovery/ErrorState";
import { InfiniteCatalogList } from "../../components/discovery/InfiniteCatalogList";
import { fetchDatasetCatalog } from "../../lib/api/discovery-client";
import { SitePageFrame } from "../../shell/site-page-frame";

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
  const scopeParam = normalizeParam(params?.scope, "all");
  const scopeMode: DatasetScopeMode = scopeParam === "subscribed" ? "subscribed" : "all";
  const sortParam = normalizeParam(params?.sort, "recency") as DatasetSortMode;
  const sortMode: DatasetSortMode =
    sortParam === "title_asc" || sortParam === "title_desc" ? sortParam : "recency";

  try {
    const firstPage = await fetchDatasetCatalog({
      page: 1,
      sort: sortMode,
      ...(sourceFilter === "all" ? {} : { source: sourceFilter }),
      ...(categoryFilter === "all" ? {} : { category: categoryFilter }),
    });

    const sourceOptions = [
      { label: "All Sources", value: "all" },
      ...firstPage.aggregations.sources.map((item) => ({
        label: item.source.name,
        value: item.source.id,
      })),
    ];
    const categoryOptions = [
      { label: "All Categories", value: "all" },
      ...firstPage.aggregations.categories.map((item) => ({
        label: item.value,
        value: item.value,
      })),
    ];

    return (
      <SitePageFrame
        activeTab="datasets"
        mainClassName="grid content-start gap-[1.2rem]"
        mainTestId="catalog-page"
      >
        <DiscoveryListPageHeader
          headerTestId="dataset-list-page-header"
          title="Datasets"
          totalNoun="series"
          totalTestId="dataset-list-total-series"
          totalValue={formatSeriesCount(firstPage.aggregations.total_dataset_count)}
        />

        <DatasetListControls
          categoryOptions={categoryOptions}
          selectedCategory={categoryFilter}
          selectedScope={scopeMode}
          selectedSort={sortMode}
          selectedSource={sourceFilter}
          sourceOptions={sourceOptions}
        />

        {scopeMode === "subscribed" ? (
          <ClientScopedCatalogList
            emptyMessage="You are not following any datasets that match these filters yet."
            requestPath="/api/discovery/datasets"
            requestQuery={{
              ...(sortMode ? { sort: sortMode } : {}),
              ...(sourceFilter === "all" ? {} : { source: sourceFilter }),
              ...(categoryFilter === "all" ? {} : { category: categoryFilter }),
              subscribed_only: "true",
            }}
          />
        ) : (
          <InfiniteCatalogList
            emptyMessage="No datasets match the selected filters. Reset filters to see the full catalog."
            initialItems={firstPage.items}
            initialPage={firstPage.page}
            initialTotalPages={firstPage.total_pages}
            requestPath="/api/discovery/datasets"
            requestQuery={{
              ...(sortMode ? { sort: sortMode } : {}),
              ...(sourceFilter === "all" ? {} : { source: sourceFilter }),
              ...(categoryFilter === "all" ? {} : { category: categoryFilter }),
            }}
          />
        )}
      </SitePageFrame>
    );
  } catch {
    return (
      <SitePageFrame
        activeTab="datasets"
        mainClassName="grid content-start gap-[1.2rem]"
        mainTestId="catalog-page"
      >
        <DiscoveryListPageHeader
          headerTestId="dataset-list-page-header"
          title="Datasets"
          totalNoun="series"
          totalTestId="dataset-list-total-series"
          totalValue="--"
        />
        <ErrorState />
      </SitePageFrame>
    );
  }
};

export default CatalogPage;
