import React from "react";
import type { JSX } from "react";
import { DatasetSearchBox } from "../components/discovery/DatasetSearchBox";
import { DatasetSearchResults } from "../components/discovery/DatasetSearchResults";
import { ErrorState } from "../components/discovery/ErrorState";
import { RecentUpdatesFeed } from "../components/discovery/RecentUpdatesFeed";
import { fetchDatasetSearch, fetchRecentDatasets } from "../lib/api/discovery-client";
import { SiteFooter } from "../shell/site-footer";
import { SiteHeader } from "../shell/site-header";

interface HomePageProps {
  searchParams?: Promise<Record<string, string | string[] | undefined>>;
}

const HomePage = async ({ searchParams }: HomePageProps): Promise<JSX.Element> => {
  const params = searchParams ? await searchParams : undefined;
  const rawQuery = params?.q;
  const query = typeof rawQuery === "string" ? rawQuery.trim() : "";

  try {
    const [recent, search] = await Promise.all([
      fetchRecentDatasets({ limit: 5 }),
      query.length > 0 ? fetchDatasetSearch({ q: query }) : Promise.resolve(null),
    ]);

    return (
      <div className="shell-page shell-scroll-anchor" data-testid="site-shell">
        <SiteHeader />
        <main data-testid="home-content">
          <DatasetSearchBox initialQuery={query} />
          {search ? <DatasetSearchResults items={search.items} query={query} /> : null}
          <RecentUpdatesFeed items={recent.items} />
        </main>
        <SiteFooter />
      </div>
    );
  } catch {
    return (
      <div className="shell-page shell-scroll-anchor" data-testid="site-shell">
        <SiteHeader />
        <main data-testid="home-content">
          <DatasetSearchBox initialQuery={query} />
          <ErrorState />
        </main>
        <SiteFooter />
      </div>
    );
  }
};

export default HomePage;
