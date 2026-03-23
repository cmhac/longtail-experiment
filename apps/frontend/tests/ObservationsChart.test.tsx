import React from "react";
import type { ReactNode } from "react";
import { describe, expect, it, vi } from "vitest";
import { ObservationsChart } from "../src/components/discovery/ObservationsChart";
import { renderMarkup } from "./test-utils";

vi.mock("recharts", () => {
  const passThrough = (name: string) => {
    return ({ children }: { children?: ReactNode }) => {
      return <div data-recharts={name}>{children}</div>;
    };
  };

  return {
    Line: passThrough("Line"),
    LineChart: passThrough("LineChart"),
    Tooltip: passThrough("Tooltip"),
    XAxis: passThrough("XAxis"),
    YAxis: passThrough("YAxis"),
  };
});

describe("ObservationsChart", () => {
  it("renders chart wrapper and recharts elements for populated observations", () => {
    const markup = renderMarkup(
      <ObservationsChart
        observations={[
          {
            observed_on: "2026-01-01",
            value: 4.1,
            reported_at: "2026-01-10T00:00:00Z",
            attributes: {},
          },
        ]}
      />,
    );

    expect(markup).toContain('data-testid="observations-chart"');
    expect(markup).toContain('aria-label="Time series chart"');
    expect(markup).toContain('data-recharts="LineChart"');
    expect(markup).toContain('data-recharts="Line"');
  });

  it("renders empty state when no observations are provided", () => {
    const markup = renderMarkup(<ObservationsChart observations={[]} />);

    expect(markup).toContain("No observation data available");
    expect(markup).not.toContain('data-testid="observations-chart"');
  });
});
