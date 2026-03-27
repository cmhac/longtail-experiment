import React from "react";
import type { JSX } from "react";

import { DatasetSearchBox } from "../../components/discovery/DatasetSearchBox";
import { EmptyState } from "../../components/discovery/EmptyState";
import { ErrorState } from "../../components/discovery/ErrorState";
import { InfiniteSearchResults } from "../../components/discovery/InfiniteSearchResults";
import { fetchDatasetSearch, fetchSearchSummary } from "../../lib/api/discovery-client";
import { SiteFooter } from "../../shell/site-footer";
import { SiteHeader } from "../../shell/site-header";
import { SHELL_LAYOUT_CLASS_NAMES } from "../../theme/monochrome-theme";

interface SearchPageProps {
  searchParams?: Promise<Record<string, string | string[] | undefined>>;
}

const SearchPage = async ({ searchParams }: SearchPageProps): Promise<JSX.Element> => {
  const params = searchParams ? await searchParams : undefined;
  const rawQuery = params?.q;
  const query = typeof rawQuery === "string" ? rawQuery.trim() : "";

  const summary = await fetchSearchSummary().catch(() => null);

  let searchError = false;
  const firstPage =
    query.length > 0
      ? await fetchDatasetSearch({ q: query, page: 1 }).catch(() => {
          searchError = true;
          return null;
        })
      : null;

  return (
    <div className="shell-page shell-scroll-anchor" data-testid="site-shell">
      <SiteHeader />
      <main
        className={SHELL_LAYOUT_CLASS_NAMES.constrainedContent}
        data-testid="search-page-content"
      >
        <DatasetSearchBox
          initialQuery={query}
          submitPath="/search"
          summary={
            summary
              ? {
                  activeDatasetCount: summary.active_dataset_count,
                  activeSourceCount: summary.active_source_count,
                }
              : null
          }
        />
        {query.length === 0 ? (
          <EmptyState message="Enter a query to search datasets." />
        ) : searchError ? (
          <ErrorState message="Search is temporarily unavailable. Please try again." />
        ) : firstPage ? (
          <InfiniteSearchResults
            initialItems={firstPage.items}
            initialPage={firstPage.page}
            initialTotalPages={firstPage.total_pages}
            query={query}
          />
        ) : (
          <EmptyState message="No datasets matched your search." />
        )}
      </main>
      <SiteFooter />
    </div>
  );
};

export default SearchPage;
