"use client";

import { usePathname, useRouter, useSearchParams } from "next/navigation";
import React from "react";
import type { JSX } from "react";

import { buildSearchUrl, getQueryFromSearchParams } from "./search-route-utils";
import type { SearchSummaryView, UnifiedSearchSurfaceVariant } from "./search-surface-types";
import { useUnifiedSearchSurface } from "./useUnifiedSearchSurface";

interface UnifiedSearchSurfaceProps {
  initialQuery?: string;
  onQuerySubmitted?: () => void;
  submitPath?: string;
  summary?: SearchSummaryView | null;
  variant?: UnifiedSearchSurfaceVariant;
}

export const UnifiedSearchSurface = ({
  initialQuery = "",
  onQuerySubmitted,
  submitPath,
  summary = null,
  variant = "hero",
}: UnifiedSearchSurfaceProps): JSX.Element => {
  const router = useRouter();
  const pathname = usePathname();
  const searchParams = useSearchParams();

  const urlQuery = getQueryFromSearchParams(searchParams);

  const {
    query,
    suggestions,
    showSuggestions,
    onInputBlur,
    onInputFocus,
    setQuery,
    setShowSuggestions,
    onSubmit,
  } = useUnifiedSearchSurface({
    initialQuery,
    urlQuery,
    onSubmitQuery: (normalizedQuery) => {
      router.push(buildSearchUrl(pathname, normalizedQuery, submitPath));
      onQuerySubmitted?.();
    },
  });

  const summaryText =
    summary === null
      ? "Searching active datasets from sources."
      : `Searching ${summary.activeDatasetCount} active datasets from ${summary.activeSourceCount} sources.`;

  const onSuggestionsWheel = (event: React.WheelEvent<HTMLUListElement>): void => {
    const target = event.currentTarget;
    const maxScrollTop = Math.max(0, target.scrollHeight - target.clientHeight);

    if (
      (event.deltaY < 0 && target.scrollTop <= 0) ||
      (event.deltaY > 0 && target.scrollTop >= maxScrollTop)
    ) {
      event.preventDefault();
    }
  };

  const formTestId = React.useMemo(
    () => (variant === "navbar" ? "navbar-search-form" : "dataset-search-form"),
    [variant],
  );
  const wrapperClass = React.useMemo(
    () => (variant === "navbar" ? "shell-navbar-search-surface" : "search-hero"),
    [variant],
  );

  return (
    <section className={wrapperClass} data-testid="dataset-search-hero">
      <form aria-label="Dataset search" data-testid={formTestId} onSubmit={onSubmit}>
        <div className="dataset-search-input-wrap" data-testid="dataset-search-input-wrap">
          <span aria-hidden="true" className="dataset-search-input-icon">
            <svg viewBox="0 0 24 24">
              <title>Search</title>
              <path
                d="M11 4a7 7 0 1 1 0 14 7 7 0 0 1 0-14m0-2a9 9 0 1 0 5.66 16l4.17 4.17 1.42-1.42-4.17-4.17A9 9 0 0 0 11 2"
                fill="currentColor"
              />
            </svg>
          </span>
          <input
            aria-label="Search datasets"
            autoComplete="off"
            id={variant === "navbar" ? "navbar-search-input" : "dataset-search-input"}
            name="q"
            onBlur={() => {
              window.setTimeout(() => onInputBlur(), 120);
            }}
            onChange={(event) => setQuery(event.target.value)}
            onFocus={onInputFocus}
            placeholder="Search datasets"
            type="text"
            value={query}
          />
          {showSuggestions ? (
            <ul
              className="dataset-search-suggestions"
              data-testid="dataset-search-suggestions"
              onWheel={onSuggestionsWheel}
            >
              <li
                className="dataset-search-suggestions-header"
                data-testid="dataset-search-suggestions-header"
              >
                <span>SEARCH RESULTS ({suggestions.length})</span>
                <small>Press ↵ to view all</small>
              </li>
              {suggestions.map((item) => (
                <li key={item.dataset_id}>
                  <button
                    className="dataset-search-suggestion-item"
                    data-testid="dataset-search-suggestion-item"
                    onClick={() => {
                      setShowSuggestions(false);
                      router.push(`/datasets/${encodeURIComponent(item.dataset_id)}`);
                      onQuerySubmitted?.();
                    }}
                    onMouseDown={(event) => {
                      event.preventDefault();
                    }}
                    type="button"
                  >
                    <span className="dataset-search-suggestion-eyebrow">
                      DATASET • {item.source.name.toUpperCase()}
                    </span>
                    <span className="dataset-search-suggestion-title">{item.title}</span>
                    <span className="dataset-search-suggestion-meta">
                      <small>{item.source.name}</small>
                      <small>{item.dataset_id}</small>
                    </span>
                  </button>
                </li>
              ))}
            </ul>
          ) : null}
        </div>
      </form>
      {variant === "hero" ? (
        <p className="dataset-search-summary" data-testid="dataset-search-summary">
          {summaryText}
        </p>
      ) : null}
    </section>
  );
};
