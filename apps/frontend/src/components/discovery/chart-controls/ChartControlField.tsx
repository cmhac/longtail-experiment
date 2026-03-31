import React from "react";
import type { JSX, ReactNode } from "react";

interface ChartControlFieldProps {
  children: ReactNode;
  className?: string;
  htmlFor?: string;
  label: string;
}

export const ChartControlField = ({
  children,
  className,
  htmlFor,
  label,
}: ChartControlFieldProps): JSX.Element => {
  return (
    <div className={className ?? "flex w-full flex-col gap-1"}>
      <label className="px-1 text-[0.68rem] tracking-[0.06em]" htmlFor={htmlFor}>
        {label}
      </label>
      {children}
    </div>
  );
};
