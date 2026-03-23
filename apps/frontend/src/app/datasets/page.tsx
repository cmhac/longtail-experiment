import React from "react";
import type { JSX } from "react";
import { DatasetCatalogList } from "../../components/discovery/DatasetCatalogList";
import { DatasetSearchBox } from "../../components/discovery/DatasetSearchBox";
import { ErrorState } from "../../components/discovery/ErrorState";
import { GroupBySourceToggle } from "../../components/discovery/GroupBySourceToggle";
import { fetchDatasetCatalog } from "../../lib/api/discovery-client";

interface CatalogPageProps {
  searchParams?: Promise<Record<string, string | string[] | undefined>>;
}

const CatalogPage = async ({ searchParams }: CatalogPageProps): Promise<JSX.Element> => {
  const params = searchParams ? await searchParams : undefined;
  const rawQuery = params?.q;
  const rawGroup = params?.group;
  const query = typeof rawQuery === "string" ? rawQuery.trim() : "";
  const grouped = rawGroup === "source";

  try {
    const request = {
      groupBySource: grouped,
      ...(query.length > 0 ? { q: query } : {}),
    };
    const result = await fetchDatasetCatalog(request);

    return (
      <main data-testid="catalog-page">
        <DatasetSearchBox initialQuery={query} />
        <GroupBySourceToggle />
        <DatasetCatalogList
          groups={result.groups}
          items={result.items}
          viewMode={grouped ? "grouped" : "flat"}
        />
      </main>
    );
  } catch {
    return (
      <main data-testid="catalog-page">
        <DatasetSearchBox initialQuery={query} />
        <GroupBySourceToggle />
        <ErrorState />
      </main>
    );
  }
};

export default CatalogPage;
