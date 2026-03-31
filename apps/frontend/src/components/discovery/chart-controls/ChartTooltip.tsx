import React from "react";
import type { JSX, ReactNode } from "react";

interface ChartTooltipRootProps {
  children: ReactNode;
  className?: string;
}

interface ChartTooltipTextProps {
  children: ReactNode;
  className?: string;
}

export const ChartTooltipRoot = ({ children, className }: ChartTooltipRootProps): JSX.Element => {
  return (
    <div
      className={[
        "min-w-48 rounded-[1.15rem] bg-[color-mix(in_srgb,var(--shell-background)_96%,#ffffff)] px-5 py-4 shadow-[0_18px_50px_rgba(15,23,42,0.14)] ring-1 ring-[color-mix(in_srgb,var(--shell-border)_82%,transparent)] backdrop-blur-sm",
        className,
      ]
        .filter(Boolean)
        .join(" ")}
    >
      {children}
    </div>
  );
};

export const ChartTooltipDate = ({ children, className }: ChartTooltipTextProps): JSX.Element => {
  return (
    <p
      className={
        className ??
        "m-0 font-[Iowan_Old_Style,Palatino_Linotype,Times_New_Roman,serif] text-(--shell-muted) text-[1.05rem] italic"
      }
    >
      {children}
    </p>
  );
};

export const ChartTooltipDivider = ({ className }: { className?: string }): JSX.Element => {
  return <div className={className ?? "mt-4 h-px w-16 bg-(--shell-border)"} />;
};

export const ChartTooltipValue = ({ children, className }: ChartTooltipTextProps): JSX.Element => {
  return (
    <p
      className={
        className ??
        "mt-5 font-[Iowan_Old_Style,Palatino_Linotype,Times_New_Roman,serif] text-(--shell-foreground) text-[2.4rem] leading-none"
      }
    >
      {children}
    </p>
  );
};

export const ChartTooltipText = ({ children, className }: ChartTooltipTextProps): JSX.Element => {
  return <p className={className ?? "mt-3 text-(--shell-muted) text-[0.95rem]"}>{children}</p>;
};
