import { Card } from "@heroui/react/card";
import React from "react";
import type { JSX } from "react";

import type {
  DiscoveryFeedListBodyProps,
  DiscoveryFeedListComponentGroup,
  DiscoveryFeedListMetadataRailProps,
  DiscoveryFeedListRowProps,
  DiscoveryFeedListTextProps,
  DiscoveryFeedListTitleProps,
  DiscoveryFeedListTitleRegionProps,
  DiscoveryFeedListWrapperProps,
} from "./discovery-feed-list-types";

const joinClassNames = (...values: Array<string | undefined>): string => {
  return values.filter(Boolean).join(" ");
};

export const DiscoveryFeedListWrapper = ({
  cardClassName,
  cardTestId,
  children,
  contentClassName,
}: DiscoveryFeedListWrapperProps): JSX.Element => {
  return (
    <Card className={cardClassName} data-testid={cardTestId} variant="default">
      <div
        className={joinClassNames("grid gap-0", contentClassName)}
        data-testid="discovery-feed-list-wrapper"
      >
        {children}
      </div>
    </Card>
  );
};

export const DiscoveryFeedListTitleRegion = ({
  children,
  className,
}: DiscoveryFeedListTitleRegionProps): JSX.Element => {
  return (
    <h2
      className={joinClassNames(
        "m-0 font-serif text-[clamp(1.7rem,2.3vw,2.05rem)] leading-[1.1]",
        className,
      )}
      data-testid="discovery-feed-list-title-region"
    >
      {children}
    </h2>
  );
};

export const DiscoveryFeedListRow = ({
  cardClassName,
  cardTestId,
  children,
  className,
}: DiscoveryFeedListRowProps): JSX.Element => {
  return (
    <Card
      className={joinClassNames(
        "rounded-none border-0 bg-transparent px-0 py-0 shadow-none",
        cardClassName,
      )}
      data-testid={cardTestId}
      variant="transparent"
    >
      <div
        className={joinClassNames(
          "recent-updates-row grid grid-cols-[minmax(7.5rem,9.25rem)_1fr] gap-[1.15rem] border-0 border-t border-t-[color-mix(in_srgb,var(--shell-border)_68%,transparent)] px-0 py-[1.55rem] text-inherit no-underline first:border-t-0 max-[720px]:grid-cols-1 max-[720px]:gap-[0.52rem] max-[720px]:py-[1.1rem]",
          className,
        )}
        data-testid="discovery-feed-list-row"
      >
        {children}
      </div>
    </Card>
  );
};

export const DiscoveryFeedListMetadataRail = ({
  children,
  className,
}: DiscoveryFeedListMetadataRailProps): JSX.Element => {
  return (
    <div
      className={joinClassNames(
        "recent-updates-meta-rail grid min-w-0 content-start gap-[0.32rem] max-[720px]:flex max-[720px]:items-center max-[720px]:gap-[0.6rem]",
        className,
      )}
      data-testid="discovery-feed-list-metadata-rail"
    >
      {children}
    </div>
  );
};

export const DiscoveryFeedListDisplayCategory = ({
  children,
  className,
}: DiscoveryFeedListTextProps): JSX.Element => {
  return (
    <span
      className={joinClassNames(
        "recent-updates-source font-bold text-[0.73rem] tracking-[0.08em]",
        className,
      )}
      data-testid="discovery-feed-list-display-category"
    >
      {children}
    </span>
  );
};

export const DiscoveryFeedListUpdateDate = ({
  children,
  className,
}: DiscoveryFeedListTextProps): JSX.Element => {
  return (
    <span
      className={joinClassNames(
        "recent-updates-date text-(--shell-muted) text-[0.82rem]",
        className,
      )}
      data-testid="discovery-feed-list-update-date"
    >
      {children}
    </span>
  );
};

export const DiscoveryFeedListBody = ({
  children,
  className,
}: DiscoveryFeedListBodyProps): JSX.Element => {
  return (
    <div className={joinClassNames("recent-updates-body grid min-w-0 gap-[0.42rem]", className)}>
      {children}
    </div>
  );
};

export const DiscoveryFeedListTitle = ({
  children,
  className,
  testId,
}: DiscoveryFeedListTitleProps): JSX.Element => {
  return (
    <h3
      className={joinClassNames(
        "m-0 font-serif text-[clamp(1.18rem,2.1vw,1.95rem)] leading-[1.05] max-[720px]:leading-[1.13]",
        className,
      )}
      {...(testId ? { "data-testid": testId } : {})}
    >
      <span data-testid="discovery-feed-list-title-text">{children}</span>
    </h3>
  );
};

export const DiscoveryFeedListSubtitle = ({
  children,
  className,
}: DiscoveryFeedListTextProps): JSX.Element => {
  return (
    <p
      className={joinClassNames("m-0 max-w-[70ch] text-(--shell-muted) leading-[1.4]", className)}
      data-testid="discovery-feed-list-subtitle"
    >
      {children}
    </p>
  );
};

export const DiscoveryFeedList: DiscoveryFeedListComponentGroup = {
  Body: DiscoveryFeedListBody,
  DisplayCategory: DiscoveryFeedListDisplayCategory,
  MetadataRail: DiscoveryFeedListMetadataRail,
  Row: DiscoveryFeedListRow,
  Subtitle: DiscoveryFeedListSubtitle,
  Title: DiscoveryFeedListTitle,
  TitleRegion: DiscoveryFeedListTitleRegion,
  UpdateDate: DiscoveryFeedListUpdateDate,
  Wrapper: DiscoveryFeedListWrapper,
};
