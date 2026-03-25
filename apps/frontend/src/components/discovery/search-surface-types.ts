import type { SuggestionItem } from "../../lib/api/discovery-types";

export type UnifiedSearchSurfaceVariant = "hero" | "navbar";

export interface SearchSummaryView {
  activeDatasetCount: number;
  activeSourceCount: number;
}

export interface UseUnifiedSearchSurfaceOptions {
  initialQuery?: string;
  urlQuery: string;
  onSubmitQuery: (query: string) => void;
}

export interface UseUnifiedSearchSurfaceResult {
  query: string;
  suggestions: SuggestionItem[];
  showSuggestions: boolean;
  onInputBlur: () => void;
  onInputFocus: () => void;
  setQuery: (value: string) => void;
  setShowSuggestions: (value: boolean) => void;
  onSubmit: (event: React.FormEvent<HTMLFormElement>) => void;
  onSuggestionSelect: (value: string) => void;
}
