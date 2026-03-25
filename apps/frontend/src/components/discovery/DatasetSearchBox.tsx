import React from "react";
import type { JSX } from "react";

import { UnifiedSearchSurface } from "./UnifiedSearchSurface";
import type { SearchSummaryView } from "./search-surface-types";
export { buildSearchUrl } from "./search-route-utils";

interface DatasetSearchBoxProps {
  initialQuery?: string;
  submitPath?: string;
  summary?: SearchSummaryView | null;
}

export const DatasetSearchBox = ({
  initialQuery = "",
  submitPath = "/search",
  summary = null,
}: DatasetSearchBoxProps): JSX.Element => {
  return (
    <UnifiedSearchSurface
      initialQuery={initialQuery}
      submitPath={submitPath}
      summary={summary}
      variant="hero"
    />
  );
};
