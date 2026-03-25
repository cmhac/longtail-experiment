import React from "react";
import type { JSX } from "react";
import { DatasetSearchBox } from "../components/discovery/DatasetSearchBox";
import { RecentUpdatesFeed } from "../components/discovery/RecentUpdatesFeed";
import { fetchRecentDatasets, fetchSearchSummary } from "../lib/api/discovery-client";
import { SiteFooter } from "../shell/site-footer";
import { SiteHeader } from "../shell/site-header";
import { SHELL_LAYOUT_CLASS_NAMES } from "../theme/monochrome-theme";

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

  const [recent, summary] = await Promise.all([
    recentPromise,
    fetchSearchSummary().catch(() => null),
  ]);

  return (
    <div className="shell-page shell-scroll-anchor" data-testid="site-shell">
      <SiteHeader />
      <main className={SHELL_LAYOUT_CLASS_NAMES.constrainedContent} data-testid="home-content">
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
        <RecentUpdatesFeed items={recent.payload.items} unavailable={recent.unavailable} />
      </main>
      <SiteFooter />
    </div>
  );
};

export default HomePage;
