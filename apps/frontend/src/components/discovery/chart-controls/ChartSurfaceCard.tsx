import { Card } from "@heroui/react";
import React from "react";
import type { JSX, ReactNode } from "react";

interface ChartSurfaceCardProps {
  children: ReactNode;
  className?: string;
  title?: string;
  titleClassName?: string;
  testId?: string;
}

const BASE_CLASS_NAME = "min-w-0 border border-(--shell-border) bg-(--shell-surface) shadow-sm";

export const ChartSurfaceCard = ({
  children,
  className,
  title,
  titleClassName,
  testId,
}: ChartSurfaceCardProps): JSX.Element => {
  return (
    <Card
      className={`${BASE_CLASS_NAME}${className ? ` ${className}` : ""}`}
      {...(testId ? { "data-testid": testId } : {})}
      variant="default"
    >
      {title ? (
        <h2
          className={
            titleClassName ??
            "m-0 font-[Iowan_Old_Style,Palatino_Linotype,Times_New_Roman,serif] text-[1.4rem]"
          }
        >
          {title}
        </h2>
      ) : null}
      {children}
    </Card>
  );
};
