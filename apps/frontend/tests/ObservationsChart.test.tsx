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
  buildRelativeChangeFixture,
} from "./fixtures/dataset-detail-fixtures";
import { renderMarkup } from "./test-utils";

void React;

vi.mock("@heroui/react", () => {
  interface MockComboBoxItem {
    value: string;
    label: string;
  }

  interface MockComboBoxProps {
    children?: React.ReactNode;
    items?: MockComboBoxItem[];
    onSelectionChange?: (value: string) => void;
    selectedKey?: string;
    "aria-label"?: string;
    "data-testid"?: string;
  }

  const ComboBoxRoot = ({
    children,
    items,
    onSelectionChange,
    selectedKey,
    "aria-label": ariaLabel,
    "data-testid": dataTestId,
  }: MockComboBoxProps) => {
    return (
      <div data-testid={dataTestId}>
        <select
          aria-label={ariaLabel}
          onChange={(event) => onSelectionChange?.(event.target.value)}
          value={selectedKey ?? ""}
        >
          {(items ?? []).map((item) => (
            <option key={item.value} value={item.value}>
              {item.label}
            </option>
          ))}
        </select>
        {children}
      </div>
    );
  };

  const Input = ({ children, ...props }: { children?: React.ReactNode }) => (
    <div {...props}>{children}</div>
  );
  const ListBox = ({ children, ...props }: { children: React.ReactNode }) => (
    <div {...props}>{children}</div>
  );
  const ListBoxItem = ({ children, ...props }: { children: React.ReactNode }) => (
    <div {...props}>{children}</div>
  );
  const ComboBox = Object.assign(ComboBoxRoot, {
    Root: ComboBoxRoot,
    InputGroup: ({ children, ...props }: { children: React.ReactNode }) => (
      <div {...props}>{children}</div>
    ),
    Trigger: ({ children, ...props }: { children?: React.ReactNode }) => (
      <div {...props}>{children}</div>
    ),
    Popover: ({ children, ...props }: { children: React.ReactNode }) => (
      <div {...props}>{children}</div>
    ),
  });

  return {
    ComboBox,
    Input,
    ListBox,
    ListBoxItem,
  };
});

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
      tickFormatter?: (value: number) => string;
      width?: number;
      height?: number;
      data?: Array<{ date?: string }>;
    }) => {
      const tickSample =
        name === "YAxis" && typeof props.tickFormatter === "function"
          ? props.tickFormatter(1.5)
          : undefined;

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
          data-series-first-date={
            name === "LineChart" && Array.isArray(props.data) && props.data[0]?.date
              ? String(props.data[0].date)
              : undefined
          }
          data-series-length={
            name === "LineChart" && Array.isArray(props.data)
              ? String(props.data.length)
              : undefined
          }
          data-stroke={name === "Line" ? props.stroke : undefined}
          data-stroke-width={
            name === "Line" && typeof props.strokeWidth === "number"
              ? String(props.strokeWidth)
              : undefined
          }
          data-tick-margin={name === "XAxis" ? String(props.tickMargin) : undefined}
          data-tick-sample={name === "YAxis" ? tickSample : undefined}
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
    const rangeControls = chart.getByTestId("observations-chart-controls");
    const buttons = within(rangeControls).getAllByRole("button");

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

  it("toggles between observed and relative modes", () => {
    const { container } = render(
      <ObservationsChart observations={buildRelativeChangeFixture().observations} />,
    );
    const chart = within(container);

    const observedButton = chart.getByRole("button", { name: "Observed" });
    const relativeButton = chart.getByRole("button", { name: "Relative %" });

    expect(observedButton.getAttribute("aria-pressed")).toBe("true");
    fireEvent.click(relativeButton);
    expect(relativeButton.getAttribute("aria-pressed")).toBe("true");
    expect(observedButton.getAttribute("aria-pressed")).toBe("false");
    expect(chart.getByTestId("observations-chart-relative-controls")).toBeDefined();
  });

  it("renders rolling baseline controls and supports offset switching", () => {
    const { container } = render(
      <ObservationsChart observations={buildRelativeChangeFixture().observations} />,
    );
    const chart = within(container);

    fireEvent.click(chart.getByRole("button", { name: "Relative %" }));
    const rollingOffset = chart.getByLabelText("Rolling offset") as HTMLSelectElement;

    expect(rollingOffset.value).toBe("1");
    fireEvent.change(rollingOffset, { target: { value: "2" } });
    expect(rollingOffset.value).toBe("2");
  });

  it("supports fixed baseline mode with exact available date options", () => {
    const fixture = buildRelativeChangeFixture();
    const { container } = render(<ObservationsChart observations={fixture.observations} />);
    const chart = within(container);

    fireEvent.click(chart.getByRole("button", { name: "Relative %" }));
    fireEvent.change(chart.getByLabelText("Relative baseline mode"), {
      target: { value: "fixed" },
    });
    fireEvent.change(chart.getByLabelText("Fixed baseline source"), {
      target: { value: "date" },
    });

    const dateSelect = chart.getByLabelText("Fixed baseline date") as HTMLSelectElement;
    const options = Array.from(dateSelect.options).map((option) => option.value);

    expect(options).toContain("2024-01-01");
    expect(options).toContain("2024-01-08");
    expect(options).toContain("2024-01-15");
    expect(options).toContain("2024-01-22");
    expect(options).not.toContain("2024-02-01");
    expect(options.slice(1, 5)).toEqual(["2024-01-22", "2024-01-15", "2024-01-08", "2024-01-01"]);

    fireEvent.change(dateSelect, { target: { value: "2024-01-08" } });
    expect(dateSelect.value).toBe("2024-01-08");
  });

  it("supports fixed baseline mode using offset selection", () => {
    const { container } = render(
      <ObservationsChart observations={buildRelativeChangeFixture().observations} />,
    );
    const chart = within(container);

    fireEvent.click(chart.getByRole("button", { name: "Relative %" }));
    fireEvent.change(chart.getByLabelText("Relative baseline mode"), {
      target: { value: "fixed" },
    });
    fireEvent.change(chart.getByLabelText("Fixed baseline source"), {
      target: { value: "offset" },
    });

    const offsetSelect = chart.getByLabelText("Fixed baseline offset") as HTMLSelectElement;
    expect(offsetSelect.value).toBe("12");
    fireEvent.change(offsetSelect, { target: { value: "2" } });
    expect(offsetSelect.value).toBe("2");
  });

  it("shows unavailable state for invalid preserved fixed-baseline settings", () => {
    const { container } = render(
      <ObservationsChart
        observations={buildRelativeChangeFixture().observations}
        relativeSettings={{
          baselineMode: "fixed",
          fixedBaselineDate: "2024-02-01",
          fixedBaselineOffset: 12,
          fixedSelectionMode: "date",
          rollingOffset: 1,
          valueMode: "relative",
        }}
      />,
    );
    const chart = within(container);

    const unavailable = chart.getByTestId("relative-change-unavailable");
    expect(unavailable.textContent).toContain("Selected baseline is unavailable");

    const dateSelect = chart.getByLabelText("Fixed baseline date") as HTMLSelectElement;
    const options = Array.from(dateSelect.options).map((option) => option.value);
    expect(options).toContain("2024-02-01");
    expect(dateSelect.value).toBe("2024-02-01");
  });

  it("preserves fixed baseline settings across range changes and shows unavailable state when invalid", () => {
    const fixture = buildLongHistoryDatasetDetailFixture();
    const relativeSettings = {
      baselineMode: "fixed" as const,
      fixedBaselineDate: fixture.observations[0]?.observed_on ?? null,
      fixedBaselineOffset: 12,
      fixedSelectionMode: "date" as const,
      rollingOffset: 1,
      valueMode: "relative" as const,
    };

    const { container, rerender } = render(
      <ObservationsChart
        observations={fixture.observations}
        relativeSettings={relativeSettings}
        selectedRange="ALL"
      />,
    );
    const chart = within(container);
    const dateSelect = chart.getByLabelText("Fixed baseline date") as HTMLSelectElement;
    expect(dateSelect.value).toBe(relativeSettings.fixedBaselineDate);

    rerender(
      <ObservationsChart
        observations={fixture.observations}
        relativeSettings={relativeSettings}
        selectedRange="1M"
      />,
    );

    const nextDateSelect = chart.getByLabelText("Fixed baseline date") as HTMLSelectElement;
    expect(nextDateSelect.value).toBe(relativeSettings.fixedBaselineDate);
    expect(chart.queryByTestId("relative-change-unavailable")).toBeNull();
    expect(chart.getByTestId("fixed-baseline-note")).toBeDefined();
  });

  it("disables year filter buttons when fixed baseline mode is active", () => {
    const fixture = buildLongHistoryDatasetDetailFixture();
    const { container } = render(
      <ObservationsChart
        observations={fixture.observations}
        relativeSettings={{
          baselineMode: "fixed",
          fixedBaselineDate: fixture.observations[0]?.observed_on ?? null,
          fixedBaselineOffset: 12,
          fixedSelectionMode: "date",
          rollingOffset: 1,
          valueMode: "relative",
        }}
        selectedRange="1M"
      />,
    );
    const chart = within(container);
    const rangeButtons = within(chart.getByTestId("observations-chart-controls")).getAllByRole(
      "button",
    );

    for (const button of rangeButtons) {
      expect(button.getAttribute("disabled")).not.toBeNull();
    }
  });

  it("starts fixed baseline chart timeline at the selected baseline date", () => {
    const fixture = buildLongHistoryDatasetDetailFixture();
    const baselineDate = fixture.observations[0]?.observed_on ?? null;

    const markup = renderMarkup(
      <ObservationsChart
        observations={fixture.observations}
        relativeSettings={{
          baselineMode: "fixed",
          fixedBaselineDate: baselineDate,
          fixedBaselineOffset: 12,
          fixedSelectionMode: "date",
          rollingOffset: 1,
          valueMode: "relative",
        }}
        selectedRange="1M"
      />,
    );

    expect(markup).toContain(`data-series-first-date="${baselineDate}"`);
    expect(markup).toContain('data-testid="fixed-baseline-note"');
  });
});
