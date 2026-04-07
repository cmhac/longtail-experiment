"use client";

import { Card, Spinner } from "@heroui/react";
import React, { useCallback, useEffect, useMemo, useState } from "react";
import type { JSX } from "react";

import type { DatasetSummary } from "../../lib/api/discovery-types";
import { DatasetCatalogList } from "./DatasetCatalogList";
import { useInfiniteScrollObserver } from "./useInfiniteScrollObserver";

interface InfiniteCatalogListProps {
  initialItems: DatasetSummary[];
  initialPage: number;
  initialTotalPages: number;
  emptyMessage: string;
  requestPath: string;
  requestQuery?: Record<string, string>;
  authorizationToken?: string;
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
  authorizationToken,
}: InfiniteCatalogListProps): JSX.Element => {
  const [items, setItems] = useState(initialItems);
  const [currentPage, setCurrentPage] = useState(initialPage);
  const [totalPages, setTotalPages] = useState(initialTotalPages);
  const [loading, setLoading] = useState(false);
  const [loadError, setLoadError] = useState(false);

  const hasMore = currentPage < totalPages;
  const stableQuery = useMemo(() => requestQuery ?? {}, [requestQuery]);
  const requestSignature = useMemo(
    () => `${requestPath}?${new URLSearchParams(stableQuery).toString()}`,
    [requestPath, stableQuery],
  );

  useEffect(() => {
    // Reset paging state whenever server-provided payload context changes.
    void requestSignature;
    setItems(initialItems);
    setCurrentPage(initialPage);
    setTotalPages(initialTotalPages);
    setLoadError(false);
    setLoading(false);
  }, [initialItems, initialPage, initialTotalPages, requestSignature]);

  const loadNextPage = useCallback(() => {
    if (!hasMore || loading) {
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
        ...(authorizationToken ? { authorization: `Bearer ${authorizationToken}` } : {}),
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
  }, [authorizationToken, currentPage, hasMore, loading, requestPath, stableQuery]);

  const sentinelRef = useInfiniteScrollObserver({
    enabled: hasMore && !loading,
    onIntersect: loadNextPage,
  });

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
          className="rounded-lg border bg-surface/95 p-4 text-sm shadow-sm"
          data-testid="infinite-scroll-error"
        >
          Unable to load more datasets right now.
        </Card>
      ) : null}
    </>
  );
};
