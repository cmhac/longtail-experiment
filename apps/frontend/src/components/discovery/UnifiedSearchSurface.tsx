"use client";

import { Card, Input } from "@heroui/react";
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
  const inputRef = React.useRef<HTMLInputElement | null>(null);
  const scrollHideTimeoutRef = React.useRef<number | null>(null);
  const [isSuggestionsScrolling, setIsSuggestionsScrolling] = React.useState(false);

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

  const onSuggestionsWheel = (event: React.WheelEvent<HTMLDivElement>): void => {
    const target = event.currentTarget;
    const maxScrollTop = Math.max(0, target.scrollHeight - target.clientHeight);

    if (
      (event.deltaY < 0 && target.scrollTop <= 0) ||
      (event.deltaY > 0 && target.scrollTop >= maxScrollTop)
    ) {
      event.preventDefault();
    }
  };

  const markSuggestionsScrolling = React.useCallback((): void => {
    setIsSuggestionsScrolling(true);

    if (scrollHideTimeoutRef.current !== null) {
      window.clearTimeout(scrollHideTimeoutRef.current);
    }

    scrollHideTimeoutRef.current = window.setTimeout(() => {
      setIsSuggestionsScrolling(false);
      scrollHideTimeoutRef.current = null;
    }, 180);
  }, []);

  React.useEffect(() => {
    return () => {
      if (scrollHideTimeoutRef.current !== null) {
        window.clearTimeout(scrollHideTimeoutRef.current);
      }
    };
  }, []);

  React.useEffect(() => {
    if (variant !== "navbar") {
      return;
    }

    inputRef.current?.focus();
    inputRef.current?.select();
  }, [variant]);

  const formTestId = React.useMemo(
    () => (variant === "navbar" ? "navbar-search-form" : "dataset-search-form"),
    [variant],
  );
  const isNavbar = variant === "navbar";

  const sectionClassName = isNavbar
    ? "h-8 w-full overflow-visible border-0 bg-(--shell-surface) p-0"
    : "mx-auto grid w-full max-w-[72rem] justify-items-center gap-[0.45rem] overflow-visible px-4 pb-[1.25rem] pt-[3.2rem] max-[720px]:pt-[1.7rem]";

  const formClassName = isNavbar
    ? "relative z-30 grid w-full gap-[0.3rem]"
    : "relative z-30 grid w-full max-w-[64rem] gap-[0.4rem] overflow-visible";

  const inputWrapClassName = isNavbar
    ? "relative grid h-8 w-full grid-cols-1 items-center gap-0 overflow-visible rounded-full border border-[color-mix(in_srgb,var(--shell-border)_78%,transparent)]"
    : "relative grid w-full grid-cols-1 items-center gap-0 overflow-visible rounded-[0.8rem]";

  const suggestionsClassName = isNavbar
    ? "dataset-search-suggestions absolute inset-x-0 top-[calc(100%+0.35rem)] z-[120] isolate overflow-hidden"
    : "dataset-search-suggestions absolute inset-x-0 top-[calc(100%+0.7rem)] z-[120] isolate overflow-hidden";

  const suggestionsScrollClassName = `${isNavbar ? "max-h-[min(55vh,22rem)]" : "max-h-[min(70vh,36rem)]"} dataset-search-suggestions-scroll overflow-x-hidden overflow-y-auto overscroll-x-contain overscroll-y-none [contain:paint] [scrollbar-width:none] [scrollbar-color:transparent_transparent] [transform:translateZ(0)] [will-change:scroll-position]`;

  const suggestionScrollStateClassName = isSuggestionsScrolling ? " is-scrolling" : "";

  return (
    <section className={sectionClassName} data-testid="dataset-search-hero">
      {variant === "navbar" ? (
        <Card
          className="h-8 w-full overflow-visible border-0 bg-(--shell-surface) p-0"
          variant="transparent"
        >
          <form
            aria-label="Dataset search"
            className={formClassName}
            data-testid={formTestId}
            onSubmit={onSubmit}
          >
            <div className={inputWrapClassName} data-testid="dataset-search-input-wrap">
              <Input
                aria-label="Search datasets"
                autoComplete="off"
                className="h-8 min-h-8 bg-transparent text-[0.95rem]"
                fullWidth
                id="navbar-search-input"
                name="q"
                ref={inputRef}
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
                <Card
                  className={suggestionsClassName}
                  data-testid="dataset-search-suggestions"
                  variant="default"
                >
                  <div
                    className="flex items-center justify-between gap-3 border-[color-mix(in_srgb,var(--shell-border)_70%,transparent)] border-b bg-[var(--surface)] px-5 py-[1.05rem] font-bold text-[0.72rem] tracking-[0.17em] max-[720px]:flex-col max-[720px]:items-start"
                    data-testid="dataset-search-suggestions-header"
                  >
                    <span>SEARCH RESULTS ({suggestions.length})</span>
                    <small className="font-semibold text-(--shell-muted) text-[0.82rem] tracking-normal">
                      Press ↵ to view all
                    </small>
                  </div>
                  <div
                    className={`${suggestionsScrollClassName}${suggestionScrollStateClassName}`}
                    onScroll={markSuggestionsScrolling}
                    onWheel={onSuggestionsWheel}
                  >
                    <ul className="m-0 list-none p-0">
                      {suggestions.map((item) => (
                        <li key={item.dataset_id}>
                          <button
                            className="grid w-full gap-[0.55rem] bg-transparent px-[1.45rem] py-[1.65rem] text-left text-inherit [margin:0.42rem_0] hover:bg-[color-mix(in_srgb,var(--shell-surface)_55%,var(--shell-background))] max-[720px]:gap-[0.45rem] max-[720px]:px-4 max-[720px]:py-[1.2rem] max-[720px]:[margin:0.28rem_0]"
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
                            <span className="font-bold text-(--shell-muted) text-[0.72rem] tracking-[0.15em]">
                              DATASET • {item.source.name.toUpperCase()}
                            </span>
                            <span className="font-bold font-serif text-[clamp(1.08rem,1.6vw,1.5rem)] text-[var(--shell-foreground)] leading-[1.1] max-[720px]:text-[1.12rem]">
                              {item.title}
                            </span>
                            <span className="flex items-center gap-[1.2rem] max-[720px]:flex-wrap max-[720px]:gap-3">
                              <small className="text-(--shell-muted) text-[0.95rem]">
                                {item.source.name}
                              </small>
                              <small className="text-(--shell-muted) text-[0.95rem]">
                                {item.dataset_id}
                              </small>
                            </span>
                          </button>
                        </li>
                      ))}
                    </ul>
                  </div>
                </Card>
              ) : null}
            </div>
          </form>
        </Card>
      ) : (
        <>
          <form
            aria-label="Dataset search"
            className={formClassName}
            data-testid={formTestId}
            onSubmit={onSubmit}
          >
            <div className={inputWrapClassName} data-testid="dataset-search-input-wrap">
              <Input
                aria-label="Search datasets"
                autoComplete="off"
                className="min-h-12 text-[1.06rem]"
                fullWidth
                id="dataset-search-input"
                name="q"
                ref={inputRef}
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
                <Card
                  className={suggestionsClassName}
                  data-testid="dataset-search-suggestions"
                  variant="default"
                >
                  <div
                    className="flex items-center justify-between gap-3 border-[color-mix(in_srgb,var(--shell-border)_70%,transparent)] border-b bg-[var(--surface)] px-5 py-[1.05rem] font-bold text-[0.72rem] tracking-[0.17em] max-[720px]:flex-col max-[720px]:items-start"
                    data-testid="dataset-search-suggestions-header"
                  >
                    <span>SEARCH RESULTS ({suggestions.length})</span>
                    <small className="font-semibold text-(--shell-muted) text-[0.82rem] tracking-normal">
                      Press ↵ to view all
                    </small>
                  </div>
                  <div
                    className={`${suggestionsScrollClassName}${suggestionScrollStateClassName}`}
                    onScroll={markSuggestionsScrolling}
                    onWheel={onSuggestionsWheel}
                  >
                    <ul className="m-0 list-none p-0">
                      {suggestions.map((item) => (
                        <li key={item.dataset_id}>
                          <button
                            className="grid w-full gap-[0.55rem] bg-transparent px-[1.45rem] py-[1.65rem] text-left text-inherit [margin:0.42rem_0] hover:bg-[color-mix(in_srgb,var(--shell-surface)_55%,var(--shell-background))] max-[720px]:gap-[0.45rem] max-[720px]:px-4 max-[720px]:py-[1.2rem] max-[720px]:[margin:0.28rem_0]"
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
                            <span className="font-bold text-(--shell-muted) text-[0.72rem] tracking-[0.15em]">
                              DATASET • {item.source.name.toUpperCase()}
                            </span>
                            <span className="font-bold font-serif text-[clamp(1.08rem,1.6vw,1.5rem)] text-[var(--shell-foreground)] leading-[1.1] max-[720px]:text-[1.12rem]">
                              {item.title}
                            </span>
                            <span className="flex items-center gap-[1.2rem] max-[720px]:flex-wrap max-[720px]:gap-3">
                              <small className="text-(--shell-muted) text-[0.95rem]">
                                {item.source.name}
                              </small>
                              <small className="text-(--shell-muted) text-[0.95rem]">
                                {item.dataset_id}
                              </small>
                            </span>
                          </button>
                        </li>
                      ))}
                    </ul>
                  </div>
                </Card>
              ) : null}
            </div>
          </form>
          <p
            className="relative z-[1] m-0 max-w-[56ch] text-center text-(--shell-muted) text-[0.9rem]"
            data-testid="dataset-search-summary"
          >
            {summaryText}
          </p>
        </>
      )}
    </section>
  );
};
