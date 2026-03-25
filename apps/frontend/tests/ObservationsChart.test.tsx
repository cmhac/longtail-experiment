/** @vitest-environment jsdom */

import { fireEvent, render, screen } from "@testing-library/react";
import React from "react";
import type { ReactNode } from "react";
import { describe, expect, it, vi } from "vitest";
import { ObservationsChart } from "../src/components/discovery/ObservationsChart";
import { buildDatasetDetailFixture } from "./fixtures/dataset-detail-fixtures";
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
    const fixture = buildDatasetDetailFixture();
    const markup = renderMarkup(<ObservationsChart observations={fixture.observations} />);

    expect(markup).toContain('data-testid="observations-chart"');
    expect(markup).toContain('aria-label="Time series chart"');
    expect(markup).toContain('data-testid="observations-chart-controls"');
    expect(markup).toContain('aria-pressed="false"');
    expect(markup).toContain('data-testid="observations-chart-footnote"');
    expect(markup).toContain('data-recharts="LineChart"');
    expect(markup).toContain('data-recharts="Line"');
  });

  it("renders empty state when no observations are provided", () => {
    const markup = renderMarkup(<ObservationsChart observations={[]} />);

    expect(markup).toContain("No observation data available");
    expect(markup).not.toContain('data-testid="observations-chart"');
  });

  it("updates active range when controls are clicked", () => {
    render(<ObservationsChart observations={buildDatasetDetailFixture().observations} />);

    const annualButton = screen.getByRole("button", { name: "1Y" });
    const allButton = screen.getByRole("button", { name: "ALL" });

    expect(annualButton.getAttribute("aria-pressed")).toBe("true");
    fireEvent.click(allButton);
    expect(allButton.getAttribute("aria-pressed")).toBe("true");
    expect(annualButton.getAttribute("aria-pressed")).toBe("false");
  });
});
