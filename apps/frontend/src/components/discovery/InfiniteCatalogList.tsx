"use client";

import { Card, Spinner } from "@heroui/react";
import React, { useEffect, useMemo, useRef, useState } from "react";
import type { JSX } from "react";

import type { DatasetSummary } from "../../lib/api/discovery-types";
import { DatasetCatalogList } from "./DatasetCatalogList";

interface InfiniteCatalogListProps {
  initialItems: DatasetSummary[];
  initialPage: number;
  initialTotalPages: number;
  emptyMessage: string;
  requestPath: string;
  requestQuery?: Record<string, string>;
}

interface PaginatedItemsPayload {
  items: DatasetSummary[];
  page: number;
  total_pages: number;
}

const buildRequestUrl = (
  path: string,
  query: Record<string, string> | undefined,
  page: number,
): string => {
  const params = new URLSearchParams(query);
  params.set("page", String(page));
  const queryText = params.toString();
  return queryText.length > 0 ? `${path}?${queryText}` : path;
};

export const InfiniteCatalogList = ({
  initialItems,
  initialPage,
  initialTotalPages,
  emptyMessage,
  requestPath,
  requestQuery,
}: InfiniteCatalogListProps): JSX.Element => {
  const [items, setItems] = useState(initialItems);
  const [currentPage, setCurrentPage] = useState(initialPage);
  const [totalPages, setTotalPages] = useState(initialTotalPages);
  const [loading, setLoading] = useState(false);
  const [loadError, setLoadError] = useState(false);
  const sentinelRef = useRef<HTMLDivElement | null>(null);

  const hasMore = currentPage < totalPages;
  const stableQuery = useMemo(() => requestQuery ?? {}, [requestQuery]);

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

      void fetch(buildRequestUrl(requestPath, stableQuery, nextPage), {
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
          return (await response.json()) as PaginatedItemsPayload;
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
  }, [currentPage, hasMore, loading, requestPath, stableQuery]);

  return (
    <>
      <DatasetCatalogList emptyMessage={emptyMessage} items={items} />
      {hasMore ? <div data-testid="infinite-scroll-sentinel" ref={sentinelRef} /> : null}
      {loading ? (
        <div className="flex justify-center py-2" data-testid="infinite-scroll-loading">
          <Spinner color="current" size="sm" style={{ color: "var(--foreground)" }} />
        </div>
      ) : null}
      {loadError ? (
        <Card
          className="rounded-lg border border-border/70 bg-surface/95 p-4 text-sm shadow-sm"
          data-testid="infinite-scroll-error"
        >
          Unable to load more datasets right now.
        </Card>
      ) : null}
    </>
  );
};
