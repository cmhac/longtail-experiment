"use client";

import { usePathname, useRouter, useSearchParams } from "next/navigation";
import React, { useEffect, useState } from "react";
import type { FormEvent, JSX } from "react";

interface DatasetSearchBoxProps {
  initialQuery?: string;
}

export const buildSearchUrl = (pathname: string, rawQuery: string): string => {
  const trimmed = rawQuery.trim();

  if (trimmed.length === 0) {
    return pathname;
  }

  const query = new URLSearchParams({ q: trimmed });
  return `${pathname}?${query.toString()}`;
};

export const DatasetSearchBox = ({ initialQuery = "" }: DatasetSearchBoxProps): JSX.Element => {
  const router = useRouter();
  const pathname = usePathname();
  const searchParams = useSearchParams();
  const [query, setQuery] = useState(initialQuery);
  const urlQuery = searchParams.get("q") ?? "";

  useEffect(() => {
    setQuery(urlQuery);
  }, [urlQuery]);

  const onSubmit = (event: FormEvent<HTMLFormElement>): void => {
    event.preventDefault();
    router.push(buildSearchUrl(pathname, query));
  };

  return (
    <form aria-label="Dataset search" data-testid="dataset-search-form" onSubmit={onSubmit}>
      <label htmlFor="dataset-search-input">Search datasets</label>
      <input
        id="dataset-search-input"
        name="q"
        onChange={(event) => setQuery(event.target.value)}
        type="text"
        value={query}
      />
      <button type="submit">Search</button>
    </form>
  );
};
