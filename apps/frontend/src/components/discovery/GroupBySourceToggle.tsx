"use client";

import { usePathname, useRouter, useSearchParams } from "next/navigation";
import React from "react";
import type { JSX } from "react";

export const buildGroupToggleUrl = (pathname: string, currentParams: URLSearchParams): string => {
  const nextParams = new URLSearchParams(currentParams.toString());
  const grouped = nextParams.get("group") === "source";

  if (grouped) {
    nextParams.delete("group");
  } else {
    nextParams.set("group", "source");
  }

  const serialized = nextParams.toString();
  return serialized.length > 0 ? `${pathname}?${serialized}` : pathname;
};

export const GroupBySourceToggle = (): JSX.Element => {
  const pathname = usePathname();
  const router = useRouter();
  const searchParams = useSearchParams();
  const grouped = searchParams.get("group") === "source";

  return (
    <button
      aria-pressed={grouped}
      data-testid="group-by-source-toggle"
      onClick={() =>
        router.push(buildGroupToggleUrl(pathname, new URLSearchParams(searchParams.toString())))
      }
      type="button"
    >
      Group by source
    </button>
  );
};
