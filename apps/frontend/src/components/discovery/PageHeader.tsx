import React from "react";
import type { JSX, ReactNode } from "react";

interface PageHeaderWrapperProps {
  children: ReactNode;
  className?: string;
  testId?: string;
}

interface PageHeaderKickerProps {
  children: ReactNode;
  className?: string;
  testId?: string;
}

interface PageHeaderTitleProps {
  children: ReactNode;
  className?: string;
  size?: "default" | "hero";
  testId?: string;
}

interface PageHeaderSubtitleProps {
  children: ReactNode;
  className?: string;
  testId?: string;
}

export const PageHeaderWrapper = ({
  children,
  className,
  testId,
}: PageHeaderWrapperProps): JSX.Element => {
  return (
    <header
      className={[
        "page-header-wrapper mb-[0.35rem] grid gap-3 border-[color-mix(in_srgb,var(--shell-border)_80%,transparent)] border-b bg-transparent px-0 pt-2 pb-[0.8rem]",
        className,
      ]
        .filter(Boolean)
        .join(" ")}
      {...(testId ? { "data-testid": testId } : {})}
    >
      {children}
    </header>
  );
};

export const PageHeaderKicker = ({
  children,
  className,
  testId,
}: PageHeaderKickerProps): JSX.Element => {
  return (
    <p
      className={[
        "page-header-kicker m-0 text-(--shell-muted) text-[0.8rem] uppercase tracking-[0.08em]",
        className,
      ]
        .filter(Boolean)
        .join(" ")}
      {...(testId ? { "data-testid": testId } : {})}
    >
      {children}
    </p>
  );
};

export const PageHeaderTitle = ({
  children,
  className,
  size = "default",
  testId,
}: PageHeaderTitleProps): JSX.Element => {
  return (
    <h1
      className={[
        "page-header-title m-0 font-serif",
        size === "hero"
          ? "text-[clamp(2rem,3.9vw,3.45rem)] leading-[0.96]"
          : "text-[clamp(2rem,4vw,2.8rem)] leading-[1.05]",
        className,
      ]
        .filter(Boolean)
        .join(" ")}
      {...(testId ? { "data-testid": testId } : {})}
    >
      {children}
    </h1>
  );
};

export const PageHeaderSubtitle = ({
  children,
  className,
  testId,
}: PageHeaderSubtitleProps): JSX.Element => {
  return (
    <p
      className={["page-header-subtitle m-0 text-(--shell-muted)", className]
        .filter(Boolean)
        .join(" ")}
      {...(testId ? { "data-testid": testId } : {})}
    >
      {children}
    </p>
  );
};
