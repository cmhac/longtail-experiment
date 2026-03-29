"use client";

import { Card, Spinner } from "@heroui/react";
import React, { useEffect, useRef, useState } from "react";
import type { JSX } from "react";

import type { DatasetSummary } from "../../lib/api/discovery-types";
import { DatasetSearchResults } from "./DatasetSearchResults";

interface InfiniteSearchResultsProps {
  query: string;
  initialItems: DatasetSummary[];
  initialPage: number;
  initialTotalPages: number;
}

interface SearchPayload {
  items: DatasetSummary[];
  page: number;
  total_pages: number;
}

const buildSearchUrl = (query: string, page: number): string => {
  const params = new URLSearchParams();
  params.set("q", query);
  params.set("page", String(page));
  return `/api/discovery/datasets/search?${params.toString()}`;
};

export const InfiniteSearchResults = ({
  query,
  initialItems,
  initialPage,
  initialTotalPages,
}: InfiniteSearchResultsProps): JSX.Element => {
  const [items, setItems] = useState(initialItems);
  const [currentPage, setCurrentPage] = useState(initialPage);
  const [totalPages, setTotalPages] = useState(initialTotalPages);
  const [loading, setLoading] = useState(false);
  const [loadError, setLoadError] = useState(false);
  const sentinelRef = useRef<HTMLDivElement | null>(null);

  const hasMore = currentPage < totalPages;

  useEffect(() => {
    if (!hasMore || loading) {
      return;
    }

    const sentinel = sentinelRef.current;
    if (!sentinel) {
      return;
    }

    const observer = new IntersectionObserver((entries) => {
      const [entry] = entries;
      if (!entry?.isIntersecting) {
        return;
      }

      const nextPage = currentPage + 1;
      setLoading(true);
      setLoadError(false);

      void fetch(buildSearchUrl(query, nextPage), {
        method: "GET",
        cache: "no-store",
        headers: {
          accept: "application/json",
        },
      })
        .then(async (response) => {
          if (!response.ok) {
            throw new Error("Failed to fetch next page");
          }
          return (await response.json()) as SearchPayload;
        })
        .then((payload) => {
          setItems((previous) => [...previous, ...payload.items]);
          setCurrentPage(payload.page);
          setTotalPages(payload.total_pages);
        })
        .catch(() => {
          setLoadError(true);
        })
        .finally(() => {
          setLoading(false);
        });
    });

    observer.observe(sentinel);
    return () => observer.disconnect();
  }, [currentPage, hasMore, loading, query]);

  return (
    <>
      <DatasetSearchResults items={items} query={query} />
      {hasMore ? <div data-testid="infinite-search-sentinel" ref={sentinelRef} /> : null}
      {loading ? (
        <div className="flex justify-center py-2" data-testid="infinite-search-loading">
          <Spinner color="current" size="sm" style={{ color: "var(--foreground)" }} />
        </div>
      ) : null}
      {loadError ? (
        <Card
          className="rounded-lg border border-border/70 bg-surface/95 p-4 text-sm shadow-sm"
          data-testid="infinite-search-error"
        >
          Unable to load more search results right now.
        </Card>
      ) : null}
    </>
  );
};
