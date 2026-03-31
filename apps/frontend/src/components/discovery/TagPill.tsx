import Link from "next/link";
import React from "react";
import type { JSX, ReactNode } from "react";

interface TagPillProps {
  href: string;
  label: string;
  emphasized?: boolean;
}

interface TagPillGroupProps {
  emphasizedPills?: string[];
  fallback?: ReactNode;
  groupClassName?: string;
  showFallbackWhenTagPillsEmpty?: boolean;
  tagPills: string[];
  testId?: string;
}

export const toMetadataSlug = (value: string): string => {
  return (
    value
      .trim()
      .toLowerCase()
      .replace(/[^a-z0-9]+/g, "-")
      .replace(/^-+|-+$/g, "") || "unknown"
  );
};

const TagPill = ({ emphasized = false, href, label }: TagPillProps): JSX.Element => (
  <Link
    className={
      emphasized ? "recent-updates-pill recent-updates-geography-pill" : "recent-updates-pill"
    }
    href={href}
  >
    {label}
  </Link>
);

const TAG_PILL_GROUP_STYLE =
  "[&_a.recent-updates-pill]:inline-flex [&_a.recent-updates-pill]:items-center [&_a.recent-updates-pill]:rounded-full [&_a.recent-updates-pill]:border [&_a.recent-updates-pill]:border-(--shell-border) [&_a.recent-updates-pill]:bg-[color-mix(in_srgb,var(--shell-surface)_78%,transparent)] [&_a.recent-updates-pill]:px-[0.52rem] [&_a.recent-updates-pill]:py-[0.18rem] [&_a.recent-updates-pill]:text-[0.72rem] [&_a.recent-updates-pill]:tracking-[0.02em] [&_a.recent-updates-pill]:text-(--shell-muted) [&_a.recent-updates-pill]:no-underline [&_a.recent-updates-pill:hover]:bg-[color-mix(in_srgb,var(--shell-surface)_90%,var(--shell-background))] [&_a.recent-updates-pill:hover]:text-(--shell-foreground) [&_a.recent-updates-geography-pill]:font-semibold [&_a.recent-updates-geography-pill]:text-(--shell-foreground)";

export const TagPillGroup = ({
  emphasizedPills = [],
  fallback = null,
  groupClassName,
  showFallbackWhenTagPillsEmpty = false,
  tagPills,
  testId,
}: TagPillGroupProps): JSX.Element | null => {
  const hasPills = emphasizedPills.length > 0 || tagPills.length > 0;

  if (!hasPills) {
    return fallback ? <>{fallback}</> : null;
  }

  const className = [
    "recent-updates-pills flex flex-wrap gap-[0.45rem]",
    TAG_PILL_GROUP_STYLE,
    groupClassName,
  ]
    .filter(Boolean)
    .join(" ");

  return (
    <>
      <div className={className} data-testid={testId}>
        {emphasizedPills.map((pill) => (
          <TagPill
            emphasized
            href={`/geographies/${encodeURIComponent(toMetadataSlug(pill))}`}
            key={`em-${pill}`}
            label={pill}
          />
        ))}
        {tagPills.map((pill) => (
          <TagPill
            href={`/topics/${encodeURIComponent(toMetadataSlug(pill))}`}
            key={`tag-${pill}`}
            label={pill}
          />
        ))}
      </div>
      {showFallbackWhenTagPillsEmpty && tagPills.length === 0 ? fallback : null}
    </>
  );
};
