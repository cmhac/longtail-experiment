"use client";

import { usePathname, useRouter, useSearchParams } from "next/navigation";
import React from "react";
import type { FormEvent, JSX } from "react";

import { fetchSearchSuggestions } from "../../lib/api/discovery-client";
import type { SuggestionItem } from "../../lib/api/discovery-types";

interface DatasetSearchBoxProps {
  initialQuery?: string;
  summary?: {
    activeDatasetCount: number;
    activeSourceCount: number;
  } | null;
}

export const buildSearchUrl = (pathname: string, rawQuery: string): string => {
  const trimmed = rawQuery.trim();

  if (trimmed.length === 0) {
    return pathname;
  }

  const query = new URLSearchParams({ q: trimmed });
  return `${pathname}?${query.toString()}`;
};

export const DatasetSearchBox = ({
  initialQuery = "",
  summary = null,
}: DatasetSearchBoxProps): JSX.Element => {
  const router = useRouter();
  const pathname = usePathname();
  const searchParams = useSearchParams();
  const [query, setQuery] = React.useState(initialQuery);
  const [suggestions, setSuggestions] = React.useState<SuggestionItem[]>([]);
  const [showSuggestions, setShowSuggestions] = React.useState(false);
  const urlQuery = searchParams.get("q") ?? "";
  const requestIdRef = React.useRef(0);

  React.useEffect(() => {
    setQuery(urlQuery);
  }, [urlQuery]);

  React.useEffect(() => {
    const normalized = query.trim();
    if (normalized.length === 0) {
      setSuggestions([]);
      setShowSuggestions(false);
      return;
    }

    const requestId = requestIdRef.current + 1;
    requestIdRef.current = requestId;

    const timeoutId = window.setTimeout(() => {
      fetchSearchSuggestions({ q: normalized, limit: 10 })
        .then((response) => {
          if (requestId !== requestIdRef.current) {
            return;
          }
          setSuggestions(response.items);
          setShowSuggestions(response.items.length > 0);
        })
        .catch(() => {
          if (requestId !== requestIdRef.current) {
            return;
          }
          setSuggestions([]);
          setShowSuggestions(false);
        });
    }, 160);

    return () => {
      window.clearTimeout(timeoutId);
    };
  }, [query]);

  const onSubmit = (event: FormEvent<HTMLFormElement>): void => {
    event.preventDefault();
    setShowSuggestions(false);
    router.push(buildSearchUrl(pathname, query));
  };

  const summaryText =
    summary === null
      ? "Searching active datasets from sources."
      : `Searching ${summary.activeDatasetCount} active datasets from ${summary.activeSourceCount} sources.`;

  const onSuggestionsWheel = (event: React.WheelEvent<HTMLUListElement>): void => {
    const target = event.currentTarget;
    const maxScrollTop = Math.max(0, target.scrollHeight - target.clientHeight);

    // Prevent rubber-band momentum at boundaries so underlying content never peeks through.
    if (
      (event.deltaY < 0 && target.scrollTop <= 0) ||
      (event.deltaY > 0 && target.scrollTop >= maxScrollTop)
    ) {
      event.preventDefault();
    }
  };

  return (
    <section className="search-hero" data-testid="dataset-search-hero">
      <form aria-label="Dataset search" data-testid="dataset-search-form" onSubmit={onSubmit}>
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
            id="dataset-search-input"
            name="q"
            onBlur={() => {
              window.setTimeout(() => setShowSuggestions(false), 120);
            }}
            onChange={(event) => setQuery(event.target.value)}
            onFocus={() => setShowSuggestions(suggestions.length > 0)}
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
                      setQuery(item.title);
                      setShowSuggestions(false);
                      router.push(buildSearchUrl(pathname, item.title));
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
      <p className="dataset-search-summary" data-testid="dataset-search-summary">
        {summaryText}
      </p>
    </section>
  );
};
