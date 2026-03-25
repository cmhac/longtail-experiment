import React from "react";
import type { JSX } from "react";
import { DatasetSearchBox } from "../components/discovery/DatasetSearchBox";
import { DatasetSearchResults } from "../components/discovery/DatasetSearchResults";
import { ErrorState } from "../components/discovery/ErrorState";
import { RecentUpdatesFeed } from "../components/discovery/RecentUpdatesFeed";
import {
  fetchDatasetSearch,
  fetchRecentDatasets,
  fetchSearchSummary,
} from "../lib/api/discovery-client";
import { SiteFooter } from "../shell/site-footer";
import { SiteHeader } from "../shell/site-header";

interface HomePageProps {
  searchParams?: Promise<Record<string, string | string[] | undefined>>;
}

const HomePage = async ({ searchParams }: HomePageProps): Promise<JSX.Element> => {
  const params = searchParams ? await searchParams : undefined;
  const rawQuery = params?.q;
  const query = typeof rawQuery === "string" ? rawQuery.trim() : "";
  const recentPromise = fetchRecentDatasets({ limit: 5 })
    .then((payload) => ({ payload, unavailable: false }))
    .catch(() => ({
      payload: { items: [], limit: 5, sort: "latest_update_at_desc" },
      unavailable: true,
    }));

  try {
    const [recent, search, summary] = await Promise.all([
      recentPromise,
      query.length > 0 ? fetchDatasetSearch({ q: query }) : Promise.resolve(null),
      fetchSearchSummary().catch(() => null),
    ]);

    return (
      <div className="shell-page shell-scroll-anchor" data-testid="site-shell">
        <SiteHeader />
        <main data-testid="home-content">
          <DatasetSearchBox
            initialQuery={query}
            summary={
              summary
                ? {
                    activeDatasetCount: summary.active_dataset_count,
                    activeSourceCount: summary.active_source_count,
                  }
                : null
            }
          />
          {search ? <DatasetSearchResults items={search.items} query={query} /> : null}
          <RecentUpdatesFeed items={recent.payload.items} unavailable={recent.unavailable} />
        </main>
        <SiteFooter />
      </div>
    );
  } catch {
    return (
      <div className="shell-page shell-scroll-anchor" data-testid="site-shell">
        <SiteHeader />
        <main data-testid="home-content">
          <DatasetSearchBox initialQuery={query} summary={null} />
          <ErrorState />
        </main>
        <SiteFooter />
      </div>
    );
  }
};

export default HomePage;
