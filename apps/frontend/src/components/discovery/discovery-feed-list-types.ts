import type { JSX, ReactNode } from "react";

export interface DiscoveryFeedListWrapperProps {
  cardClassName?: string;
  cardTestId?: string;
  children: ReactNode;
  contentClassName?: string;
}

export interface DiscoveryFeedListTitleRegionProps {
  children: ReactNode;
  className?: string;
}

export interface DiscoveryFeedListRowProps {
  cardClassName?: string;
  cardTestId?: string;
  children: ReactNode;
  className?: string;
}

export interface DiscoveryFeedListMetadataRailProps {
  children: ReactNode;
  className?: string;
}

export interface DiscoveryFeedListBodyProps {
  children: ReactNode;
  className?: string;
}

export interface DiscoveryFeedListTextProps {
  children: ReactNode;
  className?: string;
}

export interface DiscoveryFeedListTitleProps {
  children: ReactNode;
  className?: string;
  testId?: string;
}

export interface DiscoveryFeedListComponentGroup {
  Body: (props: DiscoveryFeedListBodyProps) => JSX.Element;
  DisplayCategory: (props: DiscoveryFeedListTextProps) => JSX.Element;
  MetadataRail: (props: DiscoveryFeedListMetadataRailProps) => JSX.Element;
  Row: (props: DiscoveryFeedListRowProps) => JSX.Element;
  Subtitle: (props: DiscoveryFeedListTextProps) => JSX.Element;
  Title: (props: DiscoveryFeedListTitleProps) => JSX.Element;
  TitleRegion: (props: DiscoveryFeedListTitleRegionProps) => JSX.Element;
  UpdateDate: (props: DiscoveryFeedListTextProps) => JSX.Element;
  Wrapper: (props: DiscoveryFeedListWrapperProps) => JSX.Element;
}
