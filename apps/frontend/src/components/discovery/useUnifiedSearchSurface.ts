import React from "react";
import type { FormEvent } from "react";

import { fetchSearchSuggestions } from "../../lib/api/discovery-client";
import type { SuggestionItem } from "../../lib/api/discovery-types";
import { normalizeSearchQuery } from "./search-route-utils";
import type {
  UseUnifiedSearchSurfaceOptions,
  UseUnifiedSearchSurfaceResult,
} from "./search-surface-types";

export const useUnifiedSearchSurface = ({
  initialQuery = "",
  urlQuery,
  onSubmitQuery,
}: UseUnifiedSearchSurfaceOptions): UseUnifiedSearchSurfaceResult => {
  const [query, setQuery] = React.useState(initialQuery);
  const [suggestions, setSuggestions] = React.useState<SuggestionItem[]>([]);
  const [showSuggestions, setShowSuggestions] = React.useState(false);
  const [isInputFocused, setIsInputFocused] = React.useState(false);
  const requestIdRef = React.useRef(0);

  React.useEffect(() => {
    setQuery(urlQuery);
  }, [urlQuery]);

  React.useEffect(() => {
    const normalized = normalizeSearchQuery(query);

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
          setShowSuggestions(isInputFocused && response.items.length > 0);
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
  }, [isInputFocused, query]);

  const submitQuery = (rawQuery: string): void => {
    const normalized = normalizeSearchQuery(rawQuery);

    setShowSuggestions(false);
    setIsInputFocused(false);

    if (normalized.length === 0) {
      return;
    }

    onSubmitQuery(normalized);
  };

  const onSubmit = (event: FormEvent<HTMLFormElement>): void => {
    event.preventDefault();
    submitQuery(query);
  };

  const onSuggestionSelect = (value: string): void => {
    setQuery(value);
    submitQuery(value);
  };

  const onInputFocus = (): void => {
    setIsInputFocused(true);
    setShowSuggestions(suggestions.length > 0);
  };

  const onInputBlur = (): void => {
    setIsInputFocused(false);
    setShowSuggestions(false);
  };

  return {
    query,
    suggestions,
    showSuggestions,
    onInputBlur,
    onInputFocus,
    setQuery,
    setShowSuggestions,
    onSubmit,
    onSuggestionSelect,
  };
};
