"use client";

import React, { useEffect, useMemo, useState } from "react";
import type { JSX } from "react";
import type { DatasetCatalogResponse, DatasetSummary } from "../../lib/api/discovery-types";
import { loadAuthSessionState } from "../../lib/auth/session-state";
import { ErrorState } from "./ErrorState";
import { InfiniteCatalogList } from "./InfiniteCatalogList";

interface ClientScopedCatalogListProps {
  emptyMessage: string;
  requestPath: string;
  requestQuery: Record<string, string>;
}

const buildRequestUrl = (path: string, query: Record<string, string>): string => {
  const params = new URLSearchParams(query);
  return `${path}?${params.toString()}`;
};

export const ClientScopedCatalogList = ({
  emptyMessage,
  requestPath,
  requestQuery,
}: ClientScopedCatalogListProps): JSX.Element => {
  const [isLoading, setIsLoading] = useState(true);
  const [errorMessage, setErrorMessage] = useState<string | null>(null);
  const [initialItems, setInitialItems] = useState<DatasetSummary[]>([]);
  const [initialPage, setInitialPage] = useState(1);
  const [initialTotalPages, setInitialTotalPages] = useState(0);
  const [sessionToken, setSessionToken] = useState<string | null>(null);
  const [isUnauthenticated, setIsUnauthenticated] = useState(false);

  const requestUrl = useMemo(
    () => buildRequestUrl(requestPath, requestQuery),
    [requestPath, requestQuery],
  );

  useEffect(() => {
    let isCancelled = false;

    const load = async (): Promise<void> => {
      setIsLoading(true);
      setErrorMessage(null);
      setIsUnauthenticated(false);
      try {
        const state = loadAuthSessionState();
        const token = state?.sessionToken?.trim() ?? "";
        if (token === "") {
          if (!isCancelled) {
            setIsUnauthenticated(true);
            setSessionToken(null);
          }
          return;
        }

        const response = await fetch(requestUrl, {
          method: "GET",
          cache: "no-store",
          headers: {
            accept: "application/json",
            authorization: `Bearer ${token}`,
          },
        });

        if (response.status === 401) {
          if (!isCancelled) {
            setIsUnauthenticated(true);
            setSessionToken(null);
          }
          return;
        }

        if (!response.ok) {
          throw new Error("failed_to_load_followed_datasets");
        }

        const payload = (await response.json()) as DatasetCatalogResponse;
        if (!isCancelled) {
          setSessionToken(token);
          setInitialItems(payload.items ?? []);
          setInitialPage(payload.page ?? 1);
          setInitialTotalPages(payload.total_pages ?? 0);
        }
      } catch {
        if (!isCancelled) {
          setErrorMessage("Unable to load followed datasets. Please try again.");
        }
      } finally {
        if (!isCancelled) {
          setIsLoading(false);
        }
      }
    };

    void load();
    return () => {
      isCancelled = true;
    };
  }, [requestUrl]);

  if (isLoading) {
    return (
      <p className="text-default-500 text-sm" data-testid="dataset-scope-loading">
        Loading followed datasets...
      </p>
    );
  }

  if (isUnauthenticated) {
    return (
      <p className="text-default-500 text-sm" data-testid="dataset-scope-unauthenticated">
        Sign in to view followed datasets.
      </p>
    );
  }

  if (errorMessage) {
    return <ErrorState message={errorMessage} />;
  }

  return (
    <InfiniteCatalogList
      emptyMessage={emptyMessage}
      initialItems={initialItems}
      initialPage={initialPage}
      initialTotalPages={initialTotalPages}
      requestPath={requestPath}
      requestQuery={requestQuery}
      {...(sessionToken ? { authorizationToken: sessionToken } : {})}
    />
  );
};
