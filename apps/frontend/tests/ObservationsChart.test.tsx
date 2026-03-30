/** @vitest-environment jsdom */

import { fireEvent, render, screen, within } from "@testing-library/react";
import React from "react";
import type { ReactNode } from "react";
import { describe, expect, it, vi } from "vitest";
import { ObservationsChart } from "../src/components/discovery/ObservationsChart";
import {
  buildDatasetDetailFixture,
  buildLongHistoryDatasetDetailFixture,
  buildNoObservationsDatasetDetailFixture,
} from "./fixtures/dataset-detail-fixtures";
import { renderMarkup } from "./test-utils";

vi.mock("recharts", () => {
  const passThrough = (name: string) => {
    return ({
      children,
      ...props
    }: {
      children?: ReactNode;
      content?: ReactNode;
      dot?: boolean;
      minTickGap?: number;
      stroke?: string;
      strokeWidth?: number;
      tickMargin?: number;
      width?: number;
      height?: number;
    }) => {
      return (
        <div
          data-dot={name === "Line" ? String(props.dot) : undefined}
          data-height={
            name === "LineChart" && typeof props.height === "number"
              ? String(props.height)
              : undefined
          }
          data-has-content={name === "Tooltip" ? String(Boolean(props.content)) : undefined}
          data-min-tick-gap={name === "XAxis" ? String(props.minTickGap) : undefined}
          data-recharts={name}
          data-stroke={name === "Line" ? props.stroke : undefined}
          data-stroke-width={
            name === "Line" && typeof props.strokeWidth === "number"
              ? String(props.strokeWidth)
              : undefined
          }
          data-tick-margin={name === "XAxis" ? String(props.tickMargin) : undefined}
          data-width={
            name === "LineChart" && typeof props.width === "number"
              ? String(props.width)
              : undefined
          }
        >
          {children}
        </div>
      );
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
  class ResizeObserverMock {
    observe = vi.fn();
    disconnect = vi.fn();
    unobserve = vi.fn();
  }

  vi.stubGlobal("ResizeObserver", ResizeObserverMock);

  it("renders chart wrapper and recharts elements for populated observations", () => {
    const fixture = buildLongHistoryDatasetDetailFixture();
    const markup = renderMarkup(<ObservationsChart observations={fixture.observations} />);

    expect(markup).toContain('data-testid="observations-chart"');
    expect(markup).toContain('aria-label="Time series chart"');
    expect(markup).toContain('data-testid="observations-chart-controls"');
    expect(markup).toContain('aria-pressed="true"');
    expect(markup).not.toContain('data-testid="observations-chart-footnote"');
    expect(markup).toContain('data-recharts="LineChart"');
    expect(markup).toContain('data-recharts="Line"');
    expect(markup).toContain('data-has-content="true"');
    expect(markup).toContain('data-dot="false"');
    expect(markup).toContain('data-stroke="var(--shell-foreground)"');
    expect(markup).toContain('data-stroke-width="2.25"');
    expect(markup).toContain('data-min-tick-gap="32"');
    expect(markup).toContain('data-tick-margin="14"');
  });

  it("renders empty state when no observations are provided", () => {
    const markup = renderMarkup(
      <ObservationsChart observations={buildNoObservationsDatasetDetailFixture().observations} />,
    );

    expect(markup).toContain("No observation data available");
    expect(markup).not.toContain('data-testid="observations-chart"');
  });

  it("defaults to all-history and updates active range when controls are clicked", () => {
    render(
      <ObservationsChart observations={buildLongHistoryDatasetDetailFixture().observations} />,
    );

    const monthlyButton = screen.getByRole("button", { name: "1M" });
    const allButton = screen.getByRole("button", { name: "ALL" });

    expect(allButton.getAttribute("aria-pressed")).toBe("true");
    fireEvent.click(monthlyButton);
    expect(monthlyButton.getAttribute("aria-pressed")).toBe("true");
    expect(allButton.getAttribute("aria-pressed")).toBe("false");
  });

  it("renders visible controls from longest to shortest with pointer cursor styling", () => {
    const { container } = render(
      <ObservationsChart observations={buildLongHistoryDatasetDetailFixture().observations} />,
    );

    const chart = within(container);
    const buttons = chart.getAllByRole("button");

    expect(buttons.map((button) => button.textContent)).toEqual(["ALL", "5Y", "1Y", "6M", "1M"]);
    for (const button of buttons) {
      expect(button.className).toContain("cursor-pointer");
    }
  });

  it("hides the controls when only all-history is available", () => {
    const markup = renderMarkup(
      <ObservationsChart observations={buildDatasetDetailFixture().observations} />,
    );

    expect(markup).not.toContain('data-testid="observations-chart-controls"');
  });
});
